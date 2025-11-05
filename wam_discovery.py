#!/usr/bin/env python3
"""
Samsung WAM (Wireless Audio Multiroom) Speaker Discovery and Control
A Linux-compatible implementation of the PowerShell WAM controller
"""

import socket
import requests
from urllib.parse import urlparse, quote
import json
import time
import threading
from typing import List, Dict, Optional, Union
import xml.etree.ElementTree as ET


class SamsungWamSpeaker:
    """
    Represents a Samsung WAM speaker with control methods
    """
    def __init__(self, ip_address: str, name: str = "", led: str = "off", 
                 mute: str = "off", volume: int = 10, group_name: str = "", 
                 repeat: str = "off", mac: str = ""):
        self.ip_address = ip_address
        self.name = name
        self.led = led
        self.mute = mute
        self.volume = volume
        self.group_name = group_name
        self.repeat = repeat
        self.mac = mac  # Mac address for grouping operations
        self.port = 55001
        
    def _send_command(self, command_type: str, xml_command: str) -> Optional[Dict]:
        """
        Send a command to the speaker and return the response
        """
        try:
            # URL encode the XML command
            encoded_cmd = quote(xml_command, safe='')
            url = f"http://{self.ip_address}:{self.port}/{command_type}?cmd={encoded_cmd}"
            
            # Send the HTTP GET request
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Try to parse as JSON first
                try:
                    return response.json()
                except json.JSONDecodeError:
                    # If JSON fails, return raw text
                    return {"raw_response": response.text}
            else:
                print(f"Error sending command to {self.ip_address}: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request error to {self.ip_address}: {e}")
            return None
            
    def refresh(self):
        """
        Refresh the speaker's current state
        """
        try:
            # Get name
            cmd = '<name>GetSpkName</name>'
            resp = self._send_command('UIC', cmd)
            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                self.name = resp['UIC']['response'].get('spkname', {}).get('#cdata-section', self.name)
                
            # Get LED status
            cmd = '<name>GetLed</name>'
            resp = self._send_command('UIC', cmd)
            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                self.led = resp['UIC']['response'].get('led', self.led)
                
            # Get mute status
            cmd = '<name>GetMute</name>'
            resp = self._send_command('UIC', cmd)
            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                self.mute = resp['UIC']['response'].get('mute', self.mute)
                
            # Get volume
            cmd = '<name>GetVolume</name>'
            resp = self._send_command('UIC', cmd)
            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                vol = resp['UIC']['response'].get('volume', str(self.volume))
                try:
                    self.volume = int(vol)
                except ValueError:
                    self.volume = self.volume  # Keep current value
                    
            # Get group name
            cmd = '<name>GetGroupName</name>'
            resp = self._send_command('UIC', cmd)
            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                self.group_name = resp['UIC']['response'].get('groupname', {}).get('#cdata-section', self.group_name)
                
            # Get repeat mode
            cmd = '<name>GetRepeatMode</name>'
            resp = self._send_command('UIC', cmd)
            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                self.repeat = resp['UIC']['response'].get('repeat', self.repeat)
        except Exception as e:
            print(f"Error refreshing speaker {self.ip_address}: {e}")
            
    def set_volume(self, vol_level: int):
        """
        Set the speaker volume (0-30)
        """
        vol_level = max(0, min(30, vol_level))  # Clamp between 0 and 30
        cmd = f'<name>SetVolume</name><p type="dec" name="volume" val="{vol_level}"/>'
        response = self._send_command('UIC', cmd)
        if response:
            self.volume = vol_level
        return response
        
    def get_volume(self) -> int:
        """
        Get the current speaker volume
        """
        cmd = '<name>GetVolume</name>'
        resp = self._send_command('UIC', cmd)
        if resp and 'UIC' in resp and 'response' in resp['UIC']:
            vol = resp['UIC']['response'].get('volume', str(self.volume))
            try:
                vol_int = int(vol)
                self.volume = vol_int
                return vol_int
            except ValueError:
                return self.volume
        return self.volume
        
    def set_mute(self, choice: str = 'off'):
        """
        Set mute on/off ('on' or 'off')
        """
        if choice not in ['on', 'off']:
            raise ValueError("Choice must be 'on' or 'off'")
        cmd = f'<name>SetMute</name><p type="str" name="mute" val="{choice}"/>'
        response = self._send_command('UIC', cmd)
        if response:
            self.mute = choice
        return response
        
    def get_mute(self) -> str:
        """
        Get mute status
        """
        cmd = '<name>GetMute</name>'
        resp = self._send_command('UIC', cmd)
        if resp and 'UIC' in resp and 'response' in resp['UIC']:
            mute_status = resp['UIC']['response'].get('mute', self.mute)
            self.mute = mute_status
            return mute_status
        return self.mute
        
    def play(self):
        """
        Start playback
        """
        cmd = '<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="play"/>'
        return self._send_command('UIC', cmd)
        
    def pause(self):
        """
        Pause playback
        """
        cmd = '<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="pause"/>'
        return self._send_command('UIC', cmd)
        
    def resume(self):
        """
        Resume playback
        """
        cmd = '<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="resume"/>'
        return self._send_command('UIC', cmd)
        
    def next_track(self):
        """
        Skip to next track
        """
        cmd = '<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="next"/>'
        return self._send_command('UIC', cmd)
        
    def previous_track(self):
        """
        Skip to previous track
        """
        cmd = '<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="previous"/>'
        return self._send_command('UIC', cmd)
        
    def set_repeat_mode(self, mode: str = 'off'):
        """
        Set repeat mode ('off', 'all', 'one')
        """
        if mode not in ['off', 'all', 'one']:
            raise ValueError("Mode must be 'off', 'all', or 'one'")
        cmd = f'<name>SetRepeatMode</name><p type="str" name="repeatmode" val="{mode}"/>'
        response = self._send_command('UIC', cmd)
        if response:
            self.repeat = mode
        return response
        
    def set_shuffle(self, enabled: bool = True):
        """
        Set shuffle mode on/off
        """
        mode = 'on' if enabled else 'off'
        cmd = f'<name>SetShuffleMode</name><p type="str" name="shufflemode" val="{mode}"/>'
        response = self._send_command('UIC', cmd)
        return response
        
    def set_led(self, choice: str = 'off'):
        """
        Set LED on/off ('on' or 'off')
        """
        if choice not in ['on', 'off']:
            raise ValueError("Choice must be 'on' or 'off'")
        cmd = f'<name>SetLed</name><p type="str" name="option" val="{choice}"/>'
        response = self._send_command('UIC', cmd)
        if response:
            self.led = choice
        return response
        
    def set_name(self, name: str):
        """
        Set the speaker name
        """
        cmd = f'<name>SetSpkName</name><p type="cdata" name="spkname" val="empty"><![CDATA[{name}]]></p>'
        response = self._send_command('UIC', cmd)
        if response:
            self.name = name
        return response
        
    def get_ap_info(self):
        """
        Get AP (Access Point) information
        """
        cmd = '<name>GetApInfo</name>'
        return self._send_command('UIC', cmd)
        
    def get_music_info(self):
        """
        Get current music information
        """
        cmd = '<name>GetMusicInfo</name>'
        return self._send_command('UIC', cmd)
        
    def get_current_play_time(self):
        """
        Get current play time
        """
        cmd = '<name>GetCurrentPlayTime</name>'
        return self._send_command('UIC', cmd)
        
    def set_search_time(self, time_seconds: int):
        """
        Set playback position in seconds
        """
        cmd = f'<name>SetSearchTime</name><p type="dec" name="playtime" val="{time_seconds}"/>'
        return self._send_command('UIC', cmd)
        
    def get_eq_mode(self):
        """
        Get current EQ mode
        """
        cmd = '<name>GetEQMode</name>'
        return self._send_command('UIC', cmd)
        
    def set_eq_mode(self, mode: str):
        """
        Set EQ mode ('off', 'pop', 'jazz', 'classic', etc.)
        """
        cmd = f'<name>SetEQMode</name><p type="str" name="eqmode" val="{mode}"/>'
        return self._send_command('UIC', cmd)
        
    def get_7band_eq_list(self):
        """
        Get available 7-band EQ presets
        """
        cmd = '<name>Get7BandEQList</name>'
        return self._send_command('UIC', cmd)
        
    def set_7band_eq_preset(self, preset_idx: int):
        """
        Set 7-band EQ preset by index (0-5)
        """
        cmd = f'<name>Set7bandEQMode</name><p type="dec" name="presetindex" val="{preset_idx}"/>'
        return self._send_command('UIC', cmd)
        
    def set_7band_eq_value(self, preset_idx: int, eq_values: List[int]):
        """
        Set custom 7-band EQ values (7 values from -10 to 10)
        """
        if len(eq_values) != 7:
            raise ValueError("Must provide exactly 7 EQ values")
        
        cmd = f'<name>Set7bandEQValue</name><p type="dec" name="presetindex" val="{preset_idx}"/>'
        for i, val in enumerate(eq_values):
            cmd += f'<p type="dec" name="eqvalue{i+1}" val="{val}"/>'
        
        return self._send_command('UIC', cmd)
        
    def add_custom_eq_mode(self, preset_idx: int, preset_name: str):
        """
        Add a custom EQ mode
        """
        cmd = f'<name>AddCustomEQMode</name><p type="dec" name="presetindex" val="{preset_idx}"/><p type="str" name="presetname" val="{preset_name}"/>'
        return self._send_command('UIC', cmd)
        
    def remove_custom_eq_mode(self, preset_idx: int):
        """
        Remove a custom EQ mode
        """
        cmd = f'<name>DelCustomEQMode</name><p type="dec" name="presetindex" val="{preset_idx}"/>'
        return self._send_command('UIC', cmd)
        
    def group_with_speakers(self, group_name: str, other_speakers: List['SamsungWamSpeaker']):
        """
        Create a group with other speakers
        """
        # First ungroup all speakers to ensure clean state
        for speaker in [self] + other_speakers:
            speaker.ungroup()
            
        # Create group command with main speaker
        cmd = f'''<name>SetMultispkGroup</name>
<p type="cdata" name="name" val="empty"><![CDATA[{group_name}]]></p>
<p type="dec" name="index" val="1"/>
<p type="str" name="type" val="main"/>
<p type="dec" name="spknum" val="{len([self] + other_speakers)}"/>
<p type="str" name="audiosourcemacaddr" val="{self.mac if self.mac else '00:00:00:00:00:00'}"/>
<p type="cdata" name="audiosourcename" val="empty"><![CDATA[{self.name}]]></p>
<p type="str" name="audiosourcetype" val="speaker"/>'''
        
        # Add sub-speakers to command
        for speaker in other_speakers:
            cmd += f'<p type="str" name="subspkip" val="{speaker.ip_address}"/><p type="str" name="subspkmacaddr" val="{speaker.mac if speaker.mac else '00:00:00:00:00:00'}"/>'
        
        # Remove newlines and extra spaces
        cmd = cmd.replace('\n', '').replace('\r', '')
        
        response = self._send_command('UIC', cmd)
        if response:
            self.group_name = group_name
        return response
        
    def ungroup(self):
        """
        Remove speaker from any group
        """
        cmd = '<name>SetUngroup</name>'
        response = self._send_command('UIC', cmd)
        if response:
            self.group_name = ""
        return response
        
    def __str__(self):
        return f"SamsungWamSpeaker(name='{self.name}', ip='{self.ip_address}', vol={self.volume}, mute='{self.mute}')"


