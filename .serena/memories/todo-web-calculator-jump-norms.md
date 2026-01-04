# TODO: Web Calculator - Jump Performance Norms

## Overview
Create a web-based calculator tool that works in two directions using the reference value tables from coach-quick-start.md.

## Direction 1: Target Stats Calculator

**Inputs:**
- Age (number or slider)
- Sex (Male/Female)
- Training Level (dropdown with 6 options)

**Training Levels:**
1. Untrained - Sedentary, little to no regular exercise
2. Recreational - Exercises 1-3x/week, general fitness
3. Trained - Consistent structured training 3-5x/week for 1+ years
4. Advanced - High-volume training, 3+ years consistent, competitive
5. Collegiate - NCAA/university level athlete
6. Elite - Professional/national/international level

**Outputs:**
- Expected CMJ height range (cm)
- Expected Drop Jump RSI range
- Expected Ground Contact Time range

**Example Output:**
"For a 50-year-old trained male athlete:
- CMJ: 40-45 cm
- Drop Jump RSI: 1.4-1.8
- Ground Contact Time: 210-240 ms"

## Direction 2: Performance Level Calculator

**Inputs:**
- Age (number)
- Sex (Male/Female)
- Jump Type (CMJ or Drop Jump)
- Actual Result (jump height for CMJ; RSI or GCT for Drop Jump)

**Outputs:**
- Percentile ranking
- Classification (Fair/Good/Very Good/Excellent)
- Contextual feedback

**Examples:**
- CMJ: Age 50, Male, 42 cm → "Good - ~60th percentile for your age group"
- Drop Jump: Age 25, Female, RSI 2.1 → "Very Good - ~80th percentile"
- Drop Jump: Age 30, Male, GCT 190 ms → "Very Good - elite contact time"

## Technical Notes
- Use reference values from `/docs/guides/coach-quick-start.md`
- Interpolate between age brackets (30-39, 40-49, 50-59)
- Handle edge cases (youth under 20, adults over 70)
- Consider adding visual feedback (progress bars, percentile charts)

## Implementation Options
1. Add to existing kinemotion.vercel.app
2. Standalone calculator page
3. Progressive Web App for offline use

## Status
TODO - Not started
