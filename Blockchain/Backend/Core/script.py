from Blockchain.Backend.Util.util import encode_varint, int_to_little_endian


class Script:
    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def serialize(self):
        # initialize what we'll send back
        result = b""
        # go through each cmd
        for cmd in self.cmds:
            # if the cmd is an integer, it's an opcode
            if type(cmd) == int:
                # turn the cmd into a single byte integer using int_to_little_endian
                # result += int_to_little_endian(cmd, 1)
                result += int_to_little_endian(cmd, 1)
            else:
                # otherwise, this is an element
                # get the length in bytes
                length = len(cmd)
                # for large lengths, we have to use a pushdata opcode
                if length < 75:
                    # turn the length into a single byte integer
                    result += int_to_little_endian(length, 1)
                elif length > 75 and length < 0x100:
                    # 76 is pushdata1
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)
                elif length >= 0x100 and length <= 520:
                    # 77 is pushdata2
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)
                else:
                    raise ValueError("too long an cmd")

                result += cmd
        # get the length of the whole thing
        total = len(result)
        # encode_varint the total length of the result and prepend
        return encode_varint(total) + result
    
    @classmethod
    def p2pkh_script(cls, target_public_key):
        '''Returns a P2PKH script for the given target public key
        The script is of the form:
        OP_DUP OP_HASH160 <target_public_key> OP_EQUALVERIFY OP_CHECKSIG
        '''
        return Script([0x76, 0xA9, target_public_key, 0x88, 0xAC])
