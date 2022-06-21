import random
import string


def generate_unique_url_identifier(length=8):
    chars = list(string.digits + string.ascii_lowercase + string.ascii_uppercase)
    uid = chars[11 + int(random.random() * (len(chars) - 11))]

    for i in range(1, length):
        uid = uid + chars[1 + int(random.random() * (len(chars) - 1))]
    return uid.replace(' ', '')
