import numpy as np
from scipy import signal
import pywt
import pyedflib
import codecs
import re

class DataLoadAndPlot :

    def __init__( self ):

        self.minPlot = 0
        self.maxPlot = self.minPlot + 1000*20

    def readEDF( self, fileName ) :
        
        f = pyedflib.EdfReader( fileName )
        n = f.signals_in_file
        signal_labels = f.getSignalLabels()
        sigbufs = np.zeros((n, f.getNSamples()[0]))
        for i in np.arange(n):
            sigbufs[i, :] = f.readSignal(i)
        
        return sigbufs, signal_labels, f, n

    def readOpenBCIASCII( self, fileName ) :
        
        with codecs.open(fileName, encoding='utf-8-sig') as f:
                        X = [[x for x in line.split()] for line in f]

        asciiArray = np.array(X)

        dataArray = []
        patternEmpty = re.compile( "^\.$" )

        lineToJump = 4
        i = 0
            
        for line in asciiArray :
            
            # if any("Sample" in s for s in line) :
                
            #     header = line
            
            testEmpty = not any( bool( patternEmpty.match( s ) ) for s in line )
            
            if i > lineToJump  :
                
                tmp = []
                
                for word in line :
                    
                    w = word.replace(',', '.')
                    
                    try:
                        
                        tmp.append(float( w ))
                        
                    except ValueError:
                        
                        tmp.append( 0. )
                        
                dataArray.append( np.array(tmp) )
                
            i += 1
        # header = np.array( header )
    #     header = header.repace( ' ', '_');
    #     header = header.repace( ',', ' ');
        dataArray = np.array( dataArray )
        # print (dataArray[ 0: 10 ] )

        # mydata = np.zeros(( dataArray[ 0 ].shape[ 0 ], dataArray.shape[ 0 ]))

        # for i in range( dataArray.shape[ 0 ] ) :
            
        #     for j in range( dataArray[ 0 ].shape[ 0 ] ) :

        #         mydata[ i ][ j ] = dataArray[ i ][ j ]

        # print (mydata.shape )
        # print (dataArray[ 0: 10 ] )
                
        return dataArray

    def readASCII( self, asciiArray ) :
        
        dataArray = []
        patternEmpty = re.compile( "^\.$" )
            
        for line in asciiArray :
            
            testEmpty = not any( bool( patternEmpty.match( s ) ) for s in line )
            
            if any("32764" in s for s in line ) and testEmpty :
                
                tmp = []
                
                for word in line :
                    
                    w = word.replace(',', '')
                    
                    try:
                        
                        tmp.append(float( w ))
                        
                    except ValueError:
                        
                        tmp.append( 0. )
                        
                dataArray.append( tmp )
                
        dataArray = np.array( dataArray )
        # print( dataArray.shape )
        # print( dataArray )
        dataArray = dataArray[ :, 1 ]
        return dataArray

    def loadTxt( self, fileNameTxt ) :

        with codecs.open( fileNameTxt, encoding='utf-8-sig') as f:
                    X = [[x for x in line.split()] for line in f]
            
        Xnp = np.array(X)
        dataArray = self.readASCII( Xnp )

        return  self.formatLoadedSaccade( dataArray )

    def formatLoadedSaccade( self, dataArray ) :

        print( dataArray.shape )
        saccadeList = []
        sArr = [
            '',
            '1','3','1','3','3','1','1','3','3','3', '3','1','1','3','3','1','3','1','1','1', '3','1','3','1','3','3','3','3','1','1', '1','3','3','3','1','3','1','3','3','3', '3','3','3','3','3','1','3','3','1','3',
            '1','3','3','3','3','3','1','3','3','3', '3','3','1','1','3','1','3','3','1','3', '1','3','1','1','3','3','3','1','3','1', '1','3','3','1','3','3','3','3','3','3', '3','3','1','3','3','1','1','1','1','3',
            '3','3','3','3','3','3','3','3','3','3', '3','3','3','3','3','3','1','1','3','1', '1','3','3','3','1','3','3','3','3','3', '1','3','3','1','3','1','1','3','3','3', '3','1','3','1'
        ]

        i = 0
        j = 0

        for saccade in dataArray :

            start = int ( ( saccade - 0.2 ) * 1000 )
            end = int ( ( saccade + 0.6 ) * 1000 )
            if len(sArr) > i :
                saccadeList.append( [ start, end, start + ( end - start ) / 2, sArr[ i ] ] )
            else :
                saccadeList.append( [ start, end, start + ( end - start ) / 2, '' ] )

            if j % 2 == 0 :
                i += 1
        
            j += 1

        return saccadeList
            

    def changeHzTo( self, eogIn, fromHz, toHz ) :
        
        newEOG = []
        
        for sig in eogIn :
        
            newSig = []

            hzDiv = fromHz / toHz

            for i in range( 0, sig.shape[ 0 ], fromHz ) :

                j = 0.

                while ( j < fromHz and i + j + round( hzDiv ) < sig.shape[ 0 ] ) :

                    start = i + round( j )
                    newSig.append( np.mean( sig[ start : start + round( hzDiv ) ] ) )
                    j += hzDiv
            
            newEOG.append( newSig )
                
        return np.array( newEOG )
    
    def loadDataEDF( self, fileNameEDF ) :

        sigbufs, _, _, _ = self.readEDF( fileNameEDF )
        eyesData = sigbufs[ [ 64, 65, 66, 67, 68, 69, 70, 71, 72 ] ]
        print(eyesData.shape)

        # eyesData[ 6 ] = eyesData[ 0 ] - eyesData[ 1 ]
        # eyesData[ 7 ] = eyesData[ 3 ] - eyesData[ 1 ]
        # eyesData[ 7 ] = eyesData[ 2 ] - eyesData[ 3 ]
        # eyesData[ 8 ] = eyesData[ 4 ] + eyesData[ 5 ]
        # self.dataEEG = eyesData


        # self.dataEEG = np.zeros( ( 6, eyesData.shape[ 1 ] - 1 ) )

        self.dataEEG = np.zeros( ( 2, eyesData.shape[ 1 ] ) )
        self.dataEEG[ 0 ] = eyesData[ 0 ] - eyesData[ 1 ]
        self.dataEEG[ 1 ] = eyesData[ 2 ] - eyesData[ 3 ]
        

    def loadDataOpenBCI( self, fileName ) :

        dataArray = self.readOpenBCIASCII( fileName )
        ids = [ 1, 2, 3, 4, 5, 6 ]
        data = dataArray[ : , ids   ]

        data = np.swapaxes( data, 0, 1 )
        print (data.shape )
        print( data[ 0 ] )
        myData = data
        # myData[ 0 ] = data[ 1 ] - data[ 0 ]
        # myData[ 1 ] = data[ 2 ] - data[ 3 ]
        # # myData[ 1 ] = data[ 0 ] - data[ 3 ]
        # myData[ 2 ] = data[ 4 ] - data[ 5 ]


        myData[ 1 ] = data[ 0 ] - data[ 1 ]
        myData[ 2 ] = data[ 2 ] - data[ 3 ]

        self.dataEEG = myData

    def getDataToPlot( self ) :
        
        # data = self.dataEEG[ [ 0, 1, 2 ] , : ]
        self.dataEEG = signal.detrend( self.dataEEG )

        # Filter
        self.dataEEG = self.changeHzTo( self.dataEEG, 255, 100 )
        print( self.dataEEG.shape )

        sfreq = 100
        nyq = 0.5 * sfreq
        high = 10 / nyq
        filter_order = 5
        b, a = signal.butter(filter_order, high, btype='low')
        self.dataEEG = signal.filtfilt(b, a, self.dataEEG[:])


        data = np.zeros( ( 6, self.dataEEG.shape[ 1 ] - 1 ) )

        # Signal H & V
        data[ 0 ] = self.dataEEG[ 0, 1: ]
        data[ 1 ] = self.dataEEG[ 1, 1: ]

        # Signal Derivative H & V
        data[ 2 ] = self.dataEEG[ 0, 1: ] - self.dataEEG[ 0, :-1 ]
        data[ 3 ] = self.dataEEG[ 1, 1: ] - self.dataEEG[ 1, :-1 ]
        # data[ 2 ] *= 10
        # data[ 3 ] *= 10

        # Signal Wavelets H & V
        
        data[ 4 ], _ = pywt.cwt( self.dataEEG[ 0, 1: ], 30, 'mexh')
        data[ 5 ], _ = pywt.cwt( self.dataEEG[ 1, 1: ], 30, 'mexh')

        data = np.swapaxes( data, 0, 1 )

        return data