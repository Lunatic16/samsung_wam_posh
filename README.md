# Samsung WAM Linux Controller

A comprehensive Linux-compatible Python implementation for controlling Samsung Wireless Audio Multiroom (WAM) speakers. This project provides a complete interface for managing Samsung's multiroom audio system through their REST API, with a complete rewrite from the original PowerShell version to work on Linux systems.

## Features

- **Speaker Discovery**: Automatically discover Samsung WAM speakers on your local network using SSDP
- **Individual Control**: Control each speaker independently (volume, mute, playback, etc.)
- **Group Management**: Create and manage multi-speaker groups for synchronized playback
- **Playback Control**: Full playback controls including play, pause, next, previous, repeat modes
- **EQ Management**: Control equalizer settings with 7-band EQ support
- **Content Services**: Interface with various music services through CPM API
- **Network Configuration**: WiFi settings, speaker information, and system settings management
- **Command-Line Interface**: Complete CLI tool for integration into scripts and automation

## Files

### `wam_discovery.py`
Main Python library containing:
- `SamsungWamSpeaker` class with methods to control individual speakers
- `SamsungWamDiscovery` class for network discovery of speakers
- `WamController` class for high-level speaker management
- Functions to load and save speaker configurations

### `wam_cli.py`
Command-line interface for controlling speakers from the terminal with subcommands for all operations.

### `example_usage.py`
Complete examples demonstrating all the functionality of the library.

### `WAM_API.txt`
A comprehensive list of API commands available for Samsung WAM speakers, organized into:
- UIC (User Interface Control): Volume, playback, grouping, etc.
- CPM (Content Provider Management): Music services, playlists, favorites, etc.

### `speakers.txt`
A JSON file containing configuration for Samsung speakers on the network, including IP addresses, names, current settings, and grouping information.

## Installation

1. Install Python 3.6 or higher
2. Install dependencies: `pip install -r requirements.txt`

## Usage

### Command-Line Interface

```bash
# Discover speakers on your network
python3 wam_cli.py discover

# List all known speakers
python3 wam_cli.py list

# Set volume for a speaker
python3 wam_cli.py volume "Living Room" 15

# Get current volume
python3 wam_cli.py volume "Living Room" --get

# Control mute
python3 wam_cli.py mute "Kitchen" on

# Control playback
python3 wam_cli.py playback "TV Room" play

# Create a group
python3 wam_cli.py group create --name "All Speakers" --speakers "Living Room" "Kitchen" "Dining Room"

# Get speaker information
python3 wam_cli.py info "Living Room"
```

### Python Library Usage

```python
from wam_discovery import WamController

# Create controller
controller = WamController()

# Discover speakers
speakers = controller.discover()

# Control a speaker
for speaker in speakers:
    speaker.set_volume(15)
    speaker.play()
```

## Requirements

- Python 3.6+
- requests library
- Samsung WAM speakers on the local network

## API Information

Samsung WAM speakers use two main API endpoints:
- UIC (User Interface Control): For basic speaker functions
- CPM (Content Provider Management): For content services and management

The API operates on port 55001 with XML-based commands that are URL-encoded for transmission.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is without any warranty.# samsung_wam_posh
