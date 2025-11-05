#!/usr/bin/env python3
"""
Example usage of the Samsung WAM Speaker Controller
"""

from wam_discovery import WamController, SamsungWamSpeaker, PipeWireAudioStreamer
import time


def example_basic_control():
    """
    Example: Basic speaker control
    """
    print("=== Basic Speaker Control Example ===")
    
    # Create controller
    controller = WamController()
    
    # Discover speakers
    speakers = controller.discover()
    
    if not speakers:
        print("No speakers found!")
        return
        
    # Select first speaker
    speaker = speakers[0]
    print(f"Selected speaker: {speaker.name} at {speaker.ip_address}")
    
    # Refresh its status
    speaker.refresh()
    print(f"Current status - Volume: {speaker.volume}, Mute: {speaker.mute}")
    
    # Change volume
    original_volume = speaker.volume
    new_volume = min(30, original_volume + 3)
    print(f"Setting volume from {original_volume} to {new_volume}")
    speaker.set_volume(new_volume)
    
    # Wait a moment and check
    time.sleep(1)
    current_vol = speaker.get_volume()
    print(f"Current volume after setting: {current_vol}")
    
    # Toggle mute
    original_mute = speaker.mute
    new_mute = 'on' if original_mute == 'off' else 'off'
    print(f"Toggling mute from {original_mute} to {new_mute}")
    speaker.set_mute(new_mute)
    
    # Wait and check
    time.sleep(1)
    current_mute = speaker.get_mute()
    print(f"Current mute after setting: {current_mute}")
    
    # Reset to original state
    speaker.set_volume(original_volume)
    speaker.set_mute(original_mute)
    print(f"Reset to original - Volume: {original_volume}, Mute: {original_mute}")


def example_playback_control():
    """
    Example: Playback control
    """
    print("\n=== Playback Control Example ===")
    
    controller = WamController()
    speakers = controller.discover()
    
    if not speakers:
        print("No speakers found!")
        return
        
    speaker = speakers[0]
    print(f"Selected speaker: {speaker.name} at {speaker.ip_address}")
    
    # Demonstrating playback controls
    print("Demonstrating playback controls...")
    print("- Play command sent")
    speaker.play()
    time.sleep(1)
    
    print("- Pause command sent")
    speaker.pause()
    time.sleep(1)
    
    print("- Resume command sent")
    speaker.resume()
    time.sleep(1)
    
    print("- Next track command sent")
    speaker.next_track()
    time.sleep(1)
    
    print("- Previous track command sent")
    speaker.previous_track()


def example_group_control():
    """
    Example: Group control
    """
    print("\n=== Group Control Example ===")
    
    controller = WamController()
    speakers = controller.discover()
    
    if len(speakers) < 2:
        print("Need at least 2 speakers for group example")
        return
        
    print(f"Found {len(speakers)} speakers")
    for i, spk in enumerate(speakers):
        print(f"  {i+1}. {spk.name}")
    
    # Create a group with first two speakers
    group_name = "TestGroup"
    speaker_names = [speakers[0].name, speakers[1].name]
    
    print(f"Creating group '{group_name}' with {speaker_names[0]} and {speaker_names[1]}")
    controller.create_group(group_name, speaker_names)
    
    # Wait and check
    time.sleep(2)
    
    # Show group status
    for spk in speakers[:2]:  # Only check the first two we grouped
        spk.refresh()  # Refresh to get latest group info
        print(f"Speaker {spk.name} is in group: '{spk.group_name}'")
    
    # Ungroup
    print("\nUngrouping speakers...")
    controller.ungroup_all()
    
    # Wait and check
    time.sleep(2)
    
    # Verify ungrouping
    for spk in speakers[:2]:
        spk.refresh()
        print(f"Speaker {spk.name} group after ungrouping: '{spk.group_name}'")


