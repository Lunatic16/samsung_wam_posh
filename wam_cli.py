#!/usr/bin/env python3
"""
Command-Line Interface for Samsung WAM Speaker Control
"""

import argparse
import sys
from wam_discovery import WamController, SamsungWamSpeaker, PipeWireAudioStreamer, GStreamerAudioStreamer
import json


def main():
    parser = argparse.ArgumentParser(description='Samsung WAM Speaker Controller')
    parser.add_argument('--config', default='speakers.txt', help='Configuration file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Discover command
    discover_parser = subparsers.add_parser('discover', help='Discover speakers on the network')
    discover_parser.add_argument('--timeout', type=int, default=5, help='Discovery timeout in seconds')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all known speakers')
    
    # Volume command
    volume_parser = subparsers.add_parser('volume', help='Control speaker volume')
    volume_parser.add_argument('speaker', help='Speaker name or IP address')
    volume_parser.add_argument('level', nargs='?', type=int, help='Volume level (0-30)')
    volume_parser.add_argument('--get', action='store_true', help='Get current volume')
    
    # Mute command
    mute_parser = subparsers.add_parser('mute', help='Control speaker mute')
    mute_parser.add_argument('speaker', help='Speaker name or IP address')
    mute_parser.add_argument('action', nargs='?', choices=['on', 'off'], help='Mute state')
    mute_parser.add_argument('--get', action='store_true', help='Get current mute status')
    
    # Playback commands
    playback_parser = subparsers.add_parser('playback', help='Control playback')
    playback_parser.add_argument('speaker', help='Speaker name or IP address')
    playback_parser.add_argument('action', choices=['play', 'pause', 'resume', 'next', 'prev'], help='Playback action')
    
    # Group commands
    group_parser = subparsers.add_parser('group', help='Manage speaker groups')
    group_parser.add_argument('action', choices=['create', 'ungroup'], help='Group action')
    group_parser.add_argument('--name', help='Group name')
    group_parser.add_argument('--speakers', nargs='+', help='Speaker names for the group')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get speaker information')
    info_parser.add_argument('speaker', help='Speaker name or IP address')
    
    # Repeat command
    repeat_parser = subparsers.add_parser('repeat', help='Set repeat mode')
    repeat_parser.add_argument('speaker', help='Speaker name or IP address')
    repeat_parser.add_argument('mode', nargs='?', choices=['off', 'all', 'one'], help='Repeat mode')
    repeat_parser.add_argument('--get', action='store_true', help='Get current repeat mode')
    
    # LED command
    led_parser = subparsers.add_parser('led', help='Control LED')
    led_parser.add_argument('speaker', help='Speaker name or IP address')
    led_parser.add_argument('state', nargs='?', choices=['on', 'off'], help='LED state')
    led_parser.add_argument('--get', action='store_true', help='Get current LED state')
    
    # PipeWire commands
    pipewire_parser = subparsers.add_parser('pipewire', help='PipeWire integration commands')
    pipewire_subparsers = pipewire_parser.add_subparsers(dest='pipewire_action', help='PipeWire actions')
    
    # List PipeWire devices
    pipewire_subparsers.add_parser('devices', help='List available PipeWire devices')
    
    # Stream to speaker
    stream_parser = pipewire_subparsers.add_parser('stream', help='Stream audio to speaker')
    stream_parser.add_argument('speaker', help='Speaker name or IP address')
    stream_parser.add_argument('--device', help='PipeWire device to stream from (optional)')
    
    # Sync volumes
    sync_parser = pipewire_subparsers.add_parser('sync', help='Sync speaker volume with PipeWire')
    sync_parser.add_argument('speaker', help='Speaker name or IP address')
    sync_parser.add_argument('device', help='PipeWire device ID to sync with')
    
    # GStreamer commands
    gstreamer_parser = subparsers.add_parser('gstreamer', help='GStreamer integration commands')
    gstreamer_subparsers = gstreamer_parser.add_subparsers(dest='gstreamer_action', help='GStreamer actions')
    
    # Stream to speaker with GStreamer
    gst_stream_parser = gstreamer_subparsers.add_parser('stream', help='Stream audio to speaker using GStreamer')
    gst_stream_parser.add_argument('speaker', help='Speaker name or IP address')
    gst_stream_parser.add_argument('--source-type', choices=['pulse', 'alsa', 'file'], default='pulse', 
                                  help='Audio source type (default: pulse)')
    gst_stream_parser.add_argument('--source-device', help='Specific device to use (optional)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Create controller
    controller = WamController(config_file=args.config)
    
    # Handle discover command
    if args.command == 'discover':
        # Create discovery object with timeout
        from wam_discovery import SamsungWamDiscovery
        discovery = SamsungWamDiscovery()
        speakers = discovery.discover_speakers(timeout=args.timeout)
        
        print(f"Found {len(speakers)} speaker(s):")
        for i, speaker in enumerate(speakers):
            print(f"  {i+1}. {speaker.name} at {speaker.ip_address}")
        
        # Save to config if desired
        if speakers:
            response = input(f"\nSave these {len(speakers)} speakers to {args.config}? (y/n): ")
            if response.lower() == 'y':
                from wam_discovery import save_speakers_to_config
                save_speakers_to_config(speakers, args.config)
                print(f"Speakers saved to {args.config}")
    
    # Handle list command
    elif args.command == 'list':
        controller.discover()  # Refresh the list
        controller.list_speakers()
    
    # Handle volume command
    elif args.command == 'volume':
        controller.discover()  # Make sure we have latest list
        speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
        
        if not speaker:
            print(f"Speaker '{args.speaker}' not found")
            return
            
        if args.get:
            vol = speaker.get_volume()
            print(f"Volume for {speaker.name}: {vol}")
        elif args.level is not None:
            speaker.set_volume(args.level)
            print(f"Set volume for {speaker.name} to {args.level}")
        else:
            # Just show current volume
            vol = speaker.get_volume()
            print(f"Current volume for {speaker.name}: {vol}")
    
    # Handle mute command
    elif args.command == 'mute':
        controller.discover()  # Make sure we have latest list
        speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
        
        if not speaker:
            print(f"Speaker '{args.speaker}' not found")
            return
            
        if args.get:
            mute_status = speaker.get_mute()
            print(f"Mute status for {speaker.name}: {mute_status}")
        elif args.action:
            speaker.set_mute(args.action)
            print(f"Set mute for {speaker.name} to {args.action}")
        else:
            # Just show current status
            mute_status = speaker.get_mute()
            print(f"Current mute status for {speaker.name}: {mute_status}")
    
    # Handle playback command
    elif args.command == 'playback':
        controller.discover()  # Make sure we have latest list
        speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
        
        if not speaker:
            print(f"Speaker '{args.speaker}' not found")
            return
            
        if args.action == 'play':
            speaker.play()
            print(f"Sent play command to {speaker.name}")
        elif args.action == 'pause':
            speaker.pause()
            print(f"Sent pause command to {speaker.name}")
        elif args.action == 'resume':
            speaker.resume()
            print(f"Sent resume command to {speaker.name}")
        elif args.action == 'next':
            speaker.next_track()
            print(f"Sent next track command to {speaker.name}")
        elif args.action == 'prev':
            speaker.previous_track()
            print(f"Sent previous track command to {speaker.name}")
    
    # Handle group command
    elif args.command == 'group':
        controller.discover()  # Make sure we have latest list
        
        if args.action == 'create':
            if not args.name:
                print("Group name is required for create action")
                return
            if not args.speakers:
                print("At least one speaker is required for create action")
                return
                
            controller.create_group(args.name, args.speakers)
            
        elif args.action == 'ungroup':
            controller.ungroup_all()
            print("All speakers have been ungrouped")
    
    # Handle info command
    elif args.command == 'info':
        controller.discover()  # Make sure we have latest list
        speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
        
        if not speaker:
            print(f"Speaker '{args.speaker}' not found")
            return
            
        # Refresh speaker info
        speaker.refresh()
        
        print(f"Information for {speaker.name}:")
        print(f"  IP Address: {speaker.ip_address}")
        print(f"  Volume: {speaker.volume}")
        print(f"  Mute: {speaker.mute}")
        print(f"  LED: {speaker.led}")
        print(f"  Group: {speaker.group_name or 'None'}")
        print(f"  Repeat: {speaker.repeat}")
        
        # Get additional info
        music_info = speaker.get_music_info()
        if music_info:
            print(f"  Music info: {music_info}")
    
    # Handle repeat command
    elif args.command == 'repeat':
        controller.discover()  # Make sure we have latest list
        speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
        
        if not speaker:
            print(f"Speaker '{args.speaker}' not found")
            return
            
        if args.get:
            print(f"Repeat mode for {speaker.name}: {speaker.repeat}")
        elif args.mode:
            speaker.set_repeat_mode(args.mode)
            print(f"Set repeat mode for {speaker.name} to {args.mode}")
        else:
            # Just show current mode
            print(f"Current repeat mode for {speaker.name}: {speaker.repeat}")
    
    # Handle led command
    elif args.command == 'led':
        controller.discover()  # Make sure we have latest list
        speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
        
        if not speaker:
            print(f"Speaker '{args.speaker}' not found")
            return
            
        if args.get:
            print(f"LED status for {speaker.name}: {speaker.led}")
        elif args.state:
            speaker.set_led(args.state)
            print(f"Set LED for {speaker.name} to {args.state}")
        else:
            # Just show current status
            print(f"Current LED status for {speaker.name}: {speaker.led}")
    
    # Handle pipewire commands
    elif args.command == 'pipewire':
        # Create PipeWire controller
        pipewire_streamer = PipeWireAudioStreamer()
        
        if not pipewire_streamer.is_available():
            print("PipeWire integration is not available or PipeWire is not running")
            print("Please install and start PipeWire/PulseAudio on your system")
            return
        
        if args.pipewire_action == 'devices':
            devices = pipewire_streamer.get_available_devices()
            print(f"Available PipeWire devices: {len(devices)}")
            for i, device in enumerate(devices):
                print(f"  {i+1}. {device['name']} (ID: {device['id']}, Type: {device['type']})")
        
        elif args.pipewire_action == 'stream':
            controller.discover()
            speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
            
            if not speaker:
                print(f"Speaker '{args.speaker}' not found")
                return
            
            success = pipewire_streamer.stream_to_speaker(speaker, args.device)
            if success:
                print(f"Set up streaming to {speaker.name}")
                print("Note: Actual streaming requires additional setup with GStreamer")
            else:
                print("Failed to set up streaming")
        
        elif args.pipewire_action == 'sync':
            controller.discover()
            speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
            
            if not speaker:
                print(f"Speaker '{args.speaker}' not found")
                return
            
            success = pipewire_streamer.sync_volume_with_pipewire(speaker, args.device)
            if success:
                print(f"Synced volume between {speaker.name} and PipeWire device {args.device}")
            else:
                print("Failed to sync volumes")
    
    # Handle gstreamer commands
    elif args.command == 'gstreamer':
        # Create GStreamer controller
        gstreamer_streamer = GStreamerAudioStreamer()
        
        if not gstreamer_streamer.is_available():
            print("GStreamer integration is not available")
            print("Please install GStreamer and PyGObject (python3-gi) with appropriate plugins")
            return
        
        if args.gstreamer_action == 'stream':
            controller.discover()
            speaker = controller.get_speaker_by_name(args.speaker) or controller.get_speaker_by_ip(args.speaker)
            
            if not speaker:
                print(f"Speaker '{args.speaker}' not found")
                return
            
            success = gstreamer_streamer.stream_to_speaker(speaker, args.source_type, args.source_device)
            if success:
                print(f"Set up GStreamer audio streaming to {speaker.name}")
            else:
                print("Failed to set up GStreamer streaming")


if __name__ == "__main__":
    main()