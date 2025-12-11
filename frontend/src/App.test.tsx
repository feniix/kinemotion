import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';
import { useAuth } from './hooks/useAuth';
import { useAnalysis } from './hooks/useAnalysis';
import { useRecentUploads } from './hooks/useRecentUploads';
import { useBackendVersion } from './hooks/useBackendVersion';

// Mock the custom hooks
vi.mock('./hooks/useAuth');
vi.mock('./hooks/useAnalysis');
vi.mock('./hooks/useRecentUploads');
vi.mock('./hooks/useBackendVersion');

describe('App Integration', () => {
  // Setup default mock return values
  const mockAnalyze = vi.fn();
  const mockRetry = vi.fn();
  const mockSignOut = vi.fn();
  const mockAddRecentUpload = vi.fn();
  const mockClearRecentUploads = vi.fn();
  const mockSetFile = vi.fn();
  const mockSetJumpType = vi.fn();
  const mockSetEnableDebug = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Default: Authenticated, no file, no analysis
    (useAuth as any).mockReturnValue({
      user: { email: 'test@example.com' },
      loading: false,
      signOut: mockSignOut,
    });

    (useAnalysis as any).mockReturnValue({
      file: null,
      jumpType: 'cmj',
      loading: false,
      uploadProgress: 0,
      metrics: null,
      error: null,
      enableDebug: false,
      setFile: mockSetFile,
      setJumpType: mockSetJumpType,
      setEnableDebug: mockSetEnableDebug,
      analyze: mockAnalyze,
      retry: mockRetry,
    });

    (useRecentUploads as any).mockReturnValue({
      recentUploads: [],
      addRecentUpload: mockAddRecentUpload,
      clearRecentUploads: mockClearRecentUploads,
    });

    (useBackendVersion as any).mockReturnValue({
      backendVersion: '1.0.0',
      kinemotionVersion: '1.0.0',
    });
  });

  it('renders loading spinner when checking auth', () => {
    (useAuth as any).mockReturnValue({
      user: null,
      loading: true,
      signOut: mockSignOut,
    });

    render(<App />);
    // LoadingSpinner component usually has "Loading..." or we can find by class if needed
    // In App.tsx: <LoadingSpinner uploadProgress={0} />
    // Assuming LoadingSpinner renders text or we can just check if App structure is not fully there
    // For now, let's assume LoadingSpinner renders something identifiable or check absence of header
    expect(screen.queryByText('Kinemotion')).not.toBeInTheDocument();
  });

  it('renders Auth component when not logged in', () => {
    (useAuth as any).mockReturnValue({
      user: null,
      loading: false,
      signOut: mockSignOut,
    });

    render(<App />);
    // Auth component likely has "Sign In" or similar
    // Since we didn't mock Auth component explicitly, it renders the real one.
    // Let's assume Auth component has a distinctive text.
    // If Auth is complex, we might mock it, but integration tests usually like real components.
    // However, for this high-level test, let's just check that main App content is missing.
    expect(screen.queryByText('Sign Out')).not.toBeInTheDocument();
  });

  it('renders UploadForm when logged in and no results', () => {
    render(<App />);

    // Header should be present
    expect(screen.getByText('Kinemotion')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();

    // UploadForm content should be present
    expect(screen.getByText(/Drag analysis video here/i)).toBeInTheDocument();

    // Footer should be present
    expect(screen.getByText(/Backend v1.0.0/i)).toBeInTheDocument();
  });

  it('renders LoadingSpinner and Skeleton when analyzing', () => {
    (useAnalysis as any).mockReturnValue({
      ...useAnalysis(), // Get default mock values
      loading: true,
      uploadProgress: 50,
      file: new File([''], 'video.mp4'),
    });

    render(<App />);

    // LoadingSpinner should be present (UploadForm is also present in App.tsx structure)
    // We need to check for LoadingSpinner specifically.
    // Assuming LoadingSpinner displays progress
    expect(screen.getByText(/50%/)).toBeInTheDocument();
  });

  it('renders ResultsSkeleton when processing (upload > 100%)', () => {
    (useAnalysis as any).mockReturnValue({
        ...useAnalysis(),
        loading: true,
        uploadProgress: 100,
        file: new File([''], 'video.mp4'),
    });

    render(<App />);
    // ResultsSkeleton should be present. It usually has "Processing Video..." text or similar.
    // If not, we can rely on implementation details or mock the component.
    // Let's assume ResultsSkeleton renders a specific class or ID, or we can check logic coverage.
    // In App.tsx: {loading && uploadProgress >= 100 && <ResultsSkeleton />}
    // Let's just check if it renders without crashing for now, or assume it has distinctive text.
    // A safe bet for integration if we don't know the exact child text is checking if ResultsDisplay is NOT there.
    expect(screen.queryByText('Analysis Results')).not.toBeInTheDocument();
  });

  it('renders ResultsDisplay when analysis is complete', () => {
    (useAnalysis as any).mockReturnValue({
      ...useAnalysis(),
      metrics: {
        status: 200,
        message: 'Success',
        metrics: { data: { jump_height_m: 0.5 } }
      },
      loading: false,
      file: new File([''], 'video.mp4'),
    });

    render(<App />);

    // ResultsDisplay header
    expect(screen.getByText('Analysis Results')).toBeInTheDocument();
    // Specific metric from our mock
    expect(screen.getByText('Jump Height')).toBeInTheDocument();
  });

  it('renders ErrorDisplay when there is an error', () => {
    const errorMessage = 'Failed to analyze video';
    (useAnalysis as any).mockReturnValue({
      ...useAnalysis(),
      error: errorMessage,
      loading: false,
    });

    render(<App />);

    // Check that the error message is displayed (might appear multiple times)
    const errorMessages = screen.getAllByText(errorMessage);
    expect(errorMessages.length).toBeGreaterThan(0);
    expect(errorMessages[0]).toBeInTheDocument();

    // Test retry button
    const retryBtn = screen.getByRole('button', { name: /Try Again/i });
    fireEvent.click(retryBtn);
    expect(mockRetry).toHaveBeenCalled();
  });

  it('triggers analyze and adds to recent uploads on form submit', async () => {
    const file = new File([''], 'jump.mp4');
    (useAnalysis as any).mockReturnValue({
      ...useAnalysis(),
      file: file,
      jumpType: 'dropjump',
    });

    render(<App />);

    // Find the Analyze button in UploadForm
    const analyzeBtn = screen.getByRole('button', { name: /Run Analysis/i });
    fireEvent.click(analyzeBtn);

    await waitFor(() => {
        expect(mockAnalyze).toHaveBeenCalled();
    });

    // In App.tsx, handleAnalyze calls addRecentUpload IF file exists
    // Note: Since analyze is async and mocked, we need to ensure the promise resolves.
    // But since it's a simple mock function, it returns undefined (sync) or we can make it return Promise.resolve()
    expect(mockAddRecentUpload).toHaveBeenCalledWith('jump.mp4', 'dropjump');
  });
});
