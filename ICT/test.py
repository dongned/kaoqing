import sys
import os

# ========= 关键修复：PyQt6 打包闪退 =========
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.path.join(
        base_path, "PyQt6", "Qt6", "plugins", "platforms"
    )

import json
import base64
import requests
from datetime import datetime, timedelta
from PyQt6 import QtCore, QtGui, QtWidgets

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


# ========= GUI ==========
APP_QSS = """
QWidget#appRoot {
    background: #F6F7F9;
    color: #1F2933;
    font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}
QFrame#headerCard, QFrame#toolbarCard, QFrame#tableCard {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-radius: 12px;
}
QLabel#appTitle {
    color: #1F2933;
    font-size: 20px;
    font-weight: 700;
}
QLabel#headerStatus, QLabel#sectionHint, QLabel#fieldLabel, QLabel#summaryTitle {
    color: #6B7280;
}
QLabel#tableTitle {
    color: #1F2933;
    font-size: 16px;
    font-weight: 600;
}
QLineEdit {
    min-height: 38px;
    padding: 0 12px;
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-radius: 8px;
    selection-background-color: #BFDBFE;
}
QLineEdit:focus {
    border: 1px solid #2563EB;
    background: #FCFDFF;
}
QCheckBox {
    color: #1F2933;
    spacing: 8px;
}
QPushButton#primaryButton {
    min-height: 38px;
    padding: 0 22px;
    color: #FFFFFF;
    background: #2563EB;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
QPushButton#primaryButton:hover {
    background: #1D4ED8;
}
QPushButton#primaryButton:pressed {
    background: #1E40AF;
}
QPushButton#primaryButton:disabled {
    background: #9CB7F4;
    color: #EEF2FF;
}
QFrame#summarySection {
    background: transparent;
}
QFrame#summaryPrimary, QFrame#summaryCard {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-radius: 10px;
}
QFrame#summaryPrimary {
    background: #EEF6FF;
    border-left: 4px solid #2563EB;
}
QLabel#summaryValue {
    color: #1F2933;
    font-size: 26px;
    font-weight: 700;
}
QLabel#messageLabel {
    padding: 10px 12px;
    border-radius: 8px;
}
QLabel#messageLabel[kind="empty"], QLabel#messageLabel[kind="loading"] {
    color: #536171;
    background: #F8FAFC;
    border: 1px solid #E8EDF2;
}
QLabel#messageLabel[kind="success"] {
    color: #166534;
    background: #ECFDF3;
    border: 1px solid #BBF7D0;
}
QLabel#messageLabel[kind="warning"] {
    color: #92400E;
    background: #FFFBEB;
    border: 1px solid #FDE68A;
}
QLabel#messageLabel[kind="error"] {
    color: #991B1B;
    background: #FEF2F2;
    border: 1px solid #FECACA;
}
QTableWidget {
    background: #FFFFFF;
    border: 1px solid #DDE3EA;
    border-radius: 10px;
    gridline-color: #EEF2F6;
    selection-background-color: #F5F9FF;
    selection-color: #1F2933;
    alternate-background-color: #FBFCFE;
}
QTableWidget::item {
    padding: 0 10px;
    border-bottom: 1px solid #EEF2F6;
}
QTableWidget::item:hover {
    background: #F5F9FF;
}
QHeaderView::section {
    min-height: 40px;
    padding: 0 18px;
    color: #536171;
    background: #F8FAFC;
    border: none;
    border-bottom: 1px solid #DDE3EA;
    font-size: 13px;
    font-weight: 600;
}
"""


class AttendanceWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(list)
    failed = QtCore.pyqtSignal(str)

    def __init__(self, emp_no: str, pwd: str):
        super().__init__()
        self.emp_no = emp_no
        self.pwd = pwd

    @QtCore.pyqtSlot()
    def run(self):
        try:
            session = requests.Session()

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

            resp = session.post(
                login_url,
                headers=headers_login,
                json={"empNo": self.emp_no, "password": encrypt_password(self.pwd)}
            )
            resp.raise_for_status()
            token = (resp.json().get("data") or {}).get("token")
            if not token:
                self.failed.emit("登录失败")
                return

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
            self.finished.emit(json.loads(et_data))
        except Exception as e:
            self.failed.emit(str(e))


class AttendanceApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.attendance_thread = None
        self.attendance_worker = None

        self.init_ui()

        home = os.path.expanduser("~")
        self.cred_path = os.path.join(
            home, "Library", "Application Support",
            "attendance_app", "credentials.json"
        )
        os.makedirs(os.path.dirname(self.cred_path), exist_ok=True)

        self.load_credentials()

    def init_ui(self):
        self.setObjectName("appRoot")
        self.setWindowTitle("加班计算器")
        self.resize(1040, 760)
        self.setMinimumSize(860, 640)
        self.setStyleSheet(APP_QSS)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(self.build_header())
        layout.addWidget(self.build_toolbar())
        layout.addWidget(self.build_summary_section())
        layout.addWidget(self.build_table_section(), 1)

        self.login_btn.clicked.connect(self.fetch_attendance)
        self.emp_input.returnPressed.connect(self.fetch_attendance)
        self.pwd_input.returnPressed.connect(self.fetch_attendance)

        self.show_empty_state("暂无考勤数据，请输入账号密码后获取考勤")

    def build_header(self):
        frame = QtWidgets.QFrame()
        frame.setObjectName("headerCard")
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QtWidgets.QLabel("加班计算器")
        title.setObjectName("appTitle")
        subtitle = QtWidgets.QLabel("考勤数据与加班时长汇总")
        subtitle.setObjectName("sectionHint")

        title_layout = QtWidgets.QVBoxLayout()
        title_layout.setSpacing(4)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.header_status_label = QtWidgets.QLabel(self.current_month_text())
        self.header_status_label.setObjectName("headerStatus")
        self.header_status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(title_layout)
        layout.addStretch(1)
        layout.addWidget(self.header_status_label)
        return frame

    def build_toolbar(self):
        frame = QtWidgets.QFrame()
        frame.setObjectName("toolbarCard")
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        account_label = QtWidgets.QLabel("账号")
        account_label.setObjectName("fieldLabel")
        self.emp_input = QtWidgets.QLineEdit()
        self.emp_input.setPlaceholderText("请输入账号")
        self.emp_input.setFixedWidth(220)

        password_label = QtWidgets.QLabel("密码")
        password_label.setObjectName("fieldLabel")
        self.pwd_input = QtWidgets.QLineEdit()
        self.pwd_input.setPlaceholderText("请输入密码")
        self.pwd_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pwd_input.setFixedWidth(220)

        self.remember_cb = QtWidgets.QCheckBox("记住密码")
        self.login_btn = QtWidgets.QPushButton("获取考勤")
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        layout.addWidget(account_label)
        layout.addWidget(self.emp_input)
        layout.addSpacing(4)
        layout.addWidget(password_label)
        layout.addWidget(self.pwd_input)
        layout.addWidget(self.remember_cb)
        layout.addStretch(1)
        layout.addWidget(self.login_btn)
        return frame

    def build_summary_section(self):
        frame = QtWidgets.QFrame()
        frame.setObjectName("summarySection")
        layout = QtWidgets.QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        total_card, self.total_value_label = self.build_summary_card("本月总加班", "0.0h", True)
        days_card, self.overtime_days_value_label = self.build_summary_card("加班记录", "0天")

        layout.addWidget(total_card)
        layout.addWidget(days_card)
        return frame

    def build_summary_card(self, title: str, value: str, primary: bool = False):
        card = QtWidgets.QFrame()
        card.setObjectName("summaryPrimary" if primary else "summaryCard")
        layout = QtWidgets.QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("summaryTitle")
        value_label = QtWidgets.QLabel(value)
        value_label.setObjectName("summaryValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card, value_label

    def build_table_section(self):
        frame = QtWidgets.QFrame()
        frame.setObjectName("tableCard")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        title_row = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("考勤明细")
        title.setObjectName("tableTitle")
        hint = QtWidgets.QLabel("表头固定，支持滚动查看")
        hint.setObjectName("sectionHint")
        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(hint)

        self.message_label = QtWidgets.QLabel()
        self.message_label.setObjectName("messageLabel")
        self.message_label.setWordWrap(True)

        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["日期", "班次", "状态", "上班时间", "下班时间", "加班时长"])
        header_alignments = [
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter,
            QtCore.Qt.AlignmentFlag.AlignCenter,
            QtCore.Qt.AlignmentFlag.AlignCenter,
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter,
        ]
        for column, alignment in enumerate(header_alignments):
            self.table.horizontalHeaderItem(column).setTextAlignment(alignment)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(42)
        header = self.table.horizontalHeader()
        header.setHighlightSections(False)
        header.setStretchLastSection(True)
        for column, width in enumerate([130, 260, 110, 110, 110, 120]):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.Interactive)
            self.table.setColumnWidth(column, width)

        layout.addLayout(title_row)
        layout.addWidget(self.message_label)
        layout.addWidget(self.table, 1)
        return frame

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
        if self.attendance_thread and self.attendance_thread.isRunning():
            return

        if is_expired():
            self.show_message("This application has expired! Please contact the publisher to obtain a new version.", "error")
            return

        emp_no = self.emp_input.text().strip()
        pwd = self.pwd_input.text()

        if not emp_no or not pwd:
            self.show_message("请输入账号和密码", "warning")
            return

        self.save_credentials()
        self.set_loading(True)

        self.attendance_thread = QtCore.QThread(self)
        self.attendance_worker = AttendanceWorker(emp_no, pwd)
        self.attendance_worker.moveToThread(self.attendance_thread)

        self.attendance_thread.started.connect(self.attendance_worker.run)
        self.attendance_worker.finished.connect(self.handle_attendance_loaded)
        self.attendance_worker.failed.connect(self.handle_attendance_failed)
        self.attendance_worker.finished.connect(self.attendance_thread.quit)
        self.attendance_worker.failed.connect(self.attendance_thread.quit)
        self.attendance_worker.finished.connect(self.attendance_worker.deleteLater)
        self.attendance_worker.failed.connect(self.attendance_worker.deleteLater)
        self.attendance_thread.finished.connect(self.cleanup_worker)
        self.attendance_thread.finished.connect(self.attendance_thread.deleteLater)
        self.attendance_thread.start()

    def handle_attendance_loaded(self, records: list):
        self.set_loading(False)
        self.populate_table(records)

    def handle_attendance_failed(self, message: str):
        self.set_loading(False)
        detail = f"：{message}" if message else ""
        self.show_message(f"获取失败，请检查账号、密码或网络连接{detail}", "error")
        self.header_status_label.setText(self.current_month_text())

    def cleanup_worker(self):
        self.attendance_thread = None
        self.attendance_worker = None

    def set_loading(self, is_loading: bool):
        self.login_btn.setEnabled(not is_loading)
        self.login_btn.setText("获取中..." if is_loading else "获取考勤")
        if is_loading:
            self.show_message("正在获取考勤...", "loading")
            self.header_status_label.setText("正在获取...")

    def show_message(self, message: str, kind: str):
        self.message_label.setText(message)
        self.message_label.setProperty("kind", kind)
        self.message_label.setVisible(True)
        self.message_label.style().unpolish(self.message_label)
        self.message_label.style().polish(self.message_label)

    def clear_message(self):
        self.message_label.clear()
        self.message_label.setVisible(False)

    def show_empty_state(self, message: str = "暂无考勤数据"):
        self.table.setRowCount(0)
        self.update_summary(0.0, 0)
        self.show_message(message, "empty")
        self.header_status_label.setText(self.current_month_text())

    def populate_table(self, records: list):
        self.table.setRowCount(0)
        if not records:
            self.show_empty_state()
            return

        total = 0.0
        overtime_days = 0
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            beg, end = get_work_times(record)
            overtime = calculate_overtime(record)
            status = self.display_status(record)
            total += overtime
            if overtime > 0:
                overtime_days += 1

            self.set_table_item(row, 0, self.format_date(record.get("KQ_DATE", "")))
            self.set_table_item(row, 1, record.get("BCLB", "") or "-")
            self.set_status_item(row, status)
            self.set_table_item(row, 3, beg or "-", QtCore.Qt.AlignmentFlag.AlignCenter)
            self.set_table_item(row, 4, end or "-", QtCore.Qt.AlignmentFlag.AlignCenter)
            self.set_table_item(row, 5, f"{overtime:.1f}h", QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter, bold=overtime > 0)
            self.table.setRowHeight(row, 42)

        self.update_summary(total, overtime_days)
        updated_at = datetime.now().strftime("%H:%M")
        self.show_message(f"已更新 {updated_at}", "success")
        self.header_status_label.setText(f"{self.current_month_text()} · 已更新 {updated_at}")

    def set_table_item(self, row: int, column: int, text: str, alignment=None, color=None, background=None, bold: bool = False):
        item = QtWidgets.QTableWidgetItem(str(text))
        item.setToolTip(str(text))
        item.setTextAlignment(alignment or (QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter))
        if color:
            item.setForeground(QtGui.QBrush(QtGui.QColor(color)))
        if background:
            item.setBackground(QtGui.QBrush(QtGui.QColor(background)))
        if bold:
            font = item.font()
            font.setBold(True)
            item.setFont(font)
        self.table.setItem(row, column, item)

    def set_status_item(self, row: int, status: str):
        color = "#8A94A6"
        background = "#F3F4F6"
        if "未出勤" in status or "异常" in status:
            color = "#D97706"
            background = "#FFF7ED"
        elif "出勤" in status:
            color = "#16A34A"
            background = "#ECFDF3"
        elif "休息" in status:
            color = "#8A94A6"
            background = "#F3F4F6"
        self.set_table_item(row, 2, status, QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter, color, background, True)

    def update_summary(self, total: float, overtime_days: int):
        self.total_value_label.setText(f"{total:.1f}h")
        self.overtime_days_value_label.setText(f"{overtime_days}天")

    def display_status(self, record: dict):
        status = (record.get("STAT_T", "") or "").strip()
        if status:
            return status
        if "休息" in (record.get("BCLB", "") or ""):
            return "休息"
        return "-"

    def format_date(self, raw_date):
        text = str(raw_date or "").strip()
        if len(text) == 8 and text.isdigit():
            try:
                return datetime.strptime(text, "%Y%m%d").strftime("%Y-%m-%d")
            except:
                return text
        return text or "-"

    def current_month_text(self):
        today = datetime.today()
        return f"{today.year}年{today.month}月"


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = AttendanceApp()
    win.show()
    sys.exit(app.exec())