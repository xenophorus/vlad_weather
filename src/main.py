from dataclasses import dataclass
from datetime import datetime, timedelta

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox,
                               QPushButton, QLabel, QScrollArea, QComboBox, QProgressBar, QFrame, QStatusBar)
from PySide6.QtCore import QSize, Qt, QThreadPool, Slot
from PySide6.QtGui import QIcon, QPixmap, QAction

from pathlib import Path

from Settings import settings
from WeatherData import WeatherData
from DiskIO import DiskIO

# nuitka --follow-imports --onefile --windows-icon-from-ico=meteorology.ico --plugin-enable=pyside6 --windows-console-mode=disable .\main.py
'''
TODO:
- вывод сообщений в строке
- сообщения об ошибках 
https://stackoverflow.com/questions/72925772/how-to-connect-to-signal-from-one-class-to-a-slot-in-another
'''

@dataclass
class Sizes:
    win_x: int = 700
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
        self.setStatusBar(QStatusBar(self))
        self.status_icon_label = QLabel()
        self.status_label = QLabel()
        self.destination_dir = Path("/")
        self.tmp_dir = Path.cwd() / "tmp"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.check_today = QCheckBox()
        self.data = None
        self.triples = list()
        self.control_state = True
        self.setWindowIcon(QIcon("icons/meteorology.ico"))
        self.regions = dict()
        self.set_status("information", "OK")
        self.from_today = True
        self.setup_widgets()
        self.load_settings()
        self.list_files()

    def save_settings(self):
        settings.set_days(self.cmb_days.currentIndex())
        settings.set_nights(self.cmb_day_or_night.currentIndex())
        settings.set_target_folder(str(self.destination_dir))
        settings.set_from_today(self.from_today)
        settings.write_settings()

    def load_settings(self):
        self.cmb_days.setCurrentIndex(settings.get_days())
        self.cmb_day_or_night.setCurrentIndex(settings.get_nights())
        self.destination_dir = Path(settings.get_target_folder())
        self.lbl_address.setText(str(self.destination_dir))
        self.from_today = bool(settings.get_from_today())
        self.check_today.setChecked(self.from_today)

    def checkbox_status(self):
        self.from_today = self.check_today.isChecked()
        print(self.from_today)

    def forecast_thread(self):
        self.get_url_data()
        self.get_regions_forecast()
        self.hide_controls()
        self.clear_tmp_dir()
        # self.get_forecast_by_region()
        self.threadpool.start(self.get_forecast_by_region)

    def progress_bar_increment(self):
        self.progress.setValue(self.progress.value() + 1)

    def get_url_data(self):
        try:
            data = DiskIO.get_regions()
            progress_max_value = len(data)
            self.progress.setValue(0)
            self.progress.setRange(0, progress_max_value)
            self.data = data
        except FileNotFoundError:
            self.set_status("exclamation-red", "Файл с данными городов не найден!")
            # raise FileNotFoundError
        except Exception as e:
            self.set_status("exclamation-red", str(e.__context__))
            # raise Exception


    def switch_controls(self):
        self.control_state = not self.control_state
        self.cmb_day_or_night.setEnabled(self.control_state)
        self.cmb_days.setEnabled(self.control_state)
        self.btn_address.setEnabled(self.control_state)
        self.btn_load_data.setEnabled(self.control_state)

    def get_regions_forecast(self):
        days = int(self.cmb_days.currentText())
        for line in self.data:
            self.regions[line.get("town")] = WeatherData(days, self.nights,
                                                         line.get("url"), line.get("num"),
                                                         line.get("town"))

    def set_status(self, icon="information", text="OK"):
        self.status_icon_label.setPixmap(QPixmap(f"icons/{icon}.png"))
        self.status_label.setText(text)

    @Slot()
    def get_forecast_by_region(self):

        switch_controls = QAction()
        finished = QAction()
        region_status = QAction()
        error_action = QAction()

        switch_controls.triggered.connect(self.switch_controls)
        finished.triggered.connect(self.list_files)

        switch_controls.trigger()

        forecast = dict()
        for key, value in self.regions.items():

            value.run()

            if value.forecast.get("error"):
                error_action.triggered.connect(self.set_status("exclamation-red",
                                                               f"{key} {value.forecast.get('string')}"))
                error_action.trigger()
            else:
                for day, fcast in value.forecast.items():
                    if forecast.get(day):
                        forecast[day].update(value.forecast[day])
                    else:
                        forecast[day] = value.forecast.get(day)

            progress_bar = QAction()
            progress_bar.triggered.connect(self.progress_bar_increment)
            progress_bar.trigger()
            region_status.triggered.connect(lambda x: self.set_status("download", key))
            region_status.trigger()

        for date_data in forecast.items():
            d = int(not self.check_today.isChecked())
            tomorrow = datetime.today().date() + timedelta(days=d)
            this_date = datetime.strptime(date_data[0].split("_")[0], "%Y-%m-%d").date()
            if this_date >= tomorrow:
                DiskIO.write_csv(date_data, str(self.tmp_dir))

        if forecast.items():
            region_status.triggered.connect(
                lambda x: self.set_status("information", "Данные загружены"))
        else:
            region_status.triggered.connect(
                lambda x: self.set_status("exclamation-red", "Данные не загружены"))
        region_status.trigger()
        finished.trigger()
        switch_controls.trigger()


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
        layout_days.addSpacing(15)

        layout_today = QHBoxLayout()
        layout_days.setAlignment(Qt.AlignLeft)
        lbl_today = QLabel()
        lbl_today.setText("Сегодня")
        self.check_today.checkStateChanged.connect(self.checkbox_status)
        # layout_today.addSpacing(15)

        layout_today.addWidget(lbl_today)
        layout_today.addWidget(self.check_today)

        layout_dn = QHBoxLayout()
        layout_dn.setAlignment(Qt.AlignLeft)

        self.cmb_day_or_night.setMinimumWidth(Sizes.widget_min_width)
        self.cmb_day_or_night.addItems(["Только день", "День и ночь"])
        self.cmb_day_or_night.setMinimumHeight(Sizes.widget_min_height)
        self.cmb_day_or_night.currentIndexChanged.connect(self.set_day_or_night)
        layout_dn.addWidget(self.cmb_day_or_night)
        layout_dn.addSpacing(15)

        layout_load = QHBoxLayout()
        layout_load.setAlignment(Qt.AlignRight)
        layout_load.addStretch()
        self.btn_load_data.setMinimumWidth(Sizes.widget_min_width)
        self.btn_load_data.setMinimumHeight(Sizes.widget_min_height)
        self.btn_load_data.setText("Загрузить данные")
        self.btn_load_data.clicked.connect(self.forecast_thread)
        layout_load.addWidget(self.btn_load_data)
        layout_load.insertSpacing(0, 30)

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
        layout_top_up.addLayout(layout_today)
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
        self.statusBar().addPermanentWidget(self.status_icon_label)
        self.statusBar().addPermanentWidget(self.status_label, stretch=1)

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

        if Path(selected_dir) != Path('..'):
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