class SamsungWamDiscovery:
    """
    Discover Samsung WAM speakers on the network using SSDP
    """
    def __init__(self, interface_ip: str = None):
        self.ssdp_multicast_addr = "239.255.255.250"
        self.ssdp_port = 1900
        self.discovery_timeout = 5
        self.interface_ip = interface_ip  # If None, will try to auto-determine
        
    def discover_speakers(self, timeout: int = None) -> List[SamsungWamSpeaker]:
        """
        Discover Samsung WAM speakers on the network using SSDP
        """
        if timeout is None:
            timeout = self.discovery_timeout
            
        # Create SSDP discovery message
        discovery_message = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "MAN: \"ssdp:discover\"\r\n"
            f"MX: {timeout}\r\n"
            "ST: urn:samsung.com:device:RemoteControlReceiver:1\r\n"
            "\r\n"
        ).encode('utf-8')
        
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.settimeout(timeout)
        
        # Enable port reuse and broadcasting
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        # If interface IP is provided, bind to it
        if self.interface_ip:
            sock.bind((self.interface_ip, 0))
        
        speakers = []
        try:
            # Send discovery message
            sock.sendto(discovery_message, (self.ssdp_multicast_addr, self.ssdp_port))
            
            # Collect responses
            while True:
                try:
                    data, addr = sock.recvfrom(1024)
                    response = data.decode('utf-8')
                    
                    # Check if this is a Samsung WAM speaker
                    if "urn:samsung.com:device:RemoteControlReceiver:1" in response:
                        # Extract IP address from the response
                        ip = addr[0]
                        
                        # Create a basic speaker object
                        speaker = SamsungWamSpeaker(ip_address=ip)
                        
                        # Try to get more details from the speaker
                        try:
                            # First try to get the speaker name to confirm it's working
                            cmd = '<name>GetSpkName</name>'
                            resp = speaker._send_command('UIC', cmd)
                            if resp and 'UIC' in resp and 'response' in resp['UIC']:
                                name = resp['UIC']['response'].get('spkname', {}).get('#cdata-section', '')
                                if name:
                                    speaker.name = name
                                else:
                                    speaker.name = f"Samsung Speaker at {ip}"
                            else:
                                speaker.name = f"Samsung Speaker at {ip}"
                        except:
                            # If refresh fails, just use the IP address
                            speaker.name = f"Samsung Speaker at {ip}"
                        
                        # Only add if we haven't seen this speaker before
                        is_new = True
                        for existing_speaker in speakers:
                            if existing_speaker.ip_address == speaker.ip_address:
                                is_new = False
                                break
                                
                        if is_new:
                            speakers.append(speaker)
                            
                except socket.timeout:
                    break
                    
        except Exception as e:
            print(f"Error during SSDP discovery: {e}")
        finally:
            sock.close()
            
        return speakers
        

