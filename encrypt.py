from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib


# 补齐函数：PKCS7 padding
def pad(data: bytes) -> bytes:
    pad_len = AES.block_size - len(data) % AES.block_size
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    padLen = data[-1]
    return data[:-padLen]


# 加密函数
def aesEncrypt(plaintext: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()  # 生成32字节密钥
    iv = get_random_bytes(AES.block_size)  # 随机IV
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode()))
    encrypted = base64.b64encode(iv + ciphertext).decode()
    return encrypted


# 解密函数
def aesDecrypt(encrypted: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()
    raw = base64.b64decode(encrypted)
    iv = raw[:AES.block_size]
    ciphertext = raw[AES.block_size:]
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext)).decode()
    return plaintext
