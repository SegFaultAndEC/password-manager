import secrets
import string


def generatePassword(length=14, useSpecialChars=True):
    if length < 1:
        raise ValueError("密码长度必须大于0")
    letters = string.ascii_letters  # 大小写字母
    digits = string.digits  # 数字
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/"  # 特殊字符

    char_set = letters + digits
    if useSpecialChars:
        char_set += special_chars
    password = ''.join(secrets.choice(char_set) for _ in range(length))
    return password
