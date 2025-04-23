from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint,QDate
from PyQt5.QtGui import QPixmap,QTextCharFormat,QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMenu,QMessageBox, QMainWindow, QAction
from PyQt5.QtCore import QTimer,Qt,QUrl
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

import webbrowser
from PyQt5 import QtGui

import os
import sys
import random

import sys, json, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox, QLineEdit
)
from PyQt5.QtCore import QDateTime
import json # ✅ Import JSON for file storage
from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QCalendarWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QTextCharFormat, QColor


class CalendarPlanner(QWidget):  # ✅ 繼承 QWidget，確保關閉時不影響 Deskpet
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dochedual")
        self.setGeometry(100, 100, 500, 500)# Set window size

        # 🔹 Create UI elements
        self.layout = QVBoxLayout(self)

        # 📅 Calendar Widget
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.show_schedule)  # Display schedule when a date is clicked
        self.layout.addWidget(self.calendar)

        # ✅ Highlight today's date
        self.mark_today()

        # 📋 Schedule Table
        self.schedule_table = QTableWidget(0, 1, self)  # 1 column (Schedule)
        self.schedule_table.setHorizontalHeaderLabels(["Schedule"])
        self.layout.addWidget(self.schedule_table)

        # ➕ Input box & Add Button
        self.input_layout = QHBoxLayout()
        self.schedule_input = QLineEdit(self)
        self.schedule_input.setPlaceholderText("Enter schedule...")
        self.add_button = QPushButton("Add Schedule", self)
        self.add_button.clicked.connect(self.add_schedule)
        self.input_layout.addWidget(self.schedule_input)
        self.input_layout.addWidget(self.add_button)
        self.layout.addLayout(self.input_layout)

        # ❌ Delete Button
        self.delete_button = QPushButton("Delete Selected Schedule", self)
        self.delete_button.clicked.connect(self.delete_schedule)
        self.layout.addWidget(self.delete_button)

        # 📌 Dictionary to store schedules ({date: [schedule list]})
        self.schedule_data = {}

        # 📌 Load schedules from file
        self.schedule_data = self.load_schedule_data()
        
        # 🔹 Apply Styles
        self.apply_styles()
        

    def mark_today(self):
        """Highlight today's date"""
        today = QDate.currentDate()  # Get today's date
        highlight_format = QTextCharFormat()
        highlight_format.setForeground(QColor("red"))  # Set red text color
        highlight_format.setBackground(QColor(255, 220, 220))  # Light red background
        self.calendar.setDateTextFormat(today, highlight_format)

    def check_today_schedule(self):
        """檢查今天是否有行程"""
        try:
            with open("schedule_data.json", "r") as file:
                schedule_data = json.load(file)

            today = QDate.currentDate().toString("yyyy-MM-dd")  # 獲取今天日期

            return today in schedule_data  # ✅ 如果今天有行程，回傳 True，否則回傳 False

        except (FileNotFoundError, json.JSONDecodeError):
            return False  # ✅ 如果沒有行程檔案，回傳 False



    def show_schedule(self, date):
        """Display the schedule when a date is clicked"""
        selected_date = date.toString("yyyy-MM-dd")  # Format the date
        self.schedule_table.setRowCount(0)  # Clear table

        if selected_date in self.schedule_data:
            for event in self.schedule_data[selected_date]:
                row_position = self.schedule_table.rowCount()
                self.schedule_table.insertRow(row_position)
                self.schedule_table.setItem(row_position, 0, QTableWidgetItem(event))
    def highlight_date(self, date, highlight=True):
        """Change the color of a date when a schedule is added or removed"""
        today = QDate.currentDate()  # Get today's date
        date_format = QTextCharFormat()
        if date == today:
            date_format.setForeground(QColor("red"))
            date_format.setBackground(QColor(255, 220, 220))  # Light red background
        elif highlight:
            date_format.setForeground(QColor("blue"))  # Change text color to blue
            date_format.setBackground(QColor(200, 230, 255))  # Light blue background
        else:
            date_format.setForeground(QColor("black"))  # Restore default text color
            date_format.setBackground(QColor(255, 255, 255))  # Restore default background
        
        self.calendar.setDateTextFormat(date, date_format)
    def add_schedule(self):
        """Add a schedule to the selected date"""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        new_schedule = self.schedule_input.text().strip()

        if new_schedule:
            # Add schedule to dictionary
            if selected_date not in self.schedule_data:
                self.schedule_data[selected_date] = []
            self.schedule_data[selected_date].append(new_schedule)

            # Highlight the date
            self.highlight_date(self.calendar.selectedDate(), highlight=True)

            # Update UI
            row_position = self.schedule_table.rowCount()
            self.schedule_table.insertRow(row_position)
            self.schedule_table.setItem(row_position, 0, QTableWidgetItem(new_schedule))

            self.schedule_input.clear()  # Clear input box

            # ✅ Save to file
            self.save_schedule_data()

    def delete_schedule(self):
        """Delete selected schedule"""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_rows = self.schedule_table.selectionModel().selectedRows()

        for row in sorted(selected_rows, reverse=True):  # Delete in reverse order to avoid index errors
            item = self.schedule_table.item(row.row(), 0)
            if item:
                self.schedule_data[selected_date].remove(item.text())
            self.schedule_table.removeRow(row.row())
        # If no more schedules exist for the selected date, remove the highlight
        if selected_date in self.schedule_data and not self.schedule_data[selected_date]:
            del self.schedule_data[selected_date]  # Remove empty key
            self.highlight_date(self.calendar.selectedDate(), highlight=False)

        # ✅ Save to file
        self.save_schedule_data()
    
    def save_schedule_data(self):
        """Save the schedule data to a file"""
        with open("schedule_data.json", "w") as file:
            json.dump(self.schedule_data, file, indent=4)
    def closeEvent(self, event):
        """確保關閉行程視窗時，將變數設為 None，避免存取已刪除的物件"""
        print("行程視窗已關閉")  # ✅ Debug 訊息
        if hasattr(self.parent(), 'schedual'):  # ✅ 確保父類有 `schedual` 變數
            self.parent().schedual = None  # ✅ 將 `self.schedual` 設為 None，避免存取錯誤
        event.accept()  # ✅ 允許關閉

   
    def load_schedule_data(self):
        """Load schedule data from a file and highlight scheduled dates"""
        try:
            with open("schedule_data.json", "r") as file:
                self.schedule_data = json.load(file)

            # ✅ Highlight all saved schedule dates
            for date_str in self.schedule_data.keys():
                date = QDate.fromString(date_str, "yyyy-MM-dd")
                if date.isValid():  # ✅ 確保日期有效
                    self.highlight_date(date, highlight=True)

            return self.schedule_data

        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # Return empty dictionary if file does not exist


    def apply_styles(self):
        """Apply CSS styles to UI elements"""
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                background-color: rgb(255,245,250);  /* Light pink background */
                border: 2px solid rgb(255,153,204);  /* Pink border */
                border-radius: 10px;
                font-size: 14px;
                color: black;
            }
            QHeaderView::section {
                background-color: rgb(255,153,204);  /* Header background */
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                background-color: rgb(255,153,204);
            }
        """)

        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(255,153,204);  /* Pink background */
                color: white;  /* White text */
                font-size: 16px;  /* Text size */
                border-radius: 10px;  /* Rounded corners */
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgb(255,102,178);  /* Darker pink on hover */
            }
        """)

        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(255,153,204);  /* Pink background */
                color: white;
                font-size: 16px;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgb(255,102,178);
            }
        """)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     # ✅ 設定整個應用程式為英文
#     QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

#     window = CalendarPlanner()
#     window.show()
#     sys.exit(app.exec_())
#     # sys.exit(app.close())
#     # schedule_window = CalendarPlanner()
#     # schedule_window.exec_()  # ✅ This will keep it independent
#     # sys.exit(app.exec_())  # ✅ Keep the main app running




    



class NoteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📒 筆記系統")
        self.setGeometry(300, 300, 450, 550)

        self.notes_file = "notes.json"
        self.notes = self.load_notes()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🔸 分類選單
        self.category_box = QComboBox()
        self.category_box.addItems(["學習", "工作", "想法", "其他"])
        self.layout.addWidget(self.category_box)

        # 🔸 標題輸入欄
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("請輸入標題...")
        self.layout.addWidget(self.title_edit)

        # 🔸 筆記內容
        self.note_edit = QTextEdit()
        self.note_edit.setPlaceholderText("請輸入筆記內容...")
        self.layout.addWidget(self.note_edit)

        # 🔸 按鈕列
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("新增筆記")
        self.save_btn.clicked.connect(self.save_note)
        self.clear_btn = QPushButton("清除輸入")
        self.clear_btn.clicked.connect(self.clear_input)
        self.delete_btn = QPushButton("刪除筆記")
        self.delete_btn.clicked.connect(self.delete_note)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)
        self.update_btn = QPushButton("更新筆記")
        self.update_btn.clicked.connect(self.update_note)
        btn_layout.addWidget(self.update_btn)

        
      
        # 🔸 筆記列表
        self.note_list = QListWidget()
        self.layout.addWidget(self.note_list)
        self.note_list.itemClicked.connect(self.load_note_to_input)
        
        self.update_note_list()
        self.setStyleSheet(
            
            """
            background-color: rgb(255,245,250);  /* Light pink background */
                border: 2px solid rgb(255,153,204);  /* Pink border */
                border-radius: 10px;
                font-size: 14px;
                color: black;
        """)
        self.category_box.currentIndexChanged.connect(self.update_note_list)
    def load_note_to_input(self, item):
        note = item.data(1000)
        self.title_edit.setText(note.get("title", ""))
        self.note_edit.setPlainText(note.get("content", ""))
        category = note.get("category", "其他")
        index = self.category_box.findText(category)
        if index != -1:
            self.category_box.setCurrentIndex(index)

        # 儲存索引而非 note 本身
        for i, n in enumerate(self.notes):
            if n == note:
                self.selected_index = i
                break

    def update_note_list(self):
        self.note_list.clear()
        current_category = self.category_box.currentText()

        for note in self.notes:
            if current_category != "全部" and note["category"] != current_category:
                continue

            item = QListWidgetItem(note.get("title", "Untitled"))
            # 將整個筆記物件綁定到 item 上（方便點擊時讀取）
            item.setData(1000, note)  # 使用 Qt.UserRole = 1000
            self.note_list.addItem(item)



    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_note(self):
        content = self.note_edit.toPlainText().strip()
        title = self.title_edit.text().strip()
        if not content or not title:
            QMessageBox.warning(self, "提醒", "❗ 標題與內容都不能為空！")
            return

        note = {
            "title": title,
            "category": self.category_box.currentText(),
            "content": content,
            "timestamp": QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        }
        self.notes.append(note)
        self.save_notes_to_file()
        self.update_note_list()
        self.clear_input()

    def save_notes_to_file(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=4, ensure_ascii=False)

    # def update_note_list(self):
    #     self.note_list.clear()
    #     for note in self.notes:
    #         display = (
    #             f"📝 {note['title']}\n"
    #             f"[{note['category']}] {note['timestamp']}\n"
    #             f"{note['content']}"
    #         )
    #         item = QListWidgetItem(display)
    #         self.note_list.addItem(item)

    def delete_note(self):
        selected_items = self.note_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提醒", "請選擇要刪除的筆記")
            return

        selected_item = selected_items[0]
        note_to_delete = selected_item.data(1000)  # 直接取得筆記資料

        confirm = QMessageBox.question(
            self,
            "確認刪除",
            "確定要刪除這筆筆記嗎？",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # 在 notes 列表中尋找完全一樣的 note 並刪除
            self.notes = [note for note in self.notes if note != note_to_delete]

            self.save_notes_to_file()
            self.update_note_list()
            self.clear_input()


    def clear_input(self):
        self.title_edit.clear()
        self.note_edit.clear()
        self.category_box.setCurrentIndex(0)
    def update_note(self):
        if not hasattr(self, 'selected_index') or self.selected_index >= len(self.notes):
            QMessageBox.information(self, "提醒", "請先點選一筆要編輯的筆記")
            return

        title = self.title_edit.text().strip()
        content = self.note_edit.toPlainText().strip()
        category = self.category_box.currentText()
        if not title or not content:
            QMessageBox.warning(self, "提醒", "標題與內容不能為空！")
            return

        # 直接更新 notes 裡的資料
        self.notes[self.selected_index]["title"] = title
        self.notes[self.selected_index]["content"] = content
        self.notes[self.selected_index]["category"] = category
        self.notes[self.selected_index]["timestamp"] = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")

        self.save_notes_to_file()
        self.update_note_list()
        self.clear_input()




class TimerWindow(QDialog):
    """獨立的計時器視窗"""
    # timer_finished = pyqtSignal(bool)  
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(150, -70, 300, 200)
        
        self.layout = QVBoxLayout()
        self.timer_label = QLabel("PLS enter Time", self)
        self.timer_label.setFixedWidth(180)  # 設定固定寬度為 150 像素




        self.layout.addWidget(self.timer_label)

        self.input_box = QLineEdit(self)
        self.input_box.setStyleSheet("""
                                    QLineEdit {
                                        border: 2px solid rgb(255,153,204);  /* 邊框顏色 */
                                        border-radius: 8px;  /* 圓角 */
                                        padding: 5px;
                                        font-size: 16px;
                                        background-color: white;
                                    }
                                """)

        self.input_box.setPlaceholderText("enter time...")
        self.input_box.setFixedWidth(180)
        self.layout.addWidget(self.input_box)

        self.start_button = QPushButton("Start", self)
        self.start_button.setStyleSheet("""
                                        QPushButton {
                                            background-color: rgb(255,153,204);  /* 粉色背景 */
                                            color: white;  /* 文字顏色 */
                                            font-size: 16px;  /* 文字大小 */
                                            border-radius: 10px;  /* 圓角 */
                                            padding: 5px;
                                        }
                                        QPushButton:hover {
                                            background-color: rgb(255,102,178);  /* 滑鼠懸停時變深 */
                                        }
                                    """)

        self.start_button.setFixedWidth(180)  # 設定輸入框寬度為 100 像素
        self.start_button.clicked.connect(self.start_timer)
        self.layout.addWidget(self.start_button)

        self.setLayout(self.layout)

        self.remaining_time = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def start_timer(self):
        """開始倒數計時"""
        try:
            input_time = int(self.input_box.text().strip())  # 取得輸入的秒數
            if input_time <= 0:
                raise ValueError  # 確保輸入為正數
            self.remaining_time = input_time
            min_time=self.remaining_time//60
            s_time=self.remaining_time%60
            self.timer_label.setText(f"Time: {min_time:02d}:{s_time:02d} s")
            self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold;")  # ✅ 設定字體大小
            # ✅ 隱藏輸入框與按鈕
            self.input_box.hide()
            self.start_button.hide()
            print(f"[DEBUG] 計時開始，倒數 {self.remaining_time} 秒")
            self.timer.start(1000)  # 每秒更新一次
        except ValueError:
            QMessageBox.warning(self, "type error", "PLS check！")

    def update_timer(self):
        """更新倒計時"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            min_time=self.remaining_time//60
            s_time=self.remaining_time%60
            self.timer_label.setText(f"Time: {min_time:02d}:{s_time:02d} s")
            self.timer_label.setStyleSheet("font-size: 32px; font-weight: bold;")  
        else:
            self.timer_label.setText("Time out！")
            self.timer.stop()  # 停止計時器
            # ✅ 播放聲音
            self.player = QMediaPlayer()
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile("doro.mp3")))  # 指定音效檔案
            self.player.setVolume(50)  # 設定音量 (0~100)
            self.player.play()
            
           # ✅ 等待 10 秒後自動關閉視窗,,
            QTimer.singleShot(4000, lambda: (self.close(), self.input_box.show(), self.start_button.show()))  # ✅ 正確

