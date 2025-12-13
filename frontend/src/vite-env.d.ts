/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Global type declarations for third-party scripts loaded at runtime
declare global {
  interface Window {
    gtag?: (
      command: 'config' | 'event' | 'js',
      targetId: string | Record<string, any>,
      config?: Record<string, any>
    ) => void

    supabase?: {
      auth: {
        getSession?: () => Promise<{
          data: {
            session: {
              access_token: string
              // Add other Supabase session properties as needed
            } | null
          }
        }>
      }
    }
  }
}

export {}
