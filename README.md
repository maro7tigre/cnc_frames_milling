# cnc_frames_milling

A PySide6 application for generating CNC G-code files for door frame manufacturing. The application provides an intuitive interface for configuring frame dimensions, selecting hinge and lock profiles, and generating customized G-code files with automatic variable replacement.

![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![PySide6](https://img.shields.io/badge/PySide6-6.0%2B-green)

## Features

### 🎨 **Profile Management**
- Create and manage reusable hinge and lock profiles
- Define custom G-code templates with variable placeholders
- Support for L-variables, custom variables, and system $ variables
- Visual profile selection with image previews
- Type-based organization system

### 🔧 **Frame Configuration**
- Interactive frame dimension setup
- Automatic calculation of optimal component positions
- Support for left/right door orientations
- Real-time visual preview of frame layout
- Configurable PM (mounting point) positions
- Smart collision detection and validation

### 📝 **G-code Generation**
- Automatic variable replacement in templates
- Support for complex mathematical expressions in G-code
- Batch generation for all frame components
- Export to organized file structure
- Real-time syntax highlighting with error detection

### 🎭 **Theming System** (unfinished)
- Multiple color themes (Dark, Light, Purple)
- Consistent UI styling across all components
- Customizable color schemes via JSON configuration

### 💾 **Project Management**
- Save/load complete projects
- Profile set management for reusable configurations
- Auto-save current configuration
- Import/export profile libraries

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/....
cd cnc-frame-wizard
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv

# On Windows
.venv\Scripts\activate

# On Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install PySide6
```

4. Run the application:
```bash
python main.py
```

## Usage

### Quick Start

1. **Profile Selection Tab**
   - Create or select hinge and lock types
   - Configure profiles with specific dimensions and G-code templates
   - Select active profiles for your project

2. **Frame Setup Tab**
   - Enter frame dimensions (height, width, door width)
   - Configure lock and hinge positions (manual or automatic)
   - Set door orientation (left/right)
   - Adjust PM positions for optimal mounting

3. **Generate Files Tab**
   - Review generated G-code files
   - Edit files directly if needed
   - Export to organized directory structure

### Variable System

The application supports three types of variables:

- **L Variables**: `{L1}`, `{L2:default_value}` - Profile-specific dimensions
- **Custom Variables**: `{custom_name:default}` - User-defined parameters
- **$ Variables**: `{$frame_height}`, `{$lock_position}` - System variables

## Project Structure

```
cnc-frame-wizard/
├── main.py                 # Application entry point
├── theme_manager.py        # Theme management system
├── ui/
│   ├── main_window.py      # Main application window
│   ├── profile/            # Profile management components
│   ├── frame/              # Frame configuration components
│   ├── generate/           # G-code generation components
│   ├── dialogs/            # Dialog windows
│   ├── widgets/            # Reusable UI widgets
│   └── gcode_ide/          # G-code editor with syntax highlighting
├── themes/                 # Theme configuration files
│   ├── dark/              # Dark theme
│   ├── light/             # Light theme
│   └── purple/            # Purple theme (default)
├── profiles/              # Profile storage
│   ├── current.json       # Current configuration
│   └── saved/             # Saved profile sets
└── projects/              # Saved projects
```

## Configuration

### Theme Customization

Themes are defined in JSON files under the `themes/` directory. Each theme includes:

- **Color scheme** (`*_colors.json`): Define color palette
- **QSS stylesheet** (`*_theme.qss`): Qt styling rules
- **Control styles** (`control_styles.json`): Widget-specific styling
- **Graph styles** (`graph_styles.json`): Visualization settings

### Default Directories

The application uses the following default directories:
- Profile sets: `profiles/saved/`
- Projects: `projects/`
- Output: `~/CNC/Output/`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings to all classes and functions
- Comment complex logic

### Testing
Before submitting a PR, ensure:
- The application runs without errors
- New features are properly integrated
- UI elements follow the existing theme system

## Known Issues

- Preview visualization is currently a placeholder
- 3D toolpath visualization not yet implemented
- Limited to 4 hinges and 4 PM positions maximum

## Roadmap

- [ ] 3D toolpath visualization
- [ ] Advanced collision detection
- [ ] Multi-language support
- [ ] Cloud storage integration
- [ ] Batch processing for multiple frames
- [ ] Custom formula editor for calculations

## License

This project is licensed under the GNU General Public License v3.0 - see below for details.

```
CNC Frame Wizard - CNC G-code generation for door frame manufacturing
Copyright (C) 2024 [Your Name]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

## Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python

---

**Note**: This software is provided as-is for CNC frame manufacturing automation. Always verify generated G-code before running on actual CNC equipment. The authors are not responsible for any damage resulting from the use of generated code.