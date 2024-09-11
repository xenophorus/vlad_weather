from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QSize, Qt

'''
TODO
Weather class gets only one forecast at a time. Gather? Async?
progressbar alpha? Over? gets forecast 
write and read class 

'''


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.win_x = 700
        self.win_y = 500
        self.setWindowTitle("Погода по районам Владивостока")
        self.setMinimumSize(QSize(self.win_x, self.win_y))


async def main():
    app = QApplication([])
    window = Gui()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
