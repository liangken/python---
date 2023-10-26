# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 21:44:45 2022

@author: User
"""

import sys
from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal
import cv2
import math
import numpy as np
from scipy.ndimage import gaussian_filter
import time
import arduino_pyserial_and_2servo as Servo
from PIL import Image, ImageDraw, ImageFont
case_path=cv2.data.haarcascades+'haarcascade_frontalface_default.xml'
faceCascade=cv2.CascadeClassifier(case_path)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('id0-picture_gray/train.yml')
names = ['Yu_Hong', 'Mom', 'none'] 
class textForm(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        qss = """
            font: 50 20pt "Microsoft YaHei UI";
            font-weight: bold;
            color: rgb(255, 255, 255);
            text-align:left;
            height:30;
        """
        self.setStyleSheet(qss)
class scrollbarForm(QtWidgets.QScrollBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(500, 30)
        self.setMaximum(255)
        self.setValue(125.5)
        self.setStyleSheet("QScrollBar"
                                 "{"
                                 "background : lightgreen;"
                                 "}"
                                 "QScrollBar::handle"
                                 "{"
                                 "background : pink;"
                                 "}"
                                 "QScrollBar::handle::pressed"
                                 "{"
                                 "background : red;"
                                 "}"
                                 )
    
class pushButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(200, 50)

        self.color1 = QtGui.QColor(240, 53, 218)
        self.color2 = QtGui.QColor(99, 245, 132)

        self._animation = QtCore.QVariantAnimation(
            self,
            valueChanged=self._animate,
            startValue=0.00001,
            endValue=0.9999,
            duration=250
        )

    def _animate(self, value):
        qss = """
            font: 50 30pt "Microsoft YaHei UI";
            font-weight: bold;
            color: rgb(255, 255, 255);
            border-style: solid;
            border-radius:21px;
        """
        grad = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});".format(
            color1=self.color1.name(), color2=self.color2.name(), value=value
        )
        qss += grad
        self.setStyleSheet(qss)

    def enterEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self._animation.start()
        super().enterEvent(event)

class MainWindow(QtWidgets.QWidget):
    number=0
    image_path ="D:\python_code\opencv_saveimage\image"
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1000, 900)    
        self.setStyleSheet("background-color: black;")
        self.VBL = QtWidgets.QVBoxLayout()
        self.VBL.setGeometry(QtCore.QRect(50, 20, 600, 800))
        self.FeedLabel = QtWidgets.QLabel()
        self.VBL.addWidget(self.FeedLabel,0,Qt.AlignCenter|Qt.AlignTop)        
        self.VHL =QtWidgets.QHBoxLayout()
        self.VHL.addStretch(2)
        self.CancelBTN=pushButton()
        self.CancelBTN.setText("Stop")
        #self.CancelBTN = QtWidgets.QPushButton("Cancel")
        #self.CancelBTN.setFont(QFont('Times', 30))
        self.CancelBTN.clicked.connect(self.CancelFeed)
        self.VHL.addWidget(self.CancelBTN,0,Qt.AlignCenter)
        #self.RecordBTN = QtWidgets.QPushButton("Record")
        #self.RecordBTN.setFont(QFont('Times', 30))
        self.RecordBTN=pushButton()
        self.RecordBTN.setText("Record")
        self.RecordBTN.clicked.connect(self.videorecord)
        self.VHL.addWidget(self.RecordBTN,0,Qt.AlignCenter)
        #self.CaptureBTN = QtWidgets.QPushButton("Capture")
        #self.CaptureBTN.setFont(QFont('Times', 30))
        self.CaptureBTN=pushButton()
        self.CaptureBTN.setText("Capture")
        self.CaptureBTN.clicked.connect(self.Saveimage)
        self.VHL.addWidget(self.CaptureBTN,0,Qt.AlignCenter)
        #self.EnterBTN = QtWidgets.QPushButton("Start")
        #self.EnterBTN.setFont(QFont('Times', 30))
        self.EnterBTN=pushButton()
        self.EnterBTN.setText("Start")
        self.EnterBTN.clicked.connect(self.RestartFeed)
        self.VHL.addWidget(self.EnterBTN,0,Qt.AlignCenter) 
        self.VHL.addStretch(2)
        
        self.Imagesetting =QtWidgets.QHBoxLayout()
        self.settingtext = QtWidgets.QVBoxLayout()
        self.settingscrollbar = QtWidgets.QVBoxLayout()
        self.brightness=textForm()
        self.brightness.setText('Brightness')
        self.contrast=textForm()
        self.contrast.setText('Contrast')
        self.crispening=textForm()
        self.crispening.setText('Crispening')
        
        self.settingtext.addWidget(self.brightness,0,Qt.AlignLeft| Qt.AlignTop)
        self.settingtext.addWidget(self.contrast,0,Qt.AlignLeft| Qt.AlignTop)
        self.settingtext.addWidget(self.crispening,0,Qt.AlignLeft| Qt.AlignTop)  
        
        self.scrollbar1 = scrollbarForm(Qt.Horizontal)
        self.scrollbar1.valueChanged.connect(self.scrollbar_1)
        self.scrollbar2 = scrollbarForm(Qt.Horizontal)
        self.scrollbar2.valueChanged.connect(self.scrollbar_2)
        self.scrollbar3 = scrollbarForm(Qt.Horizontal)
        
        self.scrollbar3.setValue(125)
        self.scrollbar3.valueChanged.connect(self.scrollbar_3)
        self.settingscrollbar.addWidget(self.scrollbar1,0,Qt.AlignLeft| Qt.AlignTop)
        self.settingscrollbar.addWidget(self.scrollbar2,0,Qt.AlignLeft| Qt.AlignTop)
        self.settingscrollbar.addWidget(self.scrollbar3,0,Qt.AlignLeft| Qt.AlignTop)
        self.Imagesetting.addStretch(2)
        self.Imagesetting.addLayout(self.settingtext)
        self.Imagesetting.addStretch(1)
        self.Imagesetting.addLayout(self.settingscrollbar)
        self.Imagesetting.addStretch(2)
        
        
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.VBL.addLayout(self.VHL)
        self.VBL.addLayout(self.Imagesetting)
        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))
    def CancelFeed(self):
        self.Worker1.stop()
    def RestartFeed(self):
        self.Worker1.start()
    def Saveimage(self):
        image=self.Worker1.imagecapture()
        imagesave=self.image_path+str(self.number)+'.jpg'
        cv2.imwrite(imagesave,image)
        print('image'+str(self.number)+'.jpg'+' has been saved')
        self.number+=1     
    def videorecord(self):
        self.Worker1.record_state=not self.Worker1.record_state 
        if(self.Worker1.record_state):
            if(self.Worker1.video!=0):
                self.Worker1.video+=1
            self.RecordBTN.setText("Ending")
            self.Worker1.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.Worker1.videosave=Worker1.video_path+str(self.Worker1.video)+'.mp4'
            self.Worker1.out = cv2.VideoWriter(self.Worker1.videosave,self.Worker1.fourcc, 20, (640, 480))
        else:
            self.RecordBTN.setText("Record")
            self.Worker1.out.release()
    def scrollbar_1(self):
        value = self.scrollbar1.value()
        print('scrollbar1 value is '+str(value))
        self.Worker1.gamma=math.exp(-(value-125)/40)
    def scrollbar_2(self):
        value = self.scrollbar2.value()
        print('scrollbar2 value is '+str(value))
        self.Worker1.contrast=(value-125)/255
    def scrollbar_3(self):
        value = self.scrollbar3.value()
        print('scrollbar3 value is '+str(value))
        self.Worker1.crispening=1+2*int(value/15)
class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    record_state=False
    video_path ="video"
    video=0
    gamma=1
    contrast=0
    crispening=17
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    videosave=video_path+str(video)+'.mp4'
    out = cv2.VideoWriter(videosave,fourcc, 20, (640, 480))           
    def run(self):
        self.ThreadActive = True  
        Capture = cv2.VideoCapture(0) 
        while self.ThreadActive: 
            ret, frame = Capture.read()
            if ret:
                FlippedImage = cv2.flip(frame, 1)
                Image = cv2.cvtColor(FlippedImage, cv2.COLOR_BGR2RGB)
                gray = cv2.cvtColor(FlippedImage,cv2.COLOR_BGR2GRAY)               
                faces=faceCascade.detectMultiScale(Image,scaleFactor=1.1,minNeighbors=5,flags=0,minSize=(30,30),maxSize=(400,400))
                count=0
                xtol=0
                ytol=0
                for(x,y,h,w) in faces:
                    index, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                    cv2.rectangle(Image,(x,y),(x+w,y+h),(128,255,0),2)
                    if (confidence < 100):
                        name = names[index]
                        confidence = str(100 - round(confidence)) +"%"
                    else:
                        name = names[-1]
                        confidence = str(100 - round(confidence)) +"%" 
                    cv2.putText(Image, str(name), (x+5,y-5), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 255), 1, cv2.LINE_AA)
                    cv2.putText(Image, str(confidence), (x+5,y+h-5), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 255), 1, cv2.LINE_AA)
                    count=count+1
                    xtol=xtol+x+w/2
                    ytol=ytol+y+h/2
                if(count!=0):
                    xloc=xtol/count
                    yloc=ytol/count
                    if xloc>400:
                        Servo.servo_control('left')
                    elif xloc<240:
                        Servo.servo_control('right')
                    if yloc>280:
                        Servo.servo_control('down')
                    elif yloc<200:
                        Servo.servo_control('up')
                
                brightness_image=255*(Image/(255))**self.gamma
                    #brightness_image=np.array(brightness_image, dtype=np.uint8)
                k = math.tan((45 + 44 * self.contrast) / 180 * math.pi)
                contrast_image = (brightness_image - 127.5)*k+ 127.5 
                contrast_image= np.clip(contrast_image, 0, 255).astype(np.uint8)
                blur_img = cv2.GaussianBlur(contrast_image, (0,0), self.crispening)
                crispening_image= cv2.addWeighted(contrast_image, 1.0, blur_img,-0.38, 0)
                           
                self.image=cv2.cvtColor(crispening_image, cv2.COLOR_BGR2RGB)
                if (self.record_state):
                    print('recording')                
                    self.out.write(self.image)
                    cv2.waitKey(2)
                ConvertToQtFormat = QImage(crispening_image.data,crispening_image.shape[1],crispening_image.shape[0], QImage.Format_RGB888)
                self.Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(self.Pic)
                cv2.waitKey(1)
            self.out.release()        
        
    def stop(self):
        self.ThreadActive = False
    def imagecapture(self):
        return self.image
         
if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())