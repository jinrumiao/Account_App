#############################################################################
# 版本管控：
# Version: 20230501
# release date: 20230516
#############################################################################


from UI3 import *

if __name__ == "__main__":
    # Initial Qt application
    app = QApplication(sys.argv)

    # QWidget
    widget = Widget()  # QMainWindow using QWidget as central widget

    window = MainWindow(widget)
    window.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)

    # Execute application
    sys.exit(app.exec())