def load_speakers_from_config(config_file: str = "speakers.txt") -> List[SamsungWamSpeaker]:
    """
    Load speakers configuration from JSON file
    """
    try:
        with open(config_file, 'r') as f:
            speakers_data = json.load(f)
            
        speakers = []
        for speaker_data in speakers_data:
            speaker = SamsungWamSpeaker(
                ip_address=speaker_data.get('IPAddress', ''),
                name=speaker_data.get('Name', ''),
                led=speaker_data.get('LED', 'off'),
                mute=speaker_data.get('Mute', 'off'),
                volume=speaker_data.get('Volume', 10),
                group_name=speaker_data.get('GroupName', ''),
                repeat=speaker_data.get('Repeat', 'off'),
                mac=speaker_data.get('MAC', '')  # MAC address may not be in original file but could be added
            )
            speakers.append(speaker)
            
        return speakers
    except FileNotFoundError:
        print(f"Configuration file {config_file} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error parsing JSON from {config_file}")
        return []
    except Exception as e:
        print(f"Error loading speakers from config: {e}")
        return []


def save_speakers_to_config(speakers: List[SamsungWamSpeaker], config_file: str = "speakers.txt"):
    """
    Save speakers configuration to JSON file
    """
    try:
        speakers_data = []
        for speaker in speakers:
            speaker_data = {
                "IPAddress": speaker.ip_address,
                "Name": speaker.name,
                "LED": speaker.led,
                "Mute": speaker.mute,
                "Volume": speaker.volume,
                "GroupName": speaker.group_name,
                "Repeat": speaker.repeat,
                "MAC": speaker.mac  # Include MAC if we have it
            }
            speakers_data.append(speaker_data)
            
        with open(config_file, 'w') as f:
            json.dump(speakers_data, f, indent=2)
            
        print(f"Saved {len(speakers)} speakers to {config_file}")
    except Exception as e:
        print(f"Error saving speakers to config: {e}")


