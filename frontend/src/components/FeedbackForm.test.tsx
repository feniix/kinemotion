import { render, screen } from '@testing-library/react'
import FeedbackForm from './FeedbackForm'
import { useLanguage } from '../hooks/useLanguage'
import type { AnalysisResponse } from '../types/api'

vi.mock('../hooks/useLanguage')

describe('FeedbackForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  const mockT = vi.fn((key: string, options?: Record<string, unknown>) => {
    const translations: Record<string, string> = {
      'feedback.heading': `Coach Feedback - Analysis ${options?.jumpType || 'Jump'}`,
      'feedback.subtitle': 'Share your thoughts and coaching notes for this analysis',
      'feedback.overallRating': 'Overall Rating',
      'feedback.ratingLabels.excellent': 'Excellent',
      'feedback.ratingLabels.good': 'Good',
      'feedback.ratingLabels.average': 'Average',
      'feedback.ratingLabels.needsWork': 'Needs Work',
      'feedback.ratingLabels.poor': 'Poor',
      'feedback.tags': 'Tags',
      'feedback.coachNotes': 'Coach Notes',
      'feedback.addCustomTag': 'Add custom tag...',
      'feedback.addButton': 'Add',
      'feedback.cancel': 'Cancel',
      'feedback.saveFeedback': 'Save Feedback',
      'feedback.saving': 'Saving...',
      'feedback.notesHelp': 'Focus on actionable coaching points and specific observations on movement quality.',
      'feedback.commonTags': [
        'Technique',
        'Power',
        'Consistency',
        'Balance',
        'Speed',
        'Form',
        'Explosive',
        'Control'
      ]
    }
    return translations[key] || key
  })

  const mockAnalysisResponse: AnalysisResponse = {
    metrics: {
      data: {
        jump_height_m: 0.5,
        flight_time_s: 0.6,
        ground_contact_time_ms: 500,
        reactive_strength_index: 0.6
      }
    }
  } as AnalysisResponse

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useLanguage as any).mockReturnValue({
      t: mockT,
      changeLanguage: vi.fn(),
      currentLanguage: 'en',
      availableLanguages: []
    })
  })

  it('should render feedback form with heading', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByText(/Coach Feedback/)).toBeInTheDocument()
    expect(mockT).toHaveBeenCalledWith('feedback.heading', { jumpType: expect.any(String) })
  })

  it('should call translation function for form labels', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(mockT).toHaveBeenCalledWith('feedback.tags')
    expect(mockT).toHaveBeenCalledWith('feedback.coachNotes')
    expect(mockT).toHaveBeenCalledWith('feedback.overallRating')
  })

  it('should display rating stars', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    const starButtons = screen.getAllByRole('button', { name: '★' })
    expect(starButtons).toHaveLength(5)
  })

  it('should display common tags', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByText('Technique')).toBeInTheDocument()
    expect(screen.getByText('Power')).toBeInTheDocument()
    expect(screen.getByText('Consistency')).toBeInTheDocument()
  })

  it('should render submit button', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByRole('button', { name: 'Save Feedback' })).toBeInTheDocument()
  })

  it('should render cancel button', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
  })

  it('should call translation function with returnObjects for tags', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(mockT).toHaveBeenCalledWith('feedback.commonTags', { returnObjects: true })
  })

  it('should call translation function for help text', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(mockT).toHaveBeenCalledWith('feedback.notesHelp')
  })

  it('should call translation function for add tag button', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(mockT).toHaveBeenCalledWith('feedback.addButton')
  })

  it('should render textarea for notes', () => {
    const { container } = render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    const textarea = container.querySelector('textarea')
    expect(textarea).toBeInTheDocument()
    expect(textarea).toHaveAttribute('rows', '6')
  })

  it('should render tag input field', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(screen.getByPlaceholderText('Add custom tag...')).toBeInTheDocument()
  })

  it('should determine drop jump type from metrics', () => {
    render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(mockT).toHaveBeenCalledWith('feedback.heading', { jumpType: 'Drop Jump' })
  })

  it('should determine CMJ jump type when appropriate', () => {
    const cmjResponse: AnalysisResponse = {
      metrics: {
        data: {
          jump_height_m: 0.5,
          flight_time_s: 0.6,
          countermovement_depth_m: 0.4
        }
      }
    } as AnalysisResponse

    render(
      <FeedbackForm
        analysisResponse={cmjResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(mockT).toHaveBeenCalledWith('feedback.heading', { jumpType: 'CMJ' })
  })

  it('should have form section structure', () => {
    const { container } = render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    const formSections = container.querySelectorAll('.form-section')
    expect(formSections.length).toBeGreaterThan(0)
  })

  it('should have form element', () => {
    const { container } = render(
      <FeedbackForm
        analysisResponse={mockAnalysisResponse}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />
    )

    expect(container.querySelector('form')).toBeInTheDocument()
  })
})
