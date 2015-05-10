import unicodedata
import random

def removeControlCharacters(string):
    return ''.join(character for character in string if unicodedata.category(character)[0] != 'C')

# j, l, o and u are not present due to unreadable handwriting
name_characters = 'abcdefghikmnpqrstvwxyz'

def getRandomName(length=4):
    return ''.join(random.choice(name_characters) for x in range(length))

def getNthName(n):
    string = ''
    while True:
        n -= 1
        n, i = divmod(n, len(name_characters))
        string = name_characters[i] + string
        if n <= 0:
            return string
