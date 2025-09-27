import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QToolButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class TranslatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần mềm dịch thuật")
        self.resize(700, 450)

        main_layout = QVBoxLayout()

        # Tiêu đề
        title = QLabel("Phần mềm dịch thuật")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Ô nhập
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Nhập văn bản cần dịch...")
        main_layout.addWidget(self.input_text)

        # HBox cho ngôn ngữ và nút dịch
        lang_layout = QHBoxLayout()

        self.lang_src = QComboBox()
        self.lang_src.addItems(["Tiếng Anh", "Tiếng Việt", "Tiếng Nhật", "Tiếng Trung"])
        lang_layout.addWidget(self.lang_src)

        # Nút đảo ngôn ngữ
        self.swap_btn = QPushButton("↔")
        self.swap_btn.setFixedWidth(40)
        lang_layout.addWidget(self.swap_btn)

        self.lang_dst = QComboBox()
        self.lang_dst.addItems(["Tiếng Việt", "Tiếng Anh", "Tiếng Nhật", "Tiếng Trung"])
        lang_layout.addWidget(self.lang_dst)

        # Nút dịch
        self.translate_btn = QPushButton("Dịch")
        lang_layout.addWidget(self.translate_btn)

        main_layout.addLayout(lang_layout)

        # HBox cho kết quả + loa
        result_layout = QHBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Kết quả dịch sẽ hiện ở đây...")
        result_layout.addWidget(self.output_text)

        # Nút loa (biểu tượng speaker)
        self.speaker_btn = QToolButton()
        self.speaker_btn.setIcon(QIcon.fromTheme("audio-volume-high"))  # Dùng icon hệ thống
        self.speaker_btn.setText("🔊")  # fallback nếu không có icon
        self.speaker_btn.setToolTip("Nghe kết quả dịch")
        result_layout.addWidget(self.speaker_btn)

        main_layout.addLayout(result_layout)

        self.setLayout(main_layout)
        # Nút đảo ngôn ngữ
        self.swap_btn = QPushButton("↔")
        self.swap_btn.setFixedWidth(40)
        lang_layout.addWidget(self.swap_btn)

        self.lang_dst = QComboBox()
        self.lang_dst.addItems(["Tiếng Việt", "Tiếng Anh", "Tiếng Nhật", "Tiếng Trung"]) # (nữa bổ sung thêm)
        lang_layout.addWidget(self.lang_dst)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorUI()
    window.show()
    sys.exit(app.exec())
