/**
 * External links and configuration for the Kinemotion frontend
 */

export const EXTERNAL_LINKS = {
  // Feature request form - update this with your actual Google Forms URL
  FEATURE_REQUEST: 'https://docs.google.com/forms/d/e/1FAIpQLSfexample/viewform',

  // Additional useful links
  DOCUMENTATION: 'https://github.com/feniix/kinemotion#readme',
  GITHUB_ISSUES: 'https://github.com/feniix/kinemotion/issues',
  SUPPORT_EMAIL: 'mailto:support@kinemotion.dev',

  // Social links (optional)
  TWITTER: 'https://twitter.com/kinemotion_app',
  LINKEDIN: 'https://linkedin.com/company/kinemotion',
} as const

export const UI_CONFIG = {
  // Feature request settings
  FEATURE_REQUEST: {
    // Whether to show the feature request button
    enabled: true,
    // Button text
    buttonText: 'Request Feature',
    // Button icon (emoji or text)
    buttonIcon: '💡',
    // Tooltip text
    tooltip: 'Share your ideas and suggestions for improving Kinemotion',
    // Whether to open in new tab
    openInNewTab: true,
  },

  // General feedback settings
  GENERAL_FEEDBACK: {
    // Whether to show general feedback option
    enabled: true,
    buttonText: 'General Feedback',
    buttonIcon: '📝',
    tooltip: 'Share your general feedback about Kinemotion',
    url: EXTERNAL_LINKS.GITHUB_ISSUES,
  },
} as const

export type ExternalLinkKey = keyof typeof EXTERNAL_LINKS
export type UIConfigKey = keyof typeof UI_CONFIG
