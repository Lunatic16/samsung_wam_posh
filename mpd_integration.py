#!/usr/bin/env python3
"""
MPD Integration for Samsung WAM Speaker Controller
Provides integration between Music Player Daemon (MPD) and Samsung WAM speakers
"""

import threading
import time
from typing import Dict, List, Optional, Any
from mpd import MPDClient
from wam_discovery import (
    WamController, 
    SamsungWamSpeaker, 
    SamsungWamDiscovery,
    GStreamerAudioStreamer
)
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import io
import json
import urllib.parse


class WAMMPDController:
    """
    Controller that integrates MPD with Samsung WAM speakers
    """
    
    def __init__(self, mpd_host: str = "localhost", mpd_port: int = 6600):
        self.mpd_host = mpd_host
        self.mpd_port = mpd_port
        self.mpd_client = MPDClient()
        self.wam_controller = WamController()
        self.is_connected = False
        self.sync_thread = None
        self.running = False
        self.wam_speakers = {}  # Maps speaker names to SamsungWamSpeaker objects
        self.mpd_to_wam_mapping = {}  # Maps MPD output names to WAM speakers
        self.wam_groups = {}  # Tracks WAM speaker groups
        self.last_mpd_status = {}
        
    def connect_to_mpd(self) -> bool:
        """
        Connect to MPD server
        """
        try:
            self.mpd_client.connect(self.mpd_host, self.mpd_port)
            self.is_connected = True
            print(f"Connected to MPD at {self.mpd_host}:{self.mpd_port}")
            return True
        except Exception as e:
            print(f"Failed to connect to MPD: {e}")
            return False
    
    def disconnect_from_mpd(self):
        """
        Disconnect from MPD server
        """
        if self.is_connected:
            try:
                self.mpd_client.close()
                self.mpd_client.disconnect()
                print("Disconnected from MPD")
            except:
                pass
            self.is_connected = False
    
    def discover_wam_speakers(self) -> List[SamsungWamSpeaker]:
        """
        Discover WAM speakers and store them in the controller
        """
        speakers = self.wam_controller.discover()
        self.wam_speakers = {speaker.name: speaker for speaker in speakers}
        print(f"Discovered {len(speakers)} WAM speakers")
        return speakers
    
    def get_available_speakers(self) -> List[str]:
        """
        Get list of available WAM speaker names
        """
        return list(self.wam_speakers.keys())
    
    def get_mpd_outputs(self) -> List[Dict[str, Any]]:
        """
        Get current MPD outputs (for reference)
        """
        if not self.is_connected:
            return []
        
        try:
            outputs = self.mpd_client.outputs()
            return outputs
        except Exception as e:
            print(f"Error getting MPD outputs: {e}")
            return []
    
    def enable_wam_output(self, speaker_name: str) -> bool:
        """
        Enable a WAM speaker as an output (virtual concept)
        """
        if speaker_name not in self.wam_speakers:
            print(f"Speaker {speaker_name} not found")
            return False
        
        # In our implementation, enabling a WAM "output" means starting audio streaming
        speaker = self.wam_speakers[speaker_name]
        
        # Use GStreamer to stream from MPD to the speaker
        # This is a simplified approach - in reality, we'd need to capture MPD audio
        try:
            # For now, we'll just acknowledge the output is "enabled"
            self.mpd_to_wam_mapping[speaker_name] = {
                'speaker': speaker,
                'enabled': True,
                'volume': 50  # Default volume
            }
            print(f"Enabled WAM speaker output: {speaker_name}")
            return True
        except Exception as e:
            print(f"Error enabling WAM output {speaker_name}: {e}")
            return False
    
    def disable_wam_output(self, speaker_name: str) -> bool:
        """
        Disable a WAM speaker as an output
        """
        if speaker_name in self.mpd_to_wam_mapping:
            self.mpd_to_wam_mapping[speaker_name]['enabled'] = False
            print(f"Disabled WAM speaker output: {speaker_name}")
            return True
        return False
    
    def set_wam_volume(self, speaker_name: str, volume: int) -> bool:
        """
        Set volume for a WAM speaker and sync with MPD if possible
        """
        if speaker_name not in self.wam_speakers:
            print(f"Speaker {speaker_name} not found")
            return False
        
        speaker = self.wam_speakers[speaker_name]
        # Convert MPD volume (0-100) to WAM volume (0-30)
        wam_volume = max(0, min(30, int(volume * 0.3)))
        
        try:
            result = speaker.set_volume(wam_volume)
            if result:
                print(f"Set volume {volume}% ({wam_volume}/30) for {speaker_name}")
                # Update our mapping
                if speaker_name in self.mpd_to_wam_mapping:
                    self.mpd_to_wam_mapping[speaker_name]['volume'] = volume
                else:
                    self.mpd_to_wam_mapping[speaker_name] = {
                        'speaker': speaker,
                        'enabled': True,
                        'volume': volume
                    }
                return True
        except Exception as e:
            print(f"Error setting volume for {speaker_name}: {e}")
        
        return False
    
    def get_wam_volume(self, speaker_name: str) -> Optional[int]:
        """
        Get volume for a WAM speaker
        """
        if speaker_name not in self.wam_speakers:
            return None
        
        try:
            speaker = self.wam_speakers[speaker_name]
            vol = speaker.get_volume()
            # Convert WAM volume (0-30) to MPD volume (0-100)
            mpd_volume = int(vol / 30 * 100)
            return mpd_volume
        except Exception as e:
            print(f"Error getting volume for {speaker_name}: {e}")
            return None
    
    def create_group(self, group_name: str, speaker_names: List[str]) -> bool:
        """
        Create a group of WAM speakers
        """
        # Validate speakers exist
        for name in speaker_names:
            if name not in self.wam_speakers:
                print(f"Speaker {name} not found")
                return False
        
        # Get speaker objects
        group_speakers = [self.wam_speakers[name] for name in speaker_names[1:]]  # First is main
        main_speaker = self.wam_speakers[speaker_names[0]]
        
        # Create the group
        try:
            result = main_speaker.group_with_speakers(group_name, group_speakers)
            if result:
                self.wam_groups[group_name] = {
                    'main': main_speaker,
                    'sub_speakers': group_speakers,
                    'members': [main_speaker] + group_speakers
                }
                print(f"Created group '{group_name}' with {len(speaker_names)} speakers")
                return True
        except Exception as e:
            print(f"Error creating group {group_name}: {e}")
        
        return False
    
    def ungroup_speakers(self, group_name: str) -> bool:
        """
        Remove speakers from a group
        """
        if group_name not in self.wam_groups:
            print(f"Group {group_name} not found")
            return False
        
        try:
            group = self.wam_groups[group_name]
            for speaker in group['members']:
                speaker.ungroup()
            
            del self.wam_groups[group_name]
            print(f"Ungrouped '{group_name}'")
            return True
        except Exception as e:
            print(f"Error ungrouping {group_name}: {e}")
            return False
    
    def get_groups(self) -> Dict[str, Any]:
        """
        Get all WAM speaker groups
        """
        return self.wam_groups
    
    def play_on_speaker(self, speaker_name: str) -> bool:
        """
        Start playback on specific WAM speaker
        """
        if speaker_name not in self.wam_speakers:
            print(f"Speaker {speaker_name} not found")
            return False
        
        try:
            speaker = self.wam_speakers[speaker_name]
            result = speaker.play()
            print(f"Started playback on {speaker_name}")
            return result is not None
        except Exception as e:
            print(f"Error starting playback on {speaker_name}: {e}")
            return False
    
    def play_on_group(self, group_name: str) -> bool:
        """
        Start playback on a group of WAM speakers
        """
        if group_name not in self.wam_groups:
            print(f"Group {group_name} not found")
            return False
        
        try:
            group = self.wam_groups[group_name]
            # Play on main speaker (which should propagate to group)
            main_speaker = group['main']
            result = main_speaker.play()
            print(f"Started playback on group '{group_name}'")
            return result is not None
        except Exception as e:
            print(f"Error starting playback on group {group_name}: {e}")
            return False
    
    def start_sync_loop(self):
        """
        Start the synchronization loop to monitor MPD state and update WAM speakers
        """
        if not self.is_connected:
            print("Not connected to MPD, cannot start sync loop")
            return
        
        if self.sync_thread is not None and self.sync_thread.is_alive():
            print("Sync loop already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print("Started MPD-WAM synchronization loop")
    
    def stop_sync_loop(self):
        """
        Stop the synchronization loop
        """
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        print("Stopped MPD-WAM synchronization loop")
    
    def _sync_loop(self):
        """
        Internal method for synchronization loop
        """
        while self.running:
            try:
                if self.is_connected:
                    # Get current MPD status
                    current_status = self.mpd_client.status()
                    
                    # Check for changes and sync to WAM speakers
                    self._sync_status_changes(self.last_mpd_status, current_status)
                    
                    self.last_mpd_status = current_status.copy()
                
                # Wait before next check
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in sync loop: {e}")
                time.sleep(5)  # Wait longer after error
    
    def _sync_status_changes(self, old_status: Dict, new_status: Dict):
        """
        Compare old and new MPD status and sync changes to WAM speakers
        """
        # Check for playback state changes
        old_state = old_status.get('state', 'stop')
        new_state = new_status.get('state', 'stop')
        
        if old_state != new_state:
            print(f"MPD state changed from {old_state} to {new_state}")
            # Sync state change to enabled WAM speakers
            for speaker_name, data in self.mpd_to_wam_mapping.items():
                if data['enabled']:
                    speaker = data['speaker']
                    if new_state == 'play':
                        speaker.play()
                    elif new_state == 'pause':
                        speaker.pause()
                    elif new_state == 'stop':
                        speaker.pause()  # WAM doesn't have a stop, so pause
        
        # Check for volume changes
        old_volume = old_status.get('volume', '0')
        new_volume = new_status.get('volume', '0')
        
        if old_volume != new_volume:
            try:
                mpd_volume = int(new_volume)
                # Sync volume change to all enabled WAM speakers
                for speaker_name, data in self.mpd_to_wam_mapping.items():
                    if data['enabled']:
                        self.set_wam_volume(speaker_name, mpd_volume)
            except ValueError:
                pass  # Volume not a valid integer
    
    def get_mpd_current_song(self) -> Dict[str, Any]:
        """
        Get current song information from MPD
        """
        if not self.is_connected:
            return {}
        
        try:
            return self.mpd_client.currentsong()
        except Exception as e:
            print(f"Error getting current song: {e}")
            return {}
    
    def get_mpd_status(self) -> Dict[str, Any]:
        """
        Get current MPD status
        """
        if not self.is_connected:
            return {}
        
        try:
            return self.mpd_client.status()
        except Exception as e:
            print(f"Error getting MPD status: {e}")
            return {}


class WAMHTTPStreamer:
    """
    HTTP server to receive audio from MPD and forward to WAM speakers
    """
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.wam_speakers = []
        self.server = None
        self.server_thread = None
        self.running = False
    
    def add_wam_speaker(self, speaker: SamsungWamSpeaker):
        """
        Add a WAM speaker to receive audio streams
        """
        self.wam_speakers.append(speaker)
    
    def remove_wam_speaker(self, speaker: SamsungWamSpeaker):
        """
        Remove a WAM speaker from the stream list
        """
        if speaker in self.wam_speakers:
            self.wam_speakers.remove(speaker)
    
    def start(self):
        """
        Start the HTTP streaming server
        """
        # Create custom request handler
        streamer = self
        
        class StreamHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                # Handle requests from MPD or provide stream information
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                
                response = f"MPD to WAM Streamer - Serving {len(streamer.wam_speakers)} speakers"
                self.wfile.write(response.encode())
            
            def do_POST(self):
                # Receive audio stream from MPD
                content_length = int(self.headers['Content-Length'])
                audio_data = self.rfile.read(content_length)
                
                # Forward audio data to WAM speakers
                # This is a simplified example - real implementation would need 
                # proper streaming to each speaker
                print(f"Received audio stream of {len(audio_data)} bytes")
                
                # In a real implementation, we would stream this audio to the WAM speakers
                # using the play_url method with the audio data
                for speaker in streamer.wam_speakers:
                    print(f"Forwarding audio to {speaker.name}")
                
                self.send_response(200)
                self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress logging
                pass
        
        self.running = True
        self.server = HTTPServer(('', self.port), StreamHandler)
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"WAM HTTP Streamer started on port {self.port}")
    
    def _run_server(self):
        """
        Run the HTTP server
        """
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.running:
                print(f"HTTP server error: {e}")
    
    def stop(self):
        """
        Stop the HTTP streaming server
        """
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=2)
        print("WAM HTTP Streamer stopped")


