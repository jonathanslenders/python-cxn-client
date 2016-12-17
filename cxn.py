import requests
from xml.dom.minidom import parseString

# Docs: http://192.168.0.13:8050/7736537a-391e-43f3-8be9-720576796173/RecivaRadio/RecivaRadio.xml

__all__ = (
    'Keys',
    'CXN',
)

class Keys:
    STOP = 'STOP'
    PLAY_PAUSE = 'PLAY_PAUSE'
    SKIP_NEXT = 'SKIP_NEXT'
    SKIP_PREVIOUS = 'SKIP_PREVIOUS'
    POWER = 'POWER'
    VOL_UP = 'VOL_UP'
    VOL_DOWN = 'VOL_DOWN'


class AudioSource:
    RADIO = 0
    USB = 2
    CD = 5
    OPTICAL = 6
    BLUETOOTH = 14
    AIRPLAY = 23
    SPOTTIFY = 24


class CXN(object):
    """
    CXN client.
    """
    def __init__(self, host='192.168.0.13', port=8050):
        self.host = host
        self.port = port

    def choose_preset(self, number=1):
        data = u"""<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <u:PlayPreset xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                        <NewPresetNumberValue>{}</NewPresetNumberValue>
                    </u:PlayPreset>
                </s:Body>
            </s:Envelope>""".format(number)
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#PlayPreset"'

        return self._post(data, soap_action)

    def get_presets(self):
        data = u"""<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <u:GetPresetList xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                        <Start>1</Start>
                        <End>20</End>
                    </u:GetPresetList>
                </s:Body>
            </s:Envelope>"""
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#GetPresetList"'

        data = self._post(data, soap_action)

        # Get 'RetPresetListXML', a nested document that contains another XML document in a text node.
        presets_xml_data = _get_text(parseString(data).getElementsByTagName('RetPresetListXML')[0].childNodes)

        # Parse the presets.
        result = []
        presets = parseString(presets_xml_data).getElementsByTagName('preset')
        for p in presets:
            id = p.getAttribute('id')
            title = _get_text(p.getElementsByTagName('title')[0].childNodes)
            result.append((id, title))

        return result

    def set_power_state(self, power_state='IDLE'):
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#SetPowerState"'
        data = u"""<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
            xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
            <s:Body>
                <u:SetPowerState xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                    <NewPowerStateValue>{}</NewPowerStateValue>
                </u:SetPowerState>
                </s:Body>
            </s:Envelope>""".format(power_state)

        return self._post(data, soap_action)

    def do_something(self):  # XXX: not sure what this does.
        soap_action = '"urn:UuVol-com:service:StreamMagic6:1#SendCommand"'
        data = u"""<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <u:SendCommand xmlns:u="urn:UuVol-com:service:StreamMagic6:1">
                        <Command>1072</Command>
                        <Data>106f</Data>
                    </u:SendCommand>
                </s:Body>
            </s:Envelope>"""
        return self._post(data, soap_action)

    def get_playback_details(self):
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#GetPlaybackDetails"'
        data = u"""<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <u:GetPlaybackDetails
                        xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                        <NavigatorId>6dceb181-ff24-4e81-93ad-c469b110a230</NavigatorId>
                    </u:GetPlaybackDetails>
                </s:Body>
            </s:Envelope>"""
        data = self._post(data, soap_action)
        xml_data = _get_text(parseString(data).getElementsByTagName('RetPlaybackXML')[0].childNodes)
        xml = parseString(xml_data)

        state = _get_text(xml.getElementsByTagName('playback-details')[0].getElementsByTagName('state'))
        codec = xml.getElementsByTagName('format')[0].getAttribute('codec')
        sample_rate = xml.getElementsByTagName('format')[0].getAttribute('sample-rate')
        vbr = xml.getElementsByTagName('format')[0].getAttribute('vbr')
        bit_rate = xml.getElementsByTagName('format')[0].getAttribute('bit-rate')
        bit_depth = xml.getElementsByTagName('format')[0].getAttribute('bit-depth')
        status_id = xml.getElementsByTagName('station')[0].getAttribute('id')
        status_custommenuid = xml.getElementsByTagName('station')[0].getAttribute('custommenuid')
        status_logo = _get_text(xml.getElementsByTagName('station')[0].getElementsByTagName('logo'))
        artists = _get_text(xml.getElementsByTagName('artist'))
        playlist_entry_duration = _get_text(xml.getElementsByTagName('playlist-entry')[0].getElementsByTagName('duration'))
        stream_id = xml.getElementsByTagName('stream')[0].getAttribute('id')
        stream_url = _get_text(xml.getElementsByTagName('stream')[0].getElementsByTagName('url'))
        title = _get_text(xml.getElementsByTagName('title'))
        album_art_url = _get_text(xml.getElementsByTagName('album-art-url'))
        source_type = _get_text(xml.getElementsByTagName('source-type'))
        source_name = _get_text(xml.getElementsByTagName('source-name'))

        print(locals())

    def set_audio_source_by_number(self, source=5):
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#SetAudioSourceByNumber"'
        data = """<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
            <s:Body>
                <u:SetAudioSourceByNumber xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                    <NewAudioSourceValue>{}</NewAudioSourceValue>
                </u:SetAudioSourceByNumber>
            </s:Body>
            </s:Envelope>""".format(source)
        data = self._post(data, soap_action)

    def press_key(self, key=Keys.PLAY_PAUSE, duration='SHORT'):
        soap_action = '"urn:UuVol-com:service:UuVolSimpleRemote:1#KeyPressed"'
        data = """<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <u:KeyPressed xmlns:u="urn:UuVol-com:service:UuVolSimpleRemote:1">
                        <Key>{}</Key><Duration>{}</Duration>
                    </u:KeyPressed>
                </s:Body>
            </s:Envelope>""".format(key, duration)
        data = self._post(data, soap_action, simple_remote=True)

    def get_treble_test(self):  # XXX: doesn't seem to work.
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#GetToneCtrlBass"'
        data = u"""<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
                <s:Body>
                    <u:GetToneCtrlBass xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                    </u:GetPresetList>
                </s:Body>
            </s:Envelope>"""
        data = self._post(data, soap_action)
        return data  # TODO: parse from XML.

    def set_treble_test(self):  # XXX: doesn't seem to work.
        soap_action = '"urn:UuVol-com:service:UuVolControl:5#SetToneCtrlBass"'
        data = """<?xml version="1.0" encoding="UTF-8" ?>
            <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
            <s:Body>
                <u:SetToneCtrlBass xmlns:u="urn:UuVol-com:service:UuVolControl:5">
                    <NewToneCtrlBassValue>20</NewToneCtrlTrebleValue>
                </u:SetToneCtrlBass>
            </s:Body>
            </s:Envelope>"""
        data = self._post(data, soap_action)
        print(data)

    def _post(self, data, soap_action, simple_remote=False):
        headers = {
            'User-Agent': 'CambridgeConnect/2.4.10 (Android) UPnP/1.0 DLNADOC/1.50 Platinum/1.0.4.11',
            'Content-Type': 'text/xml; charset="utf-8"',
        }
        headers['SOAPAction'] = soap_action
        type = 'RecivaSimpleRemote' if simple_remote else 'RecivaRadio'

        res = requests.post('http://{}:{}/7736537a-391e-43f3-8be9-720576796173/{}/invoke'.format(
            self.host, self.port, type), headers=headers, data=data)
        res.raise_for_status()
        return res.content.decode('utf-8')


def _get_text(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def main():
    client = CXN()
    print(client.get_treble_test())
    print(client.set_treble_test())
    #print(client.get_presets())
    #client.press_key('VOL_UP')
    #client.get_playback_details()
    #client.choose_preset(1)
    #client.set_audio_source_by_number(0)
    #client.set_power_state()


if __name__ == '__main__':
    main()
