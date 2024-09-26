from dataclasses import dataclass
from datetime import datetime, timedelta

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
                               QPushButton, QLabel, QScrollArea, QComboBox, QProgressBar, QFrame, QLineEdit)
from PySide6.QtCore import QSize, Qt, QRunnable, QThreadPool, Slot
from pathlib import Path
from Settings import settings
from WeatherData import WeatherData
from DiskIO import DiskIO

# nuitka --follow-imports --onefile --windows-icon-from-ico=meteorology.ico --plugin-enable=pyside6 .\main.py


@dataclass
class Sizes:
    win_x: int = 650
    win_y: int = 500
    contents_margins: tuple[int] = (10, 10, 10, 10)
    spacing: int = 5
    widget_min_width: int = 150
    widget_min_height: int = 30


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.widget = QWidget()
        self.setWindowTitle("Погода по районам Владивостока")
        self.setMinimumSize(QSize(Sizes.win_x, Sizes.win_y))
        self.days = settings.get_days()
        self.nights = settings.get_nights()
        self.cmb_days = QComboBox()
        self.cmb_day_or_night = QComboBox()
        self.progress = QProgressBar()
        self.lbl_address = QLabel()
        self.layout_base = QVBoxLayout()
        self.layout_center = QVBoxLayout()
        self.btn_load_data = QPushButton()
        self.btn_address = QPushButton()
        self.destination_dir = Path("/")
        self.tmp_dir = Path.cwd() / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.data = None
        self.triples = list()
        self.control_state = True
        self.setup_widgets()
        self.load_settings()
        self.list_files()

    def save_settings(self):
        settings.set_days(self.cmb_days.currentIndex())
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
        # print(self.data[0])
        self.switch_controls()
        self.hide_controls()
        self.clear_tmp_dir()
        self.threadpool.start(self.get_forecast)
        # self.get_forecast()
        self.switch_controls()

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


    @Slot()
    def get_forecast(self):

        forecast = dict()
        days = int(self.cmb_days.currentText())

        for line in self.data:
            wd = WeatherData(days, self.nights, line.get("url"), line.get("num"), line.get("town"))
            wd.run()

            for key, value in wd.forecast.items():
                if forecast.get(key):
                    forecast[key].update(wd.forecast[key])
                else:
                    forecast[key] = wd.forecast.get(key)

            self.progress_bar_increment()

        for date_data in forecast.items():
            tomorrow = datetime.today().date() + timedelta(days=1)
            this_date = datetime.strptime(date_data[0].split("_")[0], "%Y-%m-%d").date()
            if this_date >= tomorrow:
                DiskIO.write_csv(date_data, str(self.tmp_dir))

        self.list_files()

    def command(self):
        sender = self.sender()
        DiskIO.move_file(sender.objectName(), self.tmp_dir, self.destination_dir)
        sender.setText("Файл перемещен")
        sender.setEnabled(False)

    def clear_tmp_dir(self):
        files = list(self.tmp_dir.iterdir())
        for file in files:
            DiskIO.delete_file(file.name, self.tmp_dir)

    def list_items(self):
        for i in range(12):
            lbl = QLabel()
            btn = QPushButton()
            btn.setObjectName(f"btn_{i}")
            lbl.setObjectName(f"lbl_{i}")

            layout_h = QHBoxLayout()
            layout_h.setContentsMargins(5, 5, 5, 5)
            lbl.setMinimumHeight(Sizes.widget_min_height)
            btn.setText(f"Переместить")
            btn.setMaximumWidth(Sizes.widget_min_width)
            btn.setMinimumHeight(Sizes.widget_min_height)

            layout_h.addWidget(lbl)
            layout_h.addWidget(btn)

            btn.setVisible(False)
            lbl.setVisible(False)

            btn.clicked.connect(self.command)

            self.layout_center.addLayout(layout_h)
            self.triples.append((btn, lbl, layout_h))

    def hide_controls(self):
        for triple in self.triples:
            button, label, layout = triple
            label.setVisible(False)
            button.setVisible(False)
            button.setText(f"Переместить")
            button.setEnabled(True)
        #     button.setParent(None)
        #     label.setParent(None)
        #     layout.setParent(None)
        # self.list_items()

    def list_files(self):
        files = list(self.tmp_dir.iterdir())
        for i in range(len(files)):
            button, label, _ = self.triples[i]
            file = files[i]

            label.setText(file.name)
            button.setObjectName(file.name)

            label.setVisible(True)
            button.setVisible(True)

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
        self.cmb_days.addItems(list(map(lambda x: str(x), range(1, 5))))
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
        self.progress.setFixedHeight(20)
        self.progress.setValue(0)

        self.layout_base.addWidget(self.progress)

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        frame_center.setLayout(self.layout_center)
        self.layout_base.addWidget(frame_center)
        self.layout_base.addStretch()

        self.list_items()

        # widget = QWidget()
        scroll_area.setWidget(self.widget)
        self.widget.setLayout(self.layout_base)
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

    def closeEvent(self, event):
        self.save_settings()


def main():
    app = QApplication([])
    window = Gui()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
