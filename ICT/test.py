import sys
import os

# ========= 关键修复：PyQt6 打包闪退 =========
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
        base_path, "PyQt6", "Qt6", "plugins", "platforms"
    )
    # WebEngine 进程路径修复（macOS PyInstaller 打包必需）
    os.environ["QTWEBENGINEPROCESS_PATH"] = os.path.join(
        base_path, "PyQt6", "Qt6", "libexec", "QtWebEngineProcess"
    )
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

import json
import base64
import requests
from datetime import datetime, timedelta
from PyQt6 import QtWidgets
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# ========= 使用期限 ==========
EXPIRY_DATE = datetime(2026, 12, 31)

def is_expired():
    return datetime.today() > EXPIRY_DATE

# ========= 密码加密 ==========
def encrypt_password(plain_password: str) -> str:
    return base64.b64encode(plain_password.encode("utf-8")).decode("utf-8")

def decrypt_password(enc_password: str) -> str:
    return base64.b64decode(enc_password.encode()).decode()

# ========= 时间工具 ==========
def parse_time_safe(t: str):
    try:
        return datetime.strptime(t, "%H:%M")
    except:
        return None

def hours_between(start: datetime, end: datetime) -> float:
    return max((end - start).total_seconds() / 3600.0, 0.0)

def calc_overlap(start, end, b_start, b_end) -> float:
    latest = max(start, b_start)
    earliest = min(end, b_end)
    return max((earliest - latest).total_seconds() / 3600.0, 0.0)

def floor_half_hour(hours: float) -> float:
    return int(hours / 0.5) * 0.5

def extract_times(ysdk: str):
    if not ysdk:
        return []
    for sep in [",", "\n", "\t"]:
        ysdk = ysdk.replace(sep, " ")
    parts = ysdk.split()
    return [p.strip() for p in parts if ":" in p]

def get_work_times(record):
    ysdk = record.get("YSDK", "")
    times = extract_times(ysdk)
    if len(times) < 2:
        return "", ""
    try:
        return min(times), max(times)
    except:
        return "", ""

# ========= 修复后的加班计算 ==========
def calculate_overtime(record: dict) -> float:
    beg, end = get_work_times(record)
    if not beg or not end:
        return 0.0

    beg_t = parse_time_safe(beg)
    end_t = parse_time_safe(end)
    if not beg_t or not end_t:
        return 0.0

    # ✅ 只处理跨天
    if end_t < beg_t:
        end_t += timedelta(days=1)

    bclb = record.get("BCLB", "")
    pdate = record.get("PDATE", "")

    is_offday = "休息" in bclb

    # ===== 非工作日 =====
    if is_offday:
        overtime = hours_between(beg_t, end_t)

        overtime -= calc_overlap(
            beg_t, end_t,
            parse_time_safe("12:00"), parse_time_safe("13:00")
        )
        overtime -= calc_overlap(
            beg_t, end_t,
            parse_time_safe("17:30"), parse_time_safe("18:30")
        )

        return floor_half_hour(max(overtime, 0.0))

    # ===== 工作日 =====
    try:
        std_end = parse_time_safe(pdate.split("-")[1])
        if not std_end:
            return 0.0
    except:
        return 0.0

    # ✅ 修复：早退直接无加班
    if end_t <= std_end:
        return 0.0

    overtime = hours_between(std_end, end_t)

    overtime -= calc_overlap(
        std_end, end_t,
        parse_time_safe("17:30"), parse_time_safe("18:30")
    )

    # 防异常
    overtime = min(overtime, 12)

    return floor_half_hour(max(overtime, 0.0))


# ========= 广告配置 ==========
# 桌面应用不嵌入 AdSense，横幅仅用于展示站内推广内容。
AD_URL = "https://dongned.github.io/ad.html"
# 横幅加载失败时显示的本地备用 HTML
AD_FALLBACK_HTML = """
<html><body style="margin:0;padding:0;display:flex;align-items:center;justify-content:center;
height:100%;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#475569;font-size:13px;">
<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:space-between;
padding:14px 18px;border:1px solid #dbeafe;background:linear-gradient(135deg,#eff6ff,#f8fafc 62%,#ecfdf5);">
<div><strong style="display:block;color:#1d4ed8;font-size:16px;margin-bottom:4px;">Dong's Tools</strong>
<span>获取加班计算器最新版本、使用说明和计算规则</span></div>
<span style="padding:8px 12px;border-radius:6px;color:#fff;background:#2563eb;font-weight:600;">打开官网</span>
</div></body></html>
"""

