import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import UploadForm from './UploadForm';
import { RecentUpload } from '../hooks/useRecentUploads';

interface UploadFormProps {
  file: File | null
  jumpType: 'cmj' | 'dropjump'
  loading: boolean
  enableDebug: boolean
  recentUploads: RecentUpload[]
  onFileChange: (file: File | null) => void
  onJumpTypeChange: (jumpType: 'cmj' | 'dropjump') => void
  onEnableDebugChange: (enable: boolean) => void
  onAnalyze: () => void
  onClearHistory?: () => void
}

describe('UploadForm', () => {
  let mockOnAnalyze: ReturnType<typeof vi.fn>;
  let mockOnClearHistory: ReturnType<typeof vi.fn>;
  let mockOnFileChange: ReturnType<typeof vi.fn>;
  let mockOnJumpTypeChange: ReturnType<typeof vi.fn>;
  let mockOnEnableDebugChange: ReturnType<typeof vi.fn>;

  let currentProps: any;

  // Helper to create fresh props for each test
  const createProps = (overrides?: Partial<UploadFormProps>) => {
    const props = {
      file: null,
      jumpType: 'cmj' as 'cmj' | 'dropjump',
      loading: false,
      enableDebug: false,
      recentUploads: [] as RecentUpload[],
      onFileChange: mockOnFileChange,
      onJumpTypeChange: mockOnJumpTypeChange,
      onEnableDebugChange: mockOnEnableDebugChange,
      onAnalyze: mockOnAnalyze,
      onClearHistory: mockOnClearHistory,
      ...overrides,
    };
    return props;
  };

  beforeEach(() => {
    // Create fresh mocks for each test
    mockOnAnalyze = vi.fn();
    mockOnClearHistory = vi.fn();
    mockOnFileChange = vi.fn();
    mockOnJumpTypeChange = vi.fn();
    mockOnEnableDebugChange = vi.fn();

    currentProps = createProps(); // Initialize default props for the test
  });

  it('renders correctly in initial state', () => {
    render(<UploadForm {...currentProps} />);

    expect(screen.getByText('CMJ')).toBeInTheDocument();
    expect(screen.getByText('CMJ')).toHaveClass('active');
    expect(screen.getByText('Drop Jump')).toBeInTheDocument();
    expect(screen.getByLabelText('Generate Overlay')).not.toBeChecked();
    expect(screen.getByText('Drag analysis video here')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Run Analysis/i })).toBeDisabled();
  });

  it('calls onJumpTypeChange when CMJ button is clicked', () => {
    currentProps = createProps({ jumpType: 'dropjump' });
    render(<UploadForm {...currentProps} />);
    fireEvent.click(screen.getByText('CMJ'));
    expect(mockOnJumpTypeChange).toHaveBeenCalledWith('cmj');
  });

  it('calls onJumpTypeChange when Drop Jump button is clicked', () => {
    currentProps = createProps({ jumpType: 'cmj' });
    render(<UploadForm {...currentProps} />);
    fireEvent.click(screen.getByText('Drop Jump'));
    expect(mockOnJumpTypeChange).toHaveBeenCalledWith('dropjump');
  });

  it('calls onEnableDebugChange when Generate Overlay checkbox is toggled', async () => {
    // Initial render with default props (enableDebug: false)
    const { rerender } = render(<UploadForm {...currentProps} />);
    const checkbox = screen.getByLabelText('Generate Overlay');

    await act(async () => {
      fireEvent.click(checkbox);
    });
    expect(mockOnEnableDebugChange).toHaveBeenCalledWith(true);

    // Clear mock to cleanly test the next interaction
    mockOnEnableDebugChange.mockClear();

    // Rerender with updated prop to simulate parent state update
    rerender(<UploadForm {...currentProps} enableDebug={true} />);

    await act(async () => {
      fireEvent.click(checkbox);
    });
    expect(mockOnEnableDebugChange).toHaveBeenCalledWith(false);
  });

  it('enables analyze button when a file is selected', () => {
    const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    currentProps = createProps({ file: file });
    render(<UploadForm {...currentProps} />);
    expect(screen.getByRole('button', { name: /Run Analysis/i })).not.toBeDisabled();
  });

  it('disables analyze button when no file is selected', () => {
    currentProps = createProps({ file: null });
    render(<UploadForm {...currentProps} />);
    expect(screen.getByRole('button', { name: /Run Analysis/i })).toBeDisabled();
  });

  it('shows loading state for analyze button when loading', () => {
    const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    currentProps = createProps({ file: file, loading: true });
    render(<UploadForm {...currentProps} />);
    expect(screen.getByRole('button', { name: /Analyzing.../i })).toBeDisabled();
  });

  it('handles valid file selection via input', async () => {
    const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    const { rerender } = render(<UploadForm {...currentProps} />); // Initial render
    const input = screen.getByTestId('file-input');

    await act(async () => {
      fireEvent.change(input, { target: { files: [file] } });
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(file);
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    currentProps = createProps({ file: file }); // Update props with the file
    rerender(<UploadForm {...currentProps} />); // Re-render with selected file
    expect(screen.getByText(/test\.mp4/)).toBeInTheDocument();
  });

  it('shows error for invalid file type via input', async () => {
    const invalidFile = new File(['text content'], 'test.txt', { type: 'text/plain' });
    const { rerender } = render(<UploadForm {...currentProps} />);
    const input = screen.getByTestId('file-input');

    await act(async () => {
      fireEvent.change(input, { target: { files: [invalidFile] } });
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(null);
    expect(screen.getByRole('alert')).toHaveTextContent('Please select a valid video file');
    currentProps = createProps({ file: null }); // Update props with no file
    rerender(<UploadForm {...currentProps} />); // Re-render with no file
    expect(screen.queryByText('test.txt')).not.toBeInTheDocument();
  });

  it('shows error for large file via input', async () => {
    const largeFile = new File(['a'], 'large.mp4', { type: 'video/mp4' });
    Object.defineProperty(largeFile, 'size', { value: 500 * 1024 * 1024 + 1 });
    const { rerender } = render(<UploadForm {...currentProps} />);
    const input = screen.getByTestId('file-input');

    await act(async () => {
      fireEvent.change(input, { target: { files: [largeFile] } });
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(null);
    expect(screen.getByRole('alert')).toHaveTextContent(/File size must be less than 500MB/);
    currentProps = createProps({ file: null }); // Update props with no file
    rerender(<UploadForm {...currentProps} />); // Re-render with no file
    expect(screen.queryByText('large.mp4')).not.toBeInTheDocument();
  });

  it('handles valid file drop', async () => {
    const file = new File(['video content'], 'dragged.mp4', { type: 'video/mp4' });
    const { rerender } = render(<UploadForm {...currentProps} />);
    const dropZone = screen.getByText('Drag analysis video here').closest('.upload-drop-zone');

    await act(async () => {
      fireEvent.drop(dropZone!, { dataTransfer: { files: [file] } });
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(file);
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    currentProps = createProps({ file: file }); // Update props with the dropped file
    rerender(<UploadForm {...currentProps} />); // Re-render with the dropped file
    expect(screen.getByText(/dragged\.mp4/)).toBeInTheDocument();
  });

  it('shows error for invalid file type on drop', async () => {
    const invalidFile = new File(['text content'], 'dragged.txt', { type: 'text/plain' });
    const { rerender } = render(<UploadForm {...currentProps} />);
    const dropZone = screen.getByText('Drag analysis video here').closest('.upload-drop-zone');

    await act(async () => {
      fireEvent.drop(dropZone!, { dataTransfer: { files: [invalidFile] } });
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(null);
    expect(screen.getByRole('alert')).toHaveTextContent('Please select a valid video file');
    currentProps = createProps({ file: null }); // Update props with no file
    rerender(<UploadForm {...currentProps} />); // Re-render with no file
  });

  it('shows error for large file on drop', async () => {
    const largeFile = new File(['a'], 'large.mp4', { type: 'video/mp4' });
    Object.defineProperty(largeFile, 'size', { value: 500 * 1024 * 1024 + 1 });
    const { rerender } = render(<UploadForm {...currentProps} />);
    const dropZone = screen.getByText('Drag analysis video here').closest('.upload-drop-zone');

    await act(async () => {
      fireEvent.drop(dropZone!, { dataTransfer: { files: [largeFile] } });
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(null);
    expect(screen.getByRole('alert')).toHaveTextContent(/File size must be less than 500MB/);
    currentProps = createProps({ file: null }); // Update props with no file
    rerender(<UploadForm {...currentProps} />); // Re-render with no file
  });

  it('calls onAnalyze when button is clicked and file is present', async () => {
    const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    currentProps = createProps({ file: file });
    render(<UploadForm {...currentProps} />);
    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /Run Analysis/i }));
    });
    expect(mockOnAnalyze).toHaveBeenCalledTimes(1);
  });

  it('calls onFileChange(null) and clears error when \'Change\' button is clicked', async () => {
    const file = new File(['video content'], 'test.mp4', { type: 'video/mp4' });
    currentProps = createProps({ file: file });
    const { rerender } = render(<UploadForm {...currentProps} />);

    await act(async () => {
      fireEvent.click(screen.getByText('Change'));
    });

    expect(mockOnFileChange).toHaveBeenCalledWith(null);
    currentProps = createProps({ file: null }); // Update props with no file
    rerender(<UploadForm {...currentProps} />); // Re-render with no file
    expect(screen.queryByText('test.mp4')).not.toBeInTheDocument();
  });

  it('calls onClearHistory when Clear History button is clicked', () => {
    const recentUploads: RecentUpload[] = [{
      filename: 'old-jump.mp4',
      jumpType: 'cmj',
      timestamp: Date.now(),
      id: '123'
    }];
    currentProps = createProps({ recentUploads: recentUploads });
    render(<UploadForm {...currentProps} />);
    fireEvent.click(screen.getByRole('button', { name: /Clear/i }));
    expect(mockOnClearHistory).toHaveBeenCalledTimes(1);
  });
});