class WamController:
    """
    Main controller class to manage Samsung WAM speakers
    """
    def __init__(self, config_file: str = "speakers.txt"):
        self.config_file = config_file
        self.discovery = SamsungWamDiscovery()
        self.speakers = []
        
    def discover(self) -> List[SamsungWamSpeaker]:
        """
        Discover speakers on the network and load from config
        """
        print("Discovering Samsung WAM speakers...")
        discovered_speakers = self.discovery.discover_speakers()
        
        print(f"Found {len(discovered_speakers)} speakers via network discovery")
        
        config_speakers = load_speakers_from_config(self.config_file)
        print(f"Loaded {len(config_speakers)} speakers from configuration")
        
        # Combine both lists, avoiding duplicates
        all_speakers = []
        seen_ips = set()
        
        for speaker in discovered_speakers + config_speakers:
            if speaker.ip_address not in seen_ips:
                all_speakers.append(speaker)
                seen_ips.add(speaker.ip_address)
                
        self.speakers = all_speakers
        return all_speakers
    
    def get_speaker_by_name(self, name: str) -> Optional[SamsungWamSpeaker]:
        """
        Get a speaker by its name
        """
        for speaker in self.speakers:
            if speaker.name.lower() == name.lower():
                return speaker
        return None
        
    def get_speaker_by_ip(self, ip: str) -> Optional[SamsungWamSpeaker]:
        """
        Get a speaker by its IP address
        """
        for speaker in self.speakers:
            if speaker.ip_address == ip:
                return speaker
        return None
        
    def list_speakers(self):
        """
        Print a list of all known speakers
        """
        if not self.speakers:
            print("No speakers found.")
            return
            
        print(f"\nFound {len(self.speakers)} speaker(s):")
        for i, speaker in enumerate(self.speakers):
            print(f"  {i+1}. Name: {speaker.name}")
            print(f"     IP: {speaker.ip_address}")
            print(f"     Volume: {speaker.volume}")
            print(f"     Mute: {speaker.mute}")
            print(f"     Group: {speaker.group_name or 'None'}")
            print()
            
    def create_group(self, group_name: str, speaker_names: List[str]):
        """
        Create a group with specified speakers
        """
        if len(speaker_names) < 2:
            print("Need at least 2 speakers to create a group")
            return
            
        # Find the speakers by name
        group_speakers = []
        main_speaker = None
        
        for name in speaker_names:
            speaker = self.get_speaker_by_name(name)
            if speaker:
                if main_speaker is None:
                    main_speaker = speaker
                else:
                    group_speakers.append(speaker)
            else:
                print(f"Speaker '{name}' not found")
                
        if not main_speaker:
            print("No valid speakers found to create group")
            return
            
        if len(group_speakers) == 0:
            print("Need at least 2 speakers to create a group")
            return
            
        # Create the group
        result = main_speaker.group_with_speakers(group_name, group_speakers)
        if result:
            print(f"Successfully created group '{group_name}' with {len(group_speakers) + 1} speakers")
        else:
            print("Failed to create group")
            
    def ungroup_all(self):
        """
        Remove all speakers from their groups
        """
        for speaker in self.speakers:
            if speaker.group_name:  # Only ungroup if in a group
                speaker.ungroup()
                print(f"Removed {speaker.name} from group '{speaker.group_name}'")


