import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useAnalysis } from './useAnalysis';

// Mock Supabase
vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: { access_token: 'mock-token' } } }),
    },
  },
}));

describe('useAnalysis Hook', () => {
  let mockXHR: any;

  beforeEach(() => {
    vi.clearAllMocks();

    // 1. Create the spies object
    mockXHR = {
      open: vi.fn(),
      send: vi.fn(),
      setRequestHeader: vi.fn(),
      upload: {
        addEventListener: vi.fn(),
      },
      addEventListener: vi.fn(),
      status: 200,
      responseText: '',
    };

    // 2. Create a Mock Class that behaves like XMLHttpRequest
    class MockXMLHttpRequest {
      open(...args: any[]) { return mockXHR.open(...args); }
      send(...args: any[]) { return mockXHR.send(...args); }
      setRequestHeader(...args: any[]) { return mockXHR.setRequestHeader(...args); }
      get upload() { return mockXHR.upload; }
      addEventListener(...args: any[]) { return mockXHR.addEventListener(...args); }
      get status() { return mockXHR.status; }
      set status(v) { mockXHR.status = v; }
      get responseText() { return mockXHR.responseText; }
      set responseText(v) { mockXHR.responseText = v; }
    }

    // 3. Assign to global
    vi.stubGlobal('XMLHttpRequest', MockXMLHttpRequest);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useAnalysis());

    expect(result.current.file).toBeNull();
    expect(result.current.jumpType).toBe('cmj');
    expect(result.current.loading).toBe(false);
    expect(result.current.metrics).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.uploadProgress).toBe(0);
  });

  it('should set file and jump type', () => {
    const { result } = renderHook(() => useAnalysis());
    const file = new File(['dummy content'], 'test.mp4', { type: 'video/mp4' });

    act(() => {
      result.current.setFile(file);
      result.current.setJumpType('dropjump');
    });

    expect(result.current.file).toBe(file);
    expect(result.current.jumpType).toBe('dropjump');
  });

  it('should show error if analyze is called without a file', async () => {
    const { result } = renderHook(() => useAnalysis());

    await act(async () => {
      await result.current.analyze();
    });

    expect(result.current.error).toBe('Please select a video file');
    expect(result.current.loading).toBe(false);
  });

  it('should handle successful analysis flow', async () => {
    const { result } = renderHook(() => useAnalysis());
    const file = new File(['dummy content'], 'test.mp4', { type: 'video/mp4' });
    const mockResponse = {
      status: 200,
      message: 'Success',
      metrics: { data: { jump_height_m: 0.5 } }
    };

    // Setup behavior
    const eventListeners: Record<string, EventListener> = {};
    const uploadEventListeners: Record<string, EventListener> = {};

    mockXHR.addEventListener.mockImplementation((event: string, cb: EventListener) => {
      eventListeners[event] = cb;
    });
    mockXHR.upload.addEventListener.mockImplementation((event: string, cb: EventListener) => {
      uploadEventListeners[event] = cb;
    });
    mockXHR.status = 200;
    mockXHR.responseText = JSON.stringify(mockResponse);

    // Set file
    act(() => {
      result.current.setFile(file);
    });

    // Trigger analyze
    let analyzePromise: Promise<void>;
    await act(async () => {
      analyzePromise = result.current.analyze();
    });

    // Check loading state (sync check after async start)
    expect(result.current.loading).toBe(true);

    // Simulate Upload Progress
    act(() => {
      if (uploadEventListeners['progress']) {
        uploadEventListeners['progress']({
          lengthComputable: true,
          loaded: 50,
          total: 100
        } as ProgressEvent);
      }
    });

    expect(result.current.uploadProgress).toBe(50);

    // Simulate Success
    await act(async () => {
      if (eventListeners['load']) {
        eventListeners['load']({} as Event);
      }
    });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.metrics).toEqual(mockResponse);
    expect(result.current.error).toBeNull();
    expect(mockXHR.open).toHaveBeenCalledWith('POST', expect.stringContaining('/api/analyze'));
    expect(mockXHR.setRequestHeader).toHaveBeenCalledWith('Authorization', 'Bearer mock-token');
  });

  it('should handle API error', async () => {
    const { result } = renderHook(() => useAnalysis());
    const file = new File(['dummy content'], 'test.mp4', { type: 'video/mp4' });
    const errorMessage = 'Invalid video format';

    // Setup behavior
    const eventListeners: Record<string, EventListener> = {};
    mockXHR.addEventListener.mockImplementation((event: string, cb: EventListener) => {
      eventListeners[event] = cb;
    });
    mockXHR.status = 400;
    mockXHR.responseText = JSON.stringify({ error: errorMessage });

    act(() => {
      result.current.setFile(file);
    });

    await act(async () => {
      result.current.analyze();
    });

    // Simulate Error Load
    await act(async () => {
      if (eventListeners['load']) {
        eventListeners['load']({} as Event);
      }
    });

    expect(result.current.error).toBe(errorMessage);
    expect(result.current.loading).toBe(false);
    expect(result.current.metrics).toBeNull();
  });

  it('should handle Network error', async () => {
    const { result } = renderHook(() => useAnalysis());
    const file = new File(['dummy content'], 'test.mp4', { type: 'video/mp4' });

    // Setup behavior
    const eventListeners: Record<string, EventListener> = {};
    mockXHR.addEventListener.mockImplementation((event: string, cb: EventListener) => {
      eventListeners[event] = cb;
    });

    act(() => {
      result.current.setFile(file);
    });

    await act(async () => {
      result.current.analyze();
    });

    // Simulate Network Error
    await act(async () => {
      if (eventListeners['error']) {
        eventListeners['error']({} as Event);
      }
    });

    expect(result.current.error).toBe('Network error: Unable to connect to the server');
    expect(result.current.loading).toBe(false);
  });

  it('should reset state', () => {
    const { result } = renderHook(() => useAnalysis());

    act(() => {
      result.current.setFile(new File([], 'test.mp4'));
      result.current.setJumpType('dropjump');
      result.current.setEnableDebug(true);
    });

    expect(result.current.file).not.toBeNull();
    expect(result.current.jumpType).toBe('dropjump');
    expect(result.current.enableDebug).toBe(true);

    act(() => {
      result.current.reset();
    });

    expect(result.current.file).toBeNull();
    expect(result.current.jumpType).toBe('cmj');
    expect(result.current.enableDebug).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.metrics).toBeNull();
  });
});
