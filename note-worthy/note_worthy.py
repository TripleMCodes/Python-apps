#===============================================================Note Worthy=====================================================================
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import (
                                QApplication,
                                QWidget,QPushButton,
                                QVBoxLayout, QHBoxLayout,
                                QTextEdit, QPushButton,
                                QFileDialog,QMessageBox,
                                QLabel,QComboBox,
                                QLineEdit,QTextBrowser
                                )
from PySide6.QtGui import QFont,QIcon
from pathlib import Path
from markdown import markdown
import shelve
import nltk
from nltk.corpus import wordnet
import sys
import json


# Download WordNet if not already downloaded
nltk.download('wordnet')

CONFIG_FILE = "config.json"  # File to store user preferences


class NoteWorthy(QWidget):
    def __init__(self):
        super().__init__()

       
#===============================================================Main Layout=====================================================================
        self.main_layout = QHBoxLayout(self)
        self.setGeometry(100, 100, 600, 400)
        # self.setMinimumHeight(600)  
        self.setWindowTitle("Note Worthy")  
        self.setWindowIcon(QIcon("./my_icon.ico"))
#===============================================================================================================================================
#================================================================Text box=======================================================================
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self.update_word_count)
        self.text_edit.textChanged.connect(self. _md_formatter)
        self.text_edit.textChanged.connect(self._restart_timer)
        self.text_edit.setPlaceholderText("Type your notes here...")

        self.preview = QTextBrowser()      
        self.md_mode = False

        self.previous_text = True

        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self._autosave)

#===============================================================================================================================================
#================================================================Sidebar Widget=================================================================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)  # Default width
        self.sidebar.setStyleSheet("background-color: #333;")
#===============================================================================================================================================#===============================================================word count label===========================================================
        self.word_count_label = QLabel("Words: 0", self)
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.text_edit)   
        self.v_layout.addWidget(self.word_count_label)
#===============================================================================================================================================
#===============================================================Dictionary======================================================================
        self.word_input = QLineEdit(self)
        self.word_input.setPlaceholderText("Enter a word for definition...")

        self.search_button = QPushButton("Get Definition", self)
        self.search_button.clicked.connect(self.get_definition)

        self.definition_output = QLabel(self)
        self.definition_output.setWordWrap(True)
        self.definition_output.setMinimumSize(14, 18)

        self.v_layout.addWidget(self.word_input)
        self.v_layout.addWidget(self.search_button)
        self.v_layout.addWidget(self.definition_output)
#===============================================================================================================================================
#============================================================Sidebar Layout (Vertical)==========================================================
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
#===============================================================================================================================================
#===========================================================Toggle Button (Collapses Sidebar)===================================================
        self.toggle_btn = QPushButton("☰")  # Unicode for menu icon
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self._toggle_sidebar)
#==============================================================================================================================================
#====================================================================Sidebar Buttons============================================================
        self.md_btn = QPushButton("Markdown ON")
        self.md_btn.clicked.connect(self._add_browser)

        self.copy_button = QPushButton("copy")
        self.copy_button.clicked.connect(self.text_edit.copy)

        self.cut_button = QPushButton("cut")     
        self.cut_button.clicked.connect(self.text_edit.cut)

        self.paste_button = QPushButton("paste")
        self.paste_button.clicked.connect(self.text_edit.paste)

        self.undo_button = QPushButton("undo")
        self.undo_button.clicked.connect(self.text_edit.undo)
        
        self.redo_button = QPushButton("redo")
        self.redo_button.clicked.connect(self.text_edit.redo)

        self.clear_button = QPushButton("clear")
        self.clear_button.clicked.connect(self.text_edit.clear)

        self.save_button = QPushButton("save")
        self.save_button.clicked.connect(self.save_file)
        
        self.exit = QPushButton("Exit")
        self.exit.clicked.connect(self.exit_button)

        self.file = QPushButton("Files")
        self.file.clicked.connect(self.open_file)

        self.theme_btn = QPushButton("🌙 Dark Mode", self)
        self.theme_btn.clicked.connect(self.theme)

        self.font_size_box = QComboBox(self)
        self.font_size_box.addItems(["10", "12", "14", "16", "18", "20", "22", "24", "26"])
        self.font_size_box.currentIndexChanged.connect(self._change_font_size)
#===============================================================================================================================================
#============================================================List of side bar buttons===========================================================
        buttons = [
                    self.file,
                    self.theme_btn,
                    self.font_size_box,
                    self.copy_button,
                    self.cut_button,
                    self.paste_button,
                    self.undo_button,
                    self.clear_button,
                    self.save_button,
                    self.md_btn,
                    self.exit

                 ]
#===============================================================================================================================================
#================================================================style Buttons==================================================================
        for btn in buttons:
            btn.setStyleSheet("color: white; background: #444; border: none; padding: 10px;")
            self.sidebar_layout.addWidget(btn)
#===============================================================================================================================================
#================================================================Add Widgets to Main Layout=====================================================
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)  # Sidebar toggle button
        self.main_layout.addLayout(self.v_layout)
       
        self.setLayout(self.main_layout)
