#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import serial
import time
from ctypes import *
from PyQt4 import QtGui
from PyQt4.QtCore import QTimer
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.button_calibration = QtGui.QPushButton('Calibration')
        self.button_calibration.clicked.connect(self.calibration)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button_calibration)
        self.setLayout(layout)

        self.axis_L = self.figure.add_subplot(121)
        self.axis_L.axis([-0.20, 0.10, -0.15, 0.15])
        self.axis_L.set_aspect('equal', 'datalim')
        self.im_L = []
        self.axis_R = self.figure.add_subplot(122)
        self.axis_R.axis([-0.10, 0.20, -0.15, 0.15])
        self.axis_R.set_aspect('equal', 'datalim')
        self.im_R = []

        self.offset_L = [0,0,0,0,0,0]
        self.offset_R = [0,0,0,0,0,0]
        self.measured_value_L = [0,0,0,0,0,0]
        self.measured_value_R = [0,0,0,0,0,0]
        self.calibrated_value_L = [0,0,0,0,0,0]
        self.calibrated_value_R = [0,0,0,0,0,0]
        self.pos_L = [0,0]
        self.pos_R = [0,0]
        self.force_L = 0
        self.force_R = 0

        self.serial_L = serial.Serial(port="/dev/ttyACM0", baudrate=460800, timeout=0)
        self.serial_R = serial.Serial(port="/dev/ttyACM1", baudrate=460800, timeout=0)
        time.sleep(1)
        start_signal = bytes.fromhex('100204FF32001003CA')
        self.serial_L.write(start_signal)
        self.serial_R.write(start_signal)

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(20)

    def calibration(self):
        for i in range(6):
            self.offset_L[i] = self.measured_value_L[i]
        for i in range(6):
            self.offset_R[i] = self.measured_value_R[i]

    def update(self):
        MAX_FORCE_N = 1000.0
        MAX_TORQUE_Nm = 30.0
        MAX_VALUE = 10000
        index = 0

        read_data_L = self.serial_L.read(1000)
        data_L = [0] * 16
        while read_data_L[index] != 0x10 or read_data_L[index+1] != 0x02:
            index += 1
        d = 0
        for i in range(16):
            if read_data_L[index + i + d + 2] == 0x10:
                d += 1
            data_L[i] = read_data_L[index + i + d + 2]
        for i in range(6):
            self.measured_value_L[i] = data_L[i * 2 + 4] + data_L[i * 2 + 5] * 0x100
            if self.measured_value_L[i] >= 0x8000:
                self.measured_value_L[i] = self.measured_value_L[i] - 0x10000
        for i in range(3):
            self.measured_value_L[i] = MAX_FORCE_N * self.measured_value_L[i] / MAX_VALUE
        for i in range(3):
            self.measured_value_L[i+3] = MAX_TORQUE_Nm * self.measured_value_L[i+3] / MAX_VALUE
        for i in range(6):
            self.calibrated_value_L[i] = self.measured_value_L[i] - self.offset_L[i]
        self.force_L = -1 * self.calibrated_value_L[2]
        if self.force_L > 5:
            self.pos_L[0] = self.calibrated_value_L[3] / self.force_L
            self.pos_L[1] = self.calibrated_value_L[4] / self.force_L
        else:
           self.force_L = 0

#        print(str(len(read_data_L)) + ": " + str(self.pos_L) + ", " + str(self.force_L))
        
        index = 0
        read_data_R = self.serial_R.read(1000)
        data_R = [0] * 16
        while read_data_R[index] != 0x10 or read_data_R[index+1] != 0x02:
            index += 1
        d = 0
        for i in range(16):
            if read_data_R[index + i + d + 2] == 0x10:
                d += 1
            data_R[i] = read_data_R[index + i + d + 2]
        for i in range(6):
            self.measured_value_R[i] = data_R[i * 2 + 4] + data_R[i * 2 + 5] * 0x100
            if self.measured_value_R[i] >= 0x8000:
                self.measured_value_R[i] = self.measured_value_R[i] - 0x10000
        for i in range(3):
            self.measured_value_R[i] = MAX_FORCE_N * self.measured_value_R[i] / MAX_VALUE
        for i in range(3):
            self.measured_value_R[i+3] = MAX_TORQUE_Nm * self.measured_value_R[i+3] / MAX_VALUE
        for i in range(6):
            self.calibrated_value_R[i] = self.measured_value_R[i] - self.offset_R[i]
        self.force_R = -1 * self.calibrated_value_R[2]
        if self.force_R > 5:
            self.pos_R[0] = -1 * self.calibrated_value_R[3] / self.force_R
            self.pos_R[1] = -1 * self.calibrated_value_R[4] / self.force_R
        else:
           self.force_R = 0

        self.plot()

    def plot(self):
        if len(self.im_L) > 0:
            self.im_L[0].remove()
            self.im_L.pop()
        self.im_L.append(self.axis_L.scatter(self.pos_L[0], self.pos_L[1], s=self.force_L * 10))

        if len(self.im_R) > 0:
            self.im_R[0].remove()
            self.im_R.pop()
        self.im_R.append(self.axis_R.scatter(self.pos_R[0], self.pos_R[1], s=self.force_R * 10))

        self.canvas.draw()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.showMaximized()
    main.show()

    sys.exit(app.exec_())

