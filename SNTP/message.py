from datetime import datetime
import time

class NTP_message:
    def __init__(self):
        self.LI = 0
        self.VN =  0
        self.mode =  0
        self.stratum =  0
        self.poll = 0
        self.precison = 0
        self.root_delay =  0
        self.root_dispersion =  0
        self.reference_id =  b'\x00\x00\x00\x00'
        self.reference_tmstmp =  0
        self.originate_tmstmp =  0
        self.receive_tmstmp =    0
        self.transmit_tmstmp =  0

    def unpack(self, byte_string):
        self.LI = (byte_string[0] & 0b11000000) >> 6
        self.VN = (byte_string[0] & 0b111000) >> 3
        self.mode = (byte_string[0] & 0b111)
        self.stratum = int(byte_string[1])
        self.poll = int.from_bytes(byte_string[2:3], "little", signed=True)
        self.precison = int.from_bytes(byte_string[3:4], "little", signed=True)
        self.root_delay = int.from_bytes(byte_string[4:8], "little", signed=True)
        self.root_dispersion = int.from_bytes(byte_string[8:12], "little", signed=False)
        self.reference_id = byte_string[12:16]
        self.reference_tmstmp = int.from_bytes(byte_string[16:24], "little", signed=False)
        self.originate_tmstmp = int.from_bytes(byte_string[24:32], "little", signed=False)
        self.receive_tmstmp =   int.from_bytes(byte_string[32:40], "little", signed=False)
        self.transmit_tmstmp =  int.from_bytes(byte_string[40:48], "little", signed=False)
        if byte_string[48:60] != b'':
            self.authenticator = byte_string[48:60]
        return self

    def pack(self):
        byte_str = b''
        byte_str += ((self.LI << 6) | (self.VN << 3) | self.mode).to_bytes(1, signed=False, byteorder="little")
        byte_str += self.stratum.to_bytes(1, signed=False, byteorder="little")
        byte_str += self.poll.to_bytes(1, signed=True, byteorder="little")
        byte_str += self.precison.to_bytes(1, signed=True, byteorder="little")
        byte_str += self.root_delay.to_bytes(4, signed=True, byteorder="little")
        byte_str += self.root_dispersion.to_bytes(4, signed=False, byteorder="little")
        byte_str += self.reference_id
        byte_str += self.reference_tmstmp.to_bytes(8, signed=False, byteorder="little")
        byte_str += self.originate_tmstmp.to_bytes(8, signed=False, byteorder="little")
        byte_str += self.receive_tmstmp.to_bytes(8, signed=False, byteorder="little")
        byte_str += self.transmit_tmstmp.to_bytes(8, signed=False, byteorder="little")
        try:
            byte_str += self.authenticator
        except Exception:
            pass
        return byte_str

    def __str__(self):
        to_str = """NTP packet:
        {0}:LI
        {1}:VN
        {2}:Mode
        {3}:Stratum
        {4}:Poll
        {5}:precison/
        {6}:root delay
        {7}:root dispersion
        {8}:reference id
        {9}s, {10}ms:reference time stamp
        {11}s, {12}ms:originate time stamp
        {13}s, {14}ms:receive time stamp
        {15}s, {16}ms:transmit time stamp
        """.format(
            self.LI, self.VN, self.mode, self.stratum,
            self.poll, self.precison, self.root_delay,
            self.root_dispersion, self.reference_id,
            (self.reference_tmstmp & 0xFFFFFFFF00000000) >> 32 , self.reference_tmstmp & 0xFFFFFFFF,
            (self.originate_tmstmp & 0xFFFFFFFF00000000) >> 32 , self.originate_tmstmp & 0xFFFFFFFF,
            (self.receive_tmstmp & 0xFFFFFFFF00000000) >> 32, self.receive_tmstmp & 0xFFFFFFFF,
            (self.transmit_tmstmp & 0xFFFFFFFF00000000) >> 32, self.transmit_tmstmp & 0xFFFFFFFF,
        )
        try:
            to_str += "{0}:auth".format(self.authenticator)
        except Exception:
            pass
        return to_str

time_1900_1970 = 2209075200
if __name__ == "__main__":
    mess = NTP_message()
    packet = b'\xd1\x06\x08\xfc\xd1\xb9\xd1\x80\xd1\x8b\xba\xbdsntp\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    mess.pack()
    packet2 = mess.unpack(packet).pack()
    assert ( packet == mess.unpack(packet).pack())