#!/usr/bin/env python3
"""
PipeWire Integration for Samsung WAM Speaker Controller
Provides audio streaming and routing capabilities using PipeWire
"""

import json
import subprocess
import os
import time
from typing import Dict, List, Optional, Any


class PipeWireController:
    """
    Controller for interacting with PipeWire audio server
    """
    
    def __init__(self):
        self.pipewire_available = self._check_pipewire()
        
    def _check_pipewire(self) -> bool:
        """
        Check if PipeWire is available and running
        """
        try:
            # Try to list PipeWire nodes
            result = subprocess.run(['pactl', 'info'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                # Try PipeWire-specific command
                result = subprocess.run(['pw-cli', 'ls'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                return False
    
    def get_audio_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available audio devices from PipeWire
        """
        if not self.pipewire_available:
            return []
            
        devices = []
        try:
            # Try PulseAudio compatibility layer
            result = subprocess.run(['pactl', 'list', 'sinks', 'short'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices.append({
                                'name': parts[1],
                                'id': parts[0],
                                'type': 'sink'  # output device
                            })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        try:
            # Try PipeWire-specific command
            result = subprocess.run(['pw-cli', 'ls', '12'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Parse PipeWire nodes
                for line in result.stdout.strip().split('\n'):
                    if 'name' in line.lower():
                        # Simplified parsing - real implementation would be more complex
                        devices.append({
                            'name': line.strip(),
                            'id': 'unknown',
                            'type': 'pipewire-node'
                        })
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        return devices
    
    def get_active_streams(self) -> List[Dict[str, Any]]:
        """
        Get list of active audio streams
        """
        if not self.pipewire_available:
            return []
            
        streams = []
        try:
            result = subprocess.run(['pactl', 'list', 'sink-inputs'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                current_stream = {}
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line.startswith('Sink Input'):
                        if current_stream:
                            streams.append(current_stream)
                        current_stream = {'id': line.split('#')[1].split()[0]}
                    elif 'media.name' in line:
                        current_stream['name'] = line.split('=')[1].strip().strip('"')
                    elif 'application.name' in line:
                        current_stream['application'] = line.split('=')[1].strip().strip('"')
                
                if current_stream:
                    streams.append(current_stream)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        return streams
    
    def set_volume(self, device_id: str, volume_percent: int) -> bool:
        """
        Set volume for a specific audio device
        """
        if not self.pipewire_available:
            return False
            
        try:
            # Use pactl to set volume
            result = subprocess.run(['pactl', 'set-sink-volume', device_id, f'{volume_percent}%'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def mute_device(self, device_id: str, mute: bool = True) -> bool:
        """
        Mute/unmute a specific audio device
        """
        if not self.pipewire_available:
            return False
            
        try:
            action = 'mute' if mute else 'unmute'
            result = subprocess.run(['pactl', f'set-sink-{action}', device_id], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def route_audio_to_speakers(self, pipewire_sink_name: str, speaker_ip: str) -> bool:
        """
        Route audio from a PipeWire sink to Samsung WAM speakers
        This is a conceptual method - actual implementation would require 
        audio streaming from computer to speaker
        """
        if not self.pipewire_available:
            return False
            
        # This would involve advanced audio streaming setup
        # For now, this is a placeholder that returns success
        print(f"Routing audio from PipeWire sink '{pipewire_sink_name}' to Samsung WAM speaker at {speaker_ip}")
        return True


class WamPipeWireIntegration:
    """
    Integrates Samsung WAM speaker control with PipeWire audio server
    """
    
    def __init__(self):
        self.pipewire = PipeWireController()
        self.speaker_streams = {}  # Map speaker IP to PipeWire stream
    
    def sync_volumes(self) -> bool:
        """
        Sync the volume of all Samsung WAM speakers with their corresponding PipeWire sinks
        """
        if not self.pipewire.pipewire_available:
            print("PipeWire not available, cannot sync volumes")
            return False
        
        # Get PipeWire devices
        devices = self.pipewire.get_audio_devices()
        if not devices:
            print("No PipeWire devices found")
            return False
            
        # This function would need to be connected to actual speaker control
        # For now, it just demonstrates the concept
        for device in devices:
            print(f"Found PipeWire device: {device['name']} (ID: {device['id']})")
            # In a real implementation, this would sync with actual speaker volumes
        
        return True
    
    def setup_audio_streaming(self, speaker_ip: str, output_device: Optional[str] = None) -> bool:
        """
        Set up audio streaming from PipeWire to Samsung WAM speaker
        """
        if not self.pipewire.pipewire_available:
            print("PipeWire not available, cannot set up streaming")
            return False
        
        # Find a PipeWire sink to use
        devices = self.pipewire.get_audio_devices()
        if not devices:
            print("No PipeWire devices available")
            return False
        
        if output_device:
            target_device = next((d for d in devices if d['name'] == output_device or d['id'] == output_device), None)
        else:
            target_device = next((d for d in devices if d['type'] == 'sink'), None)
        
        if not target_device:
            print("No suitable output device found")
            return False
            
        # This would ideally set up a streaming pipeline from the PipeWire sink to the WAM speaker
        # This is a complex operation that would typically need GStreamer or similar
        print(f"Setting up audio streaming from PipeWire device '{target_device['name']}' to speaker at {speaker_ip}")
        
        # In a real implementation, this might involve:
        # 1. Capturing audio from PipeWire
        # 2. Converting to a format the speaker accepts (e.g., WAV or MP3)
        # 3. Streaming it to the speaker via the SetUrlPlayback API
        print("Note: This requires additional streaming implementation with GStreamer or similar.")
        
        # Store the mapping
        self.speaker_streams[speaker_ip] = target_device
        return True
    
    def get_pipewire_devices(self) -> List[Dict[str, Any]]:
        """
        Get list of available PipeWire devices
        """
        return self.pipewire.get_audio_devices()
    
    def get_active_streams(self) -> List[Dict[str, Any]]:
        """
        Get list of active audio streams
        """
        return self.pipewire.get_active_streams()


def main():
    """
    Main function to demonstrate PipeWire integration
    """
    print("Samsung WAM - PipeWire Integration")
    print("==================================")
    
    # Create integration instance
    integration = WamPipeWireIntegration()
    
    if not integration.pipewire.pipewire_available:
        print("PipeWire is not available on this system")
        print("Please install and start PipeWire or PulseAudio")
        return
    
    print("PipeWire is available!")
    
    # List available devices
    devices = integration.get_pipewire_devices()
    print(f"\nAvailable PipeWire devices ({len(devices)}):")
    for i, device in enumerate(devices):
        print(f"  {i+1}. {device['name']} (ID: {device['id']}, Type: {device['type']})")
    
    # List active streams
    streams = integration.get_active_streams()
    if streams:
        print(f"\nActive audio streams ({len(streams)}):")
        for stream in streams:
            app_name = stream.get('application', 'Unknown')
            stream_name = stream.get('name', 'Unknown')
            print(f"  - {stream_name} (App: {app_name})")
    
    print("\nIntegration ready. Use WamPipeWireIntegration class to control audio routing.")


if __name__ == "__main__":
    main()