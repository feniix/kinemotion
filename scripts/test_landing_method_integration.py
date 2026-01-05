#!/usr/bin/env python3
"""
Test the new LandingMethod integration in CMJ analysis.

Compares the IMPACT (default) vs CONTACT (force-plate equivalent) methods.
"""

import sys
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kinemotion.cmj.analysis import (
    LandingMethod,
    _find_landing_contact,
    _find_landing_impact,
    compute_signed_velocity,
    find_landing_frame,
)
from kinemotion.core.smoothing import compute_acceleration_from_derivative


def test_find_landing_frame_methods():
    """Test both landing methods with synthetic data."""
    print("=" * 60)
    print("Testing find_landing_frame with both methods")
    print("=" * 60)

    # Create realistic synthetic CMJ data
    fps = 60.0
    n_frames = 200

    # Simulate a CMJ trajectory
    t = np.linspace(0, n_frames / fps, n_frames)

    # Standing phase (0-1s), countermovement (1-1.5s), flight (1.5-2s), landing (2-2.5s)
    positions = np.zeros(n_frames)

    # Standing phase
    positions[:60] = 0.5

    # Countermovement (going down)
    for i in range(60, 90):
        positions[i] = 0.5 + 0.1 * np.sin(np.pi * (i - 60) / 60)

    # Propulsion and takeoff (going up)
    positions[90:105] = 0.6 - 0.3 * np.linspace(0, 1, 15)

    # Flight phase (ascending then descending)
    peak = 110
    for i in range(105, 140):
        flight_t = (i - 107.5) / 30
        positions[i] = 0.3 - 0.2 * (1 - (flight_t ** 2))

    # Landing impact
    for i in range(140, n_frames):
        positions[i] = 0.5 + 0.05 * np.exp(-(i - 142) / 5)

    # Compute derivatives
    velocities = compute_signed_velocity(positions)
    accelerations = compute_acceleration_from_derivative(positions)

    peak_height_frame = int(np.argmin(positions))
    print(f"Peak height frame: {peak_height_frame}")

    # Test both methods
    landing_impact = find_landing_frame(
        accelerations, velocities, peak_height_frame, fps, method=LandingMethod.IMPACT
    )
    landing_contact = find_landing_frame(
        accelerations, velocities, peak_height_frame, fps, method=LandingMethod.CONTACT
    )

    # Also test string input
    landing_impact_str = find_landing_frame(
        accelerations, velocities, peak_height_frame, fps, method="impact"
    )
    landing_contact_str = find_landing_frame(
        accelerations, velocities, peak_height_frame, fps, method="contact"
    )

    print(f"\nIMPACT method:  frame {landing_impact:.1f}")
    print(f"CONTACT method: frame {landing_contact:.1f}")
    print(f"Delta: {landing_contact - landing_impact:.1f} frames")

    # Verify string input works
    assert landing_impact == landing_impact_str, "String input 'impact' should work"
    assert landing_contact == landing_contact_str, "String input 'contact' should work"
    print("\nString input verification: PASSED")

    # Verify CONTACT detects earlier or same as IMPACT
    assert landing_contact <= landing_impact, "CONTACT should detect <= IMPACT"
    print("CONTACT <= IMPACT verification: PASSED")

    print("\n" + "=" * 60)
    print("All tests PASSED!")
    print("=" * 60)


def test_landing_method_enum():
    """Test LandingMethod enum values."""
    print("\n" + "=" * 60)
    print("Testing LandingMethod enum")
    print("=" * 60)

    assert LandingMethod.IMPACT.value == "impact"
    assert LandingMethod.CONTACT.value == "contact"
    assert LandingMethod("impact") == LandingMethod.IMPACT
    assert LandingMethod("contact") == LandingMethod.CONTACT

    print("LandingMethod.IMPACT.value == 'impact': PASSED")
    print("LandingMethod.CONTACT.value == 'contact': PASSED")
    print("LandingMethod('impact') works: PASSED")
    print("LandingMethod('contact') works: PASSED")


if __name__ == "__main__":
    test_landing_method_enum()
    test_find_landing_frame_methods()
