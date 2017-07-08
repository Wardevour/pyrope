import json
from collections import OrderedDict

import bitstring

from pyrope.netstream_property_mapping import PropertyMapper
from pyrope.utils import read_string, UINT_32, UINT_64, FLOAT_LE_32, reverse_bytewise
from pyrope.frame import Frame
from pyrope.exceptions import PropertyParsingError, FrameParsingError
'''
Assumed File Structure:
4 Bytes size of header starting after CRC
4 Bytes CRC
8 Bytes Version
Header Data introduced by the string TAGame.Replay_Soccar_TA
Netstream Data
Meta Data
'''


class Replay:
    def __init__(self, path):
        self._header_raw = None
        self.header = None

        if isinstance(path, bytes):
            self._replay = bitstring.ConstBitStream(path)
        elif isinstance(path, str):
            with open(path, 'rb') as f:
                self._replay = bitstring.ConstBitStream(f.read())

        self._parse_meta()
        self._parse_header()

    def _parse_meta(self):
        self._replay.pos = 0  # Just reassure we are at the beginning
        header_size = self._replay.read(UINT_32)
        self.crc = self._replay.read('hex:32')
        self.version = str(self._replay.read(UINT_32)) + '.' + str(self._replay.read(UINT_32))

        assert int(self._replay.pos / 8) == 16
        check_bytes = self._replay.read('bytes:4')

        if (check_bytes != b'\x00\x00\x00\x00'):
            # Old replay, back it up.
            self._replay.pos -= 32

        assert read_string(self._replay) == 'TAGame.Replay_Soccar_TA'

        self._header_raw = self._replay.read((header_size - 8) * 8)
        return True

    def _parse_header(self):
        self.header = self._decode_properties(self._header_raw)

    def _decode_properties(self, bitstream):
        properties = {}
        while True:
            name, value = self._decode_property(bitstream)
            if name:
                properties[name] = value
            else:
                return properties

    def _decode_property(self, bitstream):
        property_key = read_string(bitstream)
        if property_key == 'None':
            return None, None

        property_type = read_string(bitstream)
        property_value_size = bitstream.read(UINT_64)

        if property_type == 'IntProperty':
            property_value = bitstream.read(UINT_32)
        elif property_type == 'StrProperty':
            property_value = read_string(bitstream)
        elif property_type == 'FloatProperty':
            property_value = bitstream.read(FLOAT_LE_32)
        elif property_type == 'NameProperty':
            property_value = read_string(bitstream)
        elif property_type == 'ArrayProperty':
            array_length = bitstream.read(UINT_32)
            property_value = [
                self._decode_properties(bitstream)
                for i in range(array_length)
            ]
        elif property_type == 'ByteProperty':
            key_text = read_string(bitstream)
            value_text = read_string(bitstream)
            property_value = {key_text: value_text}
        elif property_type == 'QWordProperty':
            property_value = bitstream.read(64).intle
        elif property_type == 'BoolProperty':
            property_value = bitstream.read(8).uint == 1
        else:
            msg = "Unknown property type %s for %s at position %i" % (
                property_type,
                property_key,
                int(self._replay.pos / 8)
            )
            raise PropertyParsingError(msg)
        return property_key, property_value

    def __getstate__(self):
        d = dict(self.__dict__)
        if '_replay' in d:
            del d['_replay']
        if '_netstream' in d:
            del d['_netstream_raw']
        if '_header' in d:
            del d['_header_raw']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
