
import sys
import vtk
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util.misc import vtkGetDataRoot
from app import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.read_dicom)
        self.ui.comboBox.activated.connect(self.rendring_mode)
        self.ui.horizontalSlider.valueChanged.connect(self.iso_value)
        self.skinExtractor = vtk.vtkContourFilter()

    def surface_rendring (self):

        iren = QVTKRenderWindowInteractor()
        renWin = iren.GetRenderWindow()
        aRenderer = vtk.vtkRenderer()
        renWin.AddRenderer(aRenderer) 

        self.skinExtractor.SetInputConnection(self.reader.GetOutputPort())
        self.skinExtractor.SetValue(0, 500)
        self.skinNormals = vtk.vtkPolyDataNormals()
        self.skinNormals.SetInputConnection(self.skinExtractor.GetOutputPort())
        self.skinNormals.SetFeatureAngle(60.0)
        self.skinMapper = vtk.vtkPolyDataMapper()
        self.skinMapper.SetInputConnection(self.skinNormals.GetOutputPort())
        self.skinMapper.ScalarVisibilityOff()
        skin = vtk.vtkActor()
        skin.SetMapper(self.skinMapper)

        aCamera = vtk.vtkCamera()
        aCamera.SetViewUp(0, 0, -1)
        aCamera.SetPosition(0, 1, 0)
        aCamera.SetFocalPoint(0, 0, 0)
        aCamera.ComputeViewPlaneNormal()

        aRenderer.AddActor(skin)
        aRenderer.SetActiveCamera(aCamera)
        aRenderer.ResetCamera()
        aCamera.Dolly(1)

        aRenderer.SetBackground(0, 0, 0)
        renWin.SetSize(640, 480)
        aRenderer.ResetCameraClippingRange()

        # Interact with the data.
        iren.Initialize()
        renWin.Render()
        iren.Start()
        iren.show()
    
    def casting_rendring(self):
        iren = QVTKRenderWindowInteractor()
        renWin = iren.GetRenderWindow()
        ren = vtk.vtkRenderer()
        renWin.AddRenderer(ren) 

        # ren = vtk.vtkRenderer()
        # renWin = vtk.vtkRenderWindow()
        # renWin.AddRenderer(ren)
        # iren = vtk.vtkRenderWindowInteractor()
        # iren.SetRenderWindow(renWin)

        volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
        volumeMapper.SetInputConnection(self.reader.GetOutputPort())
        volumeMapper.SetBlendModeToComposite()

        volumeColor = vtk.vtkColorTransferFunction()
        volumeColor.AddRGBPoint(0,    0.0, 0.0, 0.0)
        volumeColor.AddRGBPoint(500,  1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1000, 1.0, 0.5, 0.3)
        volumeColor.AddRGBPoint(1150, 1.0, 1.0, 0.9)

        volumeScalarOpacity = vtk.vtkPiecewiseFunction()
        volumeScalarOpacity.AddPoint(0,    0.00)
        volumeScalarOpacity.AddPoint(500,  0.15)
        volumeScalarOpacity.AddPoint(1000, 0.15)
        volumeScalarOpacity.AddPoint(1150, 0.85)

        volumeGradientOpacity = vtk.vtkPiecewiseFunction()
        volumeGradientOpacity.AddPoint(0,   0.0)
        volumeGradientOpacity.AddPoint(90,  0.5)
        volumeGradientOpacity.AddPoint(100, 1.0)

        volumeProperty = vtk.vtkVolumeProperty()
        volumeProperty.SetColor(volumeColor)
        volumeProperty.SetScalarOpacity(volumeScalarOpacity)
        volumeProperty.SetGradientOpacity(volumeGradientOpacity)
        volumeProperty.SetInterpolationTypeToLinear()
        volumeProperty.ShadeOn()
        volumeProperty.SetAmbient(0.4)
        volumeProperty.SetDiffuse(0.6)
        volumeProperty.SetSpecular(0.2)

        volume = vtk.vtkVolume()
        volume.SetMapper(volumeMapper)
        volume.SetProperty(volumeProperty)

        ren.AddViewProp(volume)

        camera =  ren.GetActiveCamera()
        c = volume.GetCenter()
        camera.SetFocalPoint(c[0], c[1], c[2])
        camera.SetPosition(c[0] + 500, c[1], c[2])
        camera.SetViewUp(0, 0, -1)

        renWin.SetSize(640, 480)

        iren.Initialize()
        renWin.Render()
        iren.Start()
        iren.show()

    def read_dicom (self):
        path=QFileDialog.getExistingDirectory(self, 'Choose DICOM Directory') + '/'
        self.reader = vtk.vtkDICOMImageReader()
        self.reader.SetDirectoryName(path)
        self.reader.Update()
      
    def rendring_mode (self):
        rendmd = self.ui.comboBox.currentIndex()

        if rendmd == 1:
            self.surface_rendring()

        elif rendmd == 2:
            self.casting_rendring() 
    
    def iso_value (self):
        val = self.ui.horizontalSlider.value()
        iren = QVTKRenderWindowInteractor()
        self.skinExtractor.SetValue(0, val)
        iren.update()



def main():
    path = os.getcwd()
    os.chdir(path + '/data')
    directory = os.getcwd()
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()        