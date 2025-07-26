import sys
import json
import random
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QInputDialog, QMessageBox, QGraphicsOpacityEffect
)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QTimer




#=================================================================App Class=====================================================================
class RandomQuote(QWidget):
    def __init__(self):
        super().__init__()
#=============================================================set main layout and title=========================================================
        self.setWindowTitle("QuoteGen")
        self.main_layout = QHBoxLayout(self)
#===============================================================================================================================================
#====================================================================sidebar widget=============================================================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #333;")

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #1e1e2f;  /* Deep navy-black */
                    color: #f1f1f1;             /* Soft white text */
                    border-right: 1px solid #2a2a40;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
#===============================================================================================================================================
#======================================================================sidebar toggle button====================================================
        self.toggle_btn = QPushButton("")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
#-----------------------------------------------------------------side bar buttons--------------------------------------------------------------
        self.exit = QPushButton("Exit")
        self.exit.clicked.connect(self.terminate)

        self.btn_about = QPushButton("About")
        self.btn_about.clicked.connect(self.show_about)

        self.thm_btn = QPushButton("☀️ Light Mode")
        self.thm_btn.clicked.connect(self.toggle_thm)
        self.thm_mode = "dark mode"

        self.btn_add_qoute = QPushButton("➕ Add Quote")
        self.btn_add_qoute.clicked.connect(self.add_quote)
        self.btn_add_qoute.setStyleSheet("color: white; background: #917c5a; border: none; padding: 10px;")
        self.sidebar_layout.addWidget(self.btn_add_qoute)

        self.btn_favorites = QPushButton("Favorites")
        self.btn_favorites.clicked.connect(self.show_favorites)
#------------------------------------------------------------------Apply opacity effect to the button-------------------------------------------
        self.add_opacity = QGraphicsOpacityEffect()
        self.btn_add_qoute.setGraphicsEffect(self.add_opacity)
#-----------------------------------------------------------------------Create the animation----------------------------------------------------
        self.add_pulse_anim = QPropertyAnimation(self.add_opacity, b"opacity")
        self.add_pulse_anim.setDuration(2000)
        self.add_pulse_anim.setStartValue(0.5)
        self.add_pulse_anim.setEndValue(1.0)
        self.add_pulse_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.add_pulse_anim.setLoopCount(-1)  # infinite loop
        self.add_pulse_anim.start()