# ========= GUI ==========
class AttendanceApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("加班计算器")
        self.resize(700, 600)

        layout = QtWidgets.QVBoxLayout(self)

        form_layout = QtWidgets.QFormLayout()
        self.emp_input = QtWidgets.QLineEdit()
        self.pwd_input = QtWidgets.QLineEdit()
        self.pwd_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.remember_cb = QtWidgets.QCheckBox("记住密码")

        form_layout.addRow("账号:", self.emp_input)
        form_layout.addRow("密码:", self.pwd_input)
        form_layout.addRow("", self.remember_cb)
        layout.addLayout(form_layout)

        self.login_btn = QtWidgets.QPushButton("获取考勤")
        layout.addWidget(self.login_btn)

        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        # ===== 广告横幅 =====
        self.ad_view = QWebEngineView()
        self.ad_view.setFixedHeight(90)
        self.ad_view.loadFinished.connect(self.handle_ad_load_finished)
        self.ad_view.setHtml(AD_FALLBACK_HTML, QUrl("https://dongned.github.io/"))
        self.ad_view.load(QUrl(AD_URL))
        layout.addWidget(self.ad_view)

        self.login_btn.clicked.connect(self.fetch_attendance)

        home = os.path.expanduser("~")
        self.cred_path = os.path.join(
            home, "Library", "Application Support",
            "attendance_app", "credentials.json"
        )
        os.makedirs(os.path.dirname(self.cred_path), exist_ok=True)

        self.load_credentials()

    def handle_ad_load_finished(self, ok: bool):
        if not ok:
            self.ad_view.setHtml(AD_FALLBACK_HTML, QUrl("https://dongned.github.io/"))

    def load_credentials(self):
        if os.path.exists(self.cred_path):
            try:
                with open(self.cred_path, "r") as f:
                    data = json.load(f)
                    self.emp_input.setText(data.get("emp", ""))
                    enc_pwd = data.get("pwd", "")
                    if enc_pwd:
                        self.pwd_input.setText(decrypt_password(enc_pwd))
                        self.remember_cb.setChecked(True)
            except:
                pass

    def save_credentials(self):
        if self.remember_cb.isChecked():
            with open(self.cred_path, "w") as f:
                json.dump({
                    "emp": self.emp_input.text(),
                    "pwd": encrypt_password(self.pwd_input.text())
                }, f)
        else:
            if os.path.exists(self.cred_path):
                os.remove(self.cred_path)

    def fetch_attendance(self):
        # ===== 过期控制 =====
        if is_expired():
            self.output.clear()
            #self.output.append("本应用已过期，请联系发布者获取新版本")
            self.output.append("This application has expired! Please contact the publisher to obtain a new version.")
            return

        self.output.clear()

        emp_no = self.emp_input.text()
        pwd = self.pwd_input.text()

        if not emp_no or not pwd:
            self.output.append("请输入账号和密码")
            return

        self.save_credentials()
        session = requests.Session()

        # 登录
        login_url = "https://mhr.test.com/hrc-extranet-service/hrc-cert-service/user/login"
        headers_login = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "hrc-entrance-type": "MOBILE",
            "hrc-lang": "ZH-CN",
            "hrc-page-code": "LOGIN",
            "hrc-sys-code": "HRC-PORTAL-SERVICE",
            "origin": "https://mhr.test.com",
            "referer": "https://mhr.l test.com/portal-mobile/login",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0)"
        }

        try:
            resp = session.post(
                login_url,
                headers=headers_login,
                json={"empNo": emp_no, "password": encrypt_password(pwd)}
            )
            resp.raise_for_status()
            token = (resp.json().get("data") or {}).get("token")
            if not token:
                self.output.append("登录失败")
                return
        except Exception as e:
            self.output.append(f"登录异常: {e}")
            return

        # 获取考勤
        today = datetime.today()
        begda = today.replace(day=1).strftime("%Y%m%d")
        endda = today.strftime("%Y%m%d")

        attend_url = "https://mhr.test.com/hrc-extranet-service/hrc-sap-service/teamAttend/myAttend"
        headers_attend = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "hrc-authorization-token": token,
            "hrc-entrance-type": "MOBILE",
            "hrc-lang": "ZH-CN",
            "hrc-page-code": "MY-ATTENDANCE",
            "hrc-sys-code": "HRC-PORTAL-SERVICE",
            "origin": "https://mhr.test.com",
            "referer": "https://mhr.test.com/portal-mobile/home/my-attendance",
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0)"
        }

        try:
            resp = session.post(
                attend_url,
                headers=headers_attend,
                json={"IV_STAT": "", "IV_ERROR": "", "IV_BEGDA": begda, "IV_ENDDA": endda}
            )
            resp.raise_for_status()

            et_data = next(
                x["value"] for x in resp.json().get("data", [])
                if x.get("pname") == "ET_DATA"
            )
            records = json.loads(et_data)

        except Exception as e:
            self.output.append(f"获取考勤失败: {e}")
            return

        total = 0.0
        self.output.append("日期\t班次\t状态\t上班\t下班\t加班")

        for r in records:
            beg, end = get_work_times(r)
            ot = calculate_overtime(r)
            total += ot

            stat = r.get("STAT_T", "").strip() or "-"

            self.output.append(
                f"{r.get('KQ_DATE','')}\t"
                f"{r.get('BCLB','')}\t"
                f"{stat}\t"
                f"{beg or '-'}\t"
                f"{end or '-'}\t"
                f"{ot}h"
            )

        self.output.append(f"\n总加班时长: {total}h")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AttendanceApp()
    win.show()
    sys.exit(app.exec())
