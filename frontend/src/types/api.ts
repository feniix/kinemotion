/**
 * API Types for Kinemotion
 */

/**
 * Validation issue reported by the API
 */
export interface ValidationIssue {
  metric: string
  severity: 'ERROR' | 'WARNING' | 'INFO'
  message: string
}

/**
 * Validation results from analysis
 */
export interface ValidationResults {
  status: 'PASS' | 'FAIL' | 'WARNING' | 'PASS_WITH_WARNINGS'
  issues: ValidationIssue[]
}

/**
 * Normative range for a metric interpretation
 */
export interface InterpretationRange {
  low: number
  high: number
  unit: string
}

/**
 * Single metric interpretation with coaching context
 */
export interface MetricInterpretation {
  category: string
  value: number
  range: InterpretationRange
  recommendation: string
}

/**
 * Demographic context returned when athlete demographics were provided
 */
export interface DemographicContext {
  sex?: 'male' | 'female'
  age_group?: string
  training_level?: string
}

/**
 * Coaching interpretations keyed by metric name
 */
export interface InterpretationData {
  interpretations: Record<string, MetricInterpretation>
  demographic_context?: DemographicContext
}

/**
 * Biological sex for normative comparison
 */
export type BiologicalSex = 'male' | 'female'

/**
 * Training level for normative comparison
 */
export type TrainingLevel = 'untrained' | 'recreational' | 'trained' | 'competitive' | 'elite'

/**
 * Analysis metrics response from the API
 */
export interface AnalysisResponse {
  status: number
  message: string
  metrics?: {
    data?: Record<string, string | number>
    metadata?: Record<string, unknown>
    validation?: ValidationResults
    interpretation?: InterpretationData
  }
  results_url?: string
  debug_video_url?: string
  original_video_url?: string
  processing_time_s?: number
  error?: string | null
}

/**
 * Supported jump types
 */
export type JumpType = 'cmj' | 'dropjump'

/**
 * Metric metadata with units and descriptions
 */
export interface MetricMetadata {
  unit: string
  description: string
}

/**
 * Map of metric names to their metadata
 */
export const METRIC_METADATA: Record<string, MetricMetadata> = {
  jump_height_m: {
    unit: 'm',
    description: 'Maximum height achieved during the jump',
  },
  jump_height_cm: {
    unit: 'cm',
    description: 'Maximum height achieved during the jump',
  },
  flight_time_ms: {
    unit: 'ms',
    description: 'Time spent in the air during the jump',
  },
  flight_time_s: {
    unit: 's',
    description: 'Time spent in the air during the jump',
  },
  ground_contact_time_ms: {
    unit: 'ms',
    description: 'Time with feet in contact with the ground',
  },
  reactive_strength_index: {
    unit: 'm/s',
    description: 'Jump height divided by ground contact time',
  },
  takeoff_velocity_mps: {
    unit: 'm/s',
    description: 'Vertical velocity at the moment of takeoff',
  },
  countermovement_depth_m: {
    unit: 'm',
    description: 'Depth of the squat during countermovement',
  },
  countermovement_depth_cm: {
    unit: 'cm',
    description: 'Depth of the squat during countermovement',
  },
  landing_force_normalized: {
    unit: 'BW',
    description: 'Landing force relative to body weight',
  },
  eccentric_duration_ms: {
    unit: 'ms',
    description: 'Duration of the downward (eccentric) phase',
  },
  concentric_duration_ms: {
    unit: 'ms',
    description: 'Duration of the upward (concentric) phase',
  },
  total_movement_time_ms: {
    unit: 'ms',
    description: 'Total time for countermovement and jump',
  },
  peak_power_w: {
    unit: 'W',
    description: 'Maximum power output during the jump',
  },
  peak_eccentric_velocity_m_s: {
    unit: 'm/s',
    description: 'Maximum velocity during the downward phase',
  },
  peak_concentric_velocity_m_s: {
    unit: 'm/s',
    description: 'Maximum velocity during the upward phase',
  },
  transition_time_ms: {
    unit: 'ms',
    description: 'Time between end of eccentric and start of concentric phase',
  },
  standing_start_frame: {
    unit: '',
    description: 'Frame number at standing position',
  },
  lowest_point_frame: {
    unit: '',
    description: 'Frame number at lowest point of squat',
  },
  takeoff_frame: {
    unit: '',
    description: 'Frame number at takeoff',
  },
  landing_frame: {
    unit: '',
    description: 'Frame number at landing',
  },
  tracking_method: {
    unit: '',
    description: 'Method used for motion tracking',
  },
}