class Deskpet(QWidget):
    tool_name = 'Doro'

    def __init__(self, parent=None, **kwargs):
        super(Deskpet, self).__init__(parent)
        self.clocktimer=QTimer
        # Pet counters
        self.against=0
        self.stop=False
        self.sleep_counter = 0
        self.dark_counter = 0
        self.death_counter=0
        self.nope_counter=0
        self.timer_counter=0
        self.animation_type = 'walk'  # animation type

        # window for invisible
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint )
        # | Qt.SubWindow
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(900, 900)



        # init load
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True) 
         # 自動縮放圖片以適應窗口大小

        # 加載圖片
        self.frames = self.load_frames("img")  # 替換為你的動畫圖片文件夾路徑
        self.current_frame = 0

        # 設置定時器進行動畫切換
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)  # 每 100 毫秒更新一幀

        # 定時器用於桌寵移動
        self.timer_move = QTimer(self)
        
        self.timer_move.timeout.connect(self.random_move)
        self.timer_move.start(2000)  # 每2秒移動一次

       # ✅ 檢查今天是否有行程
        self.schedule_manager = CalendarPlanner()  # ✅ 創建行程管理器
        if self.schedule_manager.check_today_schedule():
            self.mark_with_green_dot()  # ✅ 如果有行程，顯示綠點

    def mark_with_green_dot(self):
        """在 Deskpet 上顯示一個小綠點"""
        self.dot_label = QLabel(self)
        self.dot_label.setGeometry(40, 10, 20, 20)  # ✅ 設置綠點位置 (右上角)
        self.dot_label.setStyleSheet("background-color: green; border-radius: 10px;")  # ✅ 圓形綠點
        self.dot_label.show()  


    def start_timer(self):
        """開始倒數計時"""
        try:
            input_time = int(self.input_box.text())  # 取得輸入的秒數
            if input_time <= 0:
                raise ValueError  # 確保輸入為正數
            self.remaining_time = input_time
            self.timer_label.setText(f"剩餘時間: {self.remaining_time} 秒")
            self.clocktimer.start(1000)  # 每秒更新一次
        except ValueError:
            QMessageBox.warning(self, "輸入錯誤", "請輸入有效的正整數！")

    def update_timer(self):
        """更新倒計時"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.setText(f"剩餘時間: {self.remaining_time} 秒")
        else:
            self.timer_label.setText("時間到！")
            self.clocktimer.stop()  # 停止計時器
    
    def load_frames(self, folder):
        """加載所有動畫類型的幀"""
        frames = {
            'walk': [],
            'dark': [],
            'death': [],
            'sleep': [],
            'death':[],
            'Nope':[],
            'Timer':[]
        }

        animation_types = ['walk', 'dark', 'death', 'sleep','death','Nope','Timer']
        for animation in animation_types:
            animation_folder = os.path.join(folder, animation)
            num_of_frames = len(os.listdir(animation_folder))-1
            for i in range(num_of_frames):
                path = os.path.join(animation_folder, f"0{i}.png")
                if os.path.exists(path):
                    pixmap = QPixmap(path)
                    scaled_pixmap = pixmap.scaled(
                        pixmap.width() * 4, pixmap.height() * 4, Qt.KeepAspectRatio
                    )
                    frames[animation].append(scaled_pixmap)
                else:
                    print(f"圖片未找到: {path}")
        return frames

    def animation_types(self):
        """更新當前的動畫類型"""
        if self.timer_counter>0:
            self.animation_type ='Timer'
            return
        if self.nope_counter > 0:
            self.sleep_counter=0
            self.dark_counter=0
            self.nope_counter -= 1
            self.animation_type = 'Nope'
            return
        if self.death_counter > 0:
            self.death_counter -= 1
            self.animation_type = 'death'
            return
        if self.sleep_counter > 0:
            self.sleep_counter -= 1
            self.animation_type = 'sleep'
            return
        if self.dark_counter > 0:
            self.dark_counter -= 1
            self.animation_type = 'dark'
            return
        
        # 隨機選擇動畫類型
        if random.randint(1, 200) == 2:
            self.animation_type = 'sleep'
            self.sleep_counter = 40
        elif random.randint(1, 100) == 1:
            self.animation_type = 'dark'
            self.dark_counter = 60
        else:
            self.animation_type = 'walk'
    def update_frame(self):
        
        """切換到下一幀"""
        # 獲取當前動畫類型的幀列表
        current_frames = self.frames.get(self.animation_type, [])
        self.animation_types()  # 更新動畫類型
        if not current_frames:  # 如果列表為空
            print(f"動畫類型 {self.animation_type} 沒有可用幀")
            return

        # 確保索引不超出範圍
        if self.current_frame >= len(current_frames):
            self.current_frame = 0

        # 更新圖片
        self.image_label.setPixmap(current_frames[self.current_frame])
        self.image_label.resize(current_frames[self.current_frame].size())

        # 更新幀索引
        self.current_frame += 1

    def mousePressEvent(self, event):
        """支持滑鼠拖動"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()  # 記錄鼠標位置

    def mouseMoveEvent(self, event):
        """拖動窗口"""
       
        if hasattr(self, "old_pos") and self.old_pos is not None:
                delta = event.globalPos() - self.old_pos
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_pos = event.globalPos()  # 更新舊位置
                self.against+=1
        
            

    def mouseReleaseEvent(self, event):
        """釋放滑鼠"""
        if event.button() == Qt.LeftButton:
            self.animation_type = 'Nope'  # 切換動畫類型為 'death'
            self.current_frame = 0  # 重置動畫幀索引，從頭開始播放動畫
            self.nope_counter=30
            self.old_pos = None 
            
            self.move(self.x() , self.y() )#反抗
            self.against-=1 # 清空舊位置
    # def mousePressEvent(self, event): 這樣會沒辦法拉
    #     """左鍵按下事件"""
    #     if event.button() == Qt.LeftButton:  # 檢查是否是左鍵
    #         print("e04")  # Debug 信息
    #         self.animation_type = 'death'  # 切換動畫類型為 'death'
    #         self.current_frame = 0  # 重置動畫幀索引，從頭開始播放動畫
        

    def open_website(self):
        """用默認瀏覽器打開網站"""
        url = "https://github.com/howardpaiM11115054/Doro_desktoppet_exe.git"  # 替換為您的網站連結
        webbrowser.open(url)
    def contextMenuEvent(self, event):
        """右鍵菜單事件"""
        # 創建一個 QMenu
        self.setStyleSheet("QMenu{background:rgb(255,102,204);margin: 0;padding: 5px;border-radius: 20px;}"
                           "QMenu::item{background:rgb(255,189,255);}"
                           "QMenu::separator{height:9px}"
                           "QMenu::separator{border-radius: 10px}"
                           )
        menu = QMenu(self)
        

        # 添加操作（QAction）
        action_exit = menu.addAction("EXIT")  # 添加一個 "退出" 選項
        action_kill = menu.addAction("Kill") 
        action_stop = menu.addAction("Stop")
        action_move = menu.addAction("Move")
        action_timer=menu.addAction("time")
        action_link = menu.addAction("github")
        action_schedual = menu.addAction("schedual")
        action_note = menu.addAction("NOTE")

        # 為 action_link 綁定觸發事件
        action_link.triggered.connect(self.open_website)
        #set icon
        '''add a label'''
        path_kill=os.path.join('img','icon','Kill.png')
        action_kill.setIcon(QtGui.QIcon(path_kill))
        path_exit=os.path.join('img','icon','Exit.png')
        action_exit.setIcon(QtGui.QIcon(path_exit))
        path_stop=os.path.join('img','icon','Stop.png')
        action_stop.setIcon(QtGui.QIcon(path_stop))
        path_move=os.path.join('img','icon','Move.png')
        action_move.setIcon(QtGui.QIcon(path_move))
        path_link=os.path.join('img','icon','GitHub.png')
        action_link.setIcon(QtGui.QIcon(path_link))
        path_timer=os.path.join('img','icon','Timer.png')
        action_timer.setIcon(QtGui.QIcon(path_timer))
        path_Dochedual=os.path.join('img','icon','Dochedual.png')
        action_schedual.setIcon(QtGui.QIcon(path_Dochedual))


        # 在鼠標位置顯示菜單
        action = menu.exec_(self.mapToGlobal(event.pos()))
        
        # 判斷選擇的選項
        if action == action_note:
            self.open_note()
        if action == action_move:
            self.stop=False
        if action == action_stop:
            self.stop=True
        if action ==action_kill:
            self.animation_type = 'death'  # 切換動畫類型為 'death'
            self.current_frame = 0  # 重置動畫幀索引，從頭開始播放動畫
            self.death_counter=50
            # self.update_frame()
        if action == action_exit:
            self.close() 
            sys.exit(app.exec_()) # 如果選擇了 "退出"，則關閉窗口
        if action == action_timer:
           self.animation_type='Timer'
           self.timer_counter=1
           self.stop=True
           self.open_timer_window()
        if action == action_schedual:
            self.open_schedual()
          

    def open_timer_window(self):
        """打開計時器視窗，確保計時結束時恢復桌寵運行"""
        if not hasattr(self, "timer_window") or self.timer_window is None:
            self.timer_window = TimerWindow(self)

        # ✅ 監聽 `finished` 事件，而不是 `destroyed`
        self.timer_window.finished.connect(self.on_timer_window_closed)

        self.stop = True  # 停止桌寵
        self.timer_window.show()
    def open_schedual(self):
        """Open the schedule window separately"""
        self.schedual = CalendarPlanner()
        self.schedual.show()  # ✅ Use show() instead of exec_()
    # def open_schedual(self):
    # """開啟行程視窗，確保 Deskpet 不會跟著關閉"""
    
    # # ✅ 如果 `self.schedual` 存在但已被刪除，就重新創建
    # if hasattr(self, 'schedual') and self.schedual is not None:
    #     if not self.schedual.isVisible():
    #         self.schedual = schedual_EN_doro.CalendarPlanner()  # ✅ 重新創建新視窗
    #         self.schedual.setAttribute(Qt.WA_DeleteOnClose, True)  # ✅ 關閉時刪除物件
    #         self.schedual.show()
    #     else:
    #         self.schedual.activateWindow()  # ✅ 視窗還在時，讓它浮到最前
    # else:
    #     self.schedual = schedual_EN_doro.CalendarPlanner()  # ✅ 創建新視窗
    #     self.schedual.setAttribute(Qt.WA_DeleteOnClose, True)
    #     self.schedual.show()
    def open_note(self):
        """開啟筆記視窗，只開一個"""
    
        self.note = NoteApp()
        self.note.setAttribute(Qt.WA_DeleteOnClose, True)  # 關閉時自動清理
        self.note.show()
    



    def on_timer_window_closed(self):
        """當計時器視窗關閉時，恢復桌寵運行"""
        print("[DEBUG] 計時視窗已關閉，桌寵恢復移動")
        self.stop = False  # 恢復桌寵移動
        self.timer_counter=0
        print(f"[DEBUG] self.stop 設定為: {self.stop}")  # 確認 stop 狀態

    

    def random_move(self):
        """讓桌寵隨機移動，並確保計時視窗始終位於其正下方"""
        
        if self.stop is False and self.animation_type == 'walk':
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()

            # 計算桌寵新位置
            new_x = random.randint(0, screen_width - self.width())
            new_y = random.randint(0, screen_height - self.height())

           

            # 設定桌寵移動動畫
            self.animation = QPropertyAnimation(self, b"pos")
            self.animation.setDuration(2000)
            self.animation.setEndValue(QPoint(new_x, new_y))
            self.animation.start()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # ✅ 創建主應用視窗
    
    # 創建 Deskpet 實例
    pet = Deskpet()
    pet.show()

    sys.exit(app.exec_())
