#!/usr/bin/env python3
"""Script to find and list all @unused and @experimental decorated functions.

Usage:
    python scripts/find_unused_features.py
"""

import ast
import sys
from pathlib import Path
from typing import NamedTuple


class Feature(NamedTuple):
    """Represents a decorated feature."""

    name: str
    file: str
    line: int
    decorator: str
    reason: str
    remove_in: str | None = None
    issue: int | None = None


def find_decorated_functions(root_dir: Path) -> list[Feature]:
    """Find all functions decorated with @unused or @experimental."""
    features: list[Feature] = []

    for py_file in root_dir.rglob("*.py"):
        if "test_" in py_file.name or "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue

                for decorator in node.decorator_list:
                    decorator_name = None
                    reason = None
                    remove_in = None
                    issue = None

                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name):
                            decorator_name = decorator.func.id

                        # Extract arguments
                        for kw in decorator.keywords:
                            if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                                if isinstance(kw.value.value, str):
                                    reason = kw.value.value
                            elif kw.arg == "remove_in" and isinstance(
                                kw.value, ast.Constant
                            ):
                                if isinstance(kw.value.value, str):
                                    remove_in = kw.value.value
                            elif kw.arg == "issue" and isinstance(
                                kw.value, ast.Constant
                            ):
                                if isinstance(kw.value.value, int):
                                    issue = kw.value.value

                        # First positional arg is reason
                        if not reason and decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                if isinstance(decorator.args[0].value, str):
                                    reason = decorator.args[0].value

                    elif isinstance(decorator, ast.Name):
                        decorator_name = decorator.id

                    if decorator_name in ("unused", "experimental"):
                        rel_path = py_file.relative_to(root_dir)
                        features.append(
                            Feature(
                                name=node.name,
                                file=str(rel_path),
                                line=node.lineno,
                                decorator=decorator_name,
                                reason=reason or "No reason provided",
                                remove_in=remove_in,
                                issue=issue,
                            )
                        )

        except SyntaxError:
            print(f"Warning: Could not parse {py_file}", file=sys.stderr)
            continue

    return features


def main() -> None:
    """Main entry point."""
    root = Path(__file__).parent.parent / "src" / "kinemotion"

    features = find_decorated_functions(root)

    if not features:
        print("✅ No @unused or @experimental features found!")
        return

    print(f"Found {len(features)} marked features:\n")

    # Group by decorator type
    by_type: dict[str, list[Feature]] = {}
    for f in features:
        by_type.setdefault(f.decorator, []).append(f)

    for decorator_type in sorted(by_type.keys()):
        items = by_type[decorator_type]
        print(f"\n{'='*70}")
        print(f"@{decorator_type} Features ({len(items)})")
        print(f"{'='*70}\n")

        for feature in sorted(items, key=lambda x: x.file):
            print(f"📍 {feature.name}()")
            print(f"   File: {feature.file}:{feature.line}")
            print(f"   Reason: {feature.reason}")
            if feature.remove_in:
                print(f"   ⚠️  Remove in: v{feature.remove_in}")
            if feature.issue:
                print(f"   🔗 Issue: #{feature.issue}")
            print()

    # Summary
    print(f"{'='*70}")
    print("Summary:")
    print(f"  • @unused: {len(by_type.get('unused', []))}")
    print(f"  • @experimental: {len(by_type.get('experimental', []))}")
    print(f"  • Total: {len(features)}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
