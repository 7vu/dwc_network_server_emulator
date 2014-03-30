import base64
import hashlib
import other.utils as utils

# GameSpy uses a slightly modified version of base64 which replaces +/= with []_
def base64_encode(input):
    output = base64.b64encode(input).replace('+', '[').replace('/', ']').replace('=', '_')
    return output


def base64_decode(input):
    output = base64.b64decode(input.replace('[', '+').replace('/', ']').replace('_', '='))
    return output


# Parse my custom authtoken generated by the emulated nas.nintendowifi.net/ac
def parse_authtoken(authtoken):
    messages = {}

    if authtoken[:3] == "NDS":
        authtoken = authtoken[3:]

    dec = base64.standard_b64decode(authtoken)

    for item in dec.split('|'):
        s = item.split('\\')
        messages[s[0]] = s[1]

    return messages


def generate_response(challenge, ac_challenge, secretkey, authtoken):
    md5 = hashlib.md5()
    md5.update(ac_challenge)

    output = md5.hexdigest()
    output += ' ' * 0x30
    output += authtoken
    output += secretkey
    output += challenge
    output += md5.hexdigest()

    md5_2 = hashlib.md5()
    md5_2.update(output)

    return md5_2.hexdigest()


# The proof is practically the same thing as the response, except it has the challenge and the secret key swapped.
# Maybe combine the two functions later?
def generate_proof(challenge, ac_challenge, secretkey, authtoken):
    md5 = hashlib.md5()
    md5.update(ac_challenge)

    output = md5.hexdigest()
    output += ' ' * 0x30
    output += authtoken
    output += challenge
    output += secretkey
    output += md5.hexdigest()

    md5_2 = hashlib.md5()
    md5_2.update(output)

    return md5_2.hexdigest()

# Code: Tetris DS @ 02057A14
def get_friendcode_from_profileid(profileid, gameid):
    friendcode = 0

    # Combine the profileid and gameid into one buffer
    buffer = [(profileid >> (8 * i)) & 0xff for i in range(4)]
    buffer += [ord(c) for c in gameid]

    crc = utils.calculate_crc8(buffer)

    # The upper 32 bits is the crc8 of the combined buffer.
    # The lower 32 bits of the friend code is the profileid.
    friendcode = ((crc & 0x7f) << 32) | profileid

    return friendcode

def get_profileid_from_friendcode(friendcode):
    # Get the lower 32 bits as the profile id
    profileid = friendcode & 0xffffffff
    return profileid