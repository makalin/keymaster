# KeyMaster

KeyMaster is a powerful keyboard-driven mouse control utility that allows you to navigate your screen and perform mouse actions without leaving your keyboard. It overlays a customizable grid system on your screen, enabling precise cursor movements and mouse actions through simple key combinations.

## Features

- **Grid-Based Navigation**: Divides your screen into a customizable grid (default 8x8) for precise cursor positioning
- **Multi-Screen Support**: Seamlessly navigate between multiple monitors using arrow keys
- **Multiple Mouse Actions**:
  - Left, right, and middle click
  - Double-click support
  - Drag and drop functionality
- **Smooth Cursor Movement**: Optional smooth cursor transitions between points
- **System Tray Integration**: Easy access to settings and controls
- **Customizable Configuration**: Adjust grid size, colors, opacity, and hotkeys
- **Always-On-Top Display**: Grid overlay stays visible when activated

## Installation

```bash
# Dependencies
pip install PyQt6 keyboard pyautogui

# Clone and run
git clone https://github.com/yourusername/keymaster.git
cd keymaster
python keymaster.py
```

## Usage

### Basic Navigation

1. Press `Cmd` (default) to show the grid overlay
2. Type a cell coordinate (e.g., 'A1', 'B2') to move the cursor
3. Press `Esc` to dismiss the grid

### Mouse Actions

- **Change Mouse Button**:
  - Press `Tab` to cycle between left, right, and middle mouse buttons
  - Use `right cmd` for right-click
  - Use `cmd+m` for middle-click
- **Drag and Drop**:
  1. Press `cmd+d` to initiate drag
  2. Select source cell
  3. Select destination cell

### Multi-Monitor Support

- Use `Left Arrow` and `Right Arrow` to switch between screens while the grid is active

## Configuration

KeyMaster uses a JSON configuration file located at `~/.keymaster/config.json`. Here's the default configuration:

```json
{
    "grid_size": 8,
    "overlay_opacity": 0.5,
    "grid_color": "#FFFFFF",
    "background_color": "#000000",
    "font_size": 14,
    "smooth_movement": true,
    "movement_duration": 0.2,
    "hotkeys": {
        "show_grid": "cmd",
        "dismiss_grid": "esc",
        "right_click": "right cmd",
        "middle_click": "cmd+m",
        "start_drag": "cmd+d"
    }
}
```

### Configuration Options

- `grid_size`: Number of cells in each row/column
- `overlay_opacity`: Transparency of the grid overlay (0.0-1.0)
- `grid_color`: Color of grid lines and labels
- `background_color`: Color of the overlay background
- `font_size`: Size of cell labels
- `smooth_movement`: Enable/disable smooth cursor transitions
- `movement_duration`: Duration of smooth movements in seconds
- `hotkeys`: Customize keyboard shortcuts

## Requirements

- Python 3.6+
- PyQt6
- keyboard
- pyautogui

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgments

KeyMaster was inspired by keyboard-driven navigation tools and aims to improve productivity for users who prefer keyboard-based controls.
