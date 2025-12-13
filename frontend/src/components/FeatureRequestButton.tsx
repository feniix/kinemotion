import React from 'react'
import { EXTERNAL_LINKS, UI_CONFIG } from '../config/links'

interface FeatureRequestButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'small' | 'medium' | 'large'
  showIcon?: boolean
  className?: string
}

export default function FeatureRequestButton({
  variant = 'primary',
  size = 'medium',
  showIcon = true,
  className = '',
}: FeatureRequestButtonProps) {
  const config = UI_CONFIG.FEATURE_REQUEST
  const link = EXTERNAL_LINKS.FEATURE_REQUEST

  if (!config.enabled || !link) {
    return null
  }

  const baseStyles: React.CSSProperties = {
    border: 'none',
    borderRadius: '6px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s, transform 0.1s',
    textDecoration: 'none',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
  }

  const variantStyles = {
    primary: {
      background: '#6366f1',
      color: 'white',
      hoverBackground: '#4f46e5',
    },
    secondary: {
      background: '#f3f4f6',
      color: '#374151',
      border: '1px solid #d1d5db',
      hoverBackground: '#e5e7eb',
    },
  }[variant]

  const sizeStyles = {
    small: {
      padding: '0.5rem 1rem',
      fontSize: '0.75rem',
    },
    medium: {
      padding: '0.75rem 1.5rem',
      fontSize: '0.875rem',
    },
    large: {
      padding: '1rem 2rem',
      fontSize: '1rem',
    },
  }[size]

  const style = {
    ...baseStyles,
    ...variantStyles,
    ...sizeStyles,
  }

  const handleMouseOver = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.currentTarget.style.backgroundColor = variantStyles.hoverBackground
  }

  const handleMouseOut = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.currentTarget.style.backgroundColor = variantStyles.background
  }

  return (
    <a
      href={link}
      target={config.openInNewTab ? '_blank' : '_self'}
      rel="noopener noreferrer"
      className={`feature-request-button ${className}`}
      style={style}
      title={config.tooltip}
      onMouseOver={handleMouseOver}
      onMouseOut={handleMouseOut}
      onClick={() => {
        // Optional: Track analytics event
        if (typeof window.gtag !== 'undefined') {
          window.gtag('event', 'feature_request_click', {
            event_category: 'engagement',
            event_label: 'feature_request_button',
          })
        }
      }}
    >
      {showIcon && <span>{config.buttonIcon}</span>}
      {config.buttonText}
    </a>
  )
}
