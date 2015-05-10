import time
import string

def b62(number):
    alphabet = string.digits + string.ascii_letters
    encoded = []
    while number > 0:
        number, index = divmod(number, len(alphabet))
        encoded.append(alphabet[index])
    return ''.join(encoded)

def getID():
    integerid = int(time.time() * 1e6)
    return b62(integerid)

def getEmail():
    return 'lyli@lyli.fi'
    # track email spammers
    #return 'lyli.%s@lyli.fi' % getID()
