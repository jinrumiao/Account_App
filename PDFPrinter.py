from PySide6.QtCore import (QIODevice, QFile, Qt, QMarginsF, QRect, QPoint)
from PySide6.QtGui import (QPagedPaintDevice, QPdfWriter, QPainter, QFont, QPageSize)
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout


class PDFPrinter(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def WritePDF(self, widget, name):
        pdffile = QFile(name)
        pdffile.open(QIODevice.WriteOnly)

        PDFWriter = QPdfWriter(pdffile)
        PDFWriter.setPageSize(QPageSize.A4)
        PDFWriter.setResolution(72)
        PDFWriter.setPageMargins(QMarginsF(0, 0, 0, 0))
        # print(PDFWriter.resolution())

        PDFPainter = QPainter(PDFWriter)

        font = QFont()
        font.setFamily("simhei.ttf")
        PDFPainter.setFont(font)

        widget.render(PDFPainter, QPoint(0, 0))
        PDFPainter.end()
        pdffile.close()


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.label1 = QLabel("123")
        self.label2 = QLabel("test")
        self.label3 = QLabel("321")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.label3)

        self.setLayout(self.layout)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QFileDialog

    app = QApplication(sys.argv)
    window = Window()
    window.show()

    pdf_writer = PDFPrinter()
    pdf_writer.show()
    name = QFileDialog.getSaveFileName(None, "Save File", "123.pdf", "*.pdf")

    if name[0]:
        print(name[0])
        pdf_writer.WritePDF(window, name[0])

    else:
        pdf_writer.close()

    sys.exit(app.exec())