def main():
    """
    Main function to demonstrate the functionality
    """
    print("Samsung WAM Speaker Controller (Linux)")
    print("=====================================")
    
    # Create controller instance
    controller = WamController()
    
    # Discover speakers
    all_speakers = controller.discover()
    
    # List all speakers
    controller.list_speakers()
    
    # If we have speakers, demonstrate some controls
    if all_speakers:
        selected_speaker = all_speakers[0]  # Use the first speaker for demonstration
        print(f"Demonstrating controls on {selected_speaker.name}:")
        
        # Show current status
        print(f"Current status: Volume={selected_speaker.volume}, Mute={selected_speaker.mute}")
        
        # Try to refresh the speaker to get latest status
        selected_speaker.refresh()
        print(f"After refresh: Volume={selected_speaker.volume}, Mute={selected_speaker.mute}")
        
        # Example: change volume
        original_volume = selected_speaker.volume
        new_volume = min(30, original_volume + 2)  # Increase by 2 but cap at 30
        if new_volume != original_volume:
            selected_speaker.set_volume(new_volume)
            print(f"Volume changed from {original_volume} to {new_volume}")
            
            # Refresh again to confirm
            selected_speaker.refresh()
            print(f"Confirmed volume: {selected_speaker.volume}")
        
        # Example: toggle mute
        original_mute = selected_speaker.mute
        new_mute = 'on' if original_mute == 'off' else 'off'
        selected_speaker.set_mute(new_mute)
        print(f"Mute changed from {original_mute} to {new_mute}")
        
    print("\nController ready. Use WamController class to manage your speakers.")


if __name__ == "__main__":
    main()