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
git clone https://github.com/maro7tigre/cnc_frames_milling
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

## Usage

### Quick Start

1. **Profile Selection Tab**
   - Create or select hinge and lock types
   - Configure profiles with specific dimensions and G-code templates
   - Select active profiles for your project

2. **Frame Setup Tab**
   - Edit the right and left Gcode with references to the System variables.
   - Enter frame dimensions (height, width, door width)
   - Configure lock and hinge positions (manual or automatic)
   - Preview door orientation (left/right)
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

## License

This project is licensed under the GNU General Public License v3.0

## Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python

---

**Note**: This software is provided as-is for CNC frame manufacturing automation. Always verify generated G-code before running on actual CNC equipment. The authors are not responsible for any damage resulting from the use of generated code.