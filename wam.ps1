[void][System.Reflection.Assembly]::LoadFrom($($PWD.path)+'/lib/Rssdp.dll')
#[void][System.Reflection.Assembly]::LoadFrom($env:SystemRoot+"\System32\"+'Rssdp.dll')

class playlist {
    [string[]]
    $Songs

    playlist([array]$url){
        ForEach($link in $url){
            $song_urls=Invoke-WebRequest $link | ForEach-Object links | ForEach-Object href | Where-Object {$_ -match "flac$|mp3$|mp4$"}
            ForEach($song in $song_urls){
                $this.Songs+="{0}/{1}"-f$link,$song
            }
        }
    }
}

class SamsungSpeaker {
    [ipaddress]
    $IPAddress
    [string]
    $SpeakerName
    [string]
    $SpeakerLED
    [string]
    $SpeakerMute
    [int]
    $SpeakerVolume
    [string]
    $SpeakerGroupName
    [string]
    $SpeakerAPInfo
    [string]
    $RepeatMode
    [string]
    $SpeakerMac
    SamsungSpeaker($IPAddress,$SpeakerName,$SpeakerLED,$SpeakerMute,[int]$SpeakerVolume,$SpeakerGroupName,$APInfo,$RepeatMode,$spkMAC){
        $this.IPAddress=$IPAddress
        $this.SpeakerName=$SpeakerName
        $this.SpeakerLED=$SpeakerLED
        $this.SpeakerMute=$SpeakerMute
        $this.SpeakerVolume=$SpeakerVolume
        $this.SpeakerGroupName=$SpeakerGroupName
        $this.SpeakerAPInfo=$APInfo
        $this.RepeatMode=$RepeatMode
        $this.SpeakerMac=$spkMAC
    }

<#    [SamsungSpeaker[]]Initiate (){
        $returnobj=@()
        $devices=Get-SamsungSpeakers -IPAddress $(get-netadapter wi* | get-netIPConfiguration).IPv4Address.IPAddress
        ForEach($device in $devices){
            $obj=[SamsungSpeaker]::new(
                $device.IPAddress,
                $device.SpeakerName,
                $device.SpeakerLED,
                $device.SpeakerMute,
                $device.SpeakerVolume,
                $device.SpeakerGroupName,
                $device.APInfo,
                $device.RepeatMode,
                $device.spkMAC
            )
            $returnobj+=$obj
        }
        return $returnobj
    }#>

    [SamsungSpeaker]Refresh(){
        $this.SpeakerName=$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetSpkName</name>'))").UIC.response.spkname.'#cdata-section'
        $this.SpeakerLED=$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetLed</name>'))").UIC.response.led
        $this.SpeakerMute=$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetMute</name>'))").UIC.response.mute
        $this.SpeakerVolume=[int]$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetVolume</name>'))").UIC.response.volume
        $this.SpeakerGroupName=$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetGroupName</name>'))").UIC.response.groupname.'#cdata-section'
        $this.SpeakerAPInfo=$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetApInfo</name>'))").UIC.response.ssid.'#cdata-section'
        $this.RepeatMode=$(Invoke-RestMethod -Uri "http://$($this.IPAddress):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetRepeatMode</name>'))").UIC.response.repeat
        return $this
    }
    [void]SetLed ([string]$choice='off'){
        if($choice -notin @('off','on')){
            throw 'Valid options are "off" and "on"'
        }
        $xml='<name>SetLed</name><p type="str" name="mute" val="{0}"/>'-f $choice
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Method Get -Uri $uri
    }
    [string]GetSpeakerName (){
        $xml='<name>GetSpkName</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=[string]$(Invoke-RestMethod -Method Get -Uri $uri).uic.response.spkname.'#cdata-section'
        return $resp
    }
    [string]GetSpeakerMute (){
        $xml='<name>GetMute</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=[string]$(Invoke-RestMethod -Method Get -Uri $uri).uic.response.mute
        return $resp
    }
    [string]GetSpeakerLED (){
        $xml='<name>GetLed</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=[string]$(Invoke-RestMethod -Method Get -Uri $uri).UIC.response.led
        return $resp
    }
    [string]GetRepeatMode (){
        $xml='<name>GetRepeatMode</name>'
        $payload=[system.uri]::EscapeDataString($xml)
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=[string]$(Invoke-RestMethod -Method Get -Uri $uri).response.repeat
        return $resp
    }
    [void]SetMute (
        [string]
        $choice='off'
        )
        {
            if($choice -notin @('on','off')){
                throw "valid values are 'on' or 'off'"
            }
            $xml='<name>SetMute</name><p type="str" name="mute" val="{0}"/>' -f $choice
            $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
            $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
            $(Invoke-RestMethod -Method Get -Uri $uri).uic.response.mute
    }
    [array]GetCpList (){
        $xml='<name>GetCpList</name><p type="dec" name="liststartindex" val="0"/><p type="dec" name="listcount" val="20"/>'
        $payload=[system.uri]::EscapeDataString($xml)
        $uri="http://{0}:55001/CPM?cmd={1}"-f$this.IPAddress,$payload
        $resp=$(Invoke-RestMethod -Method Get -Uri $uri)
        $cpobj=@()
        foreach($itm in $resp.cpm.response.cplist.cp){
            $cpobj+=[PSCustomObject]@{
                cpid=$itm.cpid
                Name=$itm.cpname
                SignInStatus=$itm.signinstatus
            }
        }
        return $cpobj
    }
    [System.Object]PlaySongFromURL($URL,$resume=1){
        $xml='<name>SetUrlPlayback</name><p type="cdata" name="url" val="empty"><![CDATA[{0}]]></p><p type="dec" name="buffersize" val="0"/><p type="dec" name="seektime" val="0"/><p type="dec" name="resume" val="{1}"/>'-f$URL,$resume
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        #Write-Host $uri
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
        #return [int]$resp.UIC.response.playtime
    }
    [System.Object]GetCurrentQueueList(){
        $xml='<name>GetCurrentQueuelist</name><p type="dec" name="liststartindex" val="0"/><p type="dec" name="listcount" val="1"/>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        #Write-Host $uri
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
        #return [int]$resp.UIC.response.playtime
    }
    [System.Object]GetCurrentPlaylist(){
        $xml='<name>GetCurrentPlaylist</name><p type="dec" name="liststartindex" val="0"/><p type="dec" name="listcount" val="1"/>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        #Write-Host $uri
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
        #return [int]$resp.UIC.response.playtime
    }
    [System.Object]GetAvSourceAll(){
        $xml='<name>GetAvSourceAll</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        #Write-Host $uri
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
        #return [int]$resp.UIC.response.playtime
    }
    [System.Object]Get7BandEQList(){
        $xml='<name>Get7BandEQList</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        #Write-Host $uri
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp.UIC.response.presetlist.preset
        #return [int]$resp.UIC.response.playtime
    }
    [System.Object]GetCPInfo(){
        $xml='<name>GetCpInfo</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/CPM?cmd={1}"-f$this.IPAddress,$payload
        #Write-Host $uri
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
        #return [int]$resp.UIC.response.playtime
    }
    [void]Play(){
        $xml='<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="play"/>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get        
    }
    [void]Resume(){
        $xml='<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="resume"/>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get        
    }
    [void]Pause(){
        $xml='<name>SetPlaybackControl</name><p type="str" name="playbackcontrol" val="pause"/>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get        
    }
    [void]RepeatOne(){
        $xml='<name>SetRepeatMode</name><p type="str" name="repeatmode" val="one"/>'
        $payload=[system.uri]::EscapeDataString($xml)
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get
    }
    [void]RepeatAll(){
        $xml='<name>SetRepeatMode</name><p type="str" name="repeatmode" val="all"/>'
        $payload=[system.uri]::EscapeDataString($xml)
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get
    }
    [void]RepeatOff(){
        $xml='<name>SetRepeatMode</name><p type="str" name="repeatmode" val="off"/>'
        $payload=[system.uri]::EscapeDataString($xml)
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get
    }
    [void]SetSearchTime([int]$time){
        $xml='<name>SetSearchTime</name><p type="dec" name="playtime" val="{0}"/>'-f$time
        $payload=[system.uri]::EscapeDataString($xml)
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get
    }
    [void]SetVolume([int]$volLevel=1){
        if($volLevel -gt 30){
            $volLevel=30
        }
        $xml='<name>SetVolume</name><p type="dec" name="volume" val="{0}"/>'-f$volLevel
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get        
    }
    [int]GetVolume(){
        $xml='<name>GetVolume</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp.UIC.response.volume
    }
    [string]GetGroupName(){
        $xml='<name>GetGroupName</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
    }
    [PSCustomObject]GetAcmMode(){
        $xml='<name>GetAcmMode</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        $obj=[PSCustomObject]@{
            SpeakerIP=$resp.uic.speakerip
            AcmMode=$resp.uic.response.acmmode
            AudioSourceMacAddr=$resp.uic.response.audiosourcemacaddr
            AudioSourceName=$resp.uic.response.audiosourcename.'#cdata-section'
            AudioSourceType=$resp.uic.response.audiosourcetype 
        }
        return $obj
    }
    [void]SetSpeakerName([string]$Name){
        $xml='<name>SetSpkName</name><p type="cdata" name="spkname" val="empty"><![CDATA[{0}]]></p>'-f$Name
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        Invoke-RestMethod -Uri $uri -Method Get
    }
    [string]GetSpeakerAPInfo(){
        $xml='<name>GetApInfo</name>'
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=Invoke-RestMethod -Uri $uri -Method Get
        return $resp
    }
    [system.object]AddCustomEQMode(
        [int]$PresetIndex,
        [string]$PresetName
    ){
        $xml='<name>AddCustomEQMode</name><p type="dec" name="presetindex" val="{0}"/><p type="str" name="presetname" val="{1}"/>'-f$PresetIndex,$PresetName
        $payload=[system.uri]::EscapeDataString($xml) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$payload
        $resp=$(Invoke-RestMethod -Uri $uri -Method Get).UIC.response
        return $resp
    }
    [SamsungSpeaker]Group([string]$GroupName,$speakers){
        $mainspeaker=$speakers[0]
        $restspeakers=$speakers.where{$PSItem.IPAddress -ne $mainspeaker.IPAddress}
        $groupCommandText=@'
<name>SetMultispkGroup</name>
<p type="cdata" name="name" val="empty"><![CDATA[{0}]]></p>
<p type="dec" name="index" val="1"/>
<p type="str" name="type" val="main"/>
<p type="dec" name="spknum" val="{1}"/>
<p type="str" name="audiosourcemacaddr" val="{2}"/>
<p type="cdata" name="audiosourcename" val="empty"><![CDATA[{3}]]></p>
<p type="str" name="audiosourcetype" val="speaker"/>
'@
        $restSpeakersCommandText=@'
<p type="str" name="subspkip" val="{0}"/>
<p type="str" name="subspkmacaddr" val="{1}"/>
'@
        $payload=$groupCommandText-f$GroupName,$speakers.count,$mainspeaker.SpeakerMac,$mainspeaker.SpeakerName -replace "`n",""
        foreach($spk in $restspeakers){
            $payload+=$restSpeakersCommandText-f$spk.IPAddress,$spk.SpeakerMac -replace "`n",""
        }
        $formattedPayload=[system.uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$mainspeaker.IPAddress,$formattedpayload
        $spkGroup=Invoke-RestMethod -Uri $uri
        return $mainspeaker
        #Write-Host $payload
    }
    [void]UnGroup(){
        $payload='<name>SetUngroup</name>'
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/"
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        Invoke-RestMethod -Uri $uri
    }
    [PSCustomObject]GetMusicInfo(){
        $payload='<name>GetMusicInfo</name>'
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/"
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]GetCurrentPlayTime(){
        $payload='<name>GetCurrentPlayTime</name>'
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/"
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]GetCurrentEQMode(){
        $payload='<name>GetCurrentEQMode</name>'
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/"
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]GetEQMode(){
        $payload='<name>GetEQMode</name>'
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/"
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]CreatePlaylist(
        [string]$Name
    ){
        $payload='<name>CreatePlaylist</name><p type="str" name="{0}" val=""/>'-f$Name
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]SetEQBalance(
        [int]$Value
    ){
        $payload='<name>SetEQBalance</name><p type="dec" name="eqbalance" val="{0}"/>'-f$Value
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]SetEQBass(
        [int]$Value
    ){
        $payload='<name>SetEQBass</name><p type="dec" name="eqbass" val="{0}"/>'-f$Value
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    
    [PSCustomObject]Set7BandEQPreset(
        [string]$PresetName
    ){
        $value=0
        switch ($PresetName) {
            None { $value=0 }
            Pop { $value=1 }
            Jazz { $value=2 }
            Classic { $value=3 }
            home { $value=4 }
            falls { $value=5 }
            Default { $value=0 }
        }
        $payload='<name>Set7bandEQMode</name><p type="dec" name="presetindex" val="{0}"/>'-f$value
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]Set7BandEQPreset(
        [int]$PresetValue
    ){
        $payload='<name>Set7bandEQMode</name><p type="dec" name="presetindex" val="{0}"/>'-f$PresetValue
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]SetEQTreble(
        [int]$Value
    ){
        $payload='<name>SetEQTreble</name><p type="dec" name="eqtreble" val="{0}"/>'-f$Value
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]Set7BandEQValue(
        [int]$PresetValue,
        [int]$EQ1,
        [int]$EQ2,
        [int]$EQ3,
        [int]$EQ4,
        [int]$EQ5,
        [int]$EQ6,
        [int]$EQ7
    ){
        $payload='<name>Set7bandEQValue</name><p type="dec" name="presetindex" val="{0}"/><p type="dec" name="eqvalue1" val="{1}"/><p type="dec" name="eqvalue2" val="{2}"/><p type="dec" name="eqvalue3" val="{3}"/><p type="dec" name="eqvalue4" val="{4}"/><p type="dec" name="eqvalue5" val="{5}"/><p type="dec" name="eqvalue6" val="{6}"/><p type="dec" name="eqvalue7" val="{7}"/>'-f$PresetValue,$EQ1,$EQ2,$EQ3,$EQ4,$EQ5,$EQ6,$EQ7
        Write-Host $payload
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        Write-Host $formattedPayload
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]Reset7bandEQValue(
        [int]$PresetValue
        #[int]$EQ1,
        #[int]$EQ2,
        #[int]$EQ3,
        #[int]$EQ4,
        #[int]$EQ5,
        #[int]$EQ6,
        #[int]$EQ7
    ){
        #$payload='<name>Reset7bandEQValue</name><p type="dec" name="presetindex" val="{0}"/><p type="dec" name="eqvalue1" val="{1}"/><p type="dec" name="eqvalue2" val="{2}"/><p type="dec" name="eqvalue3" val="{3}"/><p type="dec" name="eqvalue4" val="{4}"/><p type="dec" name="eqvalue5" val="{5}"/><p type="dec" name="eqvalue6" val="{6}"/><p type="dec" name="eqvalue7" val="{7}"/>'-f$PresetValue,$EQ1,$EQ2,$EQ3,$EQ4,$EQ5,$EQ6,$EQ7
        $payload='<name>Reset7bandEQValue</name><p type="dec" name="presetindex" val="{0}"/>'-f$PresetValue
        Write-Host $payload
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        Write-Host $formattedPayload
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]Cancel7bandEQMode()
    {
        $payload='<name>Cancel7bandEQMode</name>'
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
    [PSCustomObject]Remove7BandEQMode(
        [int]$PresetIndex
    )
    {
        $payload='<name>DelCustomEQMode</name><p type="dec" name="presetindex" val="{0}"/>'-f$PresetIndex
        $formattedPayload=[System.Uri]::EscapeDataString($payload) -replace "%2F","/" -replace "%3D","="
        $uri="http://{0}:55001/UIC?cmd={1}"-f$this.IPAddress,$formattedPayload
        $resp=$(Invoke-RestMethod -Uri $uri).UIC.response
        return $resp
    }
}

class SpeakerGroup : SamsungSpeaker {
    [string]
    $GroupName
    [SamsungSpeaker[]]
    $Speakers=$(Get-SamsungSpeakers -IPAddress $(get-netadapter wi* | get-netIPConfiguration).IPv4Address.IPAddress)
    SpeakerGroup (
        $GroupName,
        [SamsungSpeaker[]]$SpeakerDevices
    ){
        $SpeakerDevices.UnGroup()
        $SpeakerDevices[0].Group($GroupName,$SpeakerDevices)
        $this.GroupName=$GroupName
        $this.Speakers=$SpeakerDevices
    }
}

function Invoke-SpeakerCommand {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true,Position=0)]
        [ValidateSet('UIC','CPM')]
        [string]$CommandType,
        [Parameter(Mandatory=$true,Position=1)]
        [ValidateNotNullOrEmpty()]
        [string]$Command,
        [Parameter(Mandatory=$false,Position=2)]
        [ValidateNotNullOrEmpty()]
        [string]$IPAddress="192.168.1.131"
    )
    
    begin {
        
    }
    
    process {
        $uri="http://{0}:55001/{1}?cmd={2}" -f $IPAddress, $CommandType, [System.Web.HttpUtility]::UrlEncode($Command)
        Write-Host "Invoking command '$Command' on $CommandType at $IPAddress"
        Invoke-RestMethod -Uri $uri -Method Get -ErrorAction Stop | ForEach-Object {
            if ($_.UIC.response) {
                return $_.UIC.response
            } elseif ($_.CPM.response) {
                return $_.CPM.response
            } else {
                return $_
            }
        }
    }
    
    end {
        
    }
}

