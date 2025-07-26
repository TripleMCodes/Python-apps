import os
import sys
import csv
import random
import psutil
import pygame
import logging
import datetime
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt
from PySide6.QtGui import QIcon
from collections import defaultdict
from files_formats import file_types
from PySide6.QtCore import QTimer, QTime, Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QSpinBox, QComboBox, QMessageBox,QSlider
)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

class PomodoroGUI(QWidget):

    def __init__(self):
        super().__init__()
#===================================================================Window Setup================================================================
        self.setWindowTitle("Pomodoro")
        icon_path = Path("icons/icons8-pomodoro-64.ico")
        self.setWindowIcon(QIcon(str(icon_path)))
#===============================================================================================================================================
#=======================================================Main horizontal layout (sidebar + main content)=========================================
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
#===============================================================================================================================================
#=================================================================Session attributes============================================================
        self.path = "C:"
        self.sessions = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.paused = False
        self.remaining_time = None

        self.end_time = None
        self.mode = 'Work'  # or 'Break'
        self.day = None
        self.month = None
        self.year = None
        self.time_studied = 120
#===============================================================================================================================================
#===========================================================================Sidebar (left)======================================================
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #333; color: white;")
#===============================================================================================================================================
#============================================================================Sidebar layout=====================================================
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sidebar.setLayout(sidebar_layout)
        
        sidebar_layout.setContentsMargins(10, 10, 10, 10)  # Margins around the layout for breathing space
        sidebar_layout.setSpacing(12)  # Spacing between elements in the sidebar
#===============================================================================================================================================
#===================================================================Apply styling to the sidebar itself=========================================
        self.sidebar.setStyleSheet("""
            QWidget#sidebar {
                background-color: #2c2c3e;
                border-radius: 12px;
                padding: 10px;
            }
        """)
#===============================================================================================================================================
#============================================================================sidebar content====================================================
        progress = QPushButton("Progress")
        progress.clicked.connect(self.plot_sessions_from_csv)
        progress.setStyleSheet("""
            QPushButton {
                background-color: #1a4d14; 
                color: white;
                padding: 10px 20px;
                border: 2px solid #3e8e41;
                border-radius: 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;  
                border-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #3e8e41; 
            }
        """)
#========================================================================studying Music=========================================================
        pygame.mixer.init()
        self.current_sound = None
        
        self.sound_files = {
        "lofi": "sounds/lofi.mp3",
        "Forest": "sounds/forestsounds.mp3",
        "Rain": "sounds/25 Minutes Sound Rain Noise to SleepRelaxing Rain.mp3",
        "Cafe": "sounds/25 minutes of Cafe Noise.mp3"
    }

        self.sound_selector = QComboBox()
        self.sound_selector.addItems(["None", "lofi", "Forest", "Rain", "Cafe"])
        self.sound_selector.setStyleSheet("""QComboBox {
                    background-color: #1e1e2f;
                    color: #ffffff;
                    font-size: 16px;
                    padding: 6px 12px;
                    border: 2px solid #ff5c8a;
                    border-radius: 12px;
                    selection-background-color: #ff5c8a;
                }
                
                QComboBox:hover {
                    border: 2px solid #ff85a2;
                }

                QComboBox::drop-down {
                    border: none;
                    background-color: #ff5c8a;
                    border-top-right-radius: 12px;
                    border-bottom-right-radius: 12px;
                    width: 25px;
                }

                QComboBox::down-arrow {
                    width: 14px;
                    height: 14px;
                }

                QComboBox QAbstractItemView {
                    background-color: #1e1e2f;
                    color: #ffffff;
                    selection-background-color: #ff5c8a;
                    padding: 6px;
                    border-radius: 10px;
                }
            """)
        self.volume_label = QLabel("Volume:")
        self.volume_label.setStyleSheet("color: #fff; font-size: 16px;")

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Default volume: 50%
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #444;
                margin: 2px 0;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: #00c896;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.change_volume)

        self.study_music = QLabel("Study Music")
        self.study_music.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2E4053;
                padding: 8px;
                border-radius: 10px;
                background-color: #D6EAF8;
            }
        """)
                
        exit_btn = QPushButton("Exit")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #380101;
                color: white;
                font-size: 16px;
                padding: 8px 16px;
                border-radius: 10px;
                border: 2px solid #d43f3a;
            }
            QPushButton:hover {
                background-color: #ad4e4b;
            }
            QPushButton:pressed {
                background-color: #a94442;
            }
        """)
        exit_btn.clicked.connect(self.terminate)

        sidebar_layout.addWidget(self.study_music)
        sidebar_layout.addWidget(self.sound_selector)
        sidebar_layout.addWidget(self.volume_label)
        sidebar_layout.addWidget(self.volume_slider)
        sidebar_layout.addWidget(progress)
        sidebar_layout.addWidget(exit_btn)
        sidebar_layout.addStretch()
