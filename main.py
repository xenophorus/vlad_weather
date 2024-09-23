from dataclasses import dataclass
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
                               QPushButton, QLabel, QScrollArea, QComboBox, QProgressBar, QFrame, QLineEdit)
from PySide6.QtCore import QSize, Qt, QRunnable, QThreadPool
from pathlib import Path
import time
from Settings import settings
from WeatherData import WeatherData
from DiskIO import DiskIO
import random

'''
TODO
Weather class gets only one forecast at a time. Gather? Async?
progressbar alpha? Over? gets forecast 
write and read class 

'''


@dataclass
class Sizes:
    win_x: int = 750
    win_y: int = 400
    contents_margins: tuple[int] = (10, 10, 10, 10)
    spacing: int = 5
    widget_min_width: int = 150
    widget_min_height: int = 30


class Gui(QMainWindow, QRunnable):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.setWindowTitle("Погода по районам Владивостока")
        self.setMinimumSize(QSize(Sizes.win_x, Sizes.win_y))
        self.days = settings.get_days()
        self.nights = settings.get_nights()
        self.cmb_days = QComboBox()
        self.cmb_day_or_night = QComboBox()
        self.progress = QProgressBar()
        # self.address_line = QLineEdit()
        self.lbl_address = QLabel()
        self.layout_base = QVBoxLayout()
        self.layout_center = QVBoxLayout()
        self.btn_load_data = QPushButton()
        self.btn_address = QPushButton()
        self.destination_dir = Path("/")
        self.tmp_dir = Path.cwd() / "tmp"
        self.data = None
        self.control_state = True
        self.setup_widgets()
        self.load_settings()
        self.items_to_remove = list()
        self.list_files()

    def save_settings(self):
        settings.set_days(self.cmb_days.currentText())
        settings.set_nights(self.cmb_day_or_night.currentIndex())
        settings.set_target_folder(str(self.destination_dir))
        settings.write_settings()

    def load_settings(self):
        self.cmb_days.setCurrentIndex(settings.get_days())
        self.cmb_day_or_night.setCurrentIndex(settings.get_nights())
        self.destination_dir = Path(settings.get_target_folder())
        self.lbl_address.setText(str(self.destination_dir))

    def forecast_thread(self):
        self.get_url_data()
        self.get_forecast()

    def progress_bar_increment(self):
        self.progress.setValue(self.progress.value() + 1)

    def get_url_data(self):
        data = DiskIO.get_regions()
        progress_max_value = len(data)
        self.progress.setValue(0)
        self.progress.setRange(0, progress_max_value)
        self.data = data

    def switch_controls(self):
        self.control_state = not self.control_state
        self.cmb_day_or_night.setEnabled(self.control_state)
        self.cmb_days.setEnabled(self.control_state)
        self.btn_address.setEnabled(self.control_state)
        self.btn_load_data.setEnabled(self.control_state)

    def get_forecast(self):
        self.switch_controls()

        [x.setParent(None) for x in self.items_to_remove]
        forecast = dict()
        days = int(self.cmb_days.currentText())

        for line in self.data:
            wd = WeatherData(days, self.nights, line.get("url"), line.get("num"), line.get("town"))
            wd.run()

            if forecast:
                for key in forecast.keys():
                    forecast[key].update(wd.forecast[key])
            else:
                forecast.update(wd.forecast)

            self.progress_bar_increment()


        for date_data in forecast.items():
            DiskIO.write_csv(date_data, str(self.tmp_dir))

        self.switch_controls()
        self.list_files()

    def list_files(self):
        files = list(self.tmp_dir.iterdir())
        for file in files:
            lbl = QLabel()
            btn = QPushButton()

            def command():
                DiskIO.move_file(lbl.text(), self.tmp_dir, self.destination_dir)
                lbl.setText("Файл перемещен!")
                btn.setEnabled(False)

            layout_h = QHBoxLayout()
            layout_h.setContentsMargins(5, 5, 5, 5)
            lbl.setMinimumHeight(Sizes.widget_min_height)
            btn.setText(f"Переместить")
            btn.setMaximumWidth(Sizes.widget_min_width)
            btn.setMinimumHeight(Sizes.widget_min_height)
            lbl.setText(file.name)
            layout_h.addWidget(lbl)
            layout_h.addWidget(btn)

            btn.clicked.connect(command)

            self.items_to_remove += [layout_h, lbl, btn]
            self.layout_center.addLayout(layout_h)


    def setup_widgets(self):
        self.layout_base.setContentsMargins(5, 5, 5, 5)

        frame_top = QFrame()
        frame_top.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        frame_center = QFrame()
        frame_center.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        layout_top = QVBoxLayout()
        layout_top.setContentsMargins(15, 5, 15, 5)
        layout_top_up = QHBoxLayout()
        layout_top_up.setContentsMargins(0, 5, 0, 10)
        layout_top_up.setSpacing(Sizes.spacing)

        layout_days = QHBoxLayout()
        layout_days.setAlignment(Qt.AlignLeft)
        lbl_combo = QLabel()
        lbl_combo.setText("Дней: ")

        self.cmb_days.setMinimumWidth(Sizes.widget_min_width)
        self.cmb_days.setMinimumHeight(Sizes.widget_min_height)
        self.cmb_days.addItems(list(map(lambda x: str(x), range(1, 6))))
        # self.cmb_days.currentIndexChanged.connect(self._disable_cmb_dn)
        layout_days.addWidget(lbl_combo)
        layout_days.addWidget(self.cmb_days)

        layout_dn = QHBoxLayout()
        layout_dn.setAlignment(Qt.AlignCenter)

        self.cmb_day_or_night.setMinimumWidth(Sizes.widget_min_width)
        self.cmb_day_or_night.addItems(["Только день", "День и ночь"])
        self.cmb_day_or_night.setMinimumHeight(Sizes.widget_min_height)
        self.cmb_day_or_night.currentIndexChanged.connect(self.set_day_or_night)
        layout_dn.addWidget(self.cmb_day_or_night)

        layout_load = QHBoxLayout()
        layout_load.setAlignment(Qt.AlignRight)
        self.btn_load_data.setMinimumWidth(Sizes.widget_min_width)
        self.btn_load_data.setMinimumHeight(Sizes.widget_min_height)
        self.btn_load_data.setText("Загрузить данные")
        self.btn_load_data.clicked.connect(self.forecast_thread)
        layout_load.addWidget(self.btn_load_data)

        layout_address = QHBoxLayout()
        layout_address.setContentsMargins(0, 0, 0, 5)

        self.lbl_address.setMinimumHeight(Sizes.widget_min_height)
        self.lbl_address.setText(str(self.destination_dir))

        self.btn_address.setText("Выбрать папку")

        self.btn_address.setFixedWidth(Sizes.widget_min_width)
        self.btn_address.setMinimumHeight(Sizes.widget_min_height)
        self.btn_address.clicked.connect(self.get_directory)
        layout_address.addWidget(self.lbl_address)
        layout_address.addWidget(self.btn_address)
        layout_top_up.addLayout(layout_days)
        layout_top_up.addLayout(layout_dn)
        layout_top_up.addLayout(layout_load)
        layout_top.addLayout(layout_top_up)
        layout_top.addLayout(layout_address)

        self.layout_center.setContentsMargins(10, 5, 10, 5)
        self.layout_center.setSpacing(Sizes.spacing)
        frame_top.setLayout(layout_top)
        self.layout_base.addWidget(frame_top)

        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(10)
        self.progress.setValue(0)

        self.layout_base.addWidget(self.progress)

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        frame_center.setLayout(self.layout_center)
        self.layout_base.addWidget(frame_center)
        self.layout_base.addStretch()

        widget = QWidget()
        scroll_area.setWidget(widget)
        widget.setLayout(self.layout_base)
        self.setCentralWidget(scroll_area)

    def set_day_or_night(self):
        self.nights = bool(self.cmb_day_or_night.currentIndex())

    def get_directory(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setDirectoryUrl(str(self.destination_dir))
        selected_dir = dialog.getExistingDirectory()

        if Path(selected_dir) != Path('.'):
            self.destination_dir = selected_dir
            self.lbl_address.setText(str(selected_dir))
            settings.set_target_folder(str(selected_dir))

    def _disable_cmb_dn(self):
        if self.cmb_days.currentIndex() > 5:
            self.cmb_day_or_night.setCurrentIndex(0)
            self.cmb_day_or_night.setDisabled(True)
        else:
            self.cmb_day_or_night.setEnabled(True)

    def closeEvent(self, event):
        self.save_settings()


def main():
    app = QApplication([])
    window = Gui()

    window.show()
    app.exec()


if __name__ == '__main__':
    main()
