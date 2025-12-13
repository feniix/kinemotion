import { useState, useEffect } from 'react'

interface DatabaseStatus {
  database_connected: boolean
  tables_exist: boolean
  message: string
}

export function useDatabaseStatus() {
  const [status, setStatus] = useState<DatabaseStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkDatabaseStatus = async () => {
      try {
        setLoading(true)
        setError(null)

        // Try the specific database status endpoint first
        let response = await fetch('/api/analysis/database-status')

        if (response.ok) {
          const data = await response.json()
          setStatus(data)
          return
        }

        // Fallback to the health endpoint
        response = await fetch('/health')

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const healthData = await response.json()
        setStatus({
          database_connected: healthData.database_connected || false,
          tables_exist: healthData.database_connected || false,
          message: healthData.database_connected
            ? 'Database connection successful'
            : 'Database connection failed - using health check fallback'
        })

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error'
        setError(errorMessage)
        setStatus({
          database_connected: false,
          tables_exist: false,
          message: `Failed to check database status: ${errorMessage}`
        })
      } finally {
        setLoading(false)
      }
    }

    checkDatabaseStatus()
  }, [])

  return { status, loading, error }
}
