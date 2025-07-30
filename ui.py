from PySide6.QtGui import QAction, QIcon

from ui_data import UIData, initKey, hasFile, loadFile, getPassword, clearBackup
from generate_password import generatePassword
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
import pyperclip
import hashlib


class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFixedWidth(1)  # 控制物理宽度为1像素
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(192, 192, 192, 128);
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)


class HLine(QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)  # 控制物理宽度为1像素
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(192, 192, 192, 128);
                border: none;
                margin: 0px;
                padding: 0px;
            }
        """)


class CheckKeyWindow(QDialog):
    def __init__(self, data: UIData):
        super(CheckKeyWindow, self).__init__()
        self.data = data
        self.resultFlag = False
        self.setWindowTitle("密钥确认")
        self.keyEditLine = QLineEdit()
        self.ensureButton = QPushButton("确认")
        self.draw()
        self.register()

    def draw(self):
        layout = QVBoxLayout(self)
        self.keyEditLine.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("请输入密钥:"))
        layout.addWidget(self.keyEditLine)
        layout.addWidget(HLine())
        layout.addWidget(self.ensureButton)

    def ensure(self):
        self.resultFlag = False
        if hashlib.sha256(self.keyEditLine.text().encode("utf-8")).hexdigest() == self.data.key:
            self.resultFlag = True
            self.accept()
        else:
            self.resultFlag = False
            QMessageBox.critical(self, "提示", "密钥错误")

    def register(self):
        self.ensureButton.clicked.connect(self.ensure)


class PlatformItem(QPushButton):
    def __init__(self, mainWindow, name="Platform"):
        super(PlatformItem, self).__init__()
        self.mainWindow = mainWindow
        self.name = name
        self.setText(name)
        self.setMinimumSize(120, 64)
        self.setStyleSheet("font-size: 24px;")

    def refreshAccountMenu(self):
        self.mainWindow.accountMenu.platform = self.name
        self.mainWindow.accountMenu.refresh()
        self.mainWindow.accountMenu.window().update()

    def mousePressEvent(self, event):
        # 检测右键点击
        if event.button() == Qt.RightButton:
            ret = QMessageBox.question(self, "提示", f"是否删除平台:{self.name}")
            if ret != 16384:
                return
            ans = self.mainWindow.ensureKey()
            if ans[0]:
                self.mainWindow.data.deletePlatform(self.name, ans[1])
            self.mainWindow.accountMenu.platform = ""
            self.mainWindow.accountMenu.refresh()
            self.mainWindow.accountMenu.window().update()
            self.mainWindow.platformMenu.refresh()
            self.mainWindow.platformMenu.window().update()

        else:
            # 保留原始的左键点击功能
            super().mousePressEvent(event)


class AddPlatformWindow(QWidget):
    def __init__(self, data: UIData, platformMenu, ensureKey):
        super(AddPlatformWindow, self).__init__()
        self.setWindowTitle("添加平台")
        # 数据
        self.data = data
        self.platformMenu = platformMenu
        self.ensureKey = ensureKey
        # 图形
        self.nameEditLine = QLineEdit()
        self.addButton = QPushButton("添加")
        self.register()
        self.draw()

    def draw(self):
        platformNameWidget = QWidget()
        platformNameLayout = QHBoxLayout()
        platformNameLayout.addWidget(QLabel("平台名称:"))
        platformNameLayout.addWidget(self.nameEditLine)
        platformNameWidget.setLayout(platformNameLayout)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(platformNameWidget)
        layout.addWidget(self.addButton)
        self.setLayout(layout)

    def register(self):
        self.addButton.clicked.connect(self.addPlatform)

    def addPlatform(self):
        if self.nameEditLine.text() == "":
            QMessageBox.warning(self, "提示", "平台名不可为空")
            return
        ans = self.ensureKey()
        if ans[0]:
            self.data.addPlatform(self.nameEditLine.text(), ans[1])
            self.platformMenu.refresh()
            self.platformMenu.window().update()
            self.nameEditLine.setText("")


class PlatformMenu(QWidget):
    def __init__(self, data: UIData, mainWindow):
        super(PlatformMenu, self).__init__()
        # 数据
        self.data = data
        self.mainWindow = mainWindow
        # 创建布局
        self.layout = QVBoxLayout(self)
        # 初始化固定部件
        self.scrollArea = None
        self.contentWidget = None
        self.scrollLayout = None
        self.addPlatformButton = None
        self.addPlatformWindow = AddPlatformWindow(data, self, self.mainWindow.ensureKey)
        # 绘制固定部分
        self.draw()
        # 注册事件
        self.register()
        # 初始绘制平台项
        self.refresh()

    def draw(self):
        # 创建滚动区域
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumWidth(144)

        # 创建内容容器（用于放置平台项）
        self.contentWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.contentWidget)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.contentWidget)

        # 添加按钮
        self.addPlatformButton = QPushButton("添加平台", self)

        # 将固定部分添加到布局
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(self.addPlatformButton)

    def refresh(self):
        # 删除平台项
        for i in reversed(range(self.scrollLayout.count())):
            item = self.scrollLayout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # 重新添加所有平台项
        for k, v in self.data.getDict().items():
            item = PlatformItem(self.mainWindow, k)
            item.clicked.connect(item.refreshAccountMenu)
            self.scrollLayout.addWidget(item)

    def register(self):
        self.addPlatformButton.clicked.connect(self.addPlatform)

    def addPlatform(self):
        if self.addPlatformWindow is None:
            self.addPlatformWindow = AddPlatformWindow(self.data, self)
        self.addPlatformWindow.show()
        self.addPlatformWindow.raise_()
        self.addPlatformWindow.activateWindow()


class CheckAccountWindow(QDialog):
    def __init__(self, name, password):
        super(CheckAccountWindow, self).__init__()
        self.nameData = name
        self.passwordData = password
        self.name = QLabel(f"用户名:{name}")
        self.copyNameBtn = QPushButton("复制")
        self.copyPasswordBtn = QPushButton("复制密码")
        self.closeBtn = QPushButton("关闭")
        nameWidget = QWidget()
        nameLayout = QHBoxLayout(nameWidget)
        nameLayout.addWidget(self.name)
        nameLayout.addWidget(VLine())
        nameLayout.addWidget(self.copyNameBtn)
        layout = QVBoxLayout(self)
        layout.addWidget(nameWidget)
        layout.addWidget(self.copyPasswordBtn)
        layout.addWidget(HLine())
        layout.addWidget(self.closeBtn)
        self.register()

    def copyName(self):
        pyperclip.copy(self.nameData)
        QMessageBox.information(self, "提示", "已复制到剪贴板")

    def copyPassword(self):
        pyperclip.copy(self.passwordData)
        QMessageBox.information(self, "提示", "已复制到剪贴板")

    def closeWindow(self):
        self.accept()

    def register(self):
        self.copyNameBtn.clicked.connect(self.copyName)
        self.copyPasswordBtn.clicked.connect(self.copyPassword)
        self.closeBtn.clicked.connect(self.closeWindow)


class ChangeAccountWindow(QDialog):
    def __init__(self, name, accountMenu):
        super(ChangeAccountWindow, self).__init__()
        self.name = name
        self.accountMenu = accountMenu
        self.setWindowTitle("修改")
        self.resize(800, 0)
        self.nameEditLine = QLineEdit()
        self.passwordEditLine = QLineEdit()
        self.changeBtn = QPushButton("修改")
        self.register()
        self.draw()

    def draw(self):
        self.passwordEditLine.setEchoMode(QLineEdit.Password)

        nameEditLineWidget = QWidget()
        nameEditLineLayout = QHBoxLayout(nameEditLineWidget)
        nameEditLineLayout.addWidget(QLabel("用户名:"))
        nameEditLineLayout.addWidget(self.nameEditLine)

        passwordEditLineWidget = QWidget()
        passwordEditLineLayout = QHBoxLayout(passwordEditLineWidget)
        passwordEditLineLayout.addWidget(QLabel("密码:"))
        passwordEditLineLayout.addWidget(self.passwordEditLine)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(QLabel("输入为空则保留原数据"))
        layout.addWidget(nameEditLineWidget)
        layout.addWidget(passwordEditLineWidget)
        layout.addWidget(HLine())
        layout.addWidget(self.changeBtn)

    def change(self):
        ans = self.accountMenu.ensureKey()
        if ans[0]:
            ret = QMessageBox.question(self, "提示", "是否进行修改")
            if ret != 16384:
                return
            self.accountMenu.data.changeAccount(self.accountMenu.platform, self.name,
                                                getPassword(self.accountMenu.platform, self.name, ans[1]),
                                                self.nameEditLine.text(),
                                                self.passwordEditLine.text(), ans[1])
            self.accountMenu.refresh()
            self.accountMenu.window().update()
            self.accept()

    def register(self):
        self.changeBtn.clicked.connect(self.change)


class AccountItem(QWidget):
    def __init__(self, name, platform, accountMenu):
        super(AccountItem, self).__init__()
        self.name = name
        self.platform = platform
        self.accountMenu = accountMenu
        self.checkButton = QPushButton("查看")
        self.deleteButton = QPushButton("删除")
        self.changeButton = QPushButton("修改")
        self.setMinimumSize(240, 64)
        self.register()
        self.draw()

    def draw(self):
        editAreaWidget = QWidget()
        editAreaLayout = QVBoxLayout(editAreaWidget)
        editAreaLayout.addWidget(self.checkButton)
        editAreaLayout.addWidget(self.deleteButton)
        editAreaLayout.addWidget(self.changeButton)

        layout = QHBoxLayout()
        label = QLabel(self.name)
        label.setStyleSheet("font-size: 20px;")
        layout.addWidget(label, 1)
        layout.addWidget(VLine())
        layout.addWidget(editAreaWidget)
        self.setLayout(layout)

    def register(self):
        self.checkButton.clicked.connect(self.check)
        self.changeButton.clicked.connect(self.change)
        self.deleteButton.clicked.connect(self.delete)

    def check(self):
        ans = self.accountMenu.ensureKey()
        if ans[0]:
            win = CheckAccountWindow(self.name, getPassword(self.platform, self.name, ans[1]))
            win.show()
            win.exec_()

    def change(self):
        win = ChangeAccountWindow(self.name, self.accountMenu)
        win.show()
        win.exec_()

    def delete(self):
        ans = self.accountMenu.ensureKey()
        if ans[0]:
            ret = QMessageBox.question(self, "提示", f"是否删除{self.name}")
            if ret != 16384:
                return
            self.accountMenu.data.deleteAccount(self.platform, self.name, ans[1])
            self.accountMenu.refresh()
            self.accountMenu.window().update()


class AddAccountWindow(QWidget):
    def __init__(self, data: UIData, accountMenu, ensureKey):
        super(AddAccountWindow, self).__init__()
        self.data = data
        self.accountMenu = accountMenu
        self.ensureKey = ensureKey
        self.setWindowTitle("添加账户")
        self.resize(800, 0)
        self.nameEditLine = QLineEdit()
        self.passwordEditLine = QLineEdit()
        self.passwordCount = QLineEdit("14")
        self.hasSpecialChar = QCheckBox("特殊字符")
        self.hasSpecialChar.setChecked(True)
        self.randomButton = QPushButton("随机密码")
        self.addButton = QPushButton("添加")
        self.register()
        self.draw()

    def draw(self):
        self.passwordEditLine.setEchoMode(QLineEdit.Password)

        nameEditLineWidget = QWidget()
        nameEditLineLayout = QHBoxLayout(nameEditLineWidget)
        nameEditLineLayout.addWidget(QLabel("用户名:"))
        nameEditLineLayout.addWidget(self.nameEditLine)

        passwordEditLineWidget = QWidget()
        passwordEditLineLayout = QHBoxLayout(passwordEditLineWidget)
        passwordEditLineLayout.addWidget(QLabel("密码:"))
        passwordEditLineLayout.addWidget(self.passwordEditLine)

        editLineWidget = QWidget()
        editLineLayout = QVBoxLayout(editLineWidget)
        editLineLayout.addWidget(nameEditLineWidget)
        editLineLayout.addWidget(passwordEditLineWidget)

        randomAreaWidget = QWidget()
        randomAreaLayout = QVBoxLayout(randomAreaWidget)
        randomAreaLayout.addWidget(QLabel("密码位数:"))
        randomAreaLayout.addWidget(self.passwordCount)
        randomAreaLayout.addWidget(self.hasSpecialChar)
        randomAreaLayout.addWidget(self.randomButton)

        editAreaWidget = QWidget()
        editAreaLayout = QHBoxLayout(editAreaWidget)
        editAreaLayout.addWidget(editLineWidget, 1)
        editAreaLayout.addWidget(VLine())
        editAreaLayout.addWidget(randomAreaWidget)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(editAreaWidget)
        layout.addWidget(self.addButton)

    def randomPassword(self):
        password = ""
        if self.passwordCount.text() == "":
            password = generatePassword(14, self.hasSpecialChar.isChecked())
        else:
            count = 14
            try:
                count = int(self.passwordCount.text())
            except ValueError:
                pass
            password = generatePassword(count, self.hasSpecialChar.isChecked())
        self.passwordEditLine.setText(password)
        pyperclip.copy(password)
        QMessageBox.information(self, "提示", "已复制到剪贴板")

    def addAccount(self):
        if self.nameEditLine.text() == "":
            QMessageBox.warning(self, "提示", "用户名不可为空")
            return
        if self.passwordEditLine.text() == "":
            QMessageBox.warning(self, "提示", "密码不可为空")
            return
        ans = self.ensureKey()
        if ans[0]:
            self.data.addAccount(self.accountMenu.platform, self.nameEditLine.text(), self.passwordEditLine.text(),
                                 ans[1])
            self.nameEditLine.setText("")
            self.passwordEditLine.setText("")
            self.accountMenu.refresh()
            self.accountMenu.window().update()

    def register(self):
        self.randomButton.clicked.connect(self.randomPassword)
        self.addButton.clicked.connect(self.addAccount)


class AccountMenu(QWidget):
    def __init__(self, data: UIData, ensureKey):
        super(AccountMenu, self).__init__()
        # 数据
        self.data = data
        self.platform = ""
        self.ensureKey = ensureKey
        # 图形
        self.addAccountWindow = AddAccountWindow(data, self, ensureKey)
        self.addAccountButton = None
        self.platformNameLabel = QLabel(f"当前选中平台:{self.platform}")
        self.scrollArea = None
        self.scrollLayout = None
        self.contentWidget = None
        self.layout = QVBoxLayout(self)
        self.draw()
        self.refresh()

        self.register()

    def draw(self):
        self.addAccountButton = QPushButton("添加账户", self)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setMinimumWidth(256)
        self.scrollLayout = QVBoxLayout()
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.contentWidget = QWidget()
        self.contentWidget.setLayout(self.scrollLayout)
        self.scrollArea.setWidget(self.contentWidget)
        self.layout.addWidget(self.platformNameLabel)
        self.layout.addWidget(self.scrollArea)
        self.layout.addWidget(VLine())
        self.layout.addWidget(self.addAccountButton)

    def refresh(self):
        # 删除所有账户
        for i in reversed(range(self.scrollLayout.count())):
            item = self.scrollLayout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # 重新添加所有平台项
        for i in self.data.getAccount(self.platform):
            item = AccountItem(i, self.platform, self)
            self.scrollLayout.addWidget(item)
            self.scrollLayout.addWidget(HLine())
        # 刷新文字
        self.platformNameLabel.setText(f"当前选中平台:{self.platform}")

    def register(self):
        self.addAccountButton.clicked.connect(self.addAccount)

    def addAccount(self):
        if not self.data.hasPlatform(self.platform):
            QMessageBox.warning(self, "提示", "需要先选择一个平台")
            return
        if self.addAccountWindow is None:
            self.addAccountWindow = AddAccountWindow(self.data, self, self.ensureKey)
        self.addAccountWindow.show()
        self.addAccountWindow.raise_()
        self.addAccountWindow.activateWindow()


class InitKey(QDialog):
    def __init__(self, mainWindow):
        super(InitKey, self).__init__()
        self.mainWindow = mainWindow
        self.setWindowTitle("设置密钥")
        self.resize(400, 0)
        self.keyEditLine = QLineEdit()
        self.keyEnsureEditLine = QLineEdit()
        self.button = QPushButton("确认")
        self.draw()
        self.register()

    def draw(self):
        self.keyEditLine.setEchoMode(QLineEdit.Password)
        self.keyEnsureEditLine.setEchoMode(QLineEdit.Password)
        keyWidget = QWidget()
        keyLayout = QHBoxLayout(keyWidget)
        keyLayout.addWidget(QLabel("密钥:"))
        keyLayout.addWidget(self.keyEditLine)

        keyEnsureWidget = QWidget()
        keyEnsureLayout = QHBoxLayout(keyEnsureWidget)
        keyEnsureLayout.addWidget(QLabel("确认密钥:"))
        keyEnsureLayout.addWidget(self.keyEnsureEditLine)

        layout = QVBoxLayout(self)
        layout.addWidget(keyWidget)
        layout.addWidget(keyEnsureWidget)
        layout.addWidget(self.button)

    def register(self):
        self.button.clicked.connect(self.ensure)

    def ensure(self):
        if self.keyEditLine.text() == "" or self.keyEnsureEditLine.text() == "":
            QMessageBox.warning(self, "提示", "密钥不可为空")
            return
        if self.keyEditLine.text() != self.keyEnsureEditLine.text():
            QMessageBox.warning(self, "提示", "两次密钥输入不同")
            return
        initKey(self.keyEditLine.text())
        self.mainWindow.data.key = hashlib.sha256(self.keyEditLine.text().encode("utf-8")).hexdigest()
        self.accept()


class GetKeyWindow(QDialog):
    def __init__(self, mainWindow):
        super(GetKeyWindow, self).__init__()
        self.mainWindow = mainWindow
        self.setWindowTitle("登陆")
        self.resize(400, 0)
        self.keyEditLine = QLineEdit()
        self.button = QPushButton("确认")
        self.key = ""
        self.draw()
        self.register()

    def draw(self):
        self.keyEditLine.setEchoMode(QLineEdit.Password)
        keyWidget = QWidget()
        keyLayout = QHBoxLayout(keyWidget)
        keyLayout.addWidget(QLabel("密钥:"))
        keyLayout.addWidget(self.keyEditLine)

        layout = QVBoxLayout(self)
        layout.addWidget(keyWidget)
        layout.addWidget(self.button)

    def register(self):
        self.button.clicked.connect(self.ensure)

    def ensure(self):
        if self.keyEditLine.text() == "":
            QMessageBox.warning(self, "提示", "密钥不可为空")
            return
        self.key = self.keyEditLine.text()
        self.accept()


class ChangeKeyWindow(QDialog):
    def __init__(self, mainWindow):
        super(ChangeKeyWindow, self).__init__()
        self.mainWindow = mainWindow
        self.setWindowTitle("修改密钥")
        self.resize(400, 0)
        self.newKeyLineEdit = QLineEdit()
        self.newKeyEnsureLineEdit = QLineEdit()
        self.changeBtn = QPushButton("修改")
        self.register()
        self.draw()

    def draw(self):
        self.newKeyLineEdit.setEchoMode(QLineEdit.Password)
        self.newKeyEnsureLineEdit.setEchoMode(QLineEdit.Password)
        self.newKeyLineEdit.setText("")
        self.newKeyEnsureLineEdit.setText("")

        newKeyEditLineWidget = QWidget()
        newKeyEditLineLayout = QHBoxLayout(newKeyEditLineWidget)
        newKeyEditLineLayout.addWidget(QLabel("新密钥:"))
        newKeyEditLineLayout.addWidget(self.newKeyLineEdit)

        newKeyEditEnsureEditLineWidget = QWidget()
        newKeyEditEnsureEditLineLayout = QHBoxLayout(newKeyEditEnsureEditLineWidget)
        newKeyEditEnsureEditLineLayout.addWidget(QLabel("确认密钥:"))
        newKeyEditEnsureEditLineLayout.addWidget(self.newKeyEnsureLineEdit)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(newKeyEditLineWidget)
        layout.addWidget(newKeyEditEnsureEditLineWidget)
        layout.addWidget(HLine())
        layout.addWidget(self.changeBtn)

    def change(self):
        if self.newKeyLineEdit.text() != self.newKeyEnsureLineEdit.text():
            QMessageBox.warning(self, "提示", "两次密钥输入不同")
            return
        ans = self.mainWindow.ensureKey()
        if not ans[0]:
            QMessageBox.warning(self, "提示", "密钥错误")
            return
        if ans[1] == self.newKeyLineEdit.text():
            QMessageBox.warning(self, "提示", "新旧密钥相同")
            return
        ret = QMessageBox.question(self, "提示", f"确认将密钥修改为\"{self.newKeyLineEdit.text()}\"吗?")
        if ret != 16384:
            return
        self.mainWindow.data.changeKey(ans[1], self.newKeyLineEdit.text())
        QMessageBox.information(self, "提示", "已成功修改密钥")
        self.accept()

    def register(self):
        self.changeBtn.clicked.connect(self.change)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # 数据
        self.data = UIData()
        if not hasFile():
            while True:
                win = InitKey(self)
                win.show()
                ret = win.exec_()
                if ret == QDialog.Accepted:
                    break
                else:
                    exit()
        else:
            while True:
                win = GetKeyWindow(self)
                win.show()
                ret = win.exec_()
                if ret == QDialog.Accepted:
                    try:
                        self.data = loadFile(win.key)
                        break
                    except Exception:
                        QMessageBox.warning(self, "提示", "密钥错误")
                else:
                    exit()

        self.keyWindow = CheckKeyWindow(self.data)
        self.accountMenu = AccountMenu(self.data, self.ensureKey)
        self.platformMenu = PlatformMenu(self.data, self)
        self.createMenu()
        self.draw()

    # 创建菜单栏
    def createMenu(self):
        menuBar = self.menuBar()
        settingsMenu = menuBar.addMenu('设置')

        changeKeyAction = QAction(QIcon(), '修改密钥', self)
        changeKeyAction.setShortcut('Ctrl+K')
        changeKeyAction.triggered.connect(self.changeKey)

        clearBackupAction = QAction(QIcon(), '清除备份', self)
        clearBackupAction.setShortcut('Ctrl+X')
        clearBackupAction.triggered.connect(self.clearBackup)

        settingsMenu.addAction(changeKeyAction)
        settingsMenu.addAction(clearBackupAction)

    def changeKey(self):
        win = ChangeKeyWindow(self)
        win.show()
        win.exec_()

    def clearBackup(self):
        ret = QMessageBox.question(self, "提示", "是否清除所有备份")
        if ret != 16384:
            return
        clearBackup()
        QMessageBox.information(self, "提示", "已成功清除备份")

    def draw(self):
        # 图形
        self.setWindowTitle("密码管理器")
        self.resize(800, 600)

        layout = QHBoxLayout()

        layout.addWidget(self.platformMenu, 1)
        layout.addWidget(VLine())
        layout.addWidget(self.accountMenu, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def ensureKey(self):
        self.keyWindow.keyEditLine.setText("")
        if self.keyWindow.exec_() == QDialog.Accepted:  # 模态执行并等待关闭
            return [self.keyWindow.resultFlag, self.keyWindow.keyEditLine.text()]  # 返回验证结果
        return [False, ""]
