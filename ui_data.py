import hashlib
import json
import encrypt
import os
from datetime import datetime


def save(key, data):
    if data is None:
        return
    encrypted = encrypt.aesEncrypt(json.dumps(data), key)
    filePath = os.path.expanduser('~/password_manager/password.txt')

    # 备份
    if os.path.exists(filePath):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(filePath, 'r') as f:
            text = f.read()
        backupPath = os.path.expanduser(f'~/password_manager/{timestamp}')
        with open(backupPath, 'w') as f:
            f.write(text)

    # 写入内容
    with open(filePath, 'w') as f:
        f.write(encrypted)


def deleteFilesExcept(targetDir, excludeFile):
    for item in os.listdir(targetDir):
        item_path = os.path.join(targetDir, item)
        # 只处理文件，忽略子文件夹
        if os.path.isfile(item_path) and item != excludeFile:
            try:
                os.remove(item_path)
            except Exception:
                pass


def clearBackup():
    filePath = os.path.expanduser('~/password_manager/')
    if not os.path.exists(filePath):
        return
    deleteFilesExcept(filePath, "password.txt")


def load(key):
    filePath = os.path.expanduser('~/password_manager/password.txt')
    with open(filePath, 'r') as f:
        encrypted = f.read()
        plainText = encrypt.aesDecrypt(encrypted, key)
        return json.loads(plainText)


def getPassword(platform, account, key):
    data = load(key)
    return data["platforms"][platform][account]


class UIData:
    def __init__(self):
        self.platforms = dict()
        self.key = ""

    def getPlatforms(self):
        return list(self.platforms.keys())

    def getAccount(self, platform):
        if platform not in self.platforms:
            return []
        else:
            return self.platforms[platform]

    def addPlatform(self, name, key):
        if name in self.platforms:
            return
        self.platforms[name] = []
        data = load(key)
        data["platforms"][name] = {}
        save(key, data)

    def deletePlatform(self, platform, key):
        self.platforms.pop(platform)
        data = load(key)
        data["platforms"].pop(platform)
        save(key, data)

    def addAccount(self, platform, accountName, password, key):
        if platform not in self.platforms:
            return
        self.platforms[platform].append(accountName)
        data = load(key)
        data["platforms"][platform][accountName] = password
        save(key, data)

    def changeAccount(self, platform, account, password, accountC, passwordC, key):
        account_ = account
        password_ = password
        if accountC != "":
            account_ = accountC
        if passwordC != "":
            password_ = passwordC
        self.deleteAccount(platform, account, key)
        self.addAccount(platform, account_, password_, key)

    def deleteAccount(self, platform, account, key):
        self.platforms[platform].remove(account)
        data = load(key)
        data["platforms"][platform].pop(account)
        save(key, data)

    def getDict(self):
        return self.platforms

    def hasPlatform(self, platform):
        return platform in self.platforms

    def changeKey(self, key: str, newKey: str):
        data = load(key)
        data["key"] = hashlib.sha256(newKey.encode("utf-8")).hexdigest()
        save(newKey, data)
        self.key = hashlib.sha256(newKey.encode("utf-8")).hexdigest()


def initKey(key):
    filePath = os.path.expanduser('~/password_manager/password.txt')
    if not os.path.exists(filePath):
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        with open(filePath, 'w') as f:
            text = f"{{\"key\":\"{hashlib.sha256(key.encode("utf-8")).hexdigest()}\",\"platforms\":{{}}}}"
            encrypted = encrypt.aesEncrypt(text, key)
            f.write(encrypted)


def hasFile():
    filePath = os.path.expanduser('~/password_manager/password.txt')
    return os.path.exists(filePath)


def loadFile(key):
    data = UIData()
    jsonData = load(key)
    data.key = jsonData["key"]
    for k, v in jsonData["platforms"].items():
        data.platforms[k] = []
        for k2, v2 in v.items():
            data.platforms[k].append(k2)
    return data
