import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QListWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QDialog, QFileDialog, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon
from PyPDF4 import PdfFileMerger


class ListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=None)
        self.setAcceptDrops(True)
        self.setStyleSheet('''font-size:25px''')
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else: return super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else: return super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            pdfFiles = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    if url.toString().endswith('.pdf'):
                        pdfFiles.append(str(url.toLocalFile()))
            self.addItems(pdfFiles)
        else: return super().dropEvent(event)


class OutputField(QLineEdit):
    def __init__(self):
        super().__init__()
        self.height = 45
        self.setStyleSheet('''font-size: 20px;''')
        self.setFixedHeight(self.height)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else: event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else: event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            if event.mimeData().urls():
                self.setText(event.mimeData().urls()[0].toLocalFile())
        else: event.ignore()


class Button(QPushButton):
    def __init__(self, label_text):
        super().__init__()
        self.setText(label_text)
        self.setStyleSheet('''
            font-size: 20px;
            width: 180px;
            height: 50;
        ''')


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Слияние PDF-файлов')
        self.setWindowIcon(QIcon('pdf.png'))
        self.initUI()

    def initUI(self):
        self.outputFile = OutputField()

        self.buttonBrowseOutputFile = Button('&Save To')
        self.buttonBrowseOutputFile.clicked.connect(self.populateFileName)
        self.buttonBrowseOutputFile.setFixedHeight(self.outputFile.height)

        outputFolderRow = QHBoxLayout()
        outputFolderRow.addWidget(self.outputFile)
        outputFolderRow.addWidget(self.buttonBrowseOutputFile)

        self.pdfListWidget = ListWidget(self)

        # Buttons
        buttonLayout = QHBoxLayout()
        self.buttonDeleteSelect = Button('&Delete')
        self.buttonDeleteSelect.clicked.connect(self.deleteSelected)
        buttonLayout.addWidget(self.buttonDeleteSelect, 1, Qt.AlignRight)
        self.buttonMerge = Button('&Merge')
        self.buttonMerge.setIcon(QIcon('play_button.jpg'))
        self.buttonMerge.setIconSize(QSize(30, 30))
        self.buttonMerge.clicked.connect(self.mergeFile)
        buttonLayout.addWidget(self.buttonMerge)
        self.buttonClose = Button('&Exit')
        self.buttonClose.clicked.connect(QApplication.quit)
        buttonLayout.addWidget(self.buttonClose)
        self.buttonReset = Button('&Reset')
        self.buttonReset.clicked.connect(self.clearQueue)
        buttonLayout.addWidget(self.buttonReset)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(outputFolderRow)
        mainLayout.addWidget(self.pdfListWidget)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def deleteSelected(self):
        items = self.pdfListWidget.selectedItems()
        if items:
            for item in items:
                self.pdfListWidget.takeItem(self.pdfListWidget.row(item))
        else:
            self.dialogMessage(
                '''<h2 style="color: red;">Нечего удалять.<br> Выберите файл/ы для удаления!</h2>'''
            )

    def clearQueue(self):
        self.pdfListWidget.clear()
        self.outputFile.setText('')

    def populateFileName(self):
        path = self._getSaveFilePath()
        if path:
            self.outputFile.setText(path)

    def dialogMessage(self, message):
        dlg = QMessageBox(self)
        dlg.setWindowTitle('PDF Manager')
        dlg.setIcon(QMessageBox.Information)
        dlg.setText(message)
        dlg.show()

    def _getSaveFilePath(self):
        file_save_path, _ = QFileDialog.getSaveFileName(
            self, 'Save PDF file', '.', 'PDF file (*.pdf)'
        )
        return file_save_path

    def mergeFile(self):
        if not self.outputFile.text():
            # надо выбрать outputFile!
            self.populateFileName()
            return

        if self.pdfListWidget.count() > 0:
            pdfMerger = PdfFileMerger()
            try:
                for i in range(self.pdfListWidget.count()):
                    pdfMerger.append(self.pdfListWidget.item(i).text())
                pdfMerger.write(self.outputFile.text())
                pdfMerger.close()
                self.pdfListWidget.clear()
                self.dialogMessage('<h2 style="color: green;">Слияние PDF завершено!</h2>')
            except Exception as e:
                self.dialogMessage(f'Error: {e}')
        else:
            self.dialogMessage(
                '''<h2 style="color: red;">Нечего объединять.<br> Добавьте файлы для слияни!</h2>'''
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    demo = AppDemo()
    demo.resize(600, 400)
    demo.show()
    sys.exit(app.exec_())
