import sys
import json
import hashlib
import uuid
import os
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# 硬编码配置
APPID = "8888"  # 硬编码APPID
BUY_URL = "https://example.com/buy"  # 购卡地址
NOTICE = "公告：请购买正版卡密激活软件"  # 公告内容
TGID = "7ca21f108a70f132358e0d849fb7ef48"  # 推广ID

class ActivationUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化机器码
        self.machine_code = self.generate_machine_code()
        
        # 检查是否已激活
        self.activated = self.check_activation()
        if self.activated:
            self.run_app()
            sys.exit(0)
        # 主窗口设置
        self.setWindowTitle("软件激活")
        self.setFixedSize(400, 250)
        
        # 主部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 公告栏
        self.notice_label = QLabel(NOTICE)
        self.notice_label.setAlignment(Qt.AlignCenter)
        self.notice_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #333;
                margin-bottom: 10px;
            }
        """)
        
        # 卡密输入框
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("请输入卡密")
        self.key_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                margin: 0 30px 20px 30px;
            }
        """)
        
        # 激活按钮
        self.activate_btn = QPushButton("激活软件")
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                margin: 0 30px 10px 30px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # 购买按钮
        self.buy_btn = QPushButton("购买卡密")
        self.buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                margin: 0 30px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        
        # 添加到布局
        layout.addWidget(self.notice_label)
        layout.addWidget(self.key_input)
        layout.addWidget(self.activate_btn)
        layout.addWidget(self.buy_btn)
        
        # 应用扁平化样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
        # 连接按钮信号
        self.activate_btn.clicked.connect(self.on_activate_clicked)
        self.buy_btn.clicked.connect(lambda: os.startfile(BUY_URL))
    
    def generate_machine_code(self):
        """生成机器码: MAC地址 + APPID 的MD5哈希"""
        mac = uuid.getnode()
        combined = f"{mac}{APPID}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get_optimal_api(self):
        """获取最优API地址"""
        try:
            response = requests.get("https://api.apihz.cn/getapi.php")
            data = response.json()
            if data.get("code") == 200:
                return data["api"]
        except Exception:
            pass
        return None
    
    def check_cdk(self, cdk):
        """查询卡密状态"""
        api = self.get_optimal_api()
        if not api:
            return None
            
        url = f"{api}api/tuoguan/getpost.php?url={api}api/user/cdkq1.php&type=1&tgid={TGID}&dc=cdk={cdk}"
        try:
            response = requests.post(url)
            return response.json()
        except Exception:
            return None
    
    def activate_cdk(self, cdk):
        """激活卡密"""
        api = self.get_optimal_api()
        if not api:
            return False
            
        url = f"{api}api/tuoguan/getpost.php?url={api}api/user/cdksy.php&type=1&tgid={TGID}&dc=cdk={cdk}>msg1={APPID}>msg2={self.machine_code}"
        try:
            response = requests.post(url)
            data = response.json()
            return data.get("code") == 200
        except Exception:
            return False
    
    def save_activation_info(self, cdk):
        """保存激活信息到文件"""
        data = {
            "cdk": cdk,
            "appid": APPID,
            "machine_code": self.machine_code
        }
        user_dir = os.path.expanduser("~")
        key_path = os.path.join(user_dir, f"{APPID}.key")
        with open(key_path, "w") as f:
            json.dump(data, f)
    
    def check_activation(self):
        """检查本地激活状态"""
        try:
            user_dir = os.path.expanduser("~")
            key_path = os.path.join(user_dir, f"{APPID}.key")
            if not os.path.exists(key_path):
                return False
                
            with open(key_path, "r") as f:
                data = json.load(f)
                
            # 验证卡密状态
            cdk_data = self.check_cdk(data["cdk"])
            if not cdk_data or cdk_data.get("code") != 200:
                return False
                
            # 检查卡密是否已使用且信息匹配
            cdk_info = cdk_data.get("data", {})
            if (cdk_info.get("status") == "1" and
                cdk_info.get("msg1") == data["appid"] and
                cdk_info.get("msg2") == data["machine_code"]):
                return True
            return False
        except Exception:
            return False
    
    def run_app(self):
        """运行主程序"""
        try:
            os.startfile("app.exe")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法启动应用程序: {str(e)}")
    
    def on_activate_clicked(self):
        """激活按钮点击事件"""
        cdk = self.key_input.text().strip()
        if not cdk:
            QMessageBox.warning(self, "提示", "请输入卡密")
            return
            
        # 查询卡密状态
        cdk_data = self.check_cdk(cdk)
        if not cdk_data:
            QMessageBox.critical(self, "错误", "网络错误，请重试")
            return
            
        if cdk_data.get("code") != 200:
            QMessageBox.critical(self, "错误", "卡密错误，请联系管理员")
            return
            
        cdk_info = cdk_data.get("data", {})
        if cdk_info.get("status") == "0":
            # 卡密未使用，尝试激活
            if self.activate_cdk(cdk):
                self.save_activation_info(cdk)
                QMessageBox.information(self, "成功", "激活成功")
                self.run_app()
                sys.exit(0)
            else:
                QMessageBox.critical(self, "错误", "激活失败，请重试")
        elif cdk_info.get("status") == "1":
            # 卡密已使用，检查是否匹配
            if (cdk_info.get("msg1") == APPID and
                cdk_info.get("msg2") == self.machine_code):
                self.save_activation_info(cdk)
                QMessageBox.information(self, "成功", "验证通过")
                self.run_app()
                sys.exit(0)
            else:
                QMessageBox.critical(self, "错误", "卡密已被其他设备使用")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序图标
    if hasattr(sys, '_MEIPASS'):
        # 打包后模式
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")
    else:
        # 开发模式
        icon_path = "icon.ico"
        
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = ActivationUI()
    window.show()
    sys.exit(app.exec())