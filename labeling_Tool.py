import os
import numpy as np
from numpy import save, load
from scipy import signal
from scipy.signal import butter, lfilter, sosfilt
import pywt
import pyedflib
import codecs
import re

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLabel, QRadioButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseButton, KeyEvent
import matplotlib.pyplot as plt
import random

from dataLoader import DataLoadAndPlot
from label_Tool_ui_v1 import Ui_MainWindow

# used to start : https://www.geeksforgeeks.org/how-to-embed-matplotlib-graph-in-pyqt5/
# main window
# which inherits QDialog


class Window( QtWidgets.QMainWindow, Ui_MainWindow ):

    # constructor
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.saccadeListLoaded = []
        self.blinkListLoaded = []
        self.myData = DataLoadAndPlot()
        
        # fileNameEDF = '..\..\Work\elocans\data Anais\DataWassim\Testdatawassim1.edf'
        # fileNameEDF = '..\..\..\Work\elocans\data Anais\Data Guillaume\eog cerco 06_05_21\Guillaume_060521_2.edf'
        # self.myData.loadDataEDF( fileNameEDF )

        fileNameOpenBCI = '..\\..\\..\\Work\\elocans\\data Wassim\\datas_07_05_21\\julien1\\julien1_OpenBCI_EYES__data.txt'
        # fileNameOpenBCI = '.\wassim1__data.txt'
        self.myData.loadDataOpenBCI( fileNameOpenBCI )
        
        # fileNameTxtSaccade = '..\..\..\Work\elocans\data Anais\Data Guillaume\eog cerco 06_05_21\\Guillaume 060521_2.txt'
        # self.saccadeListLoaded = self.myData.loadTxt( fileNameTxtSaccade )
        # fileNameNPYSaccade = '..\\datas\\arrays\\anais_wassim\\sacTsWas1Dir.npy'
        # self.saccadeListLoaded = load( fileNameNPYSaccade )
        
        # fileNameNPYBlink = '.\\fixTsWas1Comp.npy'
        # self.blinkListLoaded = load( fileNameNPYBlink )

        self.curvesList = []
        self.blinkList = []
        self.blinkSpanList = []
        self.saccadeList = []
        self.saccadeSpanList = []
        self.modeTag = ''
        self.stateMove = 'Idle'

        self.keyTagList = [
            [ 'right', '→' ],
            [ 'left', '←' ],
            [ 'up', '↑' ],
            [ 'down', '↓' ],
            [ 'b', 'b' ]
            # [ 'v', 'V' ],
            # [ '1', 'S' ],
            # [ '2', 'M' ],
            # [ '3', 'L' ]
            ]
   
        # a figure instance to plot on
        self.figure = plt.figure()
   
        # this is the Canvas Widget that 
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        # self.canvas.setFocus()
        self.cid_enter = self.canvas.mpl_connect('axes_enter_event', self.on_enter_event)

        self.toolbar = NavigationToolbar(self.canvas, self)
        print( self.toolbar.toolitems )
   
        # Matplotlib
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
           
        self.widget_Plot.setLayout(layout)

        # self.plotData( fileNameEDF )
        self.plotData( fileNameOpenBCI )

        self.spanFromSaccadeList( self.saccadeListLoaded )

        # eventFile = '..\\..\\Work\\elocans\\data Wassim\\datas_07_05_21\\julien1\\julien1__event_general.txt'
        # self.wassimSaccadeFile( eventFile )
        # self.customSpanPreset()

        self.spanFromBlinkList( self.blinkListLoaded )

        self.tagState = "Idle"
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.canvas.mpl_connect("key_press_event", self.on_keyPressed)

    def checkBoxHAndV( self ) :

        if self.checkBox_HandV.isChecked():
            
            self.curvesList[ 0 ][ 0 ].set_linestyle('solid')
            self.curvesList[ 1 ][ 0 ].set_linestyle('solid')

        else:
            
            self.curvesList[ 0 ][ 0 ].set_linestyle('None')
            self.curvesList[ 1 ][ 0 ].set_linestyle('None')
            
        self.canvas.draw()
        

    def checkBoxDerivatives( self ) :

        if self.checkBox_Derivatives.isChecked():
            
            self.curvesList[ 2 ][ 0 ].set_linestyle('solid')
            self.curvesList[ 3 ][ 0 ].set_linestyle('solid')

        else:
            
            self.curvesList[ 2 ][ 0 ].set_linestyle('None')
            self.curvesList[ 3 ][ 0 ].set_linestyle('None')
            
        self.canvas.draw()

    def checkBoxWavelets( self ) :

        if self.checkBox_Wavelets.isChecked():
            
            self.curvesList[ 4 ][ 0 ].set_linestyle('solid')
            self.curvesList[ 5 ][ 0 ].set_linestyle('solid')

        else:
            
            self.curvesList[ 4 ][ 0 ].set_linestyle('None')
            self.curvesList[ 5 ][ 0 ].set_linestyle('None')
            
        self.canvas.draw()


    def on_enter_event(self, _):
        self.canvas.setFocus()

    def onClikedRdBtn( self ) :

        radioBtn = self.sender()
        if radioBtn.isChecked() :
            self.modeTag = radioBtn.text()

    def on_press(self, event):

        if self.tagState == "Idle" :

            if event.xdata is not None :

                if event.button is MouseButton.LEFT :

                    if self.modeTag == 'Blink' : 

                        indiceSpan = self.testSpanBlinkUnderCursor( event.xdata )

                        if indiceSpan is not None :

                            self.on_pressBlinkModify( event, indiceSpan )

                        else :
                            
                            self.on_pressBlinkCreate( event )

                    elif self.modeTag == 'Saccade' :

                        indiceSpan = self.testSpanSaccadeUnderCursor( event.xdata )

                        if indiceSpan is not None :
                            
                            self.on_pressSaccadeModify( event, indiceSpan )

                        else :

                            self.on_pressSaccadeCreate( event )
                
                elif event.button is MouseButton.RIGHT :

                    if self.stateMove == 'Idle' :

                        self.stateMove = 'ScrollX'
                        self.on_pressScrollX( event )
                        

    def on_pressBlinkCreate( self, event ) :
        self.tagState = "Create"
        self.mySpanstart = event.xdata
        end = event.xdata + 1
        self.blinkSpanList.append( self.plot.axvspan( self.mySpanstart, end, color='green', alpha=0.2 ) )
        self.canvas.draw()

    def on_pressSaccadeCreate( self, event ) :
        self.tagState = "Create"
        self.mySpanstart = event.xdata
        end = event.xdata + 1
        self.saccadeSpanList.append( self.plot.axvspan( self.mySpanstart, end, color='blue', alpha=0.2 ) )
        self.canvas.draw()


    def on_pressBlinkModify( self, event, indiceSpan ) :
        self.tagState = "Modify"
        self.indiceSpan = indiceSpan
        self.firstX = event.xdata

    def on_pressSaccadeModify( self, event, indiceSpan ) :
        self.tagState = "Modify"
        self.indiceSpan = indiceSpan
        self.firstX = event.xdata


    def on_pressScrollX( self,event ) :

        self.xStart = event.xdata



    def on_release(self, event):

        if event.button is MouseButton.LEFT :

            if self.tagState == "Create" :

                if self.modeTag == 'Blink' : 
                    self.on_releaseBlinkCreate( event )
                elif self.modeTag == 'Saccade' :
                    self.on_releaseSaccadeCreate( event )
                    
            if self.tagState == "Modify" :

                if self.modeTag == 'Blink' : 
                    self.on_releaseBlinkModify( event )
                elif self.modeTag == 'Saccade' :
                    self.on_releaseSaccadeModify( event )
                    
        elif event.button is MouseButton.RIGHT :

            if self.stateMove == 'Idle' :

                if event.xdata is not None :

                    if self.modeTag == 'Blink' : 
                        self.deleteSpanBlinkAt( event.xdata )
                    elif self.modeTag == 'Saccade' :
                        self.deleteSpanSaccadeAt( event.xdata )

            elif self.stateMove == 'ScrollX' :

                self.stateMove = 'Idle'
                self.on_releaseScrollX( event )


    def on_releaseBlinkCreate( self, event ) :

        self.tagState = "Idle"
        mySpan = self.blinkSpanList[ -1 ]
        mySpan.remove()
        del self.blinkSpanList[ - 1 ]
        
        end = event.xdata
        
        if end is not None and abs( end - self.mySpanstart ) > 9 :

            self.blinkSpanList.append( [ self.plot.axvspan( self.mySpanstart, end, color='green', alpha=0.2 ), self.plot.text( 0, -400, "" ) ] )

            if self.mySpanstart < end :
                center = self.mySpanstart + ( end - self.mySpanstart ) / 2
                self.blinkList.append( [ self.mySpanstart, end, center, "" ] )
            else :
                center = end + ( self.mySpanstart - end ) / 2
                self.blinkList.append( [ end, self.mySpanstart, center, "" ] )

        self.canvas.draw()

    def on_releaseSaccadeCreate( self, event ) :

        self.tagState = "Idle"
        mySpan = self.saccadeSpanList[ -1 ]
        mySpan.remove()
        del self.saccadeSpanList[ - 1 ]

        end = event.xdata
        
        if end is not None and abs( end - self.mySpanstart ) > 9 :
            
            self.saccadeSpanList.append( [ self.plot.axvspan( self.mySpanstart, end, color='blue', alpha=0.2 ), self.plot.text( 0, -400, "" ) ] )

            if self.mySpanstart < end :
                center = self.mySpanstart + ( end - self.mySpanstart ) / 2
                self.saccadeList.append( [ self.mySpanstart, end, center, "" ] )
            else :
                center = end + ( self.mySpanstart - end ) / 2
                self.saccadeList.append( [ end, self.mySpanstart, center, "" ] )

        self.canvas.draw()


    def on_releaseBlinkModify( self, event ) :

        self.tagState = "Idle"
        start = self.blinkList[ self.indiceSpan ][ 0 ] + event.xdata - self.firstX
        end = self.blinkList[ self.indiceSpan ][ 1 ] + event.xdata - self.firstX
        mySpan = self.blinkSpanList[ self.indiceSpan ][ 0 ]
        mySpan.remove()
        self.blinkSpanList[ self.indiceSpan ][ 0 ] = self.plot.axvspan( start, end, color='green', alpha=0.2 )
        center = start + ( end - start ) / 2
        self.blinkList[ self.indiceSpan ] = [ start, end, center, self.blinkList[ self.indiceSpan ][ 3 ] ]
        self.writeInBlink( self.indiceSpan, center - 100 )
        self.canvas.draw()

    def on_releaseSaccadeModify( self, event ) :

        self.tagState = "Idle"
        start = self.saccadeList[ self.indiceSpan ][ 0 ] + event.xdata - self.firstX
        end = self.saccadeList[ self.indiceSpan ][ 1 ] + event.xdata - self.firstX
        mySpan = self.saccadeSpanList[ self.indiceSpan ][ 0 ]
        mySpan.remove()
        self.saccadeSpanList[ self.indiceSpan ][ 0 ] = self.plot.axvspan( start, end, color='blue', alpha=0.2 )
        center = start + ( end - start ) / 2
        self.saccadeList[ self.indiceSpan ] = [ start, end, center, self.saccadeList[ self.indiceSpan ][ 3 ] ]
        self.writeInSaccade( self.indiceSpan, center - 100 )
        self.canvas.draw()


    def on_releaseScrollX( self, event ) :
        
        if event.xdata is not None :

            diffX = int( self.xStart - event.xdata )
            minPlot = self.plot.get_xlim()[ 0 ] + diffX
            maxPlot = self.plot.get_xlim()[ 1 ] + diffX
            self.plot.set_xlim( left = minPlot, right = maxPlot )
            self.canvas.draw()

            self.toolbar.push_current()



    def on_move(self, event):
        
        if self.stateMove == 'Idle' :

            if event.xdata is not None :

                if self.tagState == "Create" :

                    if self.modeTag == 'Blink' : 
                        self.on_moveBlinkCreate( event )
                    elif self.modeTag == 'Saccade' :
                        self.on_moveSaccadeCreate( event )

                elif self.tagState == "Modify" :

                    if self.modeTag == 'Blink' : 
                        self.on_moveBlinkModify( event )
                    elif self.modeTag == 'Saccade' :
                        self.on_moveSaccadeModify( event )
        
        elif self.stateMove == 'ScrollX' :

                self.on_moveScrollX( event )


    def on_moveBlinkCreate( self, event ) :

        mySpan = self.blinkSpanList[ -1 ]
        mySpan.remove()
        del self.blinkSpanList[ - 1 ]
        end = event.xdata
        self.blinkSpanList.append( self.plot.axvspan( self.mySpanstart, end, color='green', alpha=0.2 ) )
        self.canvas.draw()
        
    def on_moveSaccadeCreate( self, event ) :

        mySpan = self.saccadeSpanList[ -1 ]
        mySpan.remove()
        del self.saccadeSpanList[ - 1 ]
        end = event.xdata
        self.saccadeSpanList.append( self.plot.axvspan( self.mySpanstart, end, color='blue', alpha=0.2 ) )
        self.canvas.draw()


    def on_moveBlinkModify( self, event ) :

        start = self.blinkList[ self.indiceSpan ][ 0 ] + event.xdata -self.firstX
        end = self.blinkList[ self.indiceSpan ][ 1 ] + event.xdata - self.firstX
        mySpan = self.blinkSpanList[ self.indiceSpan ][ 0 ]
        mySpan.remove()
        self.blinkSpanList[ self.indiceSpan ][ 0 ] = self.plot.axvspan( start, end, color='green', alpha=0.2 )
        center = start + ( end - start ) / 2
        self.writeInBlink( self.indiceSpan, center - 100 )
        self.canvas.draw()

    def on_moveSaccadeModify( self, event ) :

        start = self.saccadeList[ self.indiceSpan ][ 0 ] + event.xdata -self.firstX
        end = self.saccadeList[ self.indiceSpan ][ 1 ] + event.xdata -self.firstX
        mySpan = self.saccadeSpanList[ self.indiceSpan ][ 0 ]
        mySpan.remove()
        self.saccadeSpanList[ self.indiceSpan ][ 0 ] = self.plot.axvspan( start, end, color='blue', alpha=0.2 )
        center = start + ( end - start ) / 2
        self.writeInSaccade( self.indiceSpan, center - 100 )
        self.canvas.draw()


    def on_moveScrollX( self, event ) :

        if event.xdata is not None :
            
            diffX = int( self.xStart - event.xdata )
            minPlot = self.plot.get_xlim()[ 0 ] + diffX
            maxPlot = self.plot.get_xlim()[ 1 ] + diffX
            self.plot.set_xlim( left = minPlot, right = maxPlot )
            self.canvas.draw()




    def on_keyPressed( self, event ) :

        if self.tagState == "Idle" :

            if self.modeTag == 'Blink' :

                indiceSpan = self.testSpanBlinkUnderCursor( event.xdata )

                if indiceSpan is not None :
                    
                    self.on_keyBlink( event, indiceSpan )

            if self.modeTag == 'Saccade' :

                indiceSpan = self.testSpanSaccadeUnderCursor( event.xdata )

                if indiceSpan is not None :
                    
                    self.on_keySaccade( event, indiceSpan )

    def on_keyBlink( self, event, indiceSpan ) :

        for keyTag in self.keyTagList :

            if keyTag[ 0 ] == event.key :

                if keyTag[ 0 ] in self.blinkList[ indiceSpan ][ 3 ] :

                    self.blinkList[ indiceSpan ][ 3 ] = self.blinkList[ indiceSpan ][ 3 ].replace( keyTag[ 0 ], "" )
                
                else :

                    self.blinkList[ indiceSpan ][ 3 ] = self.blinkList[ indiceSpan ][ 3 ] + keyTag[ 0 ]

                self.blinkList[ indiceSpan ][ 3 ] = self.rewriteKeyTag( self.blinkList[ indiceSpan ][ 3 ] )
                self.writeInBlink( indiceSpan, self.blinkList[ indiceSpan ][ 2 ] - 100 )
                self.canvas.draw()
                break

    def on_keySaccade( self, event, indiceSpan ) :

        for keyTag in self.keyTagList :

            if keyTag[ 0 ] == event.key :

                if keyTag[ 0 ] in self.saccadeList[ indiceSpan ][ 3 ] :

                    self.saccadeList[ indiceSpan ][ 3 ] = self.saccadeList[ indiceSpan ][ 3 ].replace( keyTag[ 0 ], "" )
                
                else :

                    self.saccadeList[ indiceSpan ][ 3 ] = self.saccadeList[ indiceSpan ][ 3 ] + keyTag[ 0 ]

                self.saccadeList[ indiceSpan ][ 3 ] = self.rewriteKeyTag( self.saccadeList[ indiceSpan ][ 3 ] )
                self.writeInSaccade( indiceSpan, self.saccadeList[ indiceSpan ][ 2 ] - 100 )
                self.canvas.draw()
                break
   


    def writeInBlink( self, indiceSpan, xText ) :

        textToWrite = self.getTextToWrite( self.blinkList[ indiceSpan ][ 3 ] )
        self.blinkSpanList[ indiceSpan ][ 1 ].set_text( textToWrite )
        yTxt = self.plot.get_ylim()[ 0 ] * 0.9
        self.blinkSpanList[ indiceSpan ][ 1 ].set_position( ( xText, yTxt ) )

    def writeInSaccade( self, indiceSpan, xText ) :

        textToWrite = self.getTextToWrite( self.saccadeList[ indiceSpan ][ 3 ] )
        self.saccadeSpanList[ indiceSpan ][ 1 ].set_text( textToWrite )
        yTxt = self.plot.get_ylim()[ 0 ] * 0.9
        self.saccadeSpanList[ indiceSpan ][ 1 ].set_position( ( xText, yTxt ) )

    def getTextToWrite( self, keyString ) :

        result = ""

        for keyTag in self.keyTagList :

            if keyTag[ 0 ] in keyString :

                result = result + keyTag[ 1 ]
            
        return result

    def rewriteKeyTag( self, keytagString ) :

        result = ""

        for keyTag in self.keyTagList :

            if keyTag[ 0 ] in keytagString :

                result = result + keyTag[ 0 ]

        return result


    def forwardBtn( self ) : 

        # diff = self.myData.maxPlot - self.myData.minPlot
        # self.myData.minPlot = self.myData.minPlot + int( diff * 3 / 4 )
        # self.myData.maxPlot = self.myData.minPlot + diff
        # self.plot.set_xlim( left = self.myData.minPlot, right = self.myData.maxPlot )

        minPlot = self.plot.get_xlim()[ 0 ]
        maxPlot = self.plot.get_xlim()[ 1 ]
        diff = maxPlot - minPlot
        minPlot = minPlot + int( diff * 3 / 4 )
        maxPlot = minPlot + diff
        self.plot.set_xlim( left = minPlot, right = maxPlot )
        # self.plot.set_ylim( bottom = -500, top = 500 )
        self.canvas.draw()

        self.toolbar.push_current()
        
    def backwardBtn( self ) : 

        # diff = self.myData.maxPlot - self.myData.minPlot
        # self.myData.minPlot = self.myData.minPlot - int( diff * 3 / 4 )
        # self.myData.maxPlot = self.myData.minPlot + diff
        # self.plot.set_xlim( left = self.myData.minPlot, right = self.myData.maxPlot )

        minPlot = self.plot.get_xlim()[ 0 ]
        maxPlot = self.plot.get_xlim()[ 1 ]
        diff = maxPlot - minPlot
        minPlot = minPlot - int( diff * 3 / 4 )
        maxPlot = minPlot + diff
        self.plot.set_xlim( left = minPlot, right = maxPlot )
        # self.plot.set_ylim( bottom = -500, top = 500 )
        self.canvas.draw()

        self.toolbar.push_current()

    def saveBtn( self ) : 

        # save to npy file
        blinkSave = np.array( self.blinkList )
        saccadeSave = np.array( self.saccadeList )
        print( blinkSave.shape )
        save( './blinkTimeStamp.npy', blinkSave )
        print( saccadeSave.shape )
        save( './saccadeTimeStamp.npy', saccadeSave )


    def deleteSpanAt( self, xdata ) :

        self.deleteSpanBlinkAt( xdata )
        self.deleteSpanSaccadeAt( xdata )
        
    def deleteSpanBlinkAt( self, xdata ) :

        for i in range ( len( self.blinkList ) ) :

            if self.blinkList[ i ][ 0 ] < xdata and  xdata < self.blinkList[ i ][ 1 ] :

                span = self.blinkSpanList[ i ][ 0 ]
                span.remove()
                text = self.blinkSpanList[ i ][ 1 ]
                if text is not None :
                    text.remove()
                del self.blinkList[ i ]
                del self.blinkSpanList[ i ]

                self.canvas.draw()
                break

    def deleteSpanSaccadeAt( self, xdata ) :

        for i in range ( len( self.saccadeList ) ) :

            if self.saccadeList[ i ][ 0 ] < xdata and  xdata < self.saccadeList[ i ][ 1 ] :

                span = self.saccadeSpanList[ i ][ 0 ]
                span.remove()
                text = self.saccadeSpanList[ i ][ 1 ]
                if text is not None :
                    text.remove()
                del self.saccadeList[ i ]
                del self.saccadeSpanList[ i ]

                self.canvas.draw()
                break


    def testSpanBlinkUnderCursor( self, xdata ) :

        for i in range ( len( self.blinkList ) ) :

            if self.blinkList[ i ][ 0 ] < xdata and  xdata < self.blinkList[ i ][ 1 ] :

                return i

    def testSpanSaccadeUnderCursor( self, xdata ) :

        for i in range ( len( self.saccadeList ) ) :

            if self.saccadeList[ i ][ 0 ] < xdata and  xdata < self.saccadeList[ i ][ 1 ] :

                return i
        

    def plotData( self, title ) :

        self.figure.clear()
        data = self.myData.getDataToPlot()
        ax = self.figure.add_subplot( 111, title = title)
        ax.set_xlim( left = self.myData.minPlot, right = self.myData.maxPlot )

        if not hasattr( self, 'init' ) :
            self.bottomPlot = np.min( data[ :, [ 0, 1, 2 ] ] ) * 1.05
            self.topPlot = np.max( data[ :, [ 0, 1, 2 ] ] ) * 1.05
            ax.set_ylim( bottom = self.bottomPlot, top = self.topPlot )
            self.init = True

        self.curvesList.append( ax.plot( data[ :, 0 ], label="horizontal" ) )
        self.curvesList.append( ax.plot( data[ :, 1 ], label="vertical" ) )
        self.curvesList.append( ax.plot( data[ :, 2 ], label="Deriv_horizontal" ) )
        self.curvesList.append( ax.plot( data[ :, 3 ], label="Deriv_vertical" ) )
        self.curvesList.append( ax.plot( data[ :, 4 ], label="wavelet_horizontal" ) )
        self.curvesList.append( ax.plot( data[ :, 5 ], label="wavelet_vertical" ) )

        if not( self.checkBox_HandV.isChecked() ) :

            self.curvesList[ 0 ][ 0 ].set_linestyle('None')
            self.curvesList[ 1 ][ 0 ].set_linestyle('None')

        if not( self.checkBox_Derivatives.isChecked() ) :

            self.curvesList[ 2 ][ 0 ].set_linestyle('None')
            self.curvesList[ 3 ][ 0 ].set_linestyle('None')
        
        if not( self.checkBox_Wavelets.isChecked() ):

            self.curvesList[ 4 ][ 0 ].set_linestyle('None')
            self.curvesList[ 5 ][ 0 ].set_linestyle('None')

        ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)
        # ax.plot(data)
        self.plot = ax
        self.canvas.draw()
        
        self.toolbar.push_current()

    def spanFromSaccadeList( self, saccadeListLoaded ) :

        for i in range( len( saccadeListLoaded ) ) :
            
            start = int( float( saccadeListLoaded[ i ][ 0 ] ) )
            end = int( float( saccadeListLoaded[ i ][ 1 ] ) )
            center = int( float( saccadeListLoaded[ i ][ 2 ] ) )
            # self.saccadeList.append( [ start, end, center, "" ] )
            self.saccadeList.append( [ start, end, center, saccadeListLoaded[ i ][ 3 ] ] )
            self.saccadeSpanList.append( [ self.plot.axvspan( start, end, color='blue', alpha=0.2 ), self.plot.text( 0, -400, "" ) ] )
            self.writeInSaccade( i, self.saccadeList[ i ][ 2 ] - 100 )

    def spanFromBlinkList( self, blinkListLoaded ) :

        for i in range( len( blinkListLoaded ) ) :
            
            start = int( float( blinkListLoaded[ i ][ 0 ] ) )
            end = int( float( blinkListLoaded[ i ][ 1 ] ) )
            center = int( float( blinkListLoaded[ i ][ 2 ] ) )
            # self.blinkList.append( [ start, end, center, "" ] )
            self.blinkList.append( [ start, end, center, blinkListLoaded[ i ][ 3 ] ] )
            self.blinkSpanList.append( [ self.plot.axvspan( start, end, color='green', alpha=0.2 ), self.plot.text( 0, -400, "" ) ] )
            self.writeInBlink( i, self.blinkList[ i ][ 2 ] - 100 )

    def customSpanPreset( self ) :

        j = 0

        for i in range( 600, self.myData.getDataToPlot().shape[ 0 ], 750  ):

            t = ""

            if j % 15 == 0 :
                t = "left3"
            if j % 15 == 1 :
                t = "right3"
            if j % 15 == 2 :
                t = "left2"
            if j % 15 == 3 :
                t = "right2"
            if j % 15 == 4 :
                t = "left1"
            if j % 15 == 5 :
                t = "right1"
            if j % 15 == 6 :
                t = "right1"
            if j % 15 == 7 :
                t = "left1"
            if j % 15 == 8 :
                t = "right2"
            if j % 15 == 9 :
                t = "left2"
            if j % 15 == 10 :
                t = "right3"
            if j % 15 == 11 :
                t = "left3"
            if j % 15 == 12 :
                t = ""
            if j % 15 == 13 :
                t = "v"
            if j % 15 == 14 :
                t = ""


            start = i - 100
            end = i + 100
            center = i
            self.saccadeList.append( [ start, end, center, t ] )
            self.saccadeSpanList.append( [ self.plot.axvspan( start, end, color='blue', alpha=0.2 ), self.plot.text( 0, -400, "" ) ] )
            self.writeInSaccade( j, center - 100 )
            j += 1
   

    def wassimSaccadeFile( self, fileName ) :

        tableauCorrespondances = [
            [ 'mid', '' ],
            [ 'ptu', 'up' ],
            [ 'ptU', 'up' ],
            [ 'ptd', 'down' ],
            [ 'ptD', 'down' ],
            [ 'ptl', 'left' ],
            [ 'ptL', 'left' ],
            [ 'ptLL', 'right' ],
            [ 'ptRLL', 'right' ], # LL
            [ 'ptr', 'right' ],
            [ 'ptR', 'right' ],
            [ 'ptRR', 'right' ],
            # [ 'pt', '' ], # ...
            # [ 'pt', '' ],
            # [ 'pt', '' ],
            # [ 'pt', '' ],
            # [ 'pt', '' ],
            # [ 'pt', '' ]
        ]

        with codecs.open(fileName, encoding='utf-8-sig') as f:
                        X = [[x for x in line.split()] for line in f]

        asciiArray = np.array(X)

        patternEmpty = re.compile( "^\.$" )

        saccadeStart = 14
        saccadeEnd = 58
        i = 0

        numSaccade = len( self.saccadeList )
            
        for line in asciiArray :

            if i == 0 :

                line = line[ 1 ].replace('_', ' ')
                ms = float( line.split(' ')[ -1 ] )
                s = float( line.split(' ')[ -2 ] )
                m = float( line.split(' ')[ -3 ] )
                h = float( line.split(' ')[ -4 ] )
                startExpe = ( ms + s * 1000 + m * 1000 * 60 + h * 60 * 1000 * 60 ) / 10
            
            testEmpty = not any( bool( patternEmpty.match( s ) ) for s in line )
            
            if i >= saccadeStart and i <= saccadeEnd :
                
                strDirection = ''

                line = line[ 0 ].replace('_', ' ')

                for c in tableauCorrespondances :

                    if( line.split(' ')[ 1 ] == c[ 0 ] ) :

                        strDirection = c[ 1 ]
                        break

                ms = float( line.split(' ')[ -1 ] )
                s = float( line.split(' ')[ -2 ] )
                m = float( line.split(' ')[ -3 ] )
                h = float( line.split(' ')[ -4 ] )

                center = ( ms + s * 1000 + m * 1000 * 60 + h * 60 * 1000 * 60 ) / 10 - startExpe

                start = center - 30
                end = center + 30
                self.saccadeList.append( [ start, end, center, strDirection ] )
                self.saccadeSpanList.append( [ self.plot.axvspan( start, end, color='blue', alpha=0.2 ), self.plot.text( 0, -400, "" ) ] )
                self.writeInSaccade( numSaccade, center - 100 )

                numSaccade += 1
                
            i += 1

        print( len( self.saccadeList ) )
        print( self.saccadeList )



# driver code
if __name__ == '__main__':
       
    # creating apyqt5 application
    app = QApplication(sys.argv)
   
    # creating a window object
    main = Window()
       
    # showing the window
    main.show()
   
    # loop
    sys.exit(app.exec_())
