/**
 * Supabase client configuration for Kinemotion frontend
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
// Prefer modern VITE_SUPABASE_PUBLISHABLE_KEY, fall back to legacy VITE_SUPABASE_ANON_KEY
const supabaseKey =
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ||
  import.meta.env.VITE_SUPABASE_ANON_KEY

const isConfigured = supabaseUrl && supabaseKey

if (!isConfigured) {
  console.warn(
    'Missing Supabase environment variables (VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY). Authentication will be mocked.'
  )
}

export const supabase = isConfigured
  ? createClient(supabaseUrl, supabaseKey)
  : null