#===============================================================================================================================================
#==========================================================================content area=========================================================
        self.content_area = QLabel("", self)
        self.content_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_area.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffecd2, stop:1 #fcb69f
                );
                padding: 40px;
                border-radius: 15px;
                font-size: 26px; 
                font-style: italic; 
                color: #333;
            }
        """)
#===============================================================================================================================================
#========================================================================set content area wrap==================================================
        self.content_area.setWordWrap(True)
#===============================================================================================================================================
#==========================================================================Apply glow effect====================================================
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(100)
        shadow.setColor(Qt.white)
        shadow.setOffset(0, 1)
        self.content_area.setGraphicsEffect(shadow)
#===============================================================================================================================================
#========================================================================content area buttons===================================================
        self.gen_btn = QPushButton("Generate Quote")
        self.gen_btn.clicked.connect(self.gen_qoute)

        self.fav_btn = QPushButton("❤️ Add to Favorites")
        self.fav_btn.clicked.connect(self.add_to_favorites)
#===============================================================================================================================================
#==================================================================applying css & adding buttons================================================
        for btn in [self.gen_btn, self.fav_btn, self.toggle_btn, self.thm_btn, self.btn_about, self.btn_favorites, self.exit]:
            btn.setStyleSheet("""
                    QPushButton {
                                background-color: #2c2c3e;
                                color: #ffffff;
                                padding: 10px 20px;
                                border: 1px solid #444c66;
                                border-radius: 10px;
                                font-size: 14px;
                            }

                QPushButton:hover {
                    background-color: #39395a;
                }

                QPushButton:pressed {
                    background-color: #30304d;
                }
                                    """)
            self.sidebar_layout.addWidget(btn)
#===============================================================================================================================================
#============================================================================v layout===========================================================
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.content_area)
        self.v_layout.addWidget(self.gen_btn)
        self.v_layout.addWidget(self.fav_btn)
#===============================================================================================================================================
#=================================================================adding widgets to main layout=================================================
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.toggle_btn)
        self.main_layout.addLayout(self.v_layout)

        self.setLayout(self.main_layout)
        self.resize(800, 600)
#===============================================================================================================================================
#=====================================================================set gradients=============================================================
        self.gradients = [
            "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #ff9a9e, stop:1 #fad0c4)",
            "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #a18cd1, stop:1 #fbc2eb)",
            "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f6d365, stop:1 #fda085)",
            "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #84fab0, stop:1 #8fd3f4)",
            "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #cfd9df, stop:1 #e2ebf0)"
        ]

        self.current_gradient = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_background)
        self.timer.start(10000)  # change gradient every 10 seconds
#===============================================================================================================================================
#==========================================================================Methods==============================================================
    def toggle_sidebar(self):
        "Toggles the side bar"
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def animate_background(self):
        """Sets the animation for the content area"""
        self.current_gradient = (self.current_gradient + 1) % len(self.gradients)
        self.content_area.setStyleSheet(f"""
            QLabel {{
                background: {self.gradients[self.current_gradient]};
                padding: 40px;
                border-radius: 15px;
                font-family: 'Georgia', serif;
                color: #222;
            }}
        """)

#-----------------------------------------------------------------------------------------------------------------------------------------------
    def gen_qoute(self):
        """Fetches quotes from json file, formats them and displays it on content_area"""
        file = Path(__file__).parent / "Q_quotes.json"


        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            num = random.randrange(1, len(data))
            quote = data[num]["quote"]
            author = data[num]["author"]

            self.current_quote = {"quote": quote, "author": author}

            formatted_quote = f"""
                <p style="font-size: 26px; font-style: italic; color: #333;">
                    “{quote}”
                </p>
                <p style="font-size: 20px; font-weight: bold; color: #555; margin-top: 20px;">
                    — {author}
                </p>
            """
            self.content_area.setText(formatted_quote)
        
        

            self.content_area.setWindowOpacity(0.0)
            self.anim = QPropertyAnimation(self.content_area, b"windowOpacity")
            self.anim.setDuration(10000)
            self.anim.setStartValue(0.0)
            self.anim.setEndValue(1.0)
            self.anim.setEasingCurve(QEasingCurve.InOutQuad)
            self.anim.start()
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "File not found")
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def add_quote(self):
        """Allows user to add quotes to the json file"""
        quote, ok1 = QInputDialog.getText(self, "Add Quote", "Enter the quote:")
        if not ok1 or not quote.strip():
            return

        author, ok2 = QInputDialog.getText(self, "Add Author", "Enter the author's name:")
        if not ok2 or not author.strip():
            return

        try:
            with open(Path(__file__).parent / "Q_quotes.json", "r+", encoding="utf-8") as f:
                data = json.load(f)

                for i in range(1, len(data)):
                    if quote == data[i]["quote"]:
                        QMessageBox.information(self, "Failure", "Quote already added")
                        return

                new_entry = {"quote": quote.strip(), "author": author.strip()}
                data.append(new_entry)

                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.truncate()

            QMessageBox.information(self, "Success", "Quote added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save quote:\n{str(e)}")
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def add_to_favorites(self):
        """Save current qoutes to favorites"""
        if not hasattr(self, "current_quote"):
            return

        try:
            with open(Path(__file__).parent /"favorites.json", "r", encoding="utf-8") as f:
                favorites = json.load(f)
        except FileNotFoundError:
            favorites = []

        if self.current_quote not in favorites:
            favorites.append(self.current_quote)
            with open(Path(__file__).parent /"favorites.json", "w", encoding="utf-8") as f:
                json.dump(favorites, f, indent=4, ensure_ascii=False)
            self.content_area.setText(self.content_area.text() + "<br><br><i style='color: green;'>Added to favorites!</i>")
        else:
            self.content_area.setText(self.content_area.text() + "<br><br><i style='color: orange;'>Already in favorites.</i>")
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def show_favorites(self):
        """Displays Favourite quotes"""
        try:
            with open(Path(__file__).parent /"favorites.json", "r", encoding="utf-8") as f:
                favorites = json.load(f)
        except FileNotFoundError:
            self.content_area.setText("No favorites saved yet.")
            return

        if not favorites:
            self.content_area.setText("Your favorites list is empty.")
            return

        html = "<h2 style='font-family: serif;'>🌟 Favorite Quotes</h2><ul>"
        for item in favorites:
            html += f"<li style='margin: 10px 0; font-size: 18px;'>“{item['quote']}” — <b>{item['author']}</b></li>"
        html += "</ul>"

        self.content_area.setText(html)
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def apply_light_mode(self):
        """Applies light mode css"""
        self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #f7f9fc;  /* Soft off-white */
                    color: #2c3e50;              /* Elegant dark grey text */
                    border-right: 1px solid #dcdfe3;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
        for btn in [self.thm_btn, self.btn_about, self.btn_favorites, self.exit,self.toggle_btn,self.gen_btn, self.fav_btn]:
            btn.setStyleSheet("""
                    QPushButton {
                                    background-color: #e1ecf4;
                                    color: #2d3e50;
                                    padding: 10px 20px;
                                    border: 1px solid #ccd6dd;
                                    border-radius: 10px;
                                    font-size: 14px;
                                }
                    QPushButton:hover {
                                background-color: #d0e6f7;
                                    }
                    QPushButton:pressed {
                                background-color: #c1dff7;
                        }
                                    """)
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def apply_dark_mode(self):
        "Applies dark mode css"
        self.sidebar.setStyleSheet("""
                QWidget {
                    background-color: #1e1e2f;  /* Deep navy-black */
                    color: #f1f1f1;             /* Soft white text */
                    border-right: 1px solid #2a2a40;
                    border-radius: 12px;
                    padding: 10px;
                }
            """)
        for btn in [self.thm_btn, self.btn_about, self.btn_favorites, self.exit,self.toggle_btn,self.gen_btn, self.fav_btn]:
                btn.setStyleSheet("""
                    QPushButton {
                                background-color: #2c2c3e;
                                color: #ffffff;
                                padding: 10px 20px;
                                border: 1px solid #444c66;
                                border-radius: 10px;
                                font-size: 14px;
                            }

                QPushButton:hover {
                    background-color: #39395a;
                }

                QPushButton:pressed {
                    background-color: #30304d;
                }
                                    """)
#---------------------------------------------------------------------------------------------------------------------------------------------- 
    def toggle_thm(self):
        """Toggle between light and dark mode"""
        #Switch to light mode
        if self.thm_mode == "dark mode":
            self.thm_mode = "light mode"
            self.apply_light_mode()
            self.thm_btn.setText("🌙 Dark Mode")

        elif self.thm_mode == "light mode":
            #Switch to dark mode
            self.thm_mode = "dark mode"
            self.apply_dark_mode()
            self.thm_btn.setText("☀️ Light Mode")
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def show_about(self):
        """Displays information about the app and creator(s)"""
        about_text = """
    <h2>About QuoteGen</h2>
    <p><strong>Welcome to QuoteGen!</strong> Your personal quote generator and keeper of wisdom. Whether you're looking for inspiration or a deep reflection, QuoteGen is here to spark that light.</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Generate a random quote with a tap</li>
        <li>Add and save your own favorite quotes</li>
        <li>Keep track of your favorite quotes in a special list</li>
        <li>Simple and easy-to-use interface</li>
    </ul>
    <p><strong>Created by:</strong> Connor Connorson, an avid creator and lifelong learner. Built with love and passion for quotes and meaningful design.</p>
    <p><strong>Version:</strong> 1.0.0</p>
    <p><strong>Credits:</strong> Quotes powered by brainyquote.com. Special thanks to PySide6 for the elegant UI design framework.</p>
    <p><strong>License:</strong> Open-source under MIT License</p>
    <p><strong>Contact Us:</strong> For feedback, suggestions, or questions, email us at: khona6047@gmail.com.</p>
    """
        msg = QMessageBox()
        msg.setWindowTitle("About QuoteGen")
        msg.setTextFormat(Qt.RichText)  # Allow HTML formatting
        msg.setInformativeText(about_text)
        msg.exec()
#-----------------------------------------------------------------------------------------------------------------------------------------------
    def terminate(self):
        """Kills the app"""
        sys.exit()
#===============================================================================================================================================
#=============================================================================Run APP===========================================================
if __name__ == "__main__":
    app = QApplication([])
    window = RandomQuote()
    window.show()
    app.exec()
