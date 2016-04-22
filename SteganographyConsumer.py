import sys
from os.path import splitext
from PySide.QtGui import *
from SteganographyGUI import *
from functools import partial
from PySide.QtCore import *
from scipy.misc import *
from Steganography import *



class SteganographyConsumer(QMainWindow, Ui_MainWindow):

    def __init__(self,parent=None):
        super(SteganographyConsumer, self).__init__(parent)
        self.setupUi(self)
        # Get the views that are required to have the drag-and-drop enabled.
        views = [self.viewPayload1, self.viewCarrier1, self.viewCarrier2]
        accept = lambda e: e.accept()

        for view in views:
            # We need to accept the drag event to be able to accept the drop.
            view.dragEnterEvent = accept
            view.dragMoveEvent = accept
            view.dragLeaveEvent = accept

            # Assign an event handler (a method,) to be invoked when a drop is performed.
            view.dropEvent = partial(self.processDrop, view)

        # NOTE: The line above links "all" views to the same function, and passes the view as a parameter in the
        # function. You could pass more than one widget to the function by adding more parameters to the signature,
        # in case you want to bind more than one widget together. you can even pass in another function, as a parameter,
        # which might significantly reduce the size of your code. Finally, if you prefer to have a separate function
        # for each view, where the view name is, say, "someView", you will need to:
        # 1- Create a function with a definition similar: funcName(self, e)
        # 2- Assign the function to be invoked as the event handler:
        #   self.someView.dropEvent = self.funcName
        self.lblLevel.setEnabled(False)
        self.txtPayloadSize.setEnabled(False)
        self.slideCompression.setEnabled(False)
        self.chkApplyCompression.stateChanged.connect(self.checked)
        self.slideCompression.valueChanged.connect(self.slidechange)
        self.payload=None
        self.carrier=None
        self.btnSave.setEnabled(False)
        self.btnSave.pressed.connect(self.embed)
        self.btnExtract.pressed.connect(self.extract)
        self.btnClean.pressed.connect(self.clean)
    def slidechange(self,value):
        self.txtCompression.setText(str(value))
        if  self.payload == None:
            return
        self.calculatePayloadSize(self.slideCompression.value())

    def processDrop(self, view, e):
        """
        Process a drop event when it occurs on the views.
        """
        mime = e.mimeData()

        # Guard against types of drops that are not pertinent to this app.
        if not mime.hasUrls():
            return

        # Obtain the file path using the OS format.
        self.filePath = mime.urls()[0].toLocalFile()
        filePath=self.filePath
        _, ext = splitext(filePath)

        if not ext == ".png":
            return

        pic=QPixmap(filePath)
        scene = QGraphicsScene()
        image=scene.addPixmap(pic)
        view.setScene(scene)
        view.fitInView(image,Qt.KeepAspectRatio)

        if view is self.viewPayload1:
            self.chkApplyCompression.setCheckState(Qt.Unchecked)
            self.slideCompression.setValue(0)
            self.lblLevel.setEnabled(False)
            self.txtPayloadSize.setEnabled(False)
            self.img=imread(filePath)
            self.payload=Payload(self.img)


            self.calculatePayloadSize(-1)
            if self.carrier != None and self.payload != None:
                self.btnSave.setEnabled(True)

        elif view is self.viewCarrier1:

            self.img2=imread(filePath)
            self.carrier=Carrier(self.img2)


            self.calculateCarrierSize()

            if self.carrier.payloadExists():
                self.lblPayloadFound.setText(">>>>Payload Found<<<<")
                self.lblPayloadFound.setVisible(True)
                self.chkOverride.setEnabled(True)

            else:
                self.lblPayloadFound.setVisible(False)
                self.chkOverride.setEnabled(False)
                self.chkOverride.setCheckState(Qt.Unchecked)
            if self.carrier != None and self.payload != None:
                self.btnSave.setEnabled(True)


        elif view is self.viewCarrier2:
            self.img3=imread(filePath)
            self.carrierTab2=Carrier(self.img3)


            self.checkCarrier()




    def checked(self):
        if self.chkApplyCompression.isChecked() == True:
            self.slideCompression.setEnabled(True)
            self.lblLevel.setEnabled(True)
            self.txtPayloadSize.setEnabled(True)
            self.txtCompression.setEnabled(True)
            if self.payload is not None:
                self.calculatePayloadSize(self.slideCompression.value())
        else:
            self.slideCompression.setEnabled(False)
            self.lblLevel.setEnabled(False)
            self.txtPayloadSize.setEnabled(False)
            self.txtCompression.setEnabled(False)
            if self.payload is not None:
                self.calculatePayloadSize(-1)


    def calculatePayloadSize(self,compressionLevel):
        self.payload.generateXML(self.img,compressionLevel)
        payloadsize=len(self.payload.xml)
        self.txtPayloadSize.setText(str(payloadsize))

    def calculateCarrierSize(self):
        if len(self.carrier.img.shape) ==3:
            carriersize=self.carrier.img.shape[0]*self.carrier.img.shape[1]*self.carrier.img.shape[2]
        else:
            carriersize=self.carrier.img.shape[0]*self.carrier.img.shape[1]
        self.txtCarrierSize.setText(str(int(carriersize/8)))


    def embed(self):
        if self.checkValid():
            new=self.carrier.embedPayload(self.payload,self.chkOverride.isChecked())
            filePath, _ = QFileDialog.getSaveFileName(self, caption='open PNG file', filter="PNG files (*.png)")

            if not filePath:
                return
            imsave(filePath,new)

    def checkValid(self):
        if int(self.txtCarrierSize.text()) < int(self.txtPayloadSize.text()):
            return False
        if self.carrier.payloadExists() and not self.chkOverride.isChecked():
            return False
        return True


    def checkCarrier(self):
        if not self.carrierTab2.payloadExists():
            self.lblCarrierEmpty.setText(">>>>Carrier Empty<<<<")
            self.btnExtract.setEnabled(False)
            self.btnClean.setEnabled(False)

        else:
            self.btnExtract.setEnabled(True)
            self.btnClean.setEnabled(True)
            self.lblCarrierEmpty.setText("")


    def extract(self):
        new=self.carrierTab2.extractPayload()
        width = new.img.shape[1]
        height = new.img.shape[0]

        if len(new.img.shape)==3:
            img = QtGui.QImage(new.img, width, height, QtGui.QImage.Format_RGB888)
        else:
            img=QtGui.QImage(new.img, width, height, QtGui.QImage.Format_Indexed8)
        pix = QtGui.QPixmap.fromImage(img)
        scene = QGraphicsScene()
        image=scene.addPixmap(pix)
        self.viewPayload2.setScene(scene)
        self.viewPayload2.fitInView(image,Qt.KeepAspectRatio)

    def clean(self):
        cleaned=self.carrierTab2.clean()
        imsave(self.filePath,cleaned)
        scene=self.viewPayload2.scene()
        scene.clear()
        self.btnClean.setEnabled(False)
        self.btnExtract.setEnabled(False)
        self.lblCarrierEmpty.setText(">>>>Carrier Empty<<<<")
if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = SteganographyConsumer()

    currentForm.show()
    currentApp.exec_()