#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import serial
#import time
#import os
import sys
import math
import matplotlib.mlab as mlab


def main(args):
  capture = False;
  fig = plt.figure(1)
  plt.ion()
  topplot = fig.add_subplot(211)
  bottomplot = fig.add_subplot(212)
  topplot.set_ylabel('ms per hit')
  topplot.set_xlabel('time (seconds)')
  bottomplot.set_ylabel('hits')
  bottomplot.set_xlabel('ms per hit')
              
  fig.show()
            
  while True:
    try:
      ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1, dsrdtr=True)
      print "Port is open"
      line = ''
      while True:
        ch = ser.read()
        if len(ch) > 0:
          if ch == chr(10):
            i = int(line)
            # start button has been pressed, system is now in standby            
            if i == -1:
              print 'Standby'
              a = []
            # first hit has been captured, timer is running            
            elif i == -2:
              print 'Capture stared'
              capture = True;
            # measureing has finished, displaying results            
            elif i == -3:
              print 'Capture finished'
              capture = False

              #convert data to numpy array of integers
              b = np.array(a, dtype=int)
              #discard outliers (upper and lower 1%)
              fc = int(math.ceil(len(b) / 100))
              print "filtered  : %d samples" % fc
              bs = np.sort(b)[fc:-fc]
              #calculate statistics
              c = np.bincount(bs)
              mean = np.mean(bs)
              std = np.std(bs)
              z = np.zeros(np.shape(b))
              print "Total     : %d hits" % (len(b))
              print "Mean      : %4.1f ms" % (mean)
              print "Deviation : %4.1f ms" % (std)

              #calculate comulative sum for creating linear time scale
              cumsum = np.cumsum(b) / 1000.0
              
              #plot hits, mean, -3 sigma and +3 sigma line
              topplot.clear()              
              topplot.plot(cumsum, b, 'k.')
              topplot.axhline(mean, color='r')
              topplot.axhline(mean - std*3, c='r', ls='dashed')
              topplot.axhline(mean + std*3, c='r', ls='dashed')
              topplot.plot(cumsum, z, 'g-')
              topplot.axis([0, 60, mean - 6*std, mean + 6*std])
              topplot.set_ylabel('ms per hit')
              topplot.set_xlabel('time (seconds)')
              
              #plot histogram of hits with normal curve
              bottomplot.clear()
              bottomplot.plot(c)
              x = np.linspace(mean-3*std, mean+3*std, 100)
              bottomplot.plot(x, mlab.normpdf(x, mean, std)*len(b), 'r-')
              bottomplot.axis([mean - 3*std, mean + 3*std, 0, np.max(c)])
              bottomplot.set_ylabel('hits')
              bottomplot.set_xlabel('ms per hit')
              ticks = [round(t) for t in [mean-3*std,mean-2*std,mean-1*std,mean,mean+1*std,mean+2*std,mean+3*std]]
              bottomplot.set_xticks(ticks, ticks)

              fig.canvas.draw()
            else:
              if capture:
                a.append(i)
            line = ''
          elif ord(ch) >= 32:
            line = line + ch
    except serial.SerialException:
      print "Unable to open port /dev/ttyUSB0"
      print "Retry in 5 seconds..."
      time.sleep(5)
    except KeyboardInterrupt:
      print "Keyboard interrupt"
      ser.close()
      sys.exit()
    
if __name__ == "__main__":
  main(sys.argv)

