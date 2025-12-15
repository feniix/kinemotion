import { render, screen } from '@testing-library/react'
import LoadingSpinner from './LoadingSpinner'
import { useLanguage } from '../hooks/useLanguage'

vi.mock('../hooks/useLanguage')

describe('LoadingSpinner', () => {
  const mockT = vi.fn((key: string, options?: Record<string, unknown>) => {
    const translations: Record<string, string> = {
      'loading.uploadingVideo': 'Uploading Video',
      'loading.analyzingVideo': 'Analyzing Video',
      'loading.estimatedTime': 'This typically takes 10-60 seconds',
      'loading.uploadProgress': `Upload progress: ${options?.progress}%`,
      'loading.steps.uploading': 'Uploading video',
      'loading.steps.processing': 'Processing video frames',
      'loading.steps.detecting': 'Detecting pose landmarks',
      'loading.steps.calculating': 'Calculating jump metrics'
    }
    return translations[key] || key
  })

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useLanguage as any).mockReturnValue({
      t: mockT,
      changeLanguage: vi.fn(),
      currentLanguage: 'en',
      availableLanguages: []
    })
  })

  it('should render with uploading state', () => {
    render(<LoadingSpinner uploadProgress={50} />)

    expect(screen.getByText('Uploading Video')).toBeInTheDocument()
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('should show progress percentage during upload', () => {
    render(<LoadingSpinner uploadProgress={50} />)

    expect(mockT).toHaveBeenCalledWith('loading.uploadProgress', { progress: 50 })
    expect(screen.getByText('Upload progress: 50%')).toBeInTheDocument()
  })

  it('should show analyzing state when progress is 100+', () => {
    render(<LoadingSpinner uploadProgress={100} />)

    expect(screen.getByText('Analyzing Video')).toBeInTheDocument()
    expect(screen.getByText('This typically takes 10-60 seconds')).toBeInTheDocument()
  })

  it('should not show progress bar when not uploading', () => {
    render(<LoadingSpinner uploadProgress={100} />)

    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
  })

  it('should show all loading steps', () => {
    render(<LoadingSpinner uploadProgress={50} />)

    expect(screen.getByText('Uploading video')).toBeInTheDocument()
    expect(screen.getByText('Processing video frames')).toBeInTheDocument()
    expect(screen.getByText('Detecting pose landmarks')).toBeInTheDocument()
    expect(screen.getByText('Calculating jump metrics')).toBeInTheDocument()
  })

  it('should mark uploading step as active and complete when uploading', () => {
    const { container } = render(<LoadingSpinner uploadProgress={50} />)

    const steps = container.querySelectorAll('.loading-steps li')
    expect(steps[0]).toHaveClass('active')
    expect(steps[0]).not.toHaveClass('complete')
  })

  it('should mark processing steps as active when analysis complete', () => {
    const { container } = render(<LoadingSpinner uploadProgress={100} />)

    const steps = container.querySelectorAll('.loading-steps li')
    expect(steps[1]).toHaveClass('active')
    expect(steps[2]).toHaveClass('active')
    expect(steps[3]).toHaveClass('active')
  })

  it('should have proper ARIA attributes', () => {
    render(<LoadingSpinner uploadProgress={50} />)

    const status = screen.getByRole('status')
    expect(status).toHaveAttribute('aria-live', 'polite')
    expect(status).toHaveAttribute('aria-busy', 'true')
  })

  it('should set correct ARIA progressbar attributes', () => {
    render(<LoadingSpinner uploadProgress={75} />)

    const progressbar = screen.getByRole('progressbar')
    expect(progressbar).toHaveAttribute('aria-valuenow', '75')
    expect(progressbar).toHaveAttribute('aria-valuemin', '0')
    expect(progressbar).toHaveAttribute('aria-valuemax', '100')
  })

  it('should call translation function with correct keys', () => {
    render(<LoadingSpinner uploadProgress={50} />)

    expect(mockT).toHaveBeenCalledWith('loading.uploadingVideo')
    expect(mockT).toHaveBeenCalledWith('loading.uploadProgress', { progress: 50 })
    expect(mockT).toHaveBeenCalledWith('loading.steps.uploading')
    expect(mockT).toHaveBeenCalledWith('loading.steps.processing')
    expect(mockT).toHaveBeenCalledWith('loading.steps.detecting')
    expect(mockT).toHaveBeenCalledWith('loading.steps.calculating')
  })

  it('should update when uploadProgress changes', () => {
    const { rerender } = render(<LoadingSpinner uploadProgress={25} />)

    expect(mockT).toHaveBeenCalledWith('loading.uploadProgress', { progress: 25 })

    rerender(<LoadingSpinner uploadProgress={75} />)

    expect(mockT).toHaveBeenCalledWith('loading.uploadProgress', { progress: 75 })
  })

  it('should update state transitions correctly', () => {
    const { rerender } = render(<LoadingSpinner uploadProgress={50} />)

    expect(screen.getByText('Uploading Video')).toBeInTheDocument()

    rerender(<LoadingSpinner uploadProgress={100} />)

    expect(screen.getByText('Analyzing Video')).toBeInTheDocument()
  })
})
