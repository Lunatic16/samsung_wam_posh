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
- **PipeWire Integration**: Advanced audio streaming and volume synchronization with PipeWire audio server
- **GStreamer Integration**: Advanced audio streaming capabilities using GStreamer
- **MPD Integration**: Full integration with Music Player Daemon for WAM speaker control
- **Command-Line Interface**: Complete CLI tool for integration into scripts and automation

## Files

### `wam_discovery.py`
Main Python library containing:
- `SamsungWamSpeaker` class with methods to control individual speakers
- `SamsungWamDiscovery` class for network discovery of speakers
- `WamController` class for high-level speaker management
- `PipeWireAudioStreamer` class for PipeWire integration
- `GStreamerAudioStreamer` class for GStreamer integration
- Functions to load and save speaker configurations

### `wam_cli.py`
Command-line interface for controlling speakers from the terminal with subcommands for all operations, including PipeWire and GStreamer integration commands.

### `pipewire_integration.py`
PipeWire-specific integration module for audio streaming and device management.

### `gstreamer_integration.py`
GStreamer-specific integration module for advanced audio streaming capabilities.

### `mpd_integration.py`
MPD (Music Player Daemon) integration module for controlling WAM speakers from MPD.

### `example_usage.py`
Complete examples demonstrating all the functionality of the library, including PipeWire, GStreamer, and MPD integration.

### `WAM_API.txt`
A comprehensive list of API commands available for Samsung WAM speakers, organized into:
- UIC (User Interface Control): Volume, playback, grouping, etc.
- CPM (Content Provider Management): Music services, playlists, favorites, etc.

### `speakers.txt`
A JSON file containing configuration for Samsung speakers on the network, including IP addresses, names, current settings, and grouping information.

## Installation

1. Install Python 3.6 or higher
2. Install dependencies: `pip install -r requirements.txt`
3. For PipeWire integration: Install system packages `pipewire` and `pipewire-alsa` (or `pulseaudio` for compatibility)
4. For GStreamer integration: Install `gstreamer` and Python GStreamer bindings:
   - Ubuntu/Debian: `sudo apt-get install python3-gi gir1.2-gstreamer-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good`
   - Fedora/RHEL: `sudo dnf install python3-gobject gstreamer1.0-plugins-base gstreamer1.0-plugins-good`
   - Arch: `sudo pacman -S python-gobject gst-plugins-base gst-plugins-good`
5. For MPD integration: Install `python-mpd2` library: `pip install python-mpd2`

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

# PipeWire integration commands
python3 wam_cli.py pipewire devices                    # List PipeWire devices
python3 wam_cli.py pipewire stream "Living Room"      # Stream to speaker
python3 wam_cli.py pipewire sync "Living Room" sink0  # Sync volumes

# GStreamer integration commands
python3 wam_cli.py gstreamer stream "Living Room" --source-type pulse  # Stream using PulseAudio source

# MPD integration commands
python3 wam_cli.py mpd init                    # Initialize MPD-WAM integration
python3 wam_cli.py mpd outputs                 # List available WAM speakers as MPD outputs
python3 wam_cli.py mpd enable "Living Room"    # Enable speaker as MPD output
python3 wam_cli.py mpd volume "Living Room" 75 # Set volume for WAM speaker from MPD
python3 wam_cli.py mpd group "All Speakers" "Living Room" "Kitchen" # Create group of speakers
python3 wam_cli.py mpd start-sync              # Start synchronization between MPD and WAM
python3 wam_cli.py mpd status                  # Show MPD-WAM integration status
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

# PipeWire integration
from wam_discovery import PipeWireAudioStreamer
pipewire = PipeWireAudioStreamer()
if pipewire.is_available():
    devices = pipewire.get_available_devices()
    # Set up streaming to a speaker
    pipewire.stream_to_speaker(speaker)
    # Sync volumes
    pipewire.sync_volume_with_pipewire(speaker, devices[0]['id'])

# GStreamer integration
from wam_discovery import GStreamerAudioStreamer
gstreamer = GStreamerAudioStreamer()
if gstreamer.is_available():
    # Stream audio from system to speaker
    gstreamer.stream_to_speaker(speaker, source_type="pulse")

# MPD integration
from wam_discovery import MPDAudioStreamer
mpd_streamer = MPDAudioStreamer()
if mpd_streamer.is_available():
    # Initialize MPD-WAM integration
    mpd_streamer.initialize()
    # Enable speaker as MPD output
    mpd_streamer.enable_output("Living Room")
    # Set volume from MPD
    mpd_streamer.set_volume("Living Room", 70)
    # Create group of speakers
    mpd_streamer.create_group("All Speakers", ["Living Room", "Kitchen", "Dining Room"])
    # Start synchronization between MPD and WAM
    mpd_streamer.start_sync()
```

## Requirements

- Python 3.6+
- requests library
- python-mpd2 library for MPD integration
- PipeWire (or PulseAudio for compatibility) audio server
- For advanced audio streaming: GStreamer with Python bindings (PyGObject)
- Samsung WAM speakers on the local network

## API Information

Samsung WAM speakers use two main API endpoints:
- UIC (User Interface Control): For basic speaker functions
- CPM (Content Provider Management): For content services and management

The API operates on port 55001 with XML-based commands that are URL-encoded for transmission.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is without any warranty.
