"""
author: Evans Djangbah
date: 4/11/2017 12:46
"""

import os
from sys import argv
import time
# from multiprocessing import Process
from threading import Thread

from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationalToolbar
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QFileDialog,
                             QGridLayout, QLabel, QLineEdit, QPushButton,
                             QTextBrowser, QWidget)
from xlrd import open_workbook

from rainflow import rainflow


class MainWindow(QWidget):
    """
    Class for making the GUI and running the rainflow program
    """

    def __init__(self):
        """
        Initializing class
        """
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Laying out GUI
        """
        self.setWindowTitle('Rainflow Counting')
        icon = QIcon('KNUST.ico')
        self.setWindowIcon(icon)

        base_layout = QGridLayout()
        self.setLayout(base_layout)

        file_label = QLabel('File')
        self.file_text_box = QLineEdit()
        self.file_text_box.setReadOnly(True)
        self.file_text_box.setMinimumWidth(400)
        file_label.setBuddy(self.file_text_box)
        self.browse_button = QPushButton('Open')
        self.browse_button.setMaximumSize(100, 25)
        self.browse_button.clicked.connect(self.open)
        self.browse_button.setAutoDefault(True)
        self.run_btn = QPushButton('Run')
        self.run_btn.clicked.connect(self.run)
        self.run_btn.setMaximumSize(100, 25)
        self.run_btn.setEnabled(False)
        self.run_btn.setAutoDefault(True)
        self.text_browser = QTextBrowser()
        self.text_browser.setMinimumWidth(300)
        self.text_browser.setMaximumWidth(400)
        base_layout.addWidget(file_label, 0, 0, 1, 1)
        base_layout.addWidget(self.file_text_box, 0, 1, 1, 2)
        base_layout.addWidget(self.browse_button, 0, 3, 1, 1)
        base_layout.addWidget(self.run_btn, 2, 3, 1, 1)
        base_layout.addWidget(self.text_browser, 1, 4, 1, 1)
        base_layout.setColumnStretch(4, 0)

        self.fig = Figure()
        self.fig.subplots_adjust(
            top=0.955, bottom=0.095, left=0.077, right=0.967)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        ntb = NavigationalToolbar(self.canvas, self)
        base_layout.addWidget(ntb, 0, 4, 1, 1)
        base_layout.addWidget(self.canvas, 1, 0, 1, 4)

        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def open(self):
        '''
        Select and open file.
        Presents the QFileDialog class and allows the opening of only .xlsx files
        '''
        loc = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH")+"\\Desktop"
        file, ok = QFileDialog.getOpenFileName(
            self, 'Open', loc, 'Excel Workbook (*.xlsx);;Excel 97-2003 Workbook (*.xls)')
        if ok:
            self.file_text_box.setText(file)
            self.run_btn.setEnabled(True)

    def run(self):
        '''
        Evalate results
        '''

        def plot_extrema(self, extremas):
            """
            Plot rainflow on canvas

            INPUT:
            this: A MainWindow class object
            extremes: A list of tuple containing only peak or valleys
            """
            for extrema in extremas:
                # Plot each extrema's data on the axes using the class' plotting mechanism
                extrema.plot(self.axes)
                text = str(extrema.value) + '\t' + str(extrema.position[-1]) + \
                    '\t' + str(extrema.range) + '\t' + '0.5'
                self.text_browser.append(text)

        # Convert excel data into list
        ts = time.time()
        file = self.file_text_box.text()
        book = open_workbook(file)  # Opening the Excel
        sheet = book.sheet_by_index(0)  # Select the first sheet
        row_len = sheet.row_len(0)  # Getting number of columns to loop through
        data = []
        for row in range(row_len):
            data += sheet.col_values(row)

        # Rejecting empty cells
        while '' in data:
            data.remove('')

        # Run rainflow sequence
        sig, peaks, valleys = rainflow(data)  # Run rainflow sequence
        self.axes.cla()  # Clear the plot axis
        # Plot the series data on the axis
        self.axes.plot(sig, 'k', linewidth='3')
        header = 'FROM\tTO\tRANGE\tCYCLES'
        self.text_browser.setText(header)

        # Run independent code of separate threads
        p = Thread(target=plot_extrema, args=(self, peaks))
        v = Thread(target=plot_extrema, args=(self, valleys))

        p.start()
        v.start()
        p.join()
        v.join()

        self.canvas.draw()
        print('Took {}s'.format(time.time() - ts))
        self.plot_range_cycle(peaks, valleys)

    def plot_range_cycle(self, peaks, valleys):
        """
        Plot Number of Cycles against Temperature Range
        """
        cycles = {}
        for peak in peaks:
            if peak.range in cycles.keys():
                cycles[peak.range] += 1
            else:
                cycles[peak.range] = 1
        for valley in valleys:
            if valley.range in cycles.keys():
                cycles[valley.range] += 1
            else:
                cycles[valley.range] = 1
        temp_range = list(cycles.keys())
        temp_range.sort()
        number_of_cycles = []
        for key in temp_range:
            number_of_cycles.append(cycles[key])
        plt.semilogy(temp_range, number_of_cycles)
        plt.xlabel('Temperature Range')
        plt.ylabel('Number of Half Cycles')
        plt.show()


if __name__ == '__main__':
    APP = QApplication(argv)
    MYINSTANCE = MainWindow()
    MYINSTANCE.show()
    APP.aboutToQuit.connect(APP.deleteLater)
    APP.exec_()