#===============================================================================================================================================
#==================================================================Main content area (right)====================================================
        self.main_content = QWidget()
        content_layout = QVBoxLayout()
        self.main_content.setLayout(content_layout)
#===============================================================================================================================================
#=====================================================================Timer display=============================================================
        self.timer_label = QLabel("""00:00""", self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
                QLabel {
                    font-size: 150px;
                    font-weight: bold;
                    color: white;
                    background-color: #FF5555;
                    border-radius: 100px;  /* half of width/height for circle */
                    border: 4px solid #AA0000;
                    qproperty-alignment: 'AlignCenter';
                }
            """)
        content_layout.addWidget(self.timer_label)
         

#----------------------------------------------------------------------Time input controls------------------------------------------------------
        time_layout = QHBoxLayout()
        self.work_input = QSpinBox()
        self.work_input.setSuffix(" min")
        self.work_input.setRange(1, 180)
        self.work_input.setValue(25)
        self.work_input.setStyleSheet("""
            QSpinBox {
                background-color: #222;
                color: #fff;
                border: 2px solid #555;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 16px;
            }

            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                background-color: #444;
                border-left: 1px solid #555;
                border-bottom: 1px solid #555;
                border-top-right-radius: 8px;
            }

            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                background-color: #444;
                border-left: 1px solid #555;
                border-top: 1px solid #555;
                border-bottom-right-radius: 8px;
            }

            QSpinBox::up-arrow, QSpinBox::down-arrow {
                image: none;  /* Optional: remove arrows and go minimalist */
            }

            QSpinBox:hover {
                border: 2px solid #777;
            }

            QSpinBox:focus {
                border: 2px solid #00bfff;
                outline: none;
            }
        """)
#----------------------------------------------------------------------------break input--------------------------------------------------------
        self.break_input = QSpinBox()
        self.break_input.setSuffix(" min")
        self.break_input.setRange(1, 60)
        self.break_input.setValue(5)
        self.break_input.setStyleSheet("""
                QSpinBox {
                    background-color: #222;
                    color: #fff;
                    border: 2px solid #555;
                    border-radius: 10px;
                    padding: 5px 10px;
                    font-size: 16px;
                }

                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 20px;
                    background-color: #444;
                    border-left: 1px solid #555;
                    border-bottom: 1px solid #555;
                    border-top-right-radius: 8px;
                }

                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 20px;
                    background-color: #444;
                    border-left: 1px solid #555;
                    border-top: 1px solid #555;
                    border-bottom-right-radius: 8px;
                }

                QSpinBox::up-arrow, QSpinBox::down-arrow {
                    image: none;  /* Optional: remove arrows and go minimalist */
                }

                QSpinBox:hover {
                    border: 2px solid #777;
                }

                QSpinBox:focus {
                    border: 2px solid #00bfff;
                    outline: none;
                }
            """)
#----------------------------------------------------------------------------work label---------------------------------------------------------
        work_label = QLabel("Work Duration:")
        work_label.setStyleSheet("""
            QLabel {
                color: #00ffcc;
                font-size: 18px;
                font-weight: bold;
                padding: 4px 10px;
                border-left: 3px solid #00ffcc;
                background-color: rgba(0, 255, 204, 0.05);
                border-radius: 6px;
                margin-bottom: 5px;
            }
        """)
#----------------------------------------------------------------------break label--------------------------------------------------------------
        break_label = QLabel("Break Duration:")
        break_label.setStyleSheet("""
            QLabel {
                color: #00ffcc;
                font-size: 18px;
                font-weight: bold;
                padding: 4px 10px;
                border-left: 3px solid #00ffcc;
                background-color: rgba(0, 255, 204, 0.05);
                border-radius: 6px;
                margin-bottom: 5px;
            }
        """)
#--------------------------------------------------------------------------time layout----------------------------------------------------------
        time_layout.addWidget(work_label)
        time_layout.addWidget(self.work_input)
        time_layout.addWidget(break_label)
        time_layout.addWidget(self.break_input)
        content_layout.addLayout(time_layout)

#==============================================================================Reward selector==================================================
        self.reward_selector = QComboBox()
        self.reward_selector.addItems(["None", "Video", "Music", "Image"])
        self.reward_selector.setStyleSheet("""
                QComboBox {
                    background-color: #1e1e2f;
                    color: #ffffff;
                    font-size: 16px;
                    padding: 6px 12px;
                    border: 2px solid #ff5c8a;
                    border-radius: 12px;
                    selection-background-color: #ff5c8a;
                }
                
                QComboBox:hover {
                    border: 2px solid #ff85a2;
                }

                QComboBox::drop-down {
                    border: none;
                    background-color: #ff5c8a;
                    border-top-right-radius: 12px;
                    border-bottom-right-radius: 12px;
                    width: 25px;
                }

                QComboBox::down-arrow {
                    image: url(:/icons/down_arrow.png);  /* optional custom icon */
                    width: 14px;
                    height: 14px;
                }

                QComboBox QAbstractItemView {
                    background-color: #1e1e2f;
                    color: #ffffff;
                    selection-background-color: #ff5c8a;
                    padding: 6px;
                    border-radius: 10px;
                }
            """)
        content_layout.addWidget(self.reward_selector)
#===============================================================================================================================================#=========================================================================button layout=========================================================
        btn_layout = QHBoxLayout()
        content_layout.addLayout(btn_layout)
#-------------------------------------------------------------------------Control buttons-------------------------------------------------------
        self.start_btn = QPushButton("Start Pomodoro")
        self.start_btn.clicked.connect(self.start_session)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }

            QPushButton:hover {
                background-color: #218838;
            }

            QPushButton:pressed {
                background-color: #1c7430;
                border-style: inset;
            }
        """)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 15px;
                    font-size: 16px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #2471a3;
                }
            """)
        self.pause_btn.clicked.connect(self.toggle_pause)
        btn_layout.addWidget(self.pause_btn)

        self.quit_btn = QPushButton("⛔ End")
        self.quit_btn.clicked.connect(self.quit_session)
        self.quit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: 4px solid #b21f2d;
                    border-radius: 75px;  /* same as Start = perfect circle */
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                }

                QPushButton:hover {
                    background-color: #c82333;
                }

                QPushButton:pressed {
                    background-color: #a71d2a;
                    border-style: inset;
                }
            """)
        content_layout.addWidget(self.quit_btn)

