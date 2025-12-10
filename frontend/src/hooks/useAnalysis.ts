import { useState } from 'react'
import { AnalysisResponse, JumpType } from '../types/api'
import { supabase } from '../lib/supabase'

interface UseAnalysisState {
  file: File | null
  jumpType: JumpType
  loading: boolean
  uploadProgress: number
  metrics: AnalysisResponse | null
  error: string | null
  enableDebug: boolean
}

interface UseAnalysisActions {
  setFile: (file: File | null) => void
  setJumpType: (jumpType: JumpType) => void
  setEnableDebug: (enable: boolean) => void
  analyze: () => Promise<void>
  retry: () => Promise<void>
  reset: () => void
}

/**
 * Custom hook for managing video analysis state and logic
 * Handles file upload, progress tracking, and error management
 */
export function useAnalysis(): UseAnalysisState & UseAnalysisActions {
  const [file, setFile] = useState<File | null>(null)
  const [jumpType, setJumpType] = useState<JumpType>('cmj')
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [metrics, setMetrics] = useState<AnalysisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [enableDebug, setEnableDebug] = useState(false)

  const analyze = async () => {
    if (!file) {
      setError('Please select a video file')
      return
    }

    setLoading(true)
    setError(null)
    setMetrics(null)
    setUploadProgress(0)

    const formData = new FormData()
    formData.append('file', file)
    // Convert frontend format (cmj/dropjump) to backend format (cmj/drop_jump)
    const backendJumpType = jumpType === 'dropjump' ? 'drop_jump' : jumpType
    formData.append('jump_type', backendJumpType)
    formData.append('debug', enableDebug ? 'true' : 'false')

    try {
      // Use environment variable for API URL in production, or relative proxy in development
      const baseApiUrl = import.meta.env.VITE_API_URL || ''
      const apiEndpoint = baseApiUrl ? `${baseApiUrl}/api/analyze` : '/api/analyze'

      // Get auth token from Supabase if configured
      let token: string | undefined
      if (supabase) {
        const { data: { session } } = await supabase.auth.getSession()
        token = session?.access_token
      }

      // Use XMLHttpRequest to track upload progress
      const response = await new Promise<AnalysisResponse>((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        // Track upload progress
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100
            setUploadProgress(Math.round(percentComplete))
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status === 200) {
            try {
              const data = JSON.parse(xhr.responseText) as AnalysisResponse
              resolve(data)
            } catch {
              reject(new Error('Failed to parse response'))
            }
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText)
              // Backend returns error in 'error' or 'message' field
              const errorMessage = errorData.error || errorData.message || errorData.detail || `Server error: ${xhr.status}`
              reject(new Error(errorMessage))
            } catch {
              reject(new Error(`Server error: ${xhr.status}`))
            }
          }
        })

        xhr.addEventListener('error', () => {
          reject(new Error('Network error: Unable to connect to the server'))
        })

        xhr.addEventListener('abort', () => {
          reject(new Error('Request was cancelled'))
        })

        xhr.open('POST', apiEndpoint)

        // Add Authorization header with Supabase token
        if (token) {
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        }

        xhr.send(formData)
      })

      setMetrics(response)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred'
      setError(errorMessage)
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
      setUploadProgress(0)
    }
  }

  const retry = async () => {
    if (file) {
      await analyze()
    }
  }

  const reset = () => {
    setFile(null)
    setJumpType('cmj')
    setLoading(false)
    setUploadProgress(0)
    setMetrics(null)
    setError(null)
    setEnableDebug(false)
  }

  return {
    // State
    file,
    jumpType,
    loading,
    uploadProgress,
    metrics,
    error,
    enableDebug,
    // Actions
    setFile,
    setJumpType,
    setEnableDebug,
    analyze,
    retry,
    reset,
  }
}
