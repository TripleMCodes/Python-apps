import sys
import random
import vlc
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QSlider, QLabel, QHBoxLayout, QListWidget, QCheckBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTabWidget,QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path

import math
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QWidget, QApplication

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0
        self.amplitude = 50  # default wave height

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(10)

    def setAmplitude(self, amplitude):
        self.amplitude = max(10, min(amplitude, 100))

    def update_animation(self):
        self.phase += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#00FFAA"), 2)
        painter.setPen(pen)

        width = self.width()
        height = self.height()
        mid_y = height / 2

        points = []
        for x in range(width):
            y = mid_y + math.sin((x / 30.0) + self.phase) * self.amplitude
            points.append(QPointF(x, y))

        painter.drawPolyline(points)

class AlbumArtView(QGraphicsView):
    def __init__(self, image_path):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        pixmap = QPixmap(image_path)
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)

        self.setAlignment(Qt.AlignCenter)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        # self.setResizeAnchor(QGraphicsView.NoAnchor)
        # self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setRenderHints(self.renderHints() | 
        #                     self.renderHints.Antialiasing |
        #                     self.renderHints.SmoothPixmapTransform)

        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("M Sona (VLC Powered musicplayer) 🎵")
        self.setGeometry(200, 200, 700, 500)
        self.setAcceptDrops(True)

        tab_layout = QVBoxLayout(self)

        tabs = QTabWidget()
        tab_layout.addWidget(tabs)


        main_layout = QWidget()
        # self.setLayout(main_layout)
        tab1 = main_layout
        

        side_layout = QWidget()
        # main_layout.addLayout(side_layout)
        tab2 = side_layout
        tab2_layout = QHBoxLayout()
        tabs.addTab(tab2, "Play List")

        # VLC Player Setup
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Playlist
        self.playlist = []
        self.current_index = -1
        self.is_shuffling = False
        self.is_looping = False

        # UI Elements
        self.btn_open = QPushButton("📂 Open Files")
        self.btn_play = QPushButton("▶ Play")
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_next = QPushButton("⏭ Next")
        self.btn_prev = QPushButton("⏮ Previous")
        self.shuffle_checkbox = QCheckBox("🔀 Shuffle")
        self.loop_checkbox = QCheckBox("🔁 Loop")

        # Volume slider
        self.volume_label = QLabel("Volume: 50%")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        # Seek slider
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.setEnabled(False)
        self.seek_label = QLabel("0:00 / 0:00")

        # Playlist Widget
        self.playlist_widget = QListWidget()
        self.playlist_widget.setStyleSheet("background-color: #222; color: #fff; font-size: 14px;")
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        #Album art and sound wave container
        art_sound_container = QHBoxLayout()
        # Album Art Display
        img_path = Path(__file__).parent / "solitude album cover.png"
        self.album_art = AlbumArtView(img_path)
        # self.album_art.setMinimumSize(150, 80)
        # self.sound_wave = WaveformWidget()
        # self.sound_wave.setMinimumSize(180, 150)
        # self.waveform_timer = QTimer(self)
        # self.waveform_timer.setInterval(50)  # 20 times per second
        # self.waveform_timer.timeout.connect(self.update_waveform_amplitude)
        # self.waveform_timer.start()
        # QGraphicsView()
        # self.album_scene = QGraphicsScene()
        # self.album_art.setScene(self.album_scene)
        # self.album_art.setFixedSize(150, 150)
        # self.album_art.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        art_sound_container.addWidget(self.album_art)
        # art_sound_container.addWidget(self.sound_wave)
        
        # self.album_art.setScaledContents(True);;
        

        # Timer to update seek bar
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_seek)

        # Layout
        layout = QVBoxLayout()
        layout.addLayout(art_sound_container)
        # layout.addWidget(self.sound_wave)


        tab2_layout.addWidget(self.playlist_widget)
        tab2_layout.addWidget(self.btn_open)
        # tab2_layout.addWidget(self.sound_wave)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_prev)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.btn_next)
        layout.addLayout(controls_layout)

        seek_layout = QHBoxLayout()
        seek_layout.addWidget(self.seek_label)
        seek_layout.addWidget(self.seek_slider)
        layout.addLayout(seek_layout)

        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_label)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)

        shuffle_loop_layout = QHBoxLayout()
        shuffle_loop_layout.addWidget(self.shuffle_checkbox)
        shuffle_loop_layout.addWidget(self.loop_checkbox)
        layout.addLayout(shuffle_loop_layout)

        # main_layout.addLayout(layout)
        tab1.setLayout(layout)
        tabs.addTab(tab1, "Music Player")

        tab2.setLayout(tab2_layout)
        tabs.addTab(tab2, "Play List")

        # self.setLayout(layout)

        # Connect Signals
        self.btn_open.clicked.connect(self.open_files)
        self.btn_play.clicked.connect(self.play_music)
        self.btn_pause.clicked.connect(self.pause_music)
        self.btn_stop.clicked.connect(self.stop_music)
        self.btn_next.clicked.connect(self.next_song)
        self.btn_prev.clicked.connect(self.prev_song)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.shuffle_checkbox.stateChanged.connect(self.toggle_shuffle)
        self.loop_checkbox.stateChanged.connect(self.toggle_loop)

        # Apply Dark Theme
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #fff; }
            QPushButton { background-color: #333; border-radius: 5px; padding: 8px; color: #fff; }
            QPushButton:hover { background-color: #444; }
            QSlider::groove:horizontal { background: #444; height: 5px; }
            QSlider::handle:horizontal { background: #ff9500; width: 10px; }
        """)

    def update_waveform_amplitude(self):
        if self.player.is_playing():
            # Get current volume (0 to 100)
            volume = self.player.audio_get_volume()

            amplitude = (volume / 100.0) * 50  # max amplitude 50
            self.sound_wave.setAmplitude(amplitude)
        else:
            self.sound_wave.setAmplitude(10)  # idle small amplitude

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Music Files", "", "Audio Files (*.mp3 *.wav *.ogg *.flac  *.m4a)")
        if files:
            self.playlist.extend(files)
            for file in files:
                self.playlist_widget.addItem(file.split("/")[-1])

            if self.current_index == -1:
                self.current_index = 0
                self.load_song(self.playlist[self.current_index])

    def play_music(self):
        if self.player.get_state() == vlc.State.Ended:
            self.next_song()
        else:
            self.player.play()

    def pause_music(self):
        self.player.pause()

    def stop_music(self):
        self.player.stop()
        self.seek_slider.setValue(0)
        self.seek_label.setText("0:00 / 0:00")

    def next_song(self):
        if self.is_shuffling:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index += 1

        if self.current_index < len(self.playlist):
            self.load_song(self.playlist[self.current_index])
        elif self.is_looping:
            self.current_index = 0
            self.load_song(self.playlist[self.current_index])

    def prev_song(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_song(self.playlist[self.current_index])

    def load_song(self, file_path):
        media = self.instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()
        self.seek_slider.setEnabled(True)
        self.timer.start()
        self.playlist_widget.setCurrentRow(self.current_index)
        self.load_album_art(file_path)

    def change_volume(self, value):
        self.player.audio_set_volume(value)
        self.volume_label.setText(f"Volume: {value}%")

    def update_seek(self):
        if self.player.get_length() > 0:
            pos = self.player.get_time() / self.player.get_length()
            self.seek_slider.setValue(int(pos * 1000))
            current_time = self.format_time(self.player.get_time())
            total_time = self.format_time(self.player.get_length())
            self.seek_label.setText(f"{current_time} / {total_time}")

    def set_position(self, value):
        if self.player.get_length() > 0:
            self.player.set_time(int((value / 1000) * self.player.get_length()))

    def toggle_shuffle(self):
        self.is_shuffling = self.shuffle_checkbox.isChecked()

    def toggle_loop(self):
        self.is_looping = self.loop_checkbox.isChecked()

    def load_album_art(self, file_path):
        try:
            audio = MP3(file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    pixmap = QPixmap()
                    pixmap.loadFromData(tag.data)
                    self.album_scene.clear()
                    self.album_scene.addPixmap(pixmap)
                    return
        except Exception:
            self.album_scene.clear()
    
    def play_selected(self):
        selected_item = self.playlist_widget.currentRow()
        if selected_item >= 0:  # Ensure a valid selection
            self.current_index = selected_item
            self.load_song(self.playlist[self.current_index])


    @staticmethod
    def format_time(ms):
        seconds = ms // 1000
        return f"{seconds // 60}:{seconds % 60:02d}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())