function Get-SamsungSpeakers {
    PARAM(
        #[IPAddress]$IPAddress=$(get-netadapter wi* | get-netIPConfiguration).IPv4Address.IPAddress
        [IPAddress]$IPAddress = $(iex "ipconfig getifaddr en0")
    )
    BEGIN{
        $search=[Rssdp.SsdpDeviceLocator]::new($IPAddress).SearchAsync().GetAwaiter().GetResult() | Where-Object NotificationType -eq "urn:samsung.com:device:RemoteControlReceiver:1"
    }
    PROCESS{
        ForEach($speaker in $search){
            $spkIP=$speaker.DescriptionLocation.Host
            $spkName=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetSpkName</name>'))").UIC.response.spkname.'#cdata-section'
            $spkLED=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetLed</name>'))").UIC.response.led
            $spkMute=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetMute</name>'))").UIC.response.mute
            $spkVol=[int]$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetVolume</name>'))").UIC.response.volume
            $spkGroupName=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetGroupName</name>'))").UIC.response.groupname.'#cdata-section'
            $spkAPInfo=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetApInfo</name>'))").UIC.response.ssid.'#cdata-section'
            $RepeatMode=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetRepeatMode</name>'))").UIC.response.repeat
            #$spkMAC=$(Get-NetNeighbor | Where-Object ipaddress -eq $($speaker.DescriptionLocation.Host)).LinkLayerAddress.replace("-",":").toLower()

            [SamsungSpeaker]::new(
                [IPAddress]$spkIP,
                $spkName,
                $spkLED,
                $spkMute,
                $spkVol,
                $spkGroupName,
                $spkAPInfo,
                $RepeatMode,
                $spkMAC
            )
        }
<#         $search | ForEach-Object -Parallel {
            $spkIP=$_.DescriptionLocation.Host
            $spkName=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetSpkName</name>'))").UIC.response.spkname.'#cdata-section'
            $spkLED=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetLed</name>'))").UIC.response.led
            $spkMute=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetMute</name>'))").UIC.response.mute
            $spkVol=[int]$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetVolume</name>'))").UIC.response.volume
            $spkGroupName=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetGroupName</name>'))").UIC.response.groupname.'#cdata-section'
            $spkAPInfo=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetApInfo</name>'))").UIC.response.ssid.'#cdata-section'
            $RepeatMode=$(Invoke-RestMethod -Uri "http://$($spkIP):55001/UIC?cmd=$([System.web.httpUtility]::UrlEncode('<name>GetRepeatMode</name>'))").UIC.response.repeat

            [SamsungSpeaker]::new(
                [IPAddress]$spkIP,
                $spkName,
                $spkLED,
                $spkMute,
                $spkVol,
                $spkGroupName,
                $spkAPInfo,
                $RepeatMode
            )
        } #>
    }
    END{

    }
}

filter supa {
    $obj = [PSCustomObject]@{
        IPAddress = $PSItem.IPAddress.IPAddressToString
        Name = $PSItem.SpeakerName
        LED = $PSItem.SpeakerLED
        Mute = $PSItem.SpeakerMute
        Volume = $PSItem.SpeakerVolume
        GroupName = $PSItem.SpeakerGroupName
        Repeat = $PSItem.RepeatMode
    }
    Write-Output $obj
}