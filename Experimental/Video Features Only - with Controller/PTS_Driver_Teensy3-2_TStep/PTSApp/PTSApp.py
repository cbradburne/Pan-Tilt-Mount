import tkinter as tk
from tkinter.constants import END
import tkinter.ttk as ttk
from serial import *
from threading import Timer
import serial.tools.list_ports

ser = ''
serBuffer = ''
backgroundColour = '#3C3C3C'

def sendSerial(sendValue):
    if (ser == ''):
        textBox1.insert(END, 'Serial port not selected!\n')
        textBox1.see(END)
    else:
        ser.write(sendValue.encode())

def serial_ports():
    ports = serial.tools.list_ports.comports()

    available_ports = []

    for p in ports:
        available_ports.append(p.device)

    return available_ports

def updateComPortlist():
    list = serial_ports()
    cb['values'] = list

def on_select(event=None):
    global ser
    serialPortSelect = cb.get()
    baudRate = 115200
    ser = Serial(serialPortSelect , baudRate, timeout=0, writeTimeout=0) #ensure non-blocking
    readSerial()

def sendUP1():
    temp='T1'
    sendSerial(temp)

def sendDOWN1():
    temp='T-1'
    sendSerial(temp)

def sendLEFT1():
    temp='P0.5'
    sendSerial(temp)

def sendRIGHT1():
    temp='P-0.5'
    sendSerial(temp)

def sendUP10():
    temp='T10'
    sendSerial(temp)

def sendDOWN10():
    temp='T-10'
    print(temp)
    sendSerial(temp)

def sendLEFT10():
    temp='P10'
    sendSerial(temp)

def sendRIGHT10():
    temp='P-10'
    sendSerial(temp)

def sendRESETpos():
    temp='h'
    sendSerial(temp)

def sendSR1():
    temp='L10'
    sendSerial(temp)

def sendSR10():
    temp='L100'
    sendSerial(temp)

def sendSL1():
    temp='L-10'
    sendSerial(temp)

def sendSL10():
    temp='L-100'
    sendSerial(temp)

def sendZOOMin():
    temp='Z'
    sendSerial(temp)

def sendZOOMout():
    temp='z'
    sendSerial(temp)

def sendREPORTall():
    temp='R'
    sendSerial(temp)

def sendREPORTpos():
    temp='r'
    sendSerial(temp)

def sendSPEEDfast():
    temp='V'
    sendSerial(temp)

def sendSPEEDslow():
    temp='v'
    sendSerial(temp)

def sendSET1():
    temp='a'
    sendSerial(temp)

def sendSET2():
    temp='b'
    sendSerial(temp)

def sendSET3():
    temp='c'
    sendSerial(temp)

def sendSET4():
    temp='d'
    sendSerial(temp)

def sendSET5():
    temp='e'
    sendSerial(temp)

def sendSET6():
    temp='f'
    sendSerial(temp)

def sendGO1():
    temp='A'
    sendSerial(temp)

def sendGO2():
    temp='B'
    sendSerial(temp)

def sendGO3():
    temp='C'
    sendSerial(temp)

def sendGO4():
    temp='D'
    sendSerial(temp)

def sendGO5():
    temp='E'
    sendSerial(temp)

def sendGO6():
    temp='F'
    sendSerial(temp)

