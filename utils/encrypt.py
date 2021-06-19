import hashlib


def md5(string):
    """ MD5 加密"""
    hash_object = hashlib.md5('jiayan'.encode('utf-8'))
    hash_object.update(string.encode('utf-8'))
    return hash_object.hexdigest()


if __name__ == '__main__':
    res = md5('1')
    print(res)
