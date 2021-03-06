import numpy as np
import cv2

import pdb

class Calibrator():
    calibrationPoints = None
    yawSlope = None
    pitchSlope = None
    phase = 0
    mode = 'DONE'   # choices: DONE, WAIT, CALIBRATE
    message = ''
    
    numTmpPts = 3
    tmpPts = []
    
    def __init__(self, calibrationInfo, outimg):
        self.calibrationInfo = calibrationInfo
        self.outimg = outimg
    
    
    def drawCalibrationPoint(self):
        """Draw calibration point bullseye
        """
        pt = (self.calibrationInfo[self.phase]['screen_pos_x'],
              self.calibrationInfo[self.phase]['screen_pos_y'])
        cv2.circle(self.outimg, pt, 8, (0,0,255), -1)
        cv2.circle(self.outimg, pt, 15, (0,0,255), 5)
        self.drawMessage()
    
    def drawMessage(self):
        if self.mode == 'WAIT':
            cv2.putText(self.outimg, 'Press "n" while looking at the point', (100,300), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 3)
        elif self.mode == 'CALIBRATE':
            cv2.putText(self.outimg, 'Continue looking at the point', (100,300), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 3)
    
    def setMode(self, mode):
        self.mode = mode
        #if mode == 'CALIBRATE':
        #    self.tmpPts = []
    
    def startCalibration(self):
        self.mode = 'WAIT'
        self.phase = 0
    
    def processPhase(self, lpt, rpt, fliplr=True):
        if fliplr == True:
            ltmp = lpt
            lpt = ((-1)*rpt[0], rpt[1])
            rpt = ((-1)*ltmp[0], ltmp[1])
        if self.mode == 'CALIBRATE':
            #pdb.set_trace()
            print 'Phase: %d' % self.phase
            print 'tmppts: %d' % len(self.tmpPts)
            print lpt, rpt
            
            self.tmpPts.append({
                'left': lpt,
                'right': rpt,
            })
            
            # average pts and move to next phase
            if len(self.tmpPts) == self.numTmpPts:
                #pdb.set_trace()
                leftavg = [0,0]
                rightavg = [0,0]
                for pt in self.tmpPts:
                    leftavg[0] += pt['left'][0]
                    leftavg[1] += pt['left'][1]
                    rightavg[0] += pt['right'][0]
                    rightavg[1] += pt['right'][1]
                leftavg[0] /= self.numTmpPts
                leftavg[1] /= self.numTmpPts
                rightavg[0] /= self.numTmpPts
                rightavg[1] /= self.numTmpPts
                
                # create the pts array if not exist
                if self.calibrationPoints == None:
                    self.calibrationPoints = []
                # append if pt not exist
                if len(self.calibrationPoints) < self.phase+1:
                    self.calibrationPoints.append({
                        'left_eye': tuple(leftavg),
                        'right_eye': tuple(rightavg),
                    })
                # overwrite if alreay exists
                else:
                    self.calibrationPoints[self.phase] = {
                        'left_eye': tuple(leftavg),
                        'right_eye': tuple(rightavg),
                    }
                self.tmpPts = []
                
                # advance phase, if last phase, wrap up and change mode
                self.phase += 1
                if self.phase == 4:
                    self.mode = 'DONE'
                    print 'Calibration mode complete.'
                else:
                    self.mode = 'WAIT'
                    print 'Press "n" while looking at the calibration point to continue to the next phase.'