mainWindow = tk.Tk()
mainWindow.title('Pan / Tilt Controller')
mainWindow.configure(height='768', width='800')
frame_1 = tk.Frame(mainWindow, bg=backgroundColour)
frame_1.configure(height='768', width='800')
frame_1.place(anchor='nw', x='0', y='0')
lbl1 = tk.Label(mainWindow, text='Serial Port')
lbl1.configure(bg=backgroundColour, fg='White')
lbl1.place(anchor='nw', x='30', y='10')
cb = ttk.Combobox(frame_1, postcommand=updateComPortlist)
cb.place(anchor='nw', height='26', width='200', x='30', y='40')
lbl2 = tk.Label(mainWindow, text='Serial Send:')
lbl2.configure(bg=backgroundColour, fg='White')
lbl2.place(anchor='nw', x='30', y='420')
textINPUT = tk.Entry(frame_1)
textINPUT.place(anchor='nw', x='30', y='450', height='30', width='740')
textINPUT.focus_set()
lbl3 = tk.Label(mainWindow, text='Serial Receive:')
lbl3.configure(bg=backgroundColour, fg='White')
lbl3.place(anchor='nw', x='30', y='510')
textBox1 = tk.Text(frame_1)
textBox1.place(anchor='nw', x='30', y='540', height='200', width='740')
buttonSET1 = tk.Button(frame_1)
buttonSET1.configure(text='SET\n 1')
buttonSET1.place(anchor='nw', height='60', width='60', x='420', y='80')
buttonSET1.configure(command=sendSET1)
buttonSET2 = tk.Button(frame_1)
buttonSET2.configure(text='SET\n 2')
buttonSET2.place(anchor='nw', height='60', width='60', x='480', y='80')
buttonSET2.configure(command=sendSET2)
buttonSET3 = tk.Button(frame_1)
buttonSET3.configure(text='SET\n3')
buttonSET3.place(anchor='nw', height='60', width='60', x='540', y='80')
buttonSET3.configure(command=sendSET3)
buttonSET4 = tk.Button(frame_1)
buttonSET4.configure(text='SET\n4')
buttonSET4.place(anchor='nw', height='60', width='60', x='600', y='80')
buttonSET4.configure(command=sendSET4)
buttonSET5 = tk.Button(frame_1)
buttonSET5.configure(text='SET\n5')
buttonSET5.place(anchor='nw', height='60', width='60', x='660', y='80')
buttonSET5.configure(command=sendSET5)
buttonSET6 = tk.Button(frame_1)
buttonSET6.configure(text='SET\n6')
buttonSET6.place(anchor='nw', height='60', width='60', x='720', y='80')
buttonSET6.configure(command=sendSET6)
buttonGO1 = tk.Button(frame_1)
buttonGO1.configure(text='GO\n1')
buttonGO1.place(anchor='nw', height='60', width='60', x='420', y='20')
buttonGO1.configure(command=sendGO1)
buttonGO2 = tk.Button(frame_1)
buttonGO2.configure(text='GO\n2')
buttonGO2.place(anchor='nw', height='60', width='60', x='480', y='20')
buttonGO2.configure(command=sendGO2)
buttonGO3 = tk.Button(frame_1)
buttonGO3.configure(text='GO\n3')
buttonGO3.place(anchor='nw', height='60', width='60', x='540', y='20')
buttonGO3.configure(command=sendGO3)
buttonGO4 = tk.Button(frame_1)
buttonGO4.configure(text='GO\n4')
buttonGO4.place(anchor='nw', height='60', width='60', x='600', y='20')
buttonGO4.configure(command=sendGO4)
buttonGO5 = tk.Button(frame_1)
buttonGO5.configure(text='GO\n5')
buttonGO5.place(anchor='nw', height='60', width='60', x='660', y='20')
buttonGO5.configure(command=sendGO5)
buttonGO6 = tk.Button(frame_1)
buttonGO6.configure(text='GO\n6')
buttonGO6.place(anchor='nw', height='60', width='60', x='720', y='20')
buttonGO6.configure(command=sendGO6)
buttonUP1 = tk.Button(frame_1)
buttonUP1.configure(text='1')
buttonUP1.place(anchor='nw', height='60', width='60', x='250', y='130')
buttonUP1.configure(command=sendUP1)
buttonDOWN1 = tk.Button(frame_1)
buttonDOWN1.configure(text='1')
buttonDOWN1.place(anchor='nw', height='60', width='60', x='250', y='270')
buttonDOWN1.configure(command=sendDOWN1)
buttonLEFT1 = tk.Button(frame_1)
buttonLEFT1.configure(text='1')
buttonLEFT1.place(anchor='nw', height='60', width='60', x='180', y='200')
buttonLEFT1.configure(command=sendLEFT1)
buttonRIGHT1 = tk.Button(frame_1)
buttonRIGHT1.configure(text='1')
buttonRIGHT1.place(anchor='nw', height='60', width='60', x='320', y='200')
buttonRIGHT1.configure(command=sendRIGHT1)
buttonUP10 = tk.Button(frame_1)
buttonUP10.configure(text='10')
buttonUP10.place(anchor='nw', height='60', width='60', x='250', y='70')
buttonUP10.configure(command=sendUP10)
buttonDOWN10 = tk.Button(frame_1)
buttonDOWN10.configure(text='10')
buttonDOWN10.place(anchor='nw', height='60', width='60', x='250', y='330')
buttonDOWN10.configure(command=sendDOWN10)
buttonLEFT10 = tk.Button(frame_1)
buttonLEFT10.configure(text='10')
buttonLEFT10.place(anchor='nw', height='60', width='60', x='120', y='200')
buttonLEFT10.configure(command=sendLEFT10)
buttonRIGHT10 = tk.Button(frame_1)
buttonRIGHT10.configure(text='10')
buttonRIGHT10.place(anchor='nw', height='60', width='60', x='380', y='200')
buttonRIGHT10.configure(command=sendRIGHT10)
buttonRESET = tk.Button(frame_1)
buttonRESET.configure(text='0')
buttonRESET.place(anchor='nw', height='60', width='60', x='250', y='200')
buttonRESET.configure(command=sendRESETpos)
buttonSL10 = tk.Button(frame_1)
buttonSL10.configure(text='100')
buttonSL10.place(anchor='nw', height='60', width='60', x='120', y='350')
buttonSL10.configure(command=sendSL10)
buttonSL1 = tk.Button(frame_1)
buttonSL1.configure(text='10')
buttonSL1.place(anchor='nw', height='60', width='60', x='180', y='350')
buttonSL1.configure(command=sendSL1)
buttonSR10 = tk.Button(frame_1)
buttonSR10.configure(text='100')
buttonSR10.place(anchor='nw', height='60', width='60', x='380', y='350')
buttonSR10.configure(command=sendSR10)
buttonSR1 = tk.Button(frame_1)
buttonSR1.configure(text='10')
buttonSR1.place(anchor='nw', height='60', width='60', x='320', y='350')
buttonSR1.configure(command=sendSR1)
buttonZOOMIN = tk.Button(frame_1)
buttonZOOMIN.configure(text='ZOOM\nIN')
buttonZOOMIN.place(anchor='nw', height='60', width='80', x='450', y='290')
buttonZOOMIN.configure(command=sendZOOMin)
buttonZOOMOUT = tk.Button(frame_1)
buttonZOOMOUT.configure(text='ZOOM\nOUT')
buttonZOOMOUT.place(anchor='nw', height='60', width='80', x='450', y='350')
buttonZOOMOUT.configure(command=sendZOOMout)
buttonSPEEDFAST = tk.Button(frame_1)
buttonSPEEDFAST.configure(text='FAST')
buttonSPEEDFAST.place(anchor='nw', height='60', width='80', x='30', y='290')
buttonSPEEDFAST.configure(command=sendSPEEDfast)
buttonSPEEDSLOW = tk.Button(frame_1)
buttonSPEEDSLOW.configure(text='SLOW')
buttonSPEEDSLOW.place(anchor='nw', height='60', width='80', x='30', y='350')
buttonSPEEDSLOW.configure(command=sendSPEEDslow)
buttonREPORTALL = tk.Button(frame_1)
buttonREPORTALL.configure(text='Report\nALL')
buttonREPORTALL.place(anchor='nw', height='60', width='80', x='690', y='290')
buttonREPORTALL.configure(command=sendREPORTall)
buttonREPORTPOS = tk.Button(frame_1)
buttonREPORTPOS.configure(text='Report\nPOS')
buttonREPORTPOS.place(anchor='nw', height='60', width='80', x='690', y='350')
buttonREPORTPOS.configure(command=sendREPORTpos)

