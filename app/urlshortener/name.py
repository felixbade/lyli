import unicodedata

def removeControlCharacters(string):
    return ''.join(character for character in string if unicodedata.category(character)[0] != 'C')

# j, l, o and u are not present due to unreadable handwriting
name_characters = 'abcdefghikmnpqrstvwxyz'

def getNthName(n):
    string = ''
    while True:
        n -= 1
        n, i = divmod(n, len(name_characters))
        string = name_characters[i] + string
        if n <= 0:
            return string

def isValidName(name):
    if not name:
        return False # if a hacker sends an empty default_name,
        # we don't care if our response is not legit
    return not any(c in ' ./' for c in name)
