import sys, json, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox, QLineEdit
)
from PyQt5.QtCore import QDateTime


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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec_())
