"""Unit tests for the validation service.

Tests canonical jump type validation and alias normalization.
"""

from __future__ import annotations

import pytest

from kinemotion_backend.services.validation import (
    CANONICAL_JUMP_TYPES,
    validate_jump_type,
)


class TestValidateJumpType:
    """Tests for validate_jump_type normalization and validation."""

    @pytest.mark.parametrize("jump_type", ["cmj", "drop_jump", "sj"])
    def test_canonical_types_pass_through(self, jump_type: str) -> None:
        """Canonical jump types are returned unchanged."""
        assert validate_jump_type(jump_type) == jump_type

    def test_squat_jump_alias_normalizes_to_sj(self) -> None:
        """The 'squat_jump' alias is normalized to the canonical 'sj'."""
        assert validate_jump_type("squat_jump") == "sj"

    def test_case_insensitive_canonical(self) -> None:
        """Uppercase canonical types are normalized to lowercase."""
        assert validate_jump_type("CMJ") == "cmj"
        assert validate_jump_type("DROP_JUMP") == "drop_jump"
        assert validate_jump_type("SJ") == "sj"

    def test_case_insensitive_alias(self) -> None:
        """Uppercase alias is normalized to canonical form."""
        assert validate_jump_type("SQUAT_JUMP") == "sj"
        assert validate_jump_type("Squat_Jump") == "sj"

    def test_invalid_type_raises_value_error(self) -> None:
        """Invalid jump types raise ValueError."""
        with pytest.raises(ValueError, match="Invalid jump type"):
            validate_jump_type("invalid")

    def test_empty_string_raises_value_error(self) -> None:
        """Empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid jump type"):
            validate_jump_type("")

    def test_canonical_jump_types_constant(self) -> None:
        """CANONICAL_JUMP_TYPES contains exactly the three canonical forms."""
        assert CANONICAL_JUMP_TYPES == {"cmj", "drop_jump", "sj"}