class WAMMPDIntegration:
    """
    Main integration class that combines MPD control and WAM speaker functionality
    """
    
    def __init__(self, mpd_host: str = "localhost", mpd_port: int = 6600):
        self.mpd_controller = WAMMPDController(mpd_host, mpd_port)
        self.http_streamer = None
    
    def initialize(self) -> bool:
        """
        Initialize the MPD-WAM integration
        """
        # Connect to MPD
        if not self.mpd_controller.connect_to_mpd():
            return False
        
        # Discover WAM speakers
        self.mpd_controller.discover_wam_speakers()
        
        return True
    
    def get_available_speakers(self) -> List[str]:
        """
        Get list of available WAM speakers
        """
        return self.mpd_controller.get_available_speakers()
    
    def enable_output(self, speaker_name: str) -> bool:
        """
        Enable a WAM speaker as an output
        """
        return self.mpd_controller.enable_wam_output(speaker_name)
    
    def set_volume(self, speaker_name: str, volume: int) -> bool:
        """
        Set volume for a WAM speaker
        """
        return self.mpd_controller.set_wam_volume(speaker_name, volume)
    
    def create_group(self, group_name: str, speaker_names: List[str]) -> bool:
        """
        Create a group of WAM speakers
        """
        return self.mpd_controller.create_group(group_name, speaker_names)
    
    def start_playback(self, target: str, target_type: str = "speaker") -> bool:
        """
        Start playback on a speaker or group
        """
        if target_type == "speaker":
            return self.mpd_controller.play_on_speaker(target)
        elif target_type == "group":
            return self.mpd_controller.play_on_group(target)
        return False
    
    def start_sync(self):
        """
        Start the synchronization loop
        """
        self.mpd_controller.start_sync_loop()
    
    def stop_sync(self):
        """
        Stop the synchronization loop
        """
        self.mpd_controller.stop_sync_loop()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get overall status of the integration
        """
        return {
            'mpd_connected': self.mpd_controller.is_connected,
            'wam_speakers': self.mpd_controller.get_available_speakers(),
            'groups': list(self.mpd_controller.get_groups().keys()),
            'mpd_status': self.mpd_controller.get_mpd_status(),
            'current_song': self.mpd_controller.get_mpd_current_song()
        }
    
    def cleanup(self):
        """
        Clean up resources
        """
        self.mpd_controller.stop_sync_loop()
        self.mpd_controller.disconnect_from_mpd()


def main():
    """
    Main function to demonstrate MPD-WAM integration
    """
    print("Samsung WAM - MPD Integration")
    print("=============================")
    
    # Create integration instance
    integration = WAMMPDIntegration()
    
    # Initialize the integration
    if not integration.initialize():
        print("Failed to initialize MPD-WAM integration")
        print("Make sure MPD is running and WAM speakers are on the network")
        return
    
    print("MPD-WAM integration initialized successfully!")
    
    # Show available speakers
    speakers = integration.get_available_speakers()
    print(f"Available WAM speakers: {speakers}")
    
    if speakers:
        # Example: Enable first speaker as output and set volume
        first_speaker = speakers[0]
        integration.enable_output(first_speaker)
        integration.set_volume(first_speaker, 50)  # 50% volume
        
        print(f"Enabled {first_speaker} and set volume to 50%")
    
    # Show current status
    status = integration.get_status()
    print(f"\nCurrent status: {json.dumps(status, indent=2)}")
    
    # Start sync loop in background
    integration.start_sync()
    print("\nStarted sync loop. Integration is now active!")
    print("Use integration object to control speakers from MPD commands.")
    
    # Keep running for a few seconds to demonstrate
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        integration.cleanup()


if __name__ == "__main__":
    main()