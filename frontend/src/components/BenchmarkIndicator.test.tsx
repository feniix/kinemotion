import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import BenchmarkIndicator from './BenchmarkIndicator'
import type { MetricInterpretation } from '../types/api'

describe('BenchmarkIndicator', () => {
  const baseInterpretation: MetricInterpretation = {
    category: 'average',
    value: 45.0,
    range: { low: 41.0, high: 50.0, unit: 'cm' },
    recommendation: 'Good foundation. Progress to moderate-intensity plyometrics.',
  }

  it('renders category label', () => {
    render(<BenchmarkIndicator interpretation={baseInterpretation} />)
    expect(screen.getByText('Average')).toBeInTheDocument()
  })

  it('renders range with unit', () => {
    render(<BenchmarkIndicator interpretation={baseInterpretation} />)
    // The range is rendered with an ndash entity
    const rangeEl = document.querySelector('.benchmark-range')
    expect(rangeEl).toBeInTheDocument()
    expect(rangeEl?.textContent).toContain('41')
    expect(rangeEl?.textContent).toContain('50')
    expect(rangeEl?.textContent).toContain('cm')
  })

  it('renders recommendation text', () => {
    render(<BenchmarkIndicator interpretation={baseInterpretation} />)
    expect(screen.getByText('Good foundation. Progress to moderate-intensity plyometrics.')).toBeInTheDocument()
  })

  it('does not render recommendation when empty', () => {
    const noRec: MetricInterpretation = {
      ...baseInterpretation,
      recommendation: '',
    }
    render(<BenchmarkIndicator interpretation={noRec} />)
    expect(document.querySelector('.benchmark-recommendation')).not.toBeInTheDocument()
  })

  it('renders colored dot for category', () => {
    render(<BenchmarkIndicator interpretation={baseInterpretation} />)
    const dot = document.querySelector('.benchmark-dot') as HTMLElement
    expect(dot).toBeInTheDocument()
    // Average color is #eab308
    expect(dot.style.backgroundColor).toBe('rgb(234, 179, 8)')
  })

  it('renders excellent category with correct color', () => {
    const excellent: MetricInterpretation = {
      ...baseInterpretation,
      category: 'excellent',
    }
    render(<BenchmarkIndicator interpretation={excellent} />)
    expect(screen.getByText('Excellent')).toBeInTheDocument()
    const dot = document.querySelector('.benchmark-dot') as HTMLElement
    expect(dot.style.backgroundColor).toBe('rgb(6, 182, 212)')
  })

  it('renders countermovement depth special category', () => {
    const optimal: MetricInterpretation = {
      category: 'optimal',
      value: 28.0,
      range: { low: 20.0, high: 35.0, unit: 'cm' },
      recommendation: 'Good countermovement depth.',
    }
    render(<BenchmarkIndicator interpretation={optimal} />)
    expect(screen.getByText('Optimal')).toBeInTheDocument()
  })
})
