import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RecentUploads from './RecentUploads'
import { useLanguage } from '../hooks/useLanguage'
import type { RecentUpload } from '../hooks/useRecentUploads'

vi.mock('../hooks/useLanguage')

describe('RecentUploads', () => {
  const mockOnSelect = vi.fn()
  const mockOnClear = vi.fn()

  const mockT = vi.fn((key: string, options?: Record<string, unknown>) => {
    const translations: Record<string, string> = {
      'recentUploads.timeLabels.justNow': 'Just now',
      'recentUploads.timeLabels.minutesAgo': `${options?.minutes}m ago`,
      'recentUploads.timeLabels.hoursAgo': `${options?.hours}h ago`,
      'recentUploads.jumpTypes.cmj': 'CMJ',
      'recentUploads.jumpTypes.dropJump': 'Drop Jump'
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

  it('should return null when no uploads', () => {
    const { container } = render(
      <RecentUploads uploads={[]} onSelect={mockOnSelect} onClear={mockOnClear} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('should render uploads when available', () => {
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(screen.getByText('test.mp4')).toBeInTheDocument()
  })

  it('should display multiple uploads', () => {
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'video1.mp4', jumpType: 'cmj', timestamp: now },
      { id: '2', filename: 'video2.mp4', jumpType: 'dropjump', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(screen.getByText('video1.mp4')).toBeInTheDocument()
    expect(screen.getByText('video2.mp4')).toBeInTheDocument()
  })

  it('should show "just now" for recent uploads', () => {
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(screen.getByText('Just now')).toBeInTheDocument()
  })

  it('should show minutes ago for recent uploads', () => {
    const now = Date.now()
    const fiveMinutesAgo = now - 5 * 60 * 1000
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: fiveMinutesAgo }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.timeLabels.minutesAgo', { minutes: 5 })
    expect(screen.getByText('5m ago')).toBeInTheDocument()
  })

  it('should show hours ago for older uploads', () => {
    const now = Date.now()
    const twoHoursAgo = now - 2 * 60 * 60 * 1000
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: twoHoursAgo }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.timeLabels.hoursAgo', { hours: 2 })
    expect(screen.getByText('2h ago')).toBeInTheDocument()
  })

  it('should format CMJ jump type', () => {
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.jumpTypes.cmj')
    expect(screen.getByText('CMJ')).toBeInTheDocument()
  })

  it('should format Drop Jump jump type', () => {
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'dropjump', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.jumpTypes.dropJump')
    expect(screen.getByText('Drop Jump')).toBeInTheDocument()
  })

  it('should call onSelect when upload clicked', async () => {
    const user = userEvent.setup()
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    const uploadButton = screen.getByRole('button', { name: /test.mp4/i })
    await user.click(uploadButton)

    expect(mockOnSelect).toHaveBeenCalledWith('test.mp4', 'cmj')
  })

  it('should call onSelect with correct jump type on click', async () => {
    const user = userEvent.setup()
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'dropjump', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    const uploadButton = screen.getByRole('button', { name: /test.mp4/i })
    await user.click(uploadButton)

    expect(mockOnSelect).toHaveBeenCalledWith('test.mp4', 'dropjump')
  })

  it('should call onClear when clear button clicked', async () => {
    const user = userEvent.setup()
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    const clearButton = screen.getByRole('button', { name: /clear/i })
    await user.click(clearButton)

    expect(mockOnClear).toHaveBeenCalled()
  })

  it('should display all translation keys', () => {
    const now = Date.now()
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: now }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.timeLabels.justNow')
    expect(mockT).toHaveBeenCalledWith('recentUploads.jumpTypes.cmj')
  })

  it('should handle edge case with 59 minutes', () => {
    const now = Date.now()
    const fiftyNineMinutesAgo = now - 59 * 60 * 1000
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: fiftyNineMinutesAgo }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.timeLabels.minutesAgo', { minutes: 59 })
  })

  it('should handle edge case with 60+ minutes', () => {
    const now = Date.now()
    const sixtyTwoMinutesAgo = now - 62 * 60 * 1000
    const uploads: RecentUpload[] = [
      { id: '1', filename: 'test.mp4', jumpType: 'cmj', timestamp: sixtyTwoMinutesAgo }
    ]

    render(<RecentUploads uploads={uploads} onSelect={mockOnSelect} onClear={mockOnClear} />)

    expect(mockT).toHaveBeenCalledWith('recentUploads.timeLabels.hoursAgo', { hours: 1 })
  })
})