#===============================================================================================================================================
#==============================================Load user preference (default: light mode)=======================================================
        # Load user preferences
        self.is_dark_mode, self.font_size = self._load_preferences()
        self._apply_theme()
        self._set_font_size(self.font_size)

        self._get_last_written()
#===============================================================================================================================================
#===================================================================Funtions====================================================================
    def _toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.toggle_btn.setText("☰")
        else:
            self.sidebar.show()
            self.toggle_btn.setText("✖")


    def paste(self):            
        self.text_edit.paste()

    def save_file(self):
        #Prompts the user for filename and location
        file_name, _ = QFileDialog.getSaveFileName(self, "save file", "", "Text Files (*.txt);;(*.html);;(*.csv);;(*.py);;(*.md)") 

        if file_name:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "save file", "", "Text Files (*.txt);;(*.html);;(*.csv);;(*.py);;(*.md)")

        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.text_edit.setText(file.read())

    def about_noteWorthy(self):
         ret = QMessageBox.information(self,"About Note worthy",
                                      "Created by Connor Connorson",
                                      QMessageBox.Ok
                                      )
    
    def get_definition(self):
        word = self.word_input.text().strip().lower()  # Ensure lowercase
        if not word:
            self.definition_output.setText("⚠️ Please enter a word.")
            return

        synsets = wordnet.synsets(word)
        if synsets:
            definitions = '\n'.join([f"• {s.definition()}" for s in synsets[:3]])  # Add bullet points
            self.definition_output.setText(definitions)
        else:
            self.definition_output.setText("❌ No definition found.")
       

    def update_word_count(self):
        text = self.text_edit.toPlainText()
        words_num = len(text.split())
        self.word_count_label.setText(f'Words: {str(words_num)}')
        

    def theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()
        self._save_preferences()

    def _apply_theme(self):
        if self.is_dark_mode:
            self._dark_mode()
        else:
            self._light_mode()

    def _dark_mode(self):
        self.setStyleSheet("""
            QTextEdit { background-color: #2e2e2e; color: white; border: 1px solid #555; }
            QLabel { color: white; }
            QPushButton { background-color: #444; color: white; border-radius: 5px; padding: 5px; }
            QPushButton:hover { background-color: #555; }
        """)
        self.theme_btn.setText("☀️ Light Mode")

    def _light_mode(self):
        """Apply light mode styles."""
        self.setStyleSheet("""
            QTextEdit { background-color: white; color: black; border: 1px solid gray; }
            QLabel { color: white; }
            QPushButton { background-color: #e0e0e0; color: black; border-radius: 5px; padding: 5px; }
            QPushButton:hover { background-color: #d6d6d6; }
        """)
        self.theme_btn.setText("🌙 Dark Mode")

    def _change_font_size(self):
        """Change the font size when the user selects a new size."""
        selected_size = int(self.font_size_box.currentText())
        self._set_font_size(selected_size)
        self._save_preferences()  # Save font size selection
    
    def _set_font_size(self, size):
        """Apply the selected font size."""
        font = QFont("Arial", size)
        self.text_edit.setFont(font)
        self.preview.setFont(font)
        self.font_size_box.setCurrentText(str(size))  # Ensure dropdown reflects the selection

    
    def _save_preferences(self):
        """Save user preferences (theme & font size) to a JSON file."""
        data = {
            "dark_mode": self.is_dark_mode,
            "font_size": self.font_size_box.currentText()
        }
        with open(CONFIG_FILE, "w") as file:
            json.dump(data, file)

    def _load_preferences(self):
        """Load user preferences (theme & font size) from a JSON file."""
        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
                return data.get("dark_mode", False), int(data.get("font_size", 14))  # Default: Light mode, Font size 14
        except (FileNotFoundError, json.JSONDecodeError):
            return False, 14  # Default values if file is missing or corrupted
        
    def _add_browser(self):
        if  self.md_mode == False:
            self.main_layout.addWidget(self.preview)
            self.md_btn.setText("Markdown OFF")
            self.md_mode = True
        else:
            index = self.main_layout.indexOf(self.preview)
            item = self.main_layout.takeAt(index)
            widget = item.widget()
            if widget != None:
                widget.setParent(None)
            self.md_mode = False
            self.md_btn.setText("Markdown ON")
   
    def _md_formatter(self):
        md_text = self.text_edit.toPlainText()
        html = markdown(md_text)
        self.preview.setHtml(html)
        
    def _restart_timer(self):
        self.typing_timer.start(1000)  # Waits 10 seconds after last keypress

    def _autosave(self):
        current_text = self.text_edit.toPlainText()
        if current_text != getattr(self, "last_saved_text",""):
            file = Path(__file__).parent / "temp.txt"
            with open(file, "w", encoding="utf-8") as f:
                f.write(current_text)
            self.last_saved_text = current_text

    def _get_last_written(self):
        file = Path(__file__).parent / "temp.txt"
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
            self.text_edit.setText(text)
            self.previous_text = False
        except FileNotFoundError:
            return
        
    def exit_button(self):
        self.destroy()
        sys.exit()
#===============================================================================================================================================
#===========================================================Run Application====================================================================
if __name__ == "__main__":
    app = QApplication([])
    window = NoteWorthy()
    window.show()
    app.exec()
#===============================================================================================================================================