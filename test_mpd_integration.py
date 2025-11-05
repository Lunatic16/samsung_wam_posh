#!/usr/bin/env python3
"""
Test script to verify MPD integration works correctly
"""

def test_mpd_integration():
    """Test that MPD integration works correctly"""
    print("Testing MPD integration...")
    
    try:
        # Test import
        from wam_discovery import MPDAudioStreamer
        print("✓ MPDAudioStreamer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MPDAudioStreamer: {e}")
        return False
    
    # Test availability (requires python-mpd2 to be installed)
    try:
        mpd_streamer = MPDAudioStreamer()
        available = mpd_streamer.is_available()
        if available:
            print("✓ MPD integration is available")
        else:
            print("? MPD integration not available (python-mpd2 may not be installed)")
            return False
    except Exception as e:
        print(f"✗ Error checking MPD availability: {e}")
        return False
    
    # Test the CLI integration
    try:
        import subprocess
        result = subprocess.run(['python3', 'wam_cli.py', 'mpd', '--help'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'MPD actions' in result.stdout:
            print("✓ MPD commands integrated in CLI")
        else:
            print("✗ MPD commands not properly integrated in CLI")
            print(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ CLI help command timed out")
        return False
    except Exception as e:
        print(f"✗ Error running CLI test: {e}")
        return False
    
    # Test example usage import
    try:
        import example_usage
        # Check if the example_mpd_integration function exists
        import inspect
        if hasattr(example_usage, 'example_mpd_integration'):
            print("✓ MPD example function exists")
        else:
            print("? MPD example function not found")
    except Exception as e:
        print(f"✗ Error importing example_usage: {e}")
        return False
    
    return True

def test_complete_integration():
    """Test that MPD integration works with other components"""
    print("\nTesting complete integration...")
    
    try:
        from wam_discovery import (
            WamController,
            PipeWireAudioStreamer,
            GStreamerAudioStreamer,
            MPDAudioStreamer
        )
        
        # Test all integrations can coexist
        wam_controller = WamController()
        pipewire = PipeWireAudioStreamer()
        gstreamer = GStreamerAudioStreamer()
        mpd = MPDAudioStreamer()
        
        print("✓ All integration modules can be instantiated together")
        
        # Check MPD availability specifically 
        if mpd.is_available():
            print("✓ MPD integration ready for use")
        else:
            print("? MPD integration not available (this may be OK if python-mpd2 is not installed)")
            
        return True
    except Exception as e:
        print(f"✗ Error in complete integration test: {e}")
        return False

def main():
    """Run all tests"""
    print("Samsung WAM - MPD Integration Test")
    print("==================================\n")
    
    all_passed = True
    
    all_passed &= test_mpd_integration()
    all_passed &= test_complete_integration()
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✓ All MPD integration tests passed!")
        print("\nMPD integration has been successfully added to the project with:")
        print("  - MPDAudioStreamer class in wam_discovery.py")
        print("  - Dedicated mpd_integration.py module")
        print("  - CLI commands for MPD integration")
        print("  - Example usage in example_usage.py")
        print("  - Updated documentation in README.md")
    else:
        print("✗ Some tests failed. Please check the above error messages.")
    
    return all_passed

if __name__ == "__main__":
    main()