def readSerial():
    global ser
    if (ser == ''):
        return
    else:

        while True:
            c = ser.read()
            if (c == b'\xb0'):                          # remove characters that cause error
                c = '°'
            elif (c == b'\xb2'):
                c = '²'
            elif (c == b'\xba') or (c == b'\xc2'):
                c = ''
            else:
                c = c.decode('ascii')
            
            #was anything read?
            if len(c) == 0:
                break
            
            # get the buffer from outside of this function
            global serBuffer
            
            # check if character is a delimeter
            if c == '\r':
                c = '' # don't want returns. chuck it
                
            if c == '\n':
                serBuffer += '\n' # add the newline to the buffer
                #add the line to the TOP of the log
                textBox1.insert(END, serBuffer)
                textBox1.see(END)
                serBuffer = '' # empty the buffer
            else:
                serBuffer += c # add to the buffer
        
        mainWindow.after(10, readSerial) # check serial again soon

def clearAll():
    textINPUT.delete(0,END)

def func(event):
    res1 = textINPUT.get()
    print(res1)
    ser.write(res1.encode())
    t = Timer(0.5, clearAll)                                                        # Clears all text after 3 seconds
    t.start()

# after initializing serial, an arduino may need a bit of time to reset
#mainWindow.after(100, readSerial)

mainWindow.bind('<Return>', func)

# assign function to combobox
cb.bind('<<ComboboxSelected>>', on_select)

mainWindow.mainloop()
    