def example_eq_control():
    """
    Example: Equalizer control
    """
    print("\n=== Equalizer Control Example ===")
    
    controller = WamController()
    speakers = controller.discover()
    
    if not speakers:
        print("No speakers found!")
        return
        
    speaker = speakers[0]
    print(f"Selected speaker: {speaker.name} at {speaker.ip_address}")
    
    # Get available EQ modes
    eq_list = speaker.get_7band_eq_list()
    print(f"Available 7-band EQ presets: {eq_list}")
    
    # Set EQ preset (if we have presets)
    if eq_list:
        # Set to first preset (usually 'None' or 0)
        print("Setting EQ preset to 0 (None)")
        speaker.set_7band_eq_preset(0)
        time.sleep(1)
        
        # Set to preset 1 (if available)
        if len([x for x in range(5)]) > 1:  # Check if more than one preset
            print("Setting EQ preset to 1")
            speaker.set_7band_eq_preset(1)
            time.sleep(1)
    
    # Set custom EQ values (7 bands with values from -10 to 10)
    custom_eq = [2, 1, 0, -1, 0, 1, 2]  # Example custom values
    print(f"Setting custom EQ values: {custom_eq}")
    speaker.set_7band_eq_value(0, custom_eq)  # Set to preset 0
    time.sleep(1)


def example_info_retrieval():
    """
    Example: Information retrieval
    """
    print("\n=== Information Retrieval Example ===")
    
    controller = WamController()
    speakers = controller.discover()
    
    if not speakers:
        print("No speakers found!")
        return
        
    speaker = speakers[0]
    print(f"Selected speaker: {speaker.name} at {speaker.ip_address}")
    
    # Get detailed information
    speaker.refresh()
    print(f"Name: {speaker.name}")
    print(f"IP: {speaker.ip_address}")
    print(f"Volume: {speaker.volume}")
    print(f"Mute: {speaker.mute}")
    print(f"LED: {speaker.led}")
    print(f"Group: {speaker.group_name}")
    print(f"Repeat: {speaker.repeat}")
    
    # Get additional info
    ap_info = speaker.get_ap_info()
    print(f"AP Info: {ap_info}")
    
    music_info = speaker.get_music_info()
    print(f"Music Info: {music_info}")
    
    play_time = speaker.get_current_play_time()
    print(f"Play Time: {play_time}")
    
    eq_mode = speaker.get_eq_mode()
    print(f"EQ Mode: {eq_mode}")


def example_pipewire_integration():
    """
    Example: PipeWire integration
    """
    print("\n=== PipeWire Integration Example ===")
    
    pipewire_streamer = PipeWireAudioStreamer()
    
    if not pipewire_streamer.is_available():
        print("PipeWire is not available on this system")
        print("Please install and start PipeWire or PulseAudio")
        return
    
    print("PipeWire is available!")
    
    # List available devices
    devices = pipewire_streamer.get_available_devices()
    print(f"\nAvailable PipeWire devices ({len(devices)}):")
    for i, device in enumerate(devices):
        print(f"  {i+1}. {device['name']} (ID: {device['id']}, Type: {device['type']})")
    
    # Try to use with a speaker
    controller = WamController()
    speakers = controller.discover()
    
    if not speakers:
        print("No speakers found to demonstrate PipeWire integration")
        return
    
    speaker = speakers[0]
    print(f"\nUsing speaker: {speaker.name}")
    
    # Try to set up streaming (conceptual)
    success = pipewire_streamer.stream_to_speaker(speaker)
    if success:
        print(f"Successfully set up streaming to {speaker.name}")
    else:
        print(f"Failed to set up streaming to {speaker.name}")
    
    # Try to sync volumes
    if devices:
        device_id = devices[0]['id']
        sync_success = pipewire_streamer.sync_volume_with_pipewire(speaker, device_id)
        if sync_success:
            print(f"Successfully synced volumes between {speaker.name} and {devices[0]['name']}")
        else:
            print(f"Failed to sync volumes")


def main():
    """
    Main function to run all examples
    """
    print("Samsung WAM Speaker Controller Examples")
    print("=======================================")
    
    # Run all examples
    example_basic_control()
    example_playback_control()
    example_group_control()
    example_eq_control()
    example_info_retrieval()
    example_pipewire_integration()
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    main()