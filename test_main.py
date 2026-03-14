import sys
from PyQt6.QtWidgets import QApplication
from main import QuMailClient

def my_excepthook(type, value, tback):
    import traceback
    with open("crash.log", "w") as f:
        traceback.print_exception(type, value, tback, file=f)
    sys.__excepthook__(type, value, tback)

sys.excepthook = my_excepthook

app = QApplication(sys.argv)
window = QuMailClient('hacker@darknet.io')
window.show()
sys.exit(app.exec())
