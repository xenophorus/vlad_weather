from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QSize, Qt

from PySide6.QtGui import QPalette, QColor

'''
TODO
Weather class gets only one forecast at a time. Gather? Async?
progressbar alpha? Over? gets forecast 
write and read class 

'''

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
        self.win_x = 850
        self.win_y = 500
        self.setWindowTitle("Погода по районам Владивостока")
        self.setMinimumSize(QSize(self.win_x, self.win_y))

        layout_h = QHBoxLayout()
        layout_v = QVBoxLayout()

        layout_h.setContentsMargins(10, 10, 10, 10)
        layout_h.setSpacing(20)

        layout_v.addWidget(Color(0xeeeeaa))
        layout_v.addWidget(Color(0xeeaaee))
        layout_v.addWidget(Color(0xaaeeee))
        layout_h.addLayout(layout_v)

        widget = QWidget()
        widget.setLayout(layout_h)
        self.setCentralWidget(widget)


def main():
    app = QApplication([])
    window = Gui()

    window.show()
    app.exec()


if __name__ == '__main__':
    main()
