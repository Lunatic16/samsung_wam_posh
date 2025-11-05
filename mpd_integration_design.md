# MPD Integration Architecture for Samsung WAM Speakers

## Overview

This document outlines the architecture for integrating Samsung WAM speakers with Music Player Daemon (MPD) to enable discovery, control, and grouping of WAM speakers through MPD.

## Goals

1. Allow MPD to recognize Samsung WAM speakers as audio outputs
2. Enable MPD to control playback on WAM speakers
3. Provide volume control for WAM speakers from MPD
4. Allow grouping of WAM speakers through MPD
5. Maintain compatibility with existing WAM functionality

## Architecture Components

### 1. MPDControllerBridge Class

This class will act as an intermediary between MPD and WAM speakers:

- Monitor MPD events and translate them to WAM speaker commands
- Handle playback control synchronization
- Manage volume synchronization between MPD and WAM speakers

### 2. WAMOutputPlugin

A virtual MPD output plugin that represents WAM speakers:

- Appears as an audio output in MPD
- Forwards audio to WAM speakers via streaming
- Reports status back to MPD

### 3. WAMMPDIntegration Module

Main module that ties everything together:

- Discovers WAM speakers
- Manages connections to both MPD and WAM speakers
- Provides unified interface for MPD-WAM interaction

## Implementation Strategy

### Option 1: HTTP Streaming Bridge (Recommended)

1. Configure MPD with HTTP streaming output
2. Create a streaming service that receives from MPD and forwards to WAM speakers
3. Use existing WAM speaker control methods for non-audio commands

### Option 2: Client-Side Integration

1. Use python-mpd2 to monitor MPD state
2. Translate MPD commands to WAM commands
3. Control WAM speakers as separate entities from audio routing

### Option 3: Custom Output Plugin (Advanced)

1. Develop a custom MPD output plugin in C++
2. Requires modifying MPD source code
3. Most integrated solution but most complex

## Recommended Approach: HTTP Streaming Bridge

The HTTP streaming approach is recommended because:

- It works with standard MPD installations
- No modification of MPD source required  
- Leverages existing WAM streaming capabilities
- Can be implemented entirely in Python
- Maintains separation of concerns

## Detailed Architecture

### Core Classes

1. `WAMMPDController`
   - Connects to MPD using python-mpd2
   - Discovers WAM speakers using existing discovery
   - Maintains state synchronization

2. `WAMHTTPStreamer`
   - Creates HTTP server to receive audio from MPD
   - Forwards audio streams to WAM speakers
   - Handles multiple simultaneous speakers

3. `WAMGroupManager`
   - Manages speaker groups
   - Synchronizes group state between MPD and WAM
   - Handles group creation/destruction

### Flow of Operations

1. **Discovery Phase**
   - WAMMPDController discovers WAM speakers
   - Registers speakers with MPD as virtual outputs

2. **Setup Phase**
   - Configure MPD HTTP stream to point to WAMHTTPStreamer
   - Establish connections to all discovered WAM speakers

3. **Operation Phase**
   - Monitor MPD for state changes
   - Translate playback commands to WAM commands
   - Handle volume changes across all speakers
   - Manage grouping operations

4. **Cleanup Phase**
   - Properly disconnect and ungroup speakers
   - Clean up HTTP streaming service

## API Design

### WAMMPDController Interface

```python
class WAMMPDController:
    def __init__(self, mpd_host="localhost", mpd_port=6600):
        """Initialize connection to MPD and discover WAM speakers"""
        
    def discover_wam_speakers(self):
        """Discover available WAM speakers on network"""
        
    def connect_to_mpd(self):
        """Establish connection to MPD server"""
        
    def start_sync_loop(self):
        """Start monitoring MPD and synchronizing to WAM speakers"""
        
    def set_volume(self, speaker_name, volume):
        """Set volume on specific WAM speaker"""
        
    def play_on_speaker(self, speaker_name):
        """Start playback on specific speaker"""
        
    def create_group(self, group_name, speaker_names):
        """Create group of WAM speakers"""
        
    def play_on_group(self, group_name):
        """Start playback on group of speakers"""
```

### Integration with Existing Code

The new MPD integration will:
- Use existing `SamsungWamDiscovery` class for speaker discovery
- Use existing `SamsungWamSpeaker` class for speaker control
- Integrate with existing `PipeWireAudioStreamer` and `GStreamerAudioStreamer` for audio streaming options
- Add new methods to `WamController` class for MPD-specific functionality

## Data Flow

1. MPD State Change → WAMMPDController receives event
2. Event Translation → Map MPD command to WAM command
3. Command Execution → Send command to appropriate WAM speaker(s)
4. Status Update → Update MPD with WAM speaker status

## Error Handling

- Network connectivity issues between MPD and WAM speakers
- Speaker discovery failures
- Audio streaming interruptions
- MPD connection failures

## Security Considerations

- Authentication for MPD connection
- Network security for audio streaming
- Protection against unauthorized speaker control

## Testing Strategy

1. Unit tests for each component
2. Integration tests for MPD-WAM communication
3. End-to-end tests for complete playback scenarios
4. Error condition testing

This architecture provides a robust and maintainable solution for integrating Samsung WAM speakers with MPD while preserving all existing functionality.