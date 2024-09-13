from dataclasses import dataclass
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
                               QPushButton, QLabel, QScrollArea, QComboBox, QProgressBar, QFrame, QLineEdit)
from PySide6.QtCore import QSize, Qt
from pathlib import Path
import time
from Settings import settings
from WeatherData import WeatherData

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


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Погода по районам Владивостока")
        self.setMinimumSize(QSize(Sizes.win_x, Sizes.win_y))
        self.cmb_days = QComboBox()
        self.cmb_day_or_night = QComboBox()
        self.progress = QProgressBar()
        self.destination_dir = Path(settings.get_target_folder())
        self.layout_base = QVBoxLayout()
        self.layout_center = QVBoxLayout()

        self.setup_widgets()
        # self.get_forecast()

    def get_forecast(self):
        [self.layout_center.removeItem(x) for x in self.layout_center.children()]
        self.layout_center.update()
        time.sleep(0.5)
        self.progress.setValue(0)
        self.progress.setRange(0, 9)

        for i in range(10):
            time.sleep(0.3)
            layout_h = QHBoxLayout()
            layout_h.setContentsMargins(5, 5, 5, 5)
            lbl = QLabel()
            lbl.setText(f"label {i} {time.time()}")
            lbl.setMinimumHeight(Sizes.widget_min_height)

            btn = QPushButton()
            btn.setText(f"Переместить")
            btn.setMaximumWidth(Sizes.widget_min_width)
            btn.setMinimumHeight(Sizes.widget_min_height)

            layout_h.addWidget(lbl)
            layout_h.addWidget(btn)
            self.layout_center.addLayout(layout_h)
            self.progress.setValue(i)

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
        self.cmb_days.addItems(list(map(lambda x: str(x), range(1, 15))))
        self.cmb_days.currentIndexChanged.connect(self._disable_cmb_dn)
        layout_days.addWidget(lbl_combo)
        layout_days.addWidget(self.cmb_days)

        layout_dn = QHBoxLayout()
        layout_dn.setAlignment(Qt.AlignCenter)

        self.cmb_day_or_night.setMinimumWidth(Sizes.widget_min_width)
        self.cmb_day_or_night.addItems(["Только день", "День и ночь"])
        self.cmb_day_or_night.setMinimumHeight(Sizes.widget_min_height)
        layout_dn.addWidget(self.cmb_day_or_night)

        layout_load = QHBoxLayout()
        layout_load.setAlignment(Qt.AlignRight)
        btn_load_data = QPushButton()
        btn_load_data.setMinimumWidth(Sizes.widget_min_width)
        btn_load_data.setMinimumHeight(Sizes.widget_min_height)
        btn_load_data.setText("Загрузить данные")
        btn_load_data.clicked.connect(self.get_forecast)
        layout_load.addWidget(btn_load_data)

        layout_address = QHBoxLayout()
        layout_address.setContentsMargins(0, 0, 0, 5)
        self.address_line = QLineEdit()
        self.address_line.setMinimumHeight(Sizes.widget_min_height)
        self.address_line.setText(self.destination_dir.as_posix())
        self.lbl_address = QLabel()
        self.lbl_address.setMinimumWidth(250)
        self.lbl_address.setMinimumHeight(Sizes.widget_min_height)
        self.lbl_address.setText(self.destination_dir.as_posix())

        btn_address = QPushButton()
        btn_address.setText("Выбрать папку")
        btn_address.setMaximumWidth(Sizes.widget_min_width)
        btn_address.setMinimumHeight(Sizes.widget_min_height)
        btn_address.clicked.connect(self.get_directory)

        layout_address.addWidget(self.address_line)
        layout_address.addWidget(btn_address)

        layout_top_up.addLayout(layout_days)
        layout_top_up.addLayout(layout_dn)
        layout_top_up.addLayout(layout_load)
        layout_top.addLayout(layout_top_up)
        layout_top.addLayout(layout_address)

        self.layout_center.setContentsMargins(10, 5, 10, 5)
        self.layout_center.setSpacing(Sizes.spacing)
        frame_top.setLayout(layout_top)
        self.layout_base.addWidget(frame_top)
        # layout_base.addLayout(layout_top_up)

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

    def get_directory(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setDirectoryUrl(self.destination_dir.as_posix())
        selected_dir = Path(dialog.getExistingDirectoryUrl().path())

        if Path(selected_dir) != Path('.'):
            self.destination_dir = selected_dir
            self.address_line.setText(selected_dir.as_posix()[1:])
            settings.set_target_folder(selected_dir.as_posix()[1:])

    def _disable_cmb_dn(self):
        if self.cmb_days.currentIndex() > 5:
            self.cmb_day_or_night.setCurrentIndex(0)
            self.cmb_day_or_night.setDisabled(True)
        else:
            self.cmb_day_or_night.setEnabled(True)

    def closeEvent(self, event):
        settings.write_settings()


def main():
    app = QApplication([])
    window = Gui()

    window.show()
    app.exec()


if __name__ == '__main__':
    main()
