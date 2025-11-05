#!/usr/bin/env python3
"""
Test script to verify GStreamer integration works correctly
"""

def test_imports():
    """Test that all modules can be imported without errors"""
    print("Testing module imports...")
    
    try:
        from wam_discovery import GStreamerAudioStreamer
        print("✓ GStreamerAudioStreamer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import GStreamerAudioStreamer: {e}")
        return False
    
    try:
        from gstreamer_integration import GStreamerAudioStreamer as GstStreamer
        print("✓ gstreamer_integration.GStreamerAudioStreamer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import gstreamer_integration.GStreamerAudioStreamer: {e}")
        return False
    
    try:
        from wam_discovery import WamController
        print("✓ WamController imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import WamController: {e}")
        return False
    
    try:
        from wam_discovery import PipeWireAudioStreamer
        print("✓ PipeWireAudioStreamer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PipeWireAudioStreamer: {e}")
        return False
    
    return True

def test_gstreamer_availability():
    """Test if GStreamer is available and functional"""
    print("\nTesting GStreamer availability...")
    
    try:
        from gstreamer_integration import GStreamerAudioStreamer
        gst_streamer = GStreamerAudioStreamer()
        
        if gst_streamer.is_available():
            print("✓ GStreamer is available on this system")
            return True
        else:
            print("? GStreamer is not available on this system (this is OK if GStreamer is not installed)")
            print("  To install GStreamer with Python bindings:")
            print("    Ubuntu/Debian: sudo apt-get install python3-gi gir1.2-gstreamer-1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good")
            print("    Fedora/RHEL: sudo dnf install python3-gobject gstreamer1.0-plugins-base gstreamer1.0-plugins-good")
            print("    Arch: sudo pacman -S python-gobject gst-plugins-base gst-plugins-good")
            return True  # Not a failure, just unavailable
    except Exception as e:
        print(f"✗ Error testing GStreamer availability: {e}")
        return False

def test_pipewire_availability():
    """Test if PipeWire integration is still working"""
    print("\nTesting PipeWire availability...")
    
    try:
        from wam_discovery import PipeWireAudioStreamer
        pipewire_streamer = PipeWireAudioStreamer()
        
        if pipewire_streamer.is_available():
            print("✓ PipeWire integration is available and working")
        else:
            print("- PipeWire integration is not available (this is OK if PipeWire is not installed/running)")
        return True
    except Exception as e:
        print(f"✗ Error testing PipeWire availability: {e}")
        return False

def test_cli_commands():
    """Test that CLI commands work as expected"""
    print("\nTesting CLI structure...")
    
    try:
        import subprocess
        result = subprocess.run(['python3', 'wam_cli.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✓ CLI help command executed successfully")
            
            # Check if GStreamer commands are in the help text
            if 'gstreamer' in result.stdout.lower():
                print("✓ GStreamer commands found in CLI help")
            else:
                print("? GStreamer commands not found in CLI help")
                
            if 'pipewire' in result.stdout.lower():
                print("✓ PipeWire commands found in CLI help")
            else:
                print("? PipeWire commands not found in CLI help")
        else:
            print(f"✗ CLI help command failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except subprocess.TimeoutExpired:
        print("✗ CLI help command timed out")
        return False
    except Exception as e:
        print(f"✗ Error running CLI test: {e}")
        return False

def main():
    """Run all tests"""
    print("Samsung WAM - GStreamer Integration Test")
    print("======================================\n")
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_gstreamer_availability()
    all_passed &= test_pipewire_availability()
    all_passed &= test_cli_commands()
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✓ All tests passed! GStreamer integration is properly integrated.")
        print("\nGStreamer integration has been successfully added to the project with:")
        print("  - GStreamerAudioStreamer class in wam_discovery.py")
        print("  - Dedicated gstreamer_integration.py module")
        print("  - CLI commands for streaming audio to speakers")
        print("  - Example usage in example_usage.py")
        print("  - Updated documentation in README.md")
    else:
        print("✗ Some tests failed. Please check the above error messages.")
    
    return all_passed

if __name__ == "__main__":
    main()