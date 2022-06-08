from PyQt5 import QtWidgets, QtGui, QtCore
from flask import g
from regex import P
from UI import Ui_MainWindow
import HSV_peak2
import test_peak_ds
import keyboard
import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        # in python3, super(Class, self).xxx = super().xxx
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_control()
        self.hsv_list=[]

    def setup_control(self):
        # TODO
        self.ui.pushButton.clicked.connect(self.buttonClicked1)
        self.ui.pushButton_2.clicked.connect(self.buttonClicked2)
        self.ui.pushButton_3.clicked.connect(self.but3)
        self.ui.pushButton_4.clicked.connect(self.buttonClicked2)


    def buttonClicked1(self):
        self.p1,self.p2,self.p3,self.p4,self.p5,self.p6=HSV_peak2.hsv_ids()
        for i in range(1,7):
            exec(f"self.hsv_list.append(self.p{i})")
        s="h_min: " + str(self.hsv_list[0])+ " h_max: " + str(self.hsv_list[1]) + " s_min: " + str(self.hsv_list[2]) + " s_max: " + str(self.hsv_list[3]) + " v_min: " + str(self.hsv_list[4]) + " v_max: "+str(self.hsv_list[5])
        self.ui.textBrowser_2.setText(str(s))
        print(self.hsv_list)
        
    def buttonClicked2(self):
        print("鍵盤輸入 q ")
        self.ui.textBrowser_2.setText("請先鍵盤輸入 q 終止")
        #,h_min,h_max,s_min,s_max,v_min,v_max
        
    def but3(self):
        self.tsu=test_peak_ds.test_sdls(self.hsv_list[0],self.hsv_list[2],self.hsv_list[4],self.hsv_list[1],self.hsv_list[3],self.hsv_list[5])
        if self.tsu==0:
            self.ui.textBrowser_2.setText("請關閉")
    

        

        

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
