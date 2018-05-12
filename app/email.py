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
    # integer of unixtime with microsecond resolution
    integerid = int(time.time() * 1e6)
    return b62(integerid)

def get_email():
    return 'flix.bade@gmail.com'
    # track email spammers
    #return 'lyli.%s@lyli.fi' % getID()
