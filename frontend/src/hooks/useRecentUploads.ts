import { useState, useEffect } from 'react'

export interface RecentUpload {
  id: string
  filename: string
  jumpType: 'cmj' | 'dropjump'
  timestamp: number
}

const STORAGE_KEY = 'kinemotion_recent_uploads'
const MAX_RECENT = 5

export function useRecentUploads() {
  const [recentUploads, setRecentUploads] = useState<RecentUpload[]>([])

  // Load from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      try {
        setRecentUploads(JSON.parse(stored))
      } catch {
        // Ignore parse errors
      }
    }
  }, [])

  const addRecentUpload = (filename: string, jumpType: 'cmj' | 'dropjump') => {
    const newUpload: RecentUpload = {
      id: `${Date.now()}-${Math.random()}`,
      filename,
      jumpType,
      timestamp: Date.now(),
    }

    const updated = [newUpload, ...recentUploads].slice(0, MAX_RECENT)
    setRecentUploads(updated)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
  }

  const removeRecentUpload = (id: string) => {
    const updated = recentUploads.filter(upload => upload.id !== id)
    setRecentUploads(updated)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
  }

  const clearRecentUploads = () => {
    setRecentUploads([])
    localStorage.removeItem(STORAGE_KEY)
  }

  return {
    recentUploads,
    addRecentUpload,
    removeRecentUpload,
    clearRecentUploads,
  }
}
