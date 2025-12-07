import { useState, useEffect } from 'react'

interface HealthResponse {
  status: string
  service: string
  version: string
  kinemotion_version: string
  timestamp: string
  r2_configured: boolean
}

export function useBackendVersion() {
  const [backendVersion, setBackendVersion] = useState<string>('...')
  const [kinemotionVersion, setKinemotionVersion] = useState<string>('...')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const baseApiUrl = import.meta.env.VITE_API_URL || ''
        const response = await fetch(`${baseApiUrl}/health`)

        if (response.ok) {
          const data: HealthResponse = await response.json()
          setBackendVersion(data.version)
          setKinemotionVersion(data.kinemotion_version)
        }
      } catch (error) {
        console.error('Failed to fetch backend version:', error)
        // Keep default '...' values on error
      } finally {
        setLoading(false)
      }
    }

    fetchVersion()
  }, [])

  return { backendVersion, kinemotionVersion, loading }
}
