# Makefile for Reveal.js Presentation with reveal-md
# Using npx - no installation required!

.PHONY: all serve watch pdf html static clean help

# Default target
all: serve

# Start presentation server (default)
serve:
	@echo "Starting Reveal.js presentation server..."
	@echo "Opening http://localhost:1948"
	@echo "Press 's' for speaker notes view"
	@echo "Press Ctrl+C to stop"
	@npx reveal-md slides.md --watch

# Watch mode with live reload
watch:
	@echo "Starting in watch mode with live reload..."
	@npx reveal-md slides.md --watch

# Export to PDF (requires Chrome/Chromium)
pdf:
	@echo "Exporting to PDF..."
	@npx reveal-md slides.md --print slides.pdf
	@echo "✅ PDF exported: slides.pdf"

# Export to static HTML site
html:
	@echo "Exporting to static HTML..."
	@npx reveal-md slides.md --static presentation-output
	@echo "✅ Static site created in presentation-output/"

# Export to standalone single HTML file
standalone:
	@echo "Creating standalone HTML file..."
	@npx reveal-md slides.md --static presentation-output --static-dirs=false
	@cp presentation-output/index.html ../kinemotion-presentation.html
	@echo "✅ Standalone HTML: ../kinemotion-presentation.html"

# Speaker view
speaker:
	@echo "Starting with speaker notes..."
	@echo "Press 's' to open speaker view"
	@npx reveal-md slides.md

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf presentation-output/
	@rm -f slides.pdf
	@rm -f ../kinemotion-presentation.html
	@echo "✅ Cleaned!"

# Help
help:
	@echo "Kinemotion Reveal.js Presentation"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  serve      - Start presentation server (default)"
	@echo "  watch      - Start with live reload"
	@echo "  pdf        - Export to PDF"
	@echo "  html       - Export to static HTML site"
	@echo "  standalone - Create single HTML file"
	@echo "  speaker    - Start with speaker notes"
	@echo "  clean      - Remove generated files"
	@echo "  help       - Show this help"
	@echo ""
	@echo "Keyboard shortcuts during presentation:"
	@echo "  s - Speaker notes"
	@echo "  f - Fullscreen"
	@echo "  o - Overview mode"
	@echo "  ? - Show all shortcuts"
