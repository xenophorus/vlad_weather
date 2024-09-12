from dataclasses import dataclass

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QScrollArea, QComboBox, QProgressBar, QFrame)
from PySide6.QtCore import QSize, Qt

from PySide6.QtGui import QPalette, QColor

import time

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
    top_widget_min_width: int = 150


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Погода по районам Владивостока")
        self.setMinimumSize(QSize(Sizes.win_x, Sizes.win_y))
        self.cmb_days = QComboBox()
        self.cmb_day_or_night = QComboBox()

        layout_base = QVBoxLayout()
        layout_base.setContentsMargins(5, 5, 5, 5)

        layout_top = QVBoxLayout()

        layout_top_up = QHBoxLayout()

        layout_top_up.setContentsMargins(*Sizes.contents_margins)
        layout_top_up.setSpacing(Sizes.spacing)

        layout_days = QHBoxLayout()
        layout_days.setAlignment(Qt.AlignCenter)
        lbl_combo = QLabel()
        lbl_combo.setText("Дней: ")

        self.cmb_days.setMinimumWidth(50)
        self.cmb_days.addItems(list(map(lambda x: str(x), range(1, 15))))
        self.cmb_days.currentIndexChanged.connect(self._disable_cmb_dn)
        layout_days.addWidget(lbl_combo)
        layout_days.addWidget(self.cmb_days)

        layout_dn = QHBoxLayout()
        layout_dn.setAlignment(Qt.AlignCenter)

        self.cmb_day_or_night.setMinimumWidth(100)
        self.cmb_day_or_night.addItems(["Только день", "День и ночь"])
        layout_dn.addWidget(self.cmb_day_or_night)

        layout_load = QHBoxLayout()
        layout_load.setAlignment(Qt.AlignCenter)
        btn_load_data = QPushButton()
        btn_load_data.setMinimumWidth(120)
        btn_load_data.setText("Загрузить данные")
        btn_load_data.clicked.connect(self.test_progress)
        layout_load.addWidget(btn_load_data)

        layout_address = QHBoxLayout()
        lbl_address = QLabel()
        lbl_address.setMinimumWidth(250)
        layout_address.setAlignment(Qt.AlignRight)
        lbl_address.setText("c:\\program flies\\some folder")

        btn_address = QPushButton()
        btn_address.setText("Выбрать папку")

        layout_address.addWidget(lbl_address)
        layout_address.addWidget(btn_address)

        layout_top_up.addLayout(layout_days)
        layout_top_up.addLayout(layout_dn)
        layout_top_up.addLayout(layout_load)
        layout_top_up.addLayout(layout_address)

        layout_center = QVBoxLayout()
        layout_center.setContentsMargins(*Sizes.contents_margins)
        layout_center.setSpacing(Sizes.spacing)
        layout_base.addLayout(layout_top_up)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 10)
        self.progress.setMaximumHeight(10)
        self.progress.setValue(0)

        layout_base.addWidget(self.progress)

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        for i in range(10):
            layout_h = QHBoxLayout()
            lbl = QLabel()
            lbl.setText(f"label {i}")
            lbl.setMinimumHeight(50)

            btn = QPushButton()
            btn.setText(f"Переместить")
            btn.setMaximumWidth(Sizes.top_widget_min_width)

            layout_h.addWidget(lbl)
            layout_h.addWidget(btn)
            layout_center.addLayout(layout_h)

        layout_center.addStretch()
        layout_base.addLayout(layout_center)

        widget = QWidget()
        scroll_area.setWidget(widget)
        widget.setLayout(layout_base)
        self.setCentralWidget(scroll_area)


    def _disable_cmb_dn(self):
        if self.cmb_days.currentIndex() > 5:
            self.cmb_day_or_night.setCurrentIndex(0)
            self.cmb_day_or_night.setDisabled(True)
        else:
            self.cmb_day_or_night.setEnabled(True)

    def test_progress(self):
        self.progress.setValue(0)
        for i in range(11):
            time.sleep(0.1)
            self.progress.setValue(i)
            time.sleep(0.1)



def main():
    app = QApplication([])
    window = Gui()

    window.show()
    app.exec()


if __name__ == '__main__':
    main()