#============================================================Add sidebar and main content to main layout========================================
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_content)
#==============================================================================================================================================
#=================================================================================Methods=======================================================
    def start_session(self):
        """Start session, studying sounds"""
        duration = self.work_input.value()
        self.end_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)
        logging.debug(self.end_time)
        self.timer.start(1000)  # fire every 1s
        self.mode = 'Work'
        self.update_timer()
        selected_sound = self.sound_selector.currentText()
        if selected_sound != "None":
            sound_path = self.sound_files.get(selected_sound)
            if sound_path:
                self.play_ambient_sound(sound_path)

    def update_timer(self):
        """Updates the timer_label every 1 second"""
        remaining = self.end_time - datetime.datetime.now()
        if remaining.total_seconds() <= 0:
            self.timer.stop()
            self.sessions += 1
            self.time_studied = self.time_studied + self.work_input.value()
            logging.debug(f'time studied {self.time_studied}')
            self.stop_ambient_sound()
            self.show_break_dialog()
        else:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            self.timer_label.setText(f"{mins:02d}:{secs:02d}")
        
    def show_break_dialog(self):
        """Display short and long break periods"""
        if self.mode == 'Work':
            reward = self.reward_selector.currentText()
            self.mode = 'Break'
            break_duration = self.break_input.value()
            if self.sessions % 4 == 0:
                break_duration = break_duration * 3
                QMessageBox.information(self, "Time for a long break!", f"Reward yourself: {reward}")
                self.end_time = datetime.datetime.now() + datetime.timedelta(minutes=break_duration)
            else:
                QMessageBox.information(self, "Time for a break!", f"Reward yourself: {reward}")
                self.end_time = datetime.datetime.now() + datetime.timedelta(minutes=break_duration)
            self.timer.start()
            self.chosen_reward()

    def date_converter(self):
        """Convert datetime.datetime.now() object into year, month and day variables"""
        string = datetime.datetime.now()
        ls_date = str(string).partition("-")
        self.year = ls_date[0]
        ls_md = ls_date[2].partition("-")
        self.month = ls_md[0]
        ls_day = ls_md[2].partition(" ")
        self.day = ls_day[0]
    
    def month_convert(self):
        """Converts self.month into complete month name"""
        if self.month == "01":
            self.month = "January"
            return self.month
        elif self.month == "02":
            self.month = "February"
            return self.month
        elif self.month == "03":
            self.month = "March"
            return self.month
        elif self.month == "04":
            self.month = "April"
            return self.month
        elif self.month == "05":
            self.month = "May"
            return self.month
        elif self.month == "06":
            self.month = "June"
            return self.month
        elif self.month == "07":
            self.month = "July"
            return self.month
        elif self.month == "08":
            self.month = "August"
            return self.month
        elif self.month == "09":
            self.month = "September"
            return self.month
        elif self.month == "10":
            self.month = "October"
            return self.month
        elif self.month == "11":
            self.month = "November"
            return self.month
        elif self.month == "12":
            self.month = "December"
            return self.month
        
    def date_format(self):
        """Gives date in this format dd//mm//yyyy"""
        self.date_converter()
        self.month_convert()
        date = f'{self.day} {self.month} {self.year}'
        return date

    def log_sessions(self):
        """Logs numbers of sessions studied into a csv file"""
        file = Path(__file__).parent / "sessions.csv"

        # Get the number of minutes studied
        hrs, mins = divmod(self.time_studied, 60)

        with open(file, "a", newline="") as f:
            log_file = csv.DictWriter(f, fieldnames=["sessions", "date", "time studied"])

            if file.stat().st_size == 0:
                log_file.writeheader()
            log_file.writerow({"sessions" : str(self.sessions), "date" : str(self.date_format()) ,"time studied": str(f'{hrs:02d} hrs {mins:02d} mins')})
    
    def plot_sessions_from_csv(self):
        """Plots the study session and show progress"""
        file_path = Path(__file__).parent / "sessions.csv"

        # Safeguard: Make sure file exists and isn't empty
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                if not reader.fieldnames or "date" not in reader.fieldnames or "sessions" not in reader.fieldnames:
                    print("CSV file format is invalid.")
                    return

                date_session_map = defaultdict(int)

                for row in reader:
                    try:
                        date_obj = datetime.datetime.strptime(row['date'], "%d %B %Y")
                        session_count = int(row['sessions'])
                        date_session_map[date_obj] += session_count
                    except ValueError as e:
                        logging.debug(f"Skipping row due to error: {e}")

            if not date_session_map:
                QMessageBox.information(self, "Notification","No data to plot.")
                return

            # Sort data by date
            sorted_dates = sorted(date_session_map)
            sorted_sessions = [date_session_map[date] for date in sorted_dates]

            # Plotting
            plt.figure(figsize=(12, 6))
            plt.plot(sorted_dates, sorted_sessions, marker='o', linestyle='-', color='teal')
            plt.fill_between(sorted_dates, sorted_sessions, color='teal', alpha=0.1)

            plt.title("📈 Study Sessions Over Time", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Sessions", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            plt.xticks(rotation=45)
            plt.show()

        except FileNotFoundError:
            print("CSV file not found. Check the path and try again.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def play_reward_and_close_app(self, file_types):
        """"Plays reward during break"""
        arr = []

        for dirpath, _, filenames in os.walk(self.path):
            arr.extend(
                os.path.join(dirpath, file)
                for file in filenames
                if any(file.endswith(ext) for ext in file_types)
            )

        if arr:
            arr_path = random.choice(arr)

            self.proc = subprocess.Popen(["start", arr_path], shell=True)
            self.break_duration = self.break_input.value()  # in minutes
            QTimer.singleShot(self.break_duration * 60 * 1000, self.on_break_over)

        else:
            logging.debug("No media app process found.")
            QMessageBox.information(self, "No media app process found.")

    
    def chosen_reward(self):
        """Plays selected reward"""
        choice = self.reward_selector.currentText()

        if choice == None:
            return
        elif choice == "Video":
            self.play_reward_and_close_app(file_types[ "Videos"])
            
        elif choice == "Music":
            self.play_reward_and_close_app(file_types["Music"])
           
        elif choice == "Image":
            self.play_reward_and_close_app(file_types["Images"])
    
    def on_break_over(self):
        """Closes reward after break"""
        # Kill viewer if still running
        common_media_apps = {
            "Photos", "mspaint", "IrfanView", "Photoshop", "VLC", "MediaMonkey",
            "MusicBee", "Media Player", "5KPlayer", "GOM Player", "PotPlayer",
            "MPV", "KMPlayer", "Quicklook", "Preview", "IINA", "Kodi", "DivX"
        }

        killed = False
        for process in psutil.process_iter(['pid', 'name']):
            if any(viewer.lower() in process.info['name'].lower() for viewer in common_media_apps):
                try:
                    os.system(f"taskkill /IM {process.info['name']} /F")
                    logging.debug(f"Killed media viewer: {process.info['name']}")
                    killed = True
                except Exception as e:
                    logging.error(f"Error closing app: {e}")
                    QMessageBox.warning(self, "Error", f"Error closing viewer: {e}")
                break

        if not killed:
            logging.debug("No media viewer found to close.")

        # Notify and resume
        QMessageBox.information(self, "Break Over", "Time to get back to work!")
        self.mode = 'Work'
        self.start_session()

    
    def toggle_pause(self):
        """For pausing or continuing a session"""
        if self.end_time != None:
            try:
                if not self.paused:
                    # Pause the timer
                    self.remaining_time = self.end_time - datetime.datetime.now()
                    self.timer.stop()
                    pygame.mixer.music.pause()
                    self.paused = True
                    self.pause_btn.setText("▶️ Continue")
                else:
                    # Resume the timer
                    self.end_time = datetime.datetime.now() + self.remaining_time
                    self.timer.start(1000)
                    pygame.mixer.music.unpause()
                    self.paused = False
                    self.pause_btn.setText("⏸️ Pause")
            except TypeError:
                QMessageBox.warning(self, "Warning", "Pomodoro session hasn't started yet.")
    
    def play_ambient_sound(self, sound_file):
        """Checks for studying music selected and plays it"""
        if self.current_sound:
            self.stop_ambient_sound()
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_sound = sound_file
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to play sound: {e}")

    def stop_ambient_sound(self):
        """"Stops the studying music"""
        volume = self.volume_slider.value() / 100
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.stop()
        self.current_sound = None
    
    def change_volume(self, value):
        """Changes the volume"""
        volume = value / 100  # pygame volume is 0.0 to 1.0
        pygame.mixer.music.set_volume(volume)

    def quit_session(self):
        """Ends session"""
        if  self.end_time == None:
            QMessageBox.warning(self, "Warning", f"Cannot end session — you haven’t even started yet.")
        else:
            self.timer.stop()
            QMessageBox.information(self, "Goodbye!", f"You completed {self.sessions} session(s).")
            self.timer_label.setText("00:00")
            self.end_time = None
            self.paused = False
            self.mode = 'Work'
            self.pause_btn.setText("⏸️ Pause")
            pygame.mixer.music.stop()

    def terminate(self):
        """Kill the app"""
        self.log_sessions()
        sys.exit()
#===============================================================================================================================================
#=========================================================================Run app===============================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroGUI()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())
