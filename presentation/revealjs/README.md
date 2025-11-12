# Kinemotion Reveal.js Presentation

This is the Reveal.js version of the Kinemotion presentation, offering advanced features like animations, themes, and plugins.

## Quick Start (No Installation Required!)

```bash
# Start presentation server
npx reveal-md slides.md

# Or use Make
make serve
```

The presentation will open at <http://localhost:1948>

## Features

### 🎯 Key Features

- **Animations**: Fragments, transitions, auto-animate
- **Themes**: Multiple built-in themes (black, white, league, etc.)
- **Speaker Notes**: Press `s` for speaker view with notes, timer, and next slide
- **Overview Mode**: Press `o` to see all slides at once
- **PDF Export**: Native PDF export with `--print`
- **Touch Support**: Swipe navigation on mobile devices
- **Plugins**: Code highlighting, math, zoom, search, and more

### 📝 Speaker Notes

Speaker notes are included in the markdown using `Note:` prefix:

```markdown
## Slide Title

Content here

Note: These are speaker notes only visible in speaker view
```

Press `s` during presentation to open speaker view.

## Commands

### Using NPX (No Installation)

```bash
# Serve presentation
npx reveal-md slides.md

# Watch mode with live reload
npx reveal-md slides.md --watch

# Export to PDF
npx reveal-md slides.md --print slides.pdf

# Export to static HTML
npx reveal-md slides.md --static output/

# With custom theme
npx reveal-md slides.md --theme solarized
```

### Using Make

```bash
make serve      # Start presentation server
make watch      # Live reload mode
make pdf        # Export to PDF
make html       # Export to static site
make standalone # Single HTML file
make speaker    # Open with speaker notes
make clean      # Clean generated files
make help       # Show all commands
```

## Keyboard Shortcuts

During presentation:

- **Arrow keys** - Navigate slides
- **Space** - Next slide
- **s** - Speaker notes view
- **f** - Fullscreen
- **o** - Overview mode
- **b** - Black screen
- **v** - Pause
- **?** - Show all shortcuts
- **Esc** - Exit fullscreen/overview

## Themes

Change theme in the YAML frontmatter:

```yaml
---
theme: black  # or white, league, beige, sky, night, serif, simple, solarized
---
```

Or via command line:

```bash
npx reveal-md slides.md --theme league
```

## Slide Structure

- `---` - Horizontal slide separator
- `----` - Vertical slide separator
- `Note:` - Speaker notes

## Advanced Features

### Fragments (Animations)

```markdown
- Item 1 <!-- .element: class="fragment" -->
- Item 2 <!-- .element: class="fragment" -->
```

### Background Images

```markdown
<!-- .slide: data-background="image.jpg" -->
## Slide with background
```

### Code Highlighting

````markdown
```python [1-2|3|4]
def hello():
    name = "World"
    print(f"Hello {name}")
    return name
```
````

## PDF Export

```bash
# Using reveal-md
make pdf

# Or directly
npx reveal-md slides.md --print slides.pdf
```

**Note**: PDF export requires Chrome/Chromium installed.

## Presenting via Zoom

1. Start the presentation:

   ```bash
   make serve
   ```

1. Open in browser: <http://localhost:1948>

1. Press `f` for fullscreen

1. Share browser window in Zoom

1. Use speaker view (`s`) on a second monitor

## Customization

### Custom CSS

Create `custom.css` and reference it:

```bash
npx reveal-md slides.md --css custom.css
```

### Custom Theme

Create a theme file and use:

```bash
npx reveal-md slides.md --theme-url custom-theme.css
```

## Troubleshooting

- **Port in use**: Change port with `--port 8080`
- **PDF issues**: Ensure Chrome is installed
- **Theme not loading**: Check theme name spelling
- **Notes not showing**: Press `s` for speaker view

## Resources

- [Reveal.js Documentation](https://revealjs.com)
- [reveal-md Documentation](https://github.com/webpro/reveal-md)
- [Markdown Guide](https://revealjs.com/markdown/)
- [Speaker View Guide](https://revealjs.com/speaker-view/)
