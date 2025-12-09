/**
 * Supabase client configuration for Kinemotion frontend
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

const isConfigured = supabaseUrl && supabaseAnonKey

if (!isConfigured) {
  console.warn(
    'Missing Supabase environment variables (VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY). Authentication will be mocked.'
  )
}

export const supabase = isConfigured
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null
