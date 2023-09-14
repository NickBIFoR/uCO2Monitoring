# 10 Jan 2023 -- Added new variable IRGA = 'LI840' -- Change to IRGA = 'LI850' Suit IRGA
# 21 Nov 2022
# Changed LiCor to Strip XML
# Pi now initiates read with <li840><data>?</data></li840>
# removed header from text file for ease of processing
# Changed Date to Date to Time to TIME .csv to .CSV Soalt SOLALT
# added code to write header into file
# Changed write date and time with y/m/d H:M:S
# Added space after plot number
# Now 7A to test in Welfare
# Added extra column for intake, layer
# Now with write to DO
# Added Port 1 N/C
#!/usr/bin/env python

from array import *
import time
import os
from datetime import datetime
import serial
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)
GPIO.setup(1,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
celltemp=0
cellpress=0
cellCO2='empty'
cellCO2_2=0
cellCO2abs=0
Pcount=0
purge=10
Rcount=1
read=20
Portcount=1
port=5
BadRead = 0
Grab=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
IN_list = [0,3,8,4,5,6]
LY_list = [0,6,1,5,4,2]
Z_list =[ 0,21,0.2,18,15,2]
#
# Check IRGA to correct model -- remember to set up LI8** strip XML no pump etc 
IRGA = 'LI850'
#

# AvrGrab is worked on 20 grabs -- check code if you change number of Grab
AvrGrab=0
AvrgPlot=0
# Added Plot number
Plot= ('8')
Plottxt=('MP8-')

Fdate = 0

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
)

# Send purge values to screen not file
# Port 1 now wired N/C
while ser.isOpen():

    while Portcount < (port+1):
        if Portcount == 1:
            GPIO.output(1,GPIO.LOW)
            GPIO.output(5,GPIO.LOW)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(24,GPIO.LOW)
            GPIO.output(25,GPIO.LOW)
        elif Portcount == 2:
            GPIO.output(1,GPIO.HIGH)
            GPIO.output(5,GPIO.HIGH)
            GPIO.output(16,GPIO.LOW)
            GPIO.output(24,GPIO.LOW)
            GPIO.output(25,GPIO.LOW)
        elif Portcount == 3:
             GPIO.output(1,GPIO.HIGH)
             GPIO.output(5,GPIO.LOW)
             GPIO.output(16,GPIO.HIGH)
             GPIO.output(24,GPIO.LOW)
             GPIO.output(25,GPIO.LOW)
        elif Portcount == 4:
             GPIO.output(1,GPIO.HIGH)
             GPIO.output(5,GPIO.LOW)
             GPIO.output(16,GPIO.LOW)
             GPIO.output(24,GPIO.HIGH)
             GPIO.output(25,GPIO.LOW)
        elif Portcount == 5:
             GPIO.output(1,GPIO.HIGH)
             GPIO.output(5,GPIO.LOW)
             GPIO.output(16,GPIO.LOW)
             GPIO.output(24,GPIO.LOW)
             GPIO.output(25,GPIO.HIGH)

        while Pcount < purge:
             Rcount=0
             time.sleep(0.800)
             command = str.encode('<'+ IRGA + '><DATA>?</DATA></'+ IRGA +'>\n')
             ser.write(command)
             datastring = ser.readline()
             'print (datastring)'
             # celltemp=datastring[23:32]
             # cellpress=datastring[53:62]
             cellCO2=datastring[20:29]
             # cellCO2abs=datastring[101:113]
             if " " in str(cellCO2):
                 BadRead = BadRead + 1
                 # Grab[Rcount] = Grab[Rcount -1]
                 print('BadRead', str(BadRead))
                 print(str(cellCO2))
             else:
                 cellCO2_2 = cellCO2
             
             print('Port ' + str(Portcount) + ' Purge ' + str(Pcount)+' ' + str(float(cellCO2_2))+' ppm' )
             Pcount = Pcount + 1
             
        while Rcount < read:
             Pcount = 0
             time.sleep(0.800)
             command = str.encode('<'+ IRGA + '><DATA>?</DATA></'+ IRGA +'>\n')
             ser.write(command)
             datastring = ser.readline()
             # Use as debugging print entire string
             # 'print (datastring)'
             #  f=open("/home/pi/7GHOST_SHARE/RAW7-"+ Fdate +".txt", "a+")
             # print Header ??
             # print ( " Plot, Date, Time, Port, CMP, G0 .. G19")
             #  f.write ( str(datetime.now())+' ' + str(datastring))
             #  f.close()
             # celltemp=datastring[23:32]
             # cellpress=datastring[53:62]
             cellCO2=datastring[20:29]
             # cellCO2abs=datastring[101:113]
             
             if " " in str(cellCO2):
                 BadRead = BadRead + 1
                 # Grab[Rcount] = Grab[Rcount -1]
                 print('BadRead', str(BadRead))
                 print(str(cellCO2))
             else:
                 Grab[Rcount] = cellCO2
                  
             AvrGrab = AvrGrab + float(Grab[Rcount])
             print('Port ' + str(Portcount)+' Grab '+ str(Rcount) + ' ' + str(float(Grab[Rcount])) +' ppm ' )
             Rcount = Rcount + 1
            # Write file only once
            # print(( Plot , datetime.now(),'CellTemp', celltemp, 'Press', cellpress, 'CO2', cellCO2))
            # print(Grab[0],Grab[1])
            # print( Grab, end= " ")  This will print entire array but adds []
            # Average 20 off values from grab change this number will change if read number change  s
            # Average is calculated G0-G19 as 19 < 20 but there are 20 values
        AvrGrab = AvrGrab / (read )
        print( 'CMP Average ' + str(AvrGrab) +' ppm')
        Fdate = (time.strftime("%Y%m%d"))
        Rdate = (time.strftime("%Y/%m/%d"))
        Rtime = (time.strftime("%H:%M:%S"))
        f=open("/home/pi/"+Plot+"GHOST_SHARE/MP"+Plot+"-"+ Fdate +".CSV", "a")
        if os.stat("/home/pi/"+Plot+"GHOST_SHARE/MP"+Plot+"-"+ Fdate +".CSV").st_size == 0:
            # print Header ??
            # print ( " Plot, Date, Time, Port, CMP, G0 .. G19")
            f.write( "P, DATE, TIME, SOLALT, T, F, D,IN,LY,X,Y,Z,TP,TS,WS,WD,FLOW,CSET,CF,CMP,HMP,G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11,G12,G13,G14,G15,G16,G17,G18,G19,G20\n")
        f.write ( str(Plot)+','+ str(Rdate)+','+str(Rtime)+',,,,,'+ str(IN_list[Portcount])+',' +str(LY_list[Portcount])+',,,' +str(Z_list[Portcount])+',,,,,,,,'+str(AvrGrab) +',,'+str(Grab[0])+',' + str(Grab[1])+','+ str(Grab[2])+','+ str(Grab[3])+','+ str(Grab[4])+','+ str(Grab[5])+','+ str(Grab[6])+','+ str(Grab[7])+','+ str(Grab[8])+','+ str(Grab[9])+','+ str(Grab[10])+','+ str(Grab[11])+','+ str(Grab[12])+','+ str(Grab[13])+','+ str(Grab[14])+','+ str(Grab[15])+','+ str(Grab[16])+','+ str(Grab[17])+','+ str(Grab[18])+','+ str(Grab[19])+"\n" )
        f.close()
        AvrgPlot = AvrGrab
        AvrGrab = 0
        Portcount = Portcount +1
    print("BadRead: " + str(BadRead));

    Portcount = 1

ser.close()

             
