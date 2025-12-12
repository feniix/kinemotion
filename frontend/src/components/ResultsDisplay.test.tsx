import React from 'react';
import { render, screen, within } from '@testing-library/react';
import '@testing-library/jest-dom';
import ResultsDisplay from './ResultsDisplay';
import { AnalysisResponse, ValidationResults } from '../types/api';

describe('ResultsDisplay', () => {
  const commonMetrics = {
    status: 200,
    message: 'Analysis successful',
    metrics: {
      data: {
        tracking_method: 'MediaPipe',
        processing_time_s: 15.5,
      },
      validation: {
        status: 'PASS' as ValidationResults['status'],
        issues: [],
      },
    },
  };

  it('renders CMJ scoreboard with correct metrics and units', () => {
    const cmjMetrics: AnalysisResponse = {
      ...commonMetrics,
      metrics: {
        ...commonMetrics.metrics,
        data: {
          ...commonMetrics.metrics?.data,
          jump_height_m: 0.50,
          peak_concentric_velocity_m_s: 3.25,
          peak_power_w: 2500,
          countermovement_depth_m: 0.30,
        },
      },
    };

    render(<ResultsDisplay metrics={cmjMetrics} />);

    // Check for Jump Height in scoreboard (highlighted, large, in cm)
    const kpiGrid = screen.getByRole('heading', { name: /key performance indicators/i }).nextElementSibling as HTMLElement;
    const jumpHeightCard = within(kpiGrid).getByText('Jump Height').closest('.metric-card') as HTMLElement;
    const jumpHeightValue = within(jumpHeightCard).getByText('50.00');
    expect(jumpHeightValue).toBeInTheDocument();
    expect(within(jumpHeightCard).getByText('cm')).toBeInTheDocument();
    expect(jumpHeightValue.classList.contains('large')).toBe(true);

    // Check for Peak Velocity in scoreboard
    const peakVelocityCard = within(kpiGrid).getByText('Peak Velocity').closest('.metric-card') as HTMLElement;
    expect(peakVelocityCard).toBeInTheDocument();
    expect(within(peakVelocityCard).getByText('3.25')).toBeInTheDocument();
    expect(within(peakVelocityCard).getByText('m/s')).toBeInTheDocument();

    // Check for Peak Power in scoreboard
    const peakPowerCard = within(kpiGrid).getByText('Peak Power').closest('.metric-card') as HTMLElement;
    expect(peakPowerCard).toBeInTheDocument();
    expect(within(peakPowerCard).getByText('2500.00')).toBeInTheDocument();
    expect(within(peakPowerCard).getByText('W')).toBeInTheDocument();

    // Check for Loading (Eccentric) phase metrics in timeline
    const jumpTimeline = screen.getByRole('heading', { name: /jump phase analysis/i }).nextElementSibling as HTMLElement;
    const loadingPhaseCard = within(jumpTimeline).getByText('Loading (Eccentric)').closest('.phase-card') as HTMLElement;
    expect(loadingPhaseCard).toBeInTheDocument();
    expect(within(loadingPhaseCard).getByText('Depth')).toBeInTheDocument();
    expect(within(loadingPhaseCard).getByText('30.00')).toBeInTheDocument(); // Converted to cm

    // Check for other details (not in scoreboard/timeline, but in additional metrics)
    expect(screen.queryByText('Countermovement Depth')).not.toBeInTheDocument();
  });

  it('renders Drop Jump scoreboard with correct metrics and units', () => {
    const dropJumpMetrics: AnalysisResponse = {
      ...commonMetrics,
      metrics: {
        ...commonMetrics.metrics,
        data: {
          ...commonMetrics.metrics?.data,
          reactive_strength_index: 2.15,
          jump_height_m: 0.45,
          ground_contact_time_ms: 250,
          flight_time_ms: 300,
        },
      },
    };

    render(<ResultsDisplay metrics={dropJumpMetrics} />);

    // Check for RSI in scoreboard (highlighted, large)
    const kpiGrid = screen.getByRole('heading', { name: /key performance indicators/i }).nextElementSibling as HTMLElement;
    const rsiCard = within(kpiGrid).getByText('RSI').closest('.metric-card') as HTMLElement;
    const rsiValue = within(rsiCard).getByText('2.15');
    expect(rsiValue).toBeInTheDocument();
    expect(within(rsiCard).getByText('m/s')).toBeInTheDocument();
    expect(rsiValue.classList.contains('large')).toBe(true);

    // Check for Jump Height in scoreboard
    const heightCard = within(kpiGrid).getByText('Height').closest('.metric-card') as HTMLElement;
    expect(heightCard).toBeInTheDocument();
    expect(within(heightCard).getByText('45.00')).toBeInTheDocument();
    expect(within(heightCard).getByText('cm')).toBeInTheDocument();

    // Check for Ground Contact Time in scoreboard
    const gctCard = within(kpiGrid).getByText('Contact Time').closest('.metric-card') as HTMLElement;
    expect(gctCard).toBeInTheDocument();
    expect(within(gctCard).getByText('250.00')).toBeInTheDocument();
    expect(within(gctCard).getByText('ms')).toBeInTheDocument();
  });

  it('renders validation banner when validation status is present', () => {
    const failedMetrics: AnalysisResponse = {
      ...commonMetrics,
      metrics: {
        ...commonMetrics.metrics,
        validation: {
          status: 'FAIL' as ValidationResults['status'],
          issues: [{ metric: 'jump_height', severity: 'ERROR', message: 'Jump height too low' }],
        },
      },
    };

    render(<ResultsDisplay metrics={failedMetrics} />);
    expect(screen.getByText('Quality Check: FAIL')).toBeInTheDocument();
    expect(screen.getByText('Jump height too low')).toBeInTheDocument();
  });

  it('renders informational validation banner for PASS_WITH_WARNINGS with correct icon and text', () => {
    const warningMetrics: AnalysisResponse = {
      ...commonMetrics,
      metrics: {
        ...commonMetrics.metrics,
        validation: {
          status: 'PASS_WITH_WARNINGS' as ValidationResults['status'],
          issues: [{ metric: 'form_detection', severity: 'INFO', message: 'Minor form inconsistencies detected.' }],
        },
      },
    };

    render(<ResultsDisplay metrics={warningMetrics} />);
    expect(screen.getByText('Quality Check: PASS WITH WARNINGS')).toBeInTheDocument();
    expect(screen.getByText('Minor form inconsistencies detected.')).toBeInTheDocument();
    // Check for the info icon. Vitest/JSDOM might not render actual emojis, so we check content
    const statusIcon = screen.getByText('ℹ');
    expect(statusIcon).toBeInTheDocument();
  });


  it('renders video previews when debug_video_url or videoFile are provided', () => {
    const metricsWithVideos: AnalysisResponse = {
      ...commonMetrics,
      debug_video_url: 'http://example.com/debug.mp4',
      metrics: {
        ...commonMetrics.metrics,
        validation: {
          status: 'PASS' as ValidationResults['status'],
          issues: [],
        },
      },
    };
    const mockFile = new File([''], 'test.mp4', { type: 'video/mp4' });

    const { rerender } = render(<ResultsDisplay metrics={metricsWithVideos} videoFile={mockFile} />);

    expect(screen.getByTitle('Original Video')).toBeInTheDocument();
    expect(screen.getByTitle('Analysis Overlay')).toBeInTheDocument();
    expect(screen.getByText('Download Original Video')).toBeInTheDocument();
    expect(screen.getByText('Download Analysis Video')).toBeInTheDocument();

    // Test with only original video (local file)
    rerender(<ResultsDisplay metrics={{...commonMetrics, metrics: {...commonMetrics.metrics, validation: {status: 'PASS' as ValidationResults['status'], issues: []}}}} videoFile={mockFile} />);
    expect(screen.getByTitle('Original Video')).toBeInTheDocument();
    expect(screen.queryByTitle('Analysis Overlay')).not.toBeInTheDocument();
    expect(screen.getByText('Download Original Video')).toBeInTheDocument();
    expect(screen.queryByText('Download Analysis Video')).not.toBeInTheDocument();

    // Test with R2 original video URL
    rerender(<ResultsDisplay metrics={{...commonMetrics, original_video_url: 'https://r2.example.com/videos/test.mp4', metrics: {...commonMetrics.metrics, validation: {status: 'PASS' as ValidationResults['status'], issues: []}}}} />);
    expect(screen.getByTitle('Original Video')).toBeInTheDocument();
    expect(screen.queryByTitle('Analysis Overlay')).not.toBeInTheDocument();
    expect(screen.getByText('Download Original Video')).toBeInTheDocument();
    expect(screen.queryByText('Download Analysis Video')).not.toBeInTheDocument();
  });

  it('formats small numeric values to fixed 2 decimal places when not exponential', () => {
    const smallValueMetrics: AnalysisResponse = {
      ...commonMetrics,
      metrics: {
        ...commonMetrics.metrics,
        data: {
          reactive_strength_index: 0.005,
          jump_height_m: 0.0001,
        },
        validation: {
          status: 'PASS' as ValidationResults['status'],
          issues: [],
        },
      },
    };

    render(<ResultsDisplay metrics={smallValueMetrics} />);
    const kpiGrid = screen.getByRole('heading', { name: /key performance indicators/i }).nextElementSibling as HTMLElement;
    const jumpHeightCard = within(kpiGrid).getByText('Height').closest('.metric-card') as HTMLElement;
    expect(within(kpiGrid).getByText('5.00e-3')).toBeInTheDocument(); // RSI - this value is < 0.01, so it will be exponential
    expect(within(jumpHeightCard).getByText('0.01')).toBeInTheDocument(); // Jump Height (0.0001m * 100 = 0.01cm, not exponential)
  });
});
