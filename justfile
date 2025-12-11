# Check python sanity
python-check:
    @echo "Running pyright..."
    uv run pyright
    (cd backend && uv run pyright)
    @echo "Running ruff check and format..."
    uv run ruff check --fix
    uv run ruff format
    (cd backend && uv run ruff check --fix)
    (cd backend && uv run ruff format)

# Clean generated and temporary files (preserves .claude/, .cursor/, .mcp.json)
clean:
    @echo "Cleaning generated files..."
    rm -rf .coverage
    rm -rf .pytest_cache
    rm -rf htmlcov
    rm -rf coverage.xml
    rm -rf .ruff_cache
    rm -rf .mypy_cache
    rm -rf .pytype
    rm -rf dist
    rm -rf build
    rm -rf *.egg-info
    find . -type d -name __pycache__ ! -path "*/.venv/*" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" ! -path "*/.venv/*" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" ! -path "*/.venv/*" -delete 2>/dev/null || true
    @echo "✓ Clean complete"

# Show what would be deleted (dry run)
clean-preview:
    @echo "Files/directories that would be deleted:"
    @test -e .coverage && echo "  .coverage" || true
    @test -d .pytest_cache && echo "  .pytest_cache/" || true
    @test -d htmlcov && echo "  htmlcov/" || true
    @test -e coverage.xml && echo "  coverage.xml" || true
    @test -d .ruff_cache && echo "  .ruff_cache/" || true
    @test -d .mypy_cache && echo "  .mypy_cache/" || true
    @test -d .pytype && echo "  .pytype/" || true
    @test -d dist && echo "  dist/" || true
    @test -d build && echo "  build/" || true
    @find . -name "*.egg-info" -type d ! -path "*/.venv/*" 2>/dev/null | sed 's/^/  /' || true
    @find . -type d -name __pycache__ ! -path "*/.venv/*" 2>/dev/null | sed 's/^/  /' || true
    @find . -type f -name "*.pyc" ! -path "*/.venv/*" 2>/dev/null | sed 's/^/  /' || true
    @find . -type f -name "*.pyo" ! -path "*/.venv/*" 2>/dev/null | sed 's/^/  /' || true
