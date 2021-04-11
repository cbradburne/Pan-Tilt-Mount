import pygame
from pygame.cursors import tri_left
import pygame_gui
import time
import serial.tools.list_ports
import os, sys
import math

from collections import deque
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.elements import UILabel
from pygame_gui.elements.ui_text_box import UITextBox
from pygame_gui.windows import UIConfirmationDialog
from serial import *
from pathlib import Path

def find_data_file(filename):
    if getattr(sys, "frozen", False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)

try:                                                                                                # Needed for macOS "py2app"
    base_path = Path(__file__).parent
    image_path = (base_path / "./PTSApp-Icon.png").resolve()
    gameIcon = pygame.image.load(image_path)
    pygame.display.set_icon(gameIcon)
except:                                                                                             # Needed for Windows "cx_freeze"
    imageFile = "PTSApp-Icon.png"
    imageFilePath = find_data_file(imageFile)
    gameIcon = pygame.image.load(imageFilePath)
    pygame.display.set_icon(gameIcon)

pygame.font.init()
myfont = pygame.font.SysFont('Trebuchet MS', 30)
myfontsmall = pygame.font.SysFont('Trebuchet MS', 20)
clk = pygame.time.Clock()

interval = 200
intervalReport = 100

baudRate = 38400 #57600 or 38400

speedFastX = 's20'
speedFastY = 'S20'
speedFastZ = 'X60'

speedSlowX = 's10'
speedSlowY = 'S10'
speedSlowZ = 'X30'

ser = ''
serBuffer = ''
serialText = ''
joystick = ''
joystickName = ''
button0Pressed = False
button1Pressed = False
button2Pressed = False
button3Pressed = False
button4Pressed = False
button5Pressed = False
button6Pressed = False
button7Pressed = False
button8Pressed = False
button9Pressed = False
button10Pressed = False
button11Pressed = False
button12Pressed = False
button13Pressed = False
button14Pressed = False
button15Pressed = False
button16Pressed = False

pos1set = False
pos2set = False
pos3set = False
pos4set = False
pos5set = False
pos6set = False

pos1run = False
pos2run = False
pos3run = False
pos4run = False
pos5run = False
pos6run = False

atPos1 = False
atPos2 = False
atPos3 = False
atPos4 = False
atPos5 = False
atPos6 = False

speedIsFast = True
speedRec = False

blinkSet = False
canSendReport = False

textBoxJoystickNames = None
joyCircle_draging = False
sliderCircle_draging = False
offset_x = 0.0
sliderOffset_x = 0.0
offset_y = 0.0
sliderOffset_y = 0.0
textBoxSerial = None
arr = []
oldAxisX = 0
oldAxisY = 0
oldAxisZ = 0
axisX = 0
axisY = 0
axisZ = 0
data = bytearray(7)
hat = ()
oldHatX = 0
oldHatY = 0
previousTime = time.time()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
OFF = (33, 40, 45)

mouseBorder = 360
radius = 15
mouseMoving = False
joyXreadDOT = 0.0
joyYreadDOT = 0.0
joyZreadDOT = 0.0
panKeyPresseed = False
tiltKeyPresseed = False
sliderKeyPresseed = False
isZooming = False
colour_light = (99,104,107) 
colour_dark = (76,80,82)
colour = (255,255,255)

zoomINtext = myfontsmall.render('IN' , True , colour)
zoomOUTtext = myfontsmall.render('OUT' , True , colour)

textsurfaceW = myfont.render('w', False, (89, 89, 89))
textsurfaceA = myfont.render('a', False, (89, 89, 89))
textsurfaceS = myfont.render('s', False, (89, 89, 89))
textsurfaceD = myfont.render('d', False, (89, 89, 89))
textsurfaceLeft = myfont.render(',', False, (89, 89, 89))
textsurfaceRight = myfont.render('.', False, (89, 89, 89))

resolution = (1200, 660)
fullscreen = False

pygame.init()
pygame.display.set_caption("PTSApp")

previousTicks = pygame.time.get_ticks() + interval
previousTicksReport = pygame.time.get_ticks() + intervalReport

def sendUP1():
    temp='^T1'
    sendSerial(temp)

def sendDOWN1():
    temp='^T-1'
    sendSerial(temp)

def sendLEFT1():
    temp='^P-0.5'
    sendSerial(temp)

def sendRIGHT1():
    temp='^P0.5'
    sendSerial(temp)

def sendUP10():
    temp='^T10'
    sendSerial(temp)

def sendDOWN10():
    temp='^T-10'
    sendSerial(temp)

def sendLEFT10():
    temp='^P-10'
    sendSerial(temp)

def sendRIGHT10():
    temp='^P10'
    sendSerial(temp)

def sendRESETpos():
    temp='^h'
    sendSerial(temp)

def sendSR1():
    temp='^L10'
    sendSerial(temp)

def sendSR10():
    temp='^L100'
    sendSerial(temp)

def sendSL1():
    temp='^L-10'
    sendSerial(temp)

def sendSL10():
    temp='^L-100'
    sendSerial(temp)

def sendZOOMin():
    temp='^Z'
    sendSerial(temp)

def sendZOOMout():
    temp='^z'
    sendSerial(temp)

def sendZOOMstop():
    temp='^N'
    sendSerial(temp)

def sendSET1():
    temp='^a'
    sendSerial(temp)

def sendSET2():
    temp='^b'
    sendSerial(temp)

def sendSET3():
    temp='^c'
    sendSerial(temp)

def sendSET4():
    temp='^d'
    sendSerial(temp)

def sendSET5():
    temp='^e'
    sendSerial(temp)

def sendSET6():
    temp='^f'
    sendSerial(temp)

def sendGO1():
    temp='^A'
    sendSerial(temp)

def sendGO2():
    temp='^B'
    sendSerial(temp)

def sendGO3():
    temp='^C'
    sendSerial(temp)

def sendGO4():
    temp='^D'
    sendSerial(temp)

def sendGO5():
    temp='^E'
    sendSerial(temp)

def sendGO6():
    temp='^F'
    sendSerial(temp)

def sendSPEEDfast():
    temp='^V'
    sendSerial(temp)

def sendSPEEDslow():
    temp='^v'
    sendSerial(temp)

def sendREPORTall():
    temp='^R'
    sendSerial(temp)

def sendREPORTpos():
    global canSendReport
    global previousTicksReport

    temp='^W'
    sendSerial(temp)
    canSendReport = True
    previousTicksReport = pygame.time.get_ticks() + intervalReport

def clearPosConfirm():
    message_window = UIConfirmationDialog(pygame.Rect((650, 200), (300, 200)), 
                                        ui_manager,
                                        action_long_desc='Clear All Position Data?')

def sendCLEARALLpos():
    temp='^Y'
    sendSerial(temp)

def sendCLEARtext():
    global serialText
    serialText = ''
    textBoxSerial.kill()
    serialPortTextBox()

def serialPort_changed():
    global ser
    global baudRate
    global current_serialPort
    global serialText
    global drop_down_serial
    
    serialPortSelect = drop_down_serial.selected_option
    try:
        ser = Serial(serialPortSelect , baudRate, timeout=0, writeTimeout=0)
        temp='^W'
        sendSerial(temp)
        readSerial()
    except:
        ser = ''
        serialNotSel = 'Serial port not available!<br>'
        textBoxSerial.kill()
        serialText = serialNotSel + serialText
        serialPortTextBox()
        drop_down_serial.kill()
        drop_down_serial = UIDropDownMenu(available_ports,                      # Recreate serial port drop down list
                                        current_serialPort[0],                  # Currently selected port
                                        pygame.Rect((620,95),
                                        (250, 30)),
                                        ui_manager)

def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))

def sendJoystick(arr):
    global ser
    global data
    
    sliderInt = int(arr[1], 16)
    panInt = int(arr[2], 16)
    tiltInt = int(arr[3], 16)

    data[0] = 4
    
    if ((sliderInt > 0) and (sliderInt < 256)):
        data[1] = 0
        data[2] = sliderInt
    elif sliderInt > 257:
        data[1] = 255
        data[2] = (sliderInt-65281)
    else:
        data[1] = 0
        data[2] = 0

    if ((panInt > 0) and (panInt < 256)):
        data[3] = 0
        data[4] = panInt
    elif panInt > 257:
        data[3] = 255
        data[4] = (panInt-65281)
    else:
        data[3] = 0
        data[4] = 0

    if ((tiltInt > 0) and (tiltInt < 256)):
        data[5] = 0
        data[6] = tiltInt
    elif tiltInt > 257:
        data[5] = 255
        data[6] = (tiltInt-65281)
    else:
        data[5] = 0
        data[6] = 0
    
    if ser == '':
        pass
    else:
        ser.write(data)
        #print(data)

def serialPortTextBox():
    global textBoxSerial
    textBoxSerial = UITextBox('<font face=roboto size=5 color=#F0F0F0>' + serialText + '</font>',
                                        pygame.Rect((620, 130), (560, 510)),
                                        ui_manager)
                                        #wrap_to_height=False)
    
def textBoxJoystickName():
    global joystickName
    global textBoxJoystickNames
    textBoxJoystickNames = UITextBox(joystickName,
                                        pygame.Rect((620, 30), (560, 35)),
                                        ui_manager)

def readSerial():
    global ser
    global serBuffer
    global serialText
    global atPos1
    global atPos2
    global atPos3
    global atPos4
    global atPos5
    global atPos6
    global pos1set
    global pos2set
    global pos3set
    global pos4set
    global pos5set
    global pos6set
    global pos1run
    global pos2run
    global pos3run
    global pos4run
    global pos5run
    global pos6run
    global speedIsFast
    global speedRec

    if (ser == ''):
        return
    else:
        while True:
            c = ser.read()
            
            if len(c) == 0:
                break
            
            if (c == b'\x04'):                                          # Ignore received joystick commands from other remote
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ''
            elif (c == b'^'):
                c = ser.read()
                c = ''
            elif (c == b'\xb0'):                                        # Change / remove characters that cause error
                c = '°'
            elif (c == b'\xb2'):
                c = '²'
            elif (c == b'\xba') or (c == b'\xc2') or (c == b'\xc9'):
                c = ''
            elif (c == b'\x23'):                                        # c = # Remove HASHTAG commands
                c = ser.read()
                if c == b'A':
                    #atPos1 = True
                    pos1set = True
                elif c == b'B':
                    #atPos2 = True
                    pos2set = True
                elif c == b'C':
                    #atPos3 = True
                    pos3set = True
                elif c == b'D':
                    #atPos4 = True
                    pos4set = True
                elif c == b'E':
                    pos5set = True
                    #atPos5 = True
                elif c == b'F':
                    #atPos6 = True
                    pos6set = True
                elif c == b'J':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                    pos1run = True
                elif c == b'K':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                    pos2run = True
                elif c == b'L':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                    pos3run = True
                elif c == b'M':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                    pos4run = True
                elif c == b'N':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                    pos5run = True
                elif c == b'O':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                    pos6run = True
                elif c == b'a':
                    pos1run = False
                    atPos1 = True
                elif c == b'b':
                    pos2run = False
                    atPos2 = True
                elif c == b'c':
                    pos3run = False
                    atPos3 = True
                elif c == b'd':
                    pos4run = False
                    atPos4 = True
                elif c == b'e':
                    pos5run = False
                    atPos5 = True
                elif c == b'f':
                    pos6run = False
                    atPos6 = True
                elif c == b'Y':
                    pos1run = False
                    pos1set = False
                    atPos1 = False
                    pos2run = False
                    pos2set = False
                    atPos2 = False
                    pos3run = False
                    pos3set = False
                    atPos3 = False
                    pos4run = False
                    pos4set = False
                    atPos4 = False
                    pos5run = False
                    pos5set = False
                    atPos5 = False
                    pos6run = False
                    pos6set = False
                    atPos6 = False
                elif c == b'y':
                    atPos1 = False
                    atPos2 = False
                    atPos3 = False
                    atPos4 = False
                    atPos5 = False
                    atPos6 = False
                elif c == b'V':
                    speedIsFast = True
                    speedRec = True
                elif c == b'v':
                    speedIsFast = False
                    speedRec = True
                #c = '\n'
                c = ''
            else:
                c = c.decode('ascii') 

            if (c == '\r'):                                             # check if character is a delimeter
                c = ''                                                  # don't want returns. chuck it

            if (c == '\t'):                                             # check if character is a tab
                c = '<br>'#' - '                                        # adjust
                
            if c == '\n':
                serBuffer += '<br>'                                     # replace \n with HTML <br>
                #textOUTPUT.insert(END, serBuffer)                      # code for tkinter
                #textOUTPUT.see(END)                                    # code for tkinter
                #serialText += serBuffer                                # code for tkinter
                textBoxSerial.kill()
                serialText = serBuffer + serialText
                serialPortTextBox()
                serBuffer = ''                                          # empty the buffer
            else:
                serBuffer += c                                          # add to the buffer

def sendSerial(sendValue):
    global ser
    global serialText
    if (ser == ''):                                                     # Checks to see if com port has been selected
        serialNotSel = 'Serial port not selected!<br>'
        textBoxSerial.kill()
        serialText = serialNotSel + serialText
        serialPortTextBox()
        #textOUTPUT.insert(END, 'Serial port not selected!\n')          # code for tkinter
        #textOUTPUT.see(END)                                            # code for tkinter
    else:
        ser.write(sendValue.encode())                                   # Send button value to coneected com port
        
def scale(val, src, dst):
    # Scale the given value from the scale of src to the scale of dst.
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
    
def initialiseJoysticks():
    global joystick
    global joystickName
    available_joysticks = []                                            # for returning
    pygame.joystick.init()                                              # Initialise the Joystick sub-module
    joystick_count = pygame.joystick.get_count()                        # Get count of joysticks

    for i in range( joystick_count ):                                   # For each joystick:
        joystick = pygame.joystick.Joystick( i )
        joystick.init()
        available_joysticks.append( joystick )

    if ( len( available_joysticks ) == 0 ):
        joystickName =  "No joystick found."
        #print( "No joystick found." )
    else:
        for i,joystk in enumerate( available_joysticks ):
            joystickName = joystk.get_name()
            #print("Joystick %d is named [%s]" % ( i, joystickName ) )

    return available_joysticks

def int_to_bytes(number: int) -> bytes:
    return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)

def doRefresh():
    global drop_down_serial
    global ser
    global current_serialPort
    global baudRate
    usb_port = 'usbserial'
    wchusb_port = 'wchusbserial'
    current_serialPort = ' - '
    drop_down_serial.kill()                                             # Clear serial port drop down box
    ports = serial.tools.list_ports.comports()                          # Search for attached serial ports
    available_ports = []
    for p in ports:
        available_ports.append(p.device)                                # Append each found serial port to array available_ports

    if current_serialPort == ' - ':
        if (wchusb_port in '\t'.join(available_ports)):
            try:
                current_serialPort = [string for string in available_ports if wchusb_port in string]
                ser = Serial(current_serialPort[0], baudRate, timeout=0, writeTimeout=0)
                temp='^W'
                sendSerial(temp)
                readSerial()
            except:
                current_serialPort = [' - ']
        elif (usb_port in '\t'.join(available_ports)):
            try:
                current_serialPort = [string for string in available_ports if usb_port in string]
                ser = Serial(current_serialPort[0], baudRate, timeout=0, writeTimeout=0)
                temp='^W'
                sendSerial(temp)
                readSerial()
            except:
                current_serialPort = [' - ']
        else:
            current_serialPort = [' - ']

    drop_down_serial = UIDropDownMenu(available_ports,                  # Recreate serial port drop down list
                                current_serialPort[0],                  # Currently selected port
                                pygame.Rect((620,95),
                                (250, 30)),
                                ui_manager)
    
    initialiseJoysticks()
    textBoxJoystickName()

initialiseJoysticks()

if fullscreen:
    window_surface = pygame.display.set_mode(resolution,
                                                    pygame.FULLSCREEN)
else:
    window_surface = pygame.display.set_mode(resolution)

background_surface = None

try:
    base_path = Path(__file__).parent                                                   # Needed for macOS "py2app"
    file_path = (base_path / "./theme.json").resolve()
    ui_manager = UIManager(resolution, file_path)
except:
    themeFile = "theme.json"
    themeFilePath = find_data_file(themeFile)
    ui_manager = UIManager(resolution, themeFilePath)

running = True

clock = pygame.time.Clock()
time_delta_stack = deque([])

button_response_timer = pygame.time.Clock()

ui_manager.set_window_resolution(resolution)
ui_manager.clear_and_reset()

background_surface = pygame.Surface(resolution)
background_surface.fill(ui_manager.get_theme().get_colour('dark_bg'))

rel_button_L1 = UIButton(pygame.Rect((120, 180), (60, 60)), '.5', ui_manager, object_id='#everything_button')
rel_button_L10 = UIButton(pygame.Rect((60, 180), (60, 60)), '10', ui_manager, object_id='#everything_button')
rel_button_R1 = UIButton(pygame.Rect((240, 180), (60, 60)), '.5', ui_manager, object_id='#everything_button')
rel_button_R10 = UIButton(pygame.Rect((300, 180), (60, 60)), '10', ui_manager, object_id='#everything_button')
rel_button_U1 = UIButton(pygame.Rect((180, 120), (60, 60)), '.5', ui_manager, object_id='#everything_button')
rel_button_U10 = UIButton(pygame.Rect((180, 60), (60, 60)), '10', ui_manager, object_id='#everything_button')
rel_button_D1 = UIButton(pygame.Rect((180, 240), (60, 60)), '.5', ui_manager, object_id='#everything_button')
rel_button_D10 = UIButton(pygame.Rect((180, 300), (60, 60)), '10', ui_manager, object_id='#everything_button')
#rel_button_set0 = UIButton(pygame.Rect((190, 190), (40, 40)), '0', ui_manager)             # Resets position back to zero
rel_button_SL10 = UIButton(pygame.Rect((120, 400), (60, 60)), '10', ui_manager, object_id='#everything_button')
rel_button_SL100 = UIButton(pygame.Rect((60, 400), (60, 60)), '100', ui_manager, object_id='#everything_button')
rel_button_SR10 = UIButton(pygame.Rect((240, 400), (60, 60)), '10', ui_manager, object_id='#everything_button')
rel_button_SR100 = UIButton(pygame.Rect((300, 400), (60, 60)), '100', ui_manager, object_id='#everything_button')

rel_button_SET1 = UIButton(pygame.Rect((30, 560), (60, 60)), 'SET 1', ui_manager, object_id='#everything_button')
rel_button_SET2 = UIButton(pygame.Rect((90, 560), (60, 60)), 'SET 2', ui_manager, object_id='#everything_button')
rel_button_SET3 = UIButton(pygame.Rect((150, 560), (60, 60)), 'SET 3', ui_manager, object_id='#everything_button')
rel_button_SET4 = UIButton(pygame.Rect((210, 560), (60, 60)), 'SET 4', ui_manager, object_id='#everything_button')
rel_button_SET5 = UIButton(pygame.Rect((270, 560), (60, 60)), 'SET 5', ui_manager, object_id='#everything_button')
rel_button_SET6 = UIButton(pygame.Rect((330, 560), (60, 60)), 'SET 6', ui_manager, object_id='#everything_button')

rel_button_GO1 = UIButton(pygame.Rect((30, 500), (60, 60)), 'GO 1', ui_manager, object_id='#everything_button')
rel_button_GO2 = UIButton(pygame.Rect((90, 500), (60, 60)), 'GO 2', ui_manager, object_id='#everything_button')
rel_button_GO3 = UIButton(pygame.Rect((150, 500), (60, 60)), 'GO 3', ui_manager, object_id='#everything_button')
rel_button_GO4 = UIButton(pygame.Rect((210, 500), (60, 60)), 'GO 4', ui_manager, object_id='#everything_button')
rel_button_GO5 = UIButton(pygame.Rect((270, 500), (60, 60)), 'GO 5', ui_manager, object_id='#everything_button')
rel_button_GO6 = UIButton(pygame.Rect((330, 500), (60, 60)), 'GO 6', ui_manager, object_id='#everything_button')

rel_button_CLEARALL = UIButton(pygame.Rect((390, 545), (100, 30)), 'Clear ALL', ui_manager, object_id='#everything_button')

rel_button_Refresh = UIButton(pygame.Rect((430, 35), (160, 35)), 'Refresh Ports', ui_manager, object_id='#everything_button')

rel_button_FAST = UIButton(pygame.Rect((480, 100), (60, 60)), 'FAST', ui_manager, object_id='#everything_button')
rel_button_SLOW = UIButton(pygame.Rect((480, 160), (60, 60)), 'SLOW', ui_manager, object_id='#everything_button')

rel_button_REPORT = UIButton(pygame.Rect((510, 470), (100, 60)), 'Report All', ui_manager, object_id='#everything_button')
rel_button_REPORTPOS = UIButton(pygame.Rect((510, 530), (100, 60)), 'Report Pos', ui_manager, object_id='#everything_button')
rel_button_CLEARtext = UIButton(pygame.Rect((510, 600), (100, 40)), 'Clear Text', ui_manager, object_id='#everything_button')

joystick_label = UILabel(pygame.Rect(540, 10, 230, 24), "Joystick", ui_manager)#, object_id='#main_text_entry')
serial_text_entry = UITextEntryLine(pygame.Rect((930, 95), (250, 35)), ui_manager, object_id='#main_text_entry')
serial_port_label = UILabel(pygame.Rect(550, 70, 230, 24), "Serial Port", ui_manager)
serial_command_label = UILabel(pygame.Rect(870, 70, 230, 24), "Serial Command", ui_manager)

usb_port = 'usbserial'
wchusb_port = 'wchusbserial'
current_serialPort = ' - '
ports = serial.tools.list_ports.comports()                                                       # Search for attached serial ports
available_ports = []
for p in ports:
    available_ports.append(p.device)                                                             # Append each found serial port to array available_ports

if current_serialPort == ' - ':
    if (wchusb_port in '\t'.join(available_ports)):
        try:
            current_serialPort = [string for string in available_ports if wchusb_port in string]
            ser = Serial(current_serialPort[0], baudRate, timeout=0, writeTimeout=0)
            temp='^W'
            sendSerial(temp)
            readSerial()
        except:
                current_serialPort = [' - ']
    elif (usb_port in '\t'.join(available_ports)):
        try:
            current_serialPort = [string for string in available_ports if usb_port in string]
            ser = Serial(current_serialPort[0], baudRate, timeout=0, writeTimeout=0)
            temp='^W'
            sendSerial(temp)
            readSerial()
        except:
                current_serialPort = [' - ']
    else:
        current_serialPort = [' - ']

drop_down_serial = UIDropDownMenu(available_ports,                                              # Recreate serial port drop down list
                            current_serialPort[0],                                              # Currently selected port
                            pygame.Rect((620,95),
                            (250, 30)),
                            ui_manager)

serialPortTextBox()
textBoxJoystickName()

joyCircle = pygame.draw.circle(window_surface, pygame.Color("blue"), (225,225), radius)
joyCircle_draging = False

joyCircle.x = 195
joyCircle.y = 195

# Generate crosshair
crosshair = pygame.surface.Surface((30, 30))
crosshair.fill(pygame.Color("magenta"))
pygame.draw.circle(crosshair, pygame.Color("blue"), (radius,radius), radius)
crosshair.set_colorkey(pygame.Color("magenta"))#, pygame.RLEACCEL)
#crosshair = crosshair.convert()

sliderCircle = pygame.draw.circle(window_surface, pygame.Color("blue"), (225,415), radius)
sliderCircle_draging = False

sliderCircle.x = 195
sliderCircle.y = 415

# Generate crosshair
crosshairSlider = pygame.surface.Surface((30, 30))
crosshairSlider.fill(pygame.Color("magenta"))
pygame.draw.circle(crosshairSlider, pygame.Color("blue"), (radius,radius), radius)
crosshairSlider.set_colorkey(pygame.Color("magenta"))#, pygame.RLEACCEL)
#crosshair = crosshair.convert()

ui_manager.set_focus_set(textBoxSerial)                                                                     # Sets focus so focus can be tested

def process_events():
    global arr
    global joystick
    global joystickName
    global button0Pressed
    global button1Pressed
    global button2Pressed
    global button3Pressed
    global button4Pressed
    global button5Pressed
    global button6Pressed
    global button7Pressed
    global button8Pressed
    global button9Pressed
    global button10Pressed
    global button11Pressed
    global button12Pressed
    global button13Pressed
    global button14Pressed
    global button15Pressed
    global button16Pressed
    global oldAxisX
    global oldAxisY
    global oldAxisZ
    global oldHatX
    global oldHatY
    global axisX
    global axisY
    global axisZ
    global previousTime
    global mouseMoving
    global joyCircle_draging
    global sliderCircle_draging
    global offset_x
    global offset_y
    global sliderOffset_x
    global sliderOffset_y
    global running
    global joyXreadDOT
    global joyYreadDOT
    global joyZreadDOT
    global panKeyPresseed
    global tiltKeyPresseed
    global sliderKeyPresseed
    global drop_down_serial
    global isZooming

    joyPS4 = "Sony"
    joyPS4BT = "DUALSHOCK"
    joyPS4Win = "PS4"
    joy360 = "360"
    joyNimbus = "Nimbus"
    joySN30 = "SN30"
    joySN30BT = "Unknown Wireless Controller"

    UITextEntry = "UITextEntryLine"
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if 482 <= mouse[0] <= 482+56 and 262 <= mouse[1] <= 262+56:
                isZooming = True
                sendZOOMin()
                #print("IN pressed")
            if 482 <= mouse[0] <= 482+56 and 322 <= mouse[1] <= 322+56:
                isZooming = True
                sendZOOMout()
                #print("OUT pressed")

        if event.type == pygame.MOUSEBUTTONUP and isZooming:
            isZooming = False
            sendZOOMstop()

        ui_manager.process_events(event)
        deadRangeLow = -0.2
        deadRangeHigh = 0.2

        whereIsFocus = str(ui_manager.get_focus_set())
        if (event.type == pygame.KEYDOWN) and not (UITextEntry in whereIsFocus):
            if event.key == ord('a'):
                axisX = int(-255)
                panKeyPresseed = True
                #print('Left')
            if event.key == ord('d'):
                axisX = int(255)
                panKeyPresseed = True
                #print('Right')
            if event.key == ord('w'):
                axisY = int(-255)
                tiltKeyPresseed = True
                #print('Up')
            if event.key == ord('s'):
                axisY = int(255)
                tiltKeyPresseed = True
                #print('Down')
            if event.key == ord(','):
                axisZ = int(-255)
                sliderKeyPresseed = True
                #print('Slider Left')
            if event.key == ord('.'):
                axisZ = int(255)
                sliderKeyPresseed = True
                #print('Slider Right')

        if (event.type == pygame.KEYUP) and not (UITextEntry in whereIsFocus):
            if event.key == ord('a'):
                axisX = int(0)
                panKeyPresseed = False
                #print('Left stop')
            if event.key == ord('d'):
                axisX = int(0)
                panKeyPresseed = False
                #print('Right stop')
            if event.key == ord('w'):
                axisY = int(0)
                tiltKeyPresseed = False
                #print('Up stop')
            if event.key == ord('s'):
                axisY = int(0)
                tiltKeyPresseed = False
                #print('Down stop')
            if event.key == ord(','):
                axisZ = int(0)
                sliderKeyPresseed = False
                #print('Slider Left stop')
            if event.key == ord('.'):
                axisZ = int(0)
                sliderKeyPresseed = False
                #print('Slider Right stop')

        # left 1
        # right 2
        # down 3
        # up 4

        if joystick == '':
            pass
        else:
            if (joyPS4 in joystickName) or (joyPS4BT in joystickName) or (joyPS4Win in joystickName):
                #print ("PS4 Controller Found")
                hat = joystick.get_hat(0)
                hatX = hat[0]
                hatY = hat[1]
                if (hatX != oldHatX):
                    oldHatX = hatX
                    if hatX == 1:                                                       # PS4 RIGHT
                        sendSET2()
                    if hatX == -1:                                                      # PS4 LEFT
                        sendSET1()

                if (hatY != oldHatY):
                    oldHatY = hatY
                    if hatY == 1:                                                       # PS4 UP
                        sendSET4()
                    if hatY == -1:                                                      # PS4 DOWN
                        sendSET3()

                if event.type == pygame.JOYBUTTONDOWN: 
                    if (joystick.get_button(0) and not button0Pressed):                 # PS4 Square
                        button0Pressed = True
                        sendGO1()
                        #print("0 - Squ") 
                    elif (joystick.get_button(1) and not button1Pressed):               # PS4 Cross
                        button1Pressed = True
                        sendGO3()
                        #print("1 - Cro")                    
                    elif (joystick.get_button(2) and not button2Pressed):               # PS4 Circle
                        button2Pressed = True
                        sendGO2()
                        #print("2" - Cir)
                    elif (joystick.get_button(3) and not button3Pressed):               # PS4 Triangle
                        button3Pressed = True
                        sendGO4()
                        #print("3 - Tri")
                    elif (joystick.get_button(4) and not button4Pressed):               # PS4 L1
                        button4Pressed = True
                        sendSPEEDslow()
                        #print("4 - L1")
                    elif (joystick.get_button(5) and not button5Pressed):               # PS4 R1
                        button5Pressed = True
                        sendSPEEDfast()
                        #print("5 - R1")
                    elif (joystick.get_button(6) and not button6Pressed):               # PS4 L2
                        button6Pressed = True
                        sendZOOMout()
                        isZooming = True
                        #print("6 - L2")
                    elif (joystick.get_button(7) and not button7Pressed):               # PS4 R2
                        button7Pressed = True
                        sendZOOMin()
                        isZooming = True
                        #print("7 - R2")
                    elif (joystick.get_button(8) and not button8Pressed):               # PS4 Share
                        button8Pressed = True
                        sendREPORTpos()
                        #print("8 - Sha")
                    elif (joystick.get_button(9) and not button9Pressed):               # PS4 Option
                        button9Pressed = True
                        sendREPORTpos()
                        #print("9 - Opt")
                    elif (joystick.get_button(10) and not button10Pressed):             # PS4 L3
                        buttonL10ressed = True
                        sendREPORTpos()
                        #print("10 - L3")
                    elif (joystick.get_button(11) and not button11Pressed):             # PS4 R3
                        button11Pressed = True
                        sendREPORTpos()
                        #print("11 - R3")
                if event.type == pygame.JOYBUTTONUP:
                    if button6Pressed and not joystick.get_button(6):
                        button6Pressed = False
                        sendZOOMstop()
                        isZooming = False
                    elif button7Pressed and not joystick.get_button(7):
                        button7Pressed = False
                        sendZOOMstop()
                        isZooming = False

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0

            elif joy360 in joystickName:
                #print ("360 Controller Found")
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # 360 - A
                        button0Pressed = True
                        sendGO3()
                        #print("0 - A") 
                    elif (joystick.get_button(1) and not button1Pressed):               # 360 - B
                        button1Pressed = True
                        sendGO2()
                        #print("1 - B")                    
                    elif (joystick.get_button(2) and not button2Pressed):               # 360 - X
                        button2Pressed = True
                        sendGO1()
                        #print("2 - X")
                    elif (joystick.get_button(3) and not button3Pressed):               # 360 - Y
                        button3Pressed = True
                        sendGO4()
                        #print("3 - Y")
                    elif (joystick.get_button(4) and not button4Pressed):               # 360 - L1
                        button4Pressed = True
                        sendSPEEDslow()
                        #print("4 - L1")
                    elif (joystick.get_button(5) and not button5Pressed):               # 360 - R1
                        button5Pressed = True
                        sendSPEEDfast()
                        #print("5 - R1")
                    elif (joystick.get_button(6) and not button6Pressed):               # 360 - L3
                        button6Pressed = True
                        sendREPORTall()
                        #print("6 - L3")
                    elif (joystick.get_button(7) and not button7Pressed):               # 360 - R3
                        button7Pressed = True
                        sendREPORTall()
                        #print("7 - R3")
                    elif (joystick.get_button(8) and not button8Pressed):               # 360 - Start
                        button8Pressed = True
                        sendREPORTall()
                        #print("8 - Start")
                    elif (joystick.get_button(9) and not button9Pressed):               # 360 - Back
                        button9Pressed = True
                        sendREPORTall()
                        #print("9 - Back")
                    elif (joystick.get_button(10) and not button10Pressed):             # 360 - XBOX
                        button10Pressed = True
                        sendREPORTall()
                        #print("10 - XBOX")
                    elif (joystick.get_button(11) and not button11Pressed):             # 360 - Up
                        button11Pressed = True
                        sendSET4()
                        #print("11 - Up")
                    elif (joystick.get_button(12) and not button12Pressed):             # 360 - Down
                        button12Pressed = True
                        sendSET3()
                        #print("12 - Down")
                    elif (joystick.get_button(13) and not button13Pressed):             # 360 - Left
                        button13Pressed = True
                        sendSET1()
                        #print("13 - Left")
                    elif (joystick.get_button(14) and not button14Pressed):             # 360 - Right
                        button14Pressed = True
                        sendSET2()
                        #print("14 - Right")

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    joyL2read = joystick.get_axis(2)
                    joyR2read = joystick.get_axis(5)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                    if (joyL2read > 0) and not button15Pressed:
                        isZooming = True
                        sendZOOMout()
                        button15Pressed = True

                    if (joyR2read > 0) and not button16Pressed:
                        isZooming = True
                        sendZOOMin()
                        button16Pressed = True
                    
                    if (button15Pressed and (joyL2read < 0)):
                        isZooming = False
                        sendZOOMstop()
                        button15Pressed = False

                    if (button16Pressed and (joyR2read < 0)):
                        isZooming = False
                        sendZOOMstop()
                        button16Pressed = False

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(3)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0

            elif joyNimbus in joystickName:
                #print ("Nimbus Controller Found")
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # Nimbus - A
                        button0Pressed = True
                        sendGO3()
                        #print("0 - A") 
                    elif (joystick.get_button(1) and not button1Pressed):               # Nimbus - B
                        button1Pressed = True
                        sendGO2()
                        #print("1 - B")                    
                    elif (joystick.get_button(2) and not button2Pressed):               # Nimbus - X
                        button2Pressed = True
                        sendGO1()
                        #print("2 - X")
                    elif (joystick.get_button(3) and not button3Pressed):               # Nimbus - Y
                        button3Pressed = True
                        sendGO4()
                        #print("3 - Y")
                    elif (joystick.get_button(4) and not button4Pressed):               # Nimbus - L1
                        button4Pressed = True
                        sendSPEEDslow()
                        #print("4 - L1")
                    elif (joystick.get_button(5) and not button5Pressed):               # Nimbus - R1
                        button5Pressed = True
                        sendSPEEDfast()
                        #print("5 - R1")
                    elif (joystick.get_button(6) and not button6Pressed):               # Nimbus - L2
                        button6Pressed = True
                        isZooming = True
                        sendZOOMout()
                        #print("6 - L2")
                    elif (joystick.get_button(7) and not button7Pressed):               # Nimbus - R2
                        button7Pressed = True
                        isZooming = True
                        sendZOOMin()
                        #print("7 - R2")
                    elif (joystick.get_button(8) and not button8Pressed):               # Nimbus - Up
                        button8Pressed = True
                        sendSET4()
                        #print("8 - Up")
                    elif (joystick.get_button(9) and not button9Pressed):               # Nimbus - Down
                        button9Pressed = True
                        sendSET3()
                        #print("9 - Down")
                    elif (joystick.get_button(10) and not button10Pressed):             # Nimbus - Right
                        button10Pressed = True
                        sendSET2()
                        #print("10 - Right")
                    elif (joystick.get_button(11) and not button11Pressed):             # Nimbus - Left
                        button11Pressed = True
                        sendSET1()
                        #print("11 - Left")
                    elif (joystick.get_button(12) and not button12Pressed):             # Nimbus - Menu
                        button12Pressed = True
                        sendREPORTall()
                        #print("12 - Menu")

                if event.type == pygame.JOYBUTTONUP:
                    if button6Pressed and not joystick.get_button(6):
                        button6Pressed = False
                        sendZOOMstop()
                        isZooming = False
                    elif button7Pressed and not joystick.get_button(7):
                        button7Pressed = False
                        sendZOOMstop()
                        isZooming = False

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = -(joystick.get_axis(1))

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0

            elif (joySN30 in joystickName) or (joySN30BT in joystickName):
                #print ("SN30 Controller Found")
                hat = joystick.get_hat(0)
                hatX = hat[0]
                hatY = hat[1]
                if (hatX != oldHatX):
                    oldHatX = hatX
                    if hatX == 1:                                                       # SN30 RIGHT
                        sendSET2()
                    if hatX == -1:                                                      # SN30 LEFT
                        sendSET1()

                if (hatY != oldHatY):
                    oldHatY = hatY
                    if hatY == 1:                                                       # SN30 UP
                        sendSET4()
                    if hatY == -1:                                                      # SN30 DOWN
                        sendSET3()

                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # SN30 - B
                        button0Pressed = True
                        sendGO3()
                        #print("0 - B") 
                    elif (joystick.get_button(1) and not button1Pressed):               # SN30 - A
                        button1Pressed = True
                        sendGO2()
                        #print("1 - A")
                    elif (joystick.get_button(2) and not button2Pressed):               # SN30 - Heart
                        button2Pressed = True
                        sendREPORTall()
                        #print("2 - Heart")
                    elif (joystick.get_button(3) and not button3Pressed):               # SN30 - X
                        button3Pressed = True
                        sendGO4()
                        #print("3 - X")
                    elif (joystick.get_button(4) and not button4Pressed):               # SN30 - Y
                        button4Pressed = True
                        sendGO1()
                        #print("4 - Y")
                    #elif (joystick.get_button(5) and not button5Pressed):               # SN30 - None
                    #    button5Pressed = True
                    #    sendREPORTall()
                        #print("5 - None")
                    elif (joystick.get_button(6) and not button6Pressed):               # SN30 - L1
                        button6Pressed = True
                        sendSPEEDslow()
                        #print("6 - L1")
                    elif (joystick.get_button(7) and not button7Pressed):               # SN30 - R1
                        button7Pressed = True
                        sendSPEEDfast()
                        #print("7 - R1")
                    elif (joystick.get_button(8) and not button8Pressed):               # SN30 - L2
                        button8Pressed = True
                        isZooming = True
                        sendZOOMout()
                        #print("8 - L2")
                    elif (joystick.get_button(9) and not button9Pressed):               # SN30 - R2
                        button9Pressed = True
                        isZooming = True
                        sendZOOMin()
                        #print("9 - R2")
                    elif (joystick.get_button(10) and not button10Pressed):             # SN30 - Select
                        button10Pressed = True
                        sendREPORTall()
                        #print("10 - Select")
                    elif (joystick.get_button(11) and not button11Pressed):             # SN30 - Start
                        button11Pressed = True
                        sendREPORTall()
                        #print("11 - Start")
                    #elif (joystick.get_button(12) and not button12Pressed):             # SN30 - None
                    #    button10Pressed = True
                    #    sendREPORTall()
                        #print("12 - None")
                    elif (joystick.get_button(13) and not button13Pressed):             # SN30 - L3
                        button13Pressed = True
                        sendREPORTall()
                        #print("13 - L3")
                    elif (joystick.get_button(14) and not button14Pressed):             # SN30 - R3
                        button14Pressed = True
                        sendREPORTall()
                        #print("14 - R3")

                if event.type == pygame.JOYBUTTONUP:
                    if button8Pressed and not joystick.get_button(8):
                        button8Pressed = False
                        sendZOOMstop()
                        isZooming = False
                    elif button9Pressed and not joystick.get_button(9):
                        button9Pressed = False
                        sendZOOMstop()
                        isZooming = False

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0

            else:
                #print ("Other Controller Found")
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # A
                        button0Pressed = True
                        sendGO4()
                        #print("0 - A") 
                    elif (joystick.get_button(1) and not button1Pressed):               # B
                        button1Pressed = True
                        sendGO1()
                        #print("1 - B")                    
                    elif (joystick.get_button(2) and not button2Pressed):               # X
                        button2Pressed = True
                        sendGO2()
                        #print("2 - X")
                    elif (joystick.get_button(3) and not button3Pressed):               # Y
                        button3Pressed = True
                        sendGO3()
                        #print("3 - Y")
                    elif (joystick.get_button(4) and not button4Pressed):               # L1
                        button4Pressed = True
                        sendSPEEDslow()
                        #print("4 - L1")
                    elif (joystick.get_button(5) and not button5Pressed):               # R1
                        button5Pressed = True
                        sendSPEEDfast()
                        #print("5 - R1")
                    elif (joystick.get_button(6) and not button6Pressed):               # L2
                        button6Pressed = True
                        isZooming = True
                        sendZOOMout()
                        #print("6 - L2")
                    elif (joystick.get_button(7) and not button7Pressed):               # R2
                        button7Pressed = True
                        isZooming = True
                        sendZOOMin()
                        #print("7 - R2")
                    elif (joystick.get_button(8) and not button8Pressed):               # Up
                        button8Pressed = True
                        sendSET3()
                        #print("8 - Up")
                    elif (joystick.get_button(9) and not button9Pressed):               # Down
                        button9Pressed = True
                        sendSET4()
                        #print("9 - Down")
                    elif (joystick.get_button(10) and not button10Pressed):             # Right
                        button10Pressed = True
                        sendSET1()
                        #print("10 - Right")
                    elif (joystick.get_button(11) and not button11Pressed):             # Left
                        button11Pressed = True
                        sendSET2()
                        #print("11 - Left")
                    elif (joystick.get_button(12) and not button12Pressed):             # Menu
                        button12Pressed = True
                        sendREPORTall()
                        #print("12 - Menu")

                if event.type == pygame.JOYBUTTONUP:
                    if button6Pressed and not joystick.get_button(6):
                        button6Pressed = False
                        sendZOOMstop()
                        isZooming = False
                    elif button7Pressed and not joystick.get_button(7):
                        button7Pressed = False
                        sendZOOMstop()
                        isZooming = False

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0

        if event.type == pygame.JOYBUTTONUP:
            if (button0Pressed and not joystick.get_button(0)):
                button0Pressed = False
            elif (button1Pressed and not joystick.get_button(1)):
                button1Pressed = False
            elif (button2Pressed and not joystick.get_button(2)):
                button2Pressed = False
            elif (button3Pressed and not joystick.get_button(3)):
                button3Pressed = False
            elif (button4Pressed and not joystick.get_button(4)):
                button4Pressed = False
            elif (button5Pressed and not joystick.get_button(5)):
                button5Pressed = False
            elif (button6Pressed and not joystick.get_button(6)):
                button6Pressed = False
            elif (button7Pressed and not joystick.get_button(7)):
                button7Pressed = False
            elif (button8Pressed and not joystick.get_button(8)):
                button8Pressed = False
            elif (button9Pressed and not joystick.get_button(9)):
                button9Pressed = False
            elif (button10Pressed and not joystick.get_button(10)):
                button10Pressed = False
            elif (button11Pressed and not joystick.get_button(11)):
                button11Pressed = False
            elif (button12Pressed and not joystick.get_button(12)):
                button12Pressed = False
            elif (button13Pressed and not joystick.get_button(13)):
                button13Pressed = False
            elif (button14Pressed and not joystick.get_button(14)):
                button14Pressed = False

        if event.type == pygame.USEREVENT:
            if (event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED):
                sendSerial(event.text)
                serial_text_entry.set_text('')

            if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                sendCLEARALLpos()

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == rel_button_L1:
                    sendLEFT1()
                elif event.ui_element == rel_button_L10:
                    sendLEFT10()
                elif event.ui_element == rel_button_R1:
                    sendRIGHT1()
                elif event.ui_element == rel_button_R10:
                    sendRIGHT10()
                elif event.ui_element == rel_button_U1:
                    sendUP1()
                elif event.ui_element == rel_button_U10:
                    sendUP10()
                elif event.ui_element == rel_button_D1:
                    sendDOWN1()
                elif event.ui_element == rel_button_D10:
                    sendDOWN10()
                #elif event.ui_element == rel_button_set0:
                #    sendRESETpos()
                elif event.ui_element == rel_button_SR10:
                    sendSR1()
                elif event.ui_element == rel_button_SR100:
                    sendSR10()
                elif event.ui_element == rel_button_SL10:
                    sendSL1()
                elif event.ui_element == rel_button_SL100:
                    sendSL10()
                elif event.ui_element == rel_button_SET1:
                    if not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendSET1()
                elif event.ui_element == rel_button_SET2:
                    if not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendSET2()
                elif event.ui_element == rel_button_SET3:
                    if not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendSET3()
                elif event.ui_element == rel_button_SET4:
                    if not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendSET4()
                elif event.ui_element == rel_button_SET5:
                    if not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendSET5()
                elif event.ui_element == rel_button_SET6:
                    if not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendSET6()
                elif event.ui_element == rel_button_GO1:
                    if pos1set and not atPos1 and not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendGO1()
                elif event.ui_element == rel_button_GO2:
                    if pos2set and not atPos2 and not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendGO2()
                elif event.ui_element == rel_button_GO3:
                    if pos3set and not atPos3 and not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendGO3()
                elif event.ui_element == rel_button_GO4:
                    if pos4set and not atPos4 and not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendGO4()
                elif event.ui_element == rel_button_GO5:
                    if pos5set and not atPos5 and not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendGO5()
                elif event.ui_element == rel_button_GO6:
                    if pos6set and not atPos6 and not (pos1run or pos2run or pos3run or pos4run or pos5run or pos6run):
                        sendGO6()
                elif event.ui_element == rel_button_CLEARALL:
                    clearPosConfirm()
                elif event.ui_element == rel_button_Refresh:
                    doRefresh()
                elif event.ui_element == rel_button_SLOW:
                    sendSPEEDslow()
                elif event.ui_element == rel_button_FAST:
                    sendSPEEDfast()
                elif event.ui_element == rel_button_REPORT:
                    sendREPORTall()
                elif event.ui_element == rel_button_REPORTPOS:
                    sendREPORTpos()
                elif event.ui_element == rel_button_CLEARtext:
                    sendCLEARtext()

            if (event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
                and event.ui_element == drop_down_serial):
                serialPort_changed()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:            
                if joyCircle.collidepoint(event.pos):
                    joyCircle_draging = True
                    mouse_x, mouse_y = event.pos
                    offset_x = joyCircle.x - mouse_x
                    offset_y = joyCircle.y - mouse_y

                if sliderCircle.collidepoint(event.pos):
                    sliderCircle_draging = True
                    mouse_x, mouse_y = event.pos
                    sliderOffset_x = sliderCircle.x - mouse_x
                    sliderOffset_y = sliderCircle.y - mouse_y

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if joyCircle_draging:
                    joyCircle_draging = False
                    joyCircle.x = 195
                    joyCircle.y = 195
                    axisX = int(0)
                    axisY = int(0)

                if sliderCircle_draging:
                    sliderCircle_draging = False
                    sliderCircle.x = 195
                    sliderCircle.y = 415
                    axisZ = int(0)

                mouseMoving = False
            if isZooming:
                sendZOOMstop()
                isZooming = False

        if event.type == pygame.MOUSEMOTION:
            if joyCircle_draging:
                mouseMoving = True
                mouse_x, mouse_y = event.pos
                joyCircle.x = mouse_x
                joyCircle.y = mouse_y
                """
                if ((mouse_x + offset_x) > mouseBorder) and ((mouse_y + offset_y) > mouseBorder):           # XY Dot out of box: right & bottom
                    joyCircle.x = mouseBorder
                    joyCircle.y = mouseBorder

                elif (((mouse_x + offset_x) > mouseBorder) and ((mouse_y + offset_y) < 30)):                # XY Dot out of box: right & top
                    joyCircle.x = mouseBorder
                    joyCircle.y = 30

                elif (((mouse_x + offset_x) < 30) and ((mouse_y + offset_y) > mouseBorder)):                # XY Dot out of box: left & bottom
                    joyCircle.x = 30
                    joyCircle.y = mouseBorder

                elif (((mouse_x + offset_x) < 30) and ((mouse_y + offset_y) < 30)):                         # XY Dot out of box: left & top
                    joyCircle.x = 30
                    joyCircle.y = 30

                elif ((mouse_x + offset_x) > (mouseBorder)):                                                # XY Dot out of box: right
                    joyCircle.x = mouseBorder
                    joyCircle.y = mouse_y + offset_y

                elif ((mouse_x + offset_x) < 30):                                                           # XY Dot out of box: left
                    joyCircle.x = 30
                    joyCircle.y = mouse_y + offset_y

                elif ((mouse_y + offset_y) > (mouseBorder)):                                                # XY Dot out of box: bottom
                    joyCircle.y = mouseBorder
                    joyCircle.x = mouse_x + offset_x

                elif ((mouse_y + offset_y) < 30):                                                           # XY Dot out of box: top
                    joyCircle.y = 30
                    joyCircle.x = mouse_x + offset_x

                else:
                    """
                joyCircle.x = mouse_x + offset_x                                                        # XY Dot inside box
                joyCircle.y = mouse_y + offset_y

                axisX = int(scale((joyCircle.x), (30,mouseBorder), (-255,255)))
                axisY = int(scale((joyCircle.y), (30,mouseBorder), (-255,255)))

                if axisX > 255:
                    axisX = 255

                if axisY > 255:
                    axisY = 255

                if axisX < -255:
                    axisX = -255

                if axisY < -255:
                    axisY = -255

            if sliderCircle_draging:
                mouseMoving = True
                mouse_x, mouse_y = event.pos
                sliderCircle.x = mouse_x
                sliderCircle.y = 420
                if ((mouse_x + sliderOffset_x) > mouseBorder):                                              # Z Dot out of box: right
                    sliderCircle.x = mouseBorder

                elif ((mouse_x + sliderOffset_x) < 30):                                                     # Z Dot out of box: left
                    sliderCircle.x = 30

                else:
                    sliderCircle.x = mouse_x + sliderOffset_x                                               # Z Dot inside box

                axisZ = int(scale((sliderCircle.x), (30,mouseBorder), (-255,255)))

        #axisXDOT = scale(axisX, (-255,255), (-1.0,1.0))
        #axisYDOT = scale(axisY, (-255,255), (-1.0,1.0))
        #axisZDOT = scale(axisZ, (-255,255), (-1.0,1.0))

        #joyCircle.x = (axisXDOT*165)+210-radius
        #joyCircle.y = (axisYDOT*165)+210-radius
        #sliderCircle.x = (axisZDOT*165)+210-radius

while running:
    time_delta = clock.tick() / 1000.0
    time_delta_stack.append(time_delta)
    
    process_events()                                                                                        # check for input

    if (((axisX != oldAxisX) or (axisY != oldAxisY) or (axisZ != oldAxisZ)) and ((time.time() - previousTime) > 0.1)):
        previousTime = time.time()
        oldAxisX = axisX
        oldAxisY = axisY
        oldAxisZ = axisZ
        axisXh = tohex(axisX, 16)
        axisYh = tohex(-axisY, 16)
        axisZh = tohex(axisZ, 16)

        arr = [4, axisZh, axisXh, axisYh]
        sendJoystick(arr)
        #print(4,' - ', axisZh, ' - ', axisXh, ' - ', axisYh)

        

    try:
        readSerial()
    except:
        ser=''
        current_serialPort = [' - ']
        serialNotSel = 'Serial port disconnected.<br>'
        textBoxSerial.kill()
        serialText = serialNotSel + serialText
        serialPortTextBox()
        
        speedRec = False
        pos1set = False
        pos2set = False
        pos3set = False
        pos4set = False
        pos5set = False
        pos6set = False
        atPos1 = False
        atPos2 = False
        atPos3 = False
        atPos4 = False
        atPos5 = False
        atPos6 = False
        pos1run = False
        pos2run = False
        pos3run = False
        pos4run = False
        pos5run = False
        pos6run = False

        ports = serial.tools.list_ports.comports()                              # Search for attached serial ports
        available_ports = []
        for p in ports:
            available_ports.append(p.device)                                    # Append each found serial port to array available_ports

        drop_down_serial.kill()
        drop_down_serial = UIDropDownMenu(available_ports,                      # Recreate serial port drop down list
                                        current_serialPort[0],                  # Currently selected port
                                        pygame.Rect((620,95),
                                        (250, 30)),
                                        ui_manager)

    ui_manager.update(time_delta)                                               # respond to input

    # Clear screen
    window_surface.blit(background_surface, (0, 0))                             # draw graphics


    # Draw position LEDs
    if pos1set and not pos1run and not atPos1:
        pygame.draw.circle(window_surface, RED, (60, 480), radius/2)
    elif pos1set and not pos1run and atPos1:
        pygame.draw.circle(window_surface, GREEN, (60, 480), radius/2)
    elif pos1set and pos1run and not atPos1:
        if blinkSet:
            pygame.draw.circle(window_surface, GREEN, (60, 480), radius/2)
        else:
            pygame.draw.circle(window_surface, OFF, (60, 480), radius/2)
    elif not pos1set:
        pygame.draw.circle(window_surface, OFF, (60, 480), radius/2)
    
    if pos2set and not pos2run and not atPos2:
        pygame.draw.circle(window_surface, RED, (120, 480), radius/2)
    elif pos2set and not pos2run and atPos2:
        pygame.draw.circle(window_surface, GREEN, (120, 480), radius/2)
    elif pos2set and pos2run and not atPos2:
        if blinkSet:
            pygame.draw.circle(window_surface, GREEN, (120, 480), radius/2)
        else:
            pygame.draw.circle(window_surface, OFF, (120, 480), radius/2)
    elif not pos2set:
        pygame.draw.circle(window_surface, OFF, (120, 480), radius/2)

    if pos3set and not pos3run and not atPos3:
        pygame.draw.circle(window_surface, RED, (180, 480), radius/2)
    elif pos3set and not pos3run and atPos3:
        pygame.draw.circle(window_surface, GREEN, (180, 480), radius/2)
    elif pos3set and pos3run and not atPos3:
        if blinkSet:
            pygame.draw.circle(window_surface, GREEN, (180, 480), radius/2)
        else:
            pygame.draw.circle(window_surface, OFF, (180, 480), radius/2)
    elif not pos3set:
        pygame.draw.circle(window_surface, OFF, (180, 480), radius/2)

    if pos4set and not pos4run and not atPos4:
        pygame.draw.circle(window_surface, RED, (240, 480), radius/2)
    elif pos4set and not pos4run and atPos4:
        pygame.draw.circle(window_surface, GREEN, (240, 480), radius/2)
    elif pos4set and pos4run and not atPos4:
        if blinkSet:
            pygame.draw.circle(window_surface, GREEN, (240, 480), radius/2)
        else:
            pygame.draw.circle(window_surface, OFF, (240, 480), radius/2)
    elif not pos4set:
        pygame.draw.circle(window_surface, OFF, (240, 480), radius/2)

    if pos5set and not pos5run and not atPos5:
        pygame.draw.circle(window_surface, RED, (300, 480), radius/2)
    elif pos5set and not pos5run and atPos5:
        pygame.draw.circle(window_surface, GREEN, (300, 480), radius/2)
    elif pos5set and pos5run and not atPos5:
        if blinkSet:
            pygame.draw.circle(window_surface, GREEN, (300, 480), radius/2)
        else:
            pygame.draw.circle(window_surface, OFF, (300, 480), radius/2)
    elif not pos5set:
        pygame.draw.circle(window_surface, OFF, (300, 480), radius/2)

    if pos6set and not pos6run and not atPos6:
        pygame.draw.circle(window_surface, RED, (360, 480), radius/2)
    elif pos6set and not pos6run and atPos6:
        pygame.draw.circle(window_surface, GREEN, (360, 480), radius/2)
    elif pos6set and pos6run and not atPos6:
        if blinkSet:
            pygame.draw.circle(window_surface, GREEN, (360, 480), radius/2)
        else:
            pygame.draw.circle(window_surface, OFF, (360, 480), radius/2)
    elif not pos6set:
        pygame.draw.circle(window_surface, OFF, (360, 480), radius/2)

    # Blink timer for position LEDs
    if previousTicks <= pygame.time.get_ticks():
        blinkSet = not blinkSet       
        previousTicks = pygame.time.get_ticks() + interval


    # Only enable sending of Report after delay
    if canSendReport and (previousTicksReport <= pygame.time.get_ticks()):
        canSendReport = False
        temp='^r'
        sendSerial(temp)


    # Speed LEDs
    if speedRec and speedIsFast:
        pygame.draw.circle(window_surface, GREEN, (460, 130), radius/2)
    elif speedRec and not speedIsFast:
        pygame.draw.circle(window_surface, GREEN, (460, 190), radius/2)


    ui_manager.draw_ui(window_surface)                                          # draw UI

    # Draw W A S D Letters
    window_surface.blit(textsurfaceW,(198,28))                                  # W
    window_surface.blit(textsurfaceA,(35,190))                                  # A
    window_surface.blit(textsurfaceS,(205,355))                                 # S
    window_surface.blit(textsurfaceD,(365,190))                                 # D
    window_surface.blit(textsurfaceLeft,(35,415))                               # ,
    window_surface.blit(textsurfaceRight,(375,415))                             # .
    
    axisXDOT = scale(axisX, (-255,255), (-1.0,1.0))
    axisYDOT = scale(axisY, (-255,255), (-1.0,1.0))
    axisZDOT = scale(axisZ, (-255,255), (-1.0,1.0))

    axisTestDot = pygame.math.Vector2((axisXDOT*10), (axisYDOT*10))

    xCircle = axisXDOT * math.sqrt(1 - 0.5*axisYDOT**2)
    yCircle = axisYDOT * math.sqrt(1 - 0.5*axisXDOT**2)

    #joyCircle.x = (axisXDOT*165)+210-radius
    #joyCircle.y = (axisYDOT*165)+210-radius
    sliderCircle.x = (axisZDOT*165)+210-radius

    joyCircle.x = (xCircle*165)+210-radius
    joyCircle.y = (yCircle*165)+210-radius

    # Draw draggable red dots
    #pygame.draw.circle(window_surface, RED, (joyCircle.x+radius,joyCircle.y+radius), radius)
    pygame.draw.circle(window_surface, RED, (axisTestDot), radius)
    pygame.draw.circle(window_surface, RED, (sliderCircle.x+radius,430), radius)
    # TEST
    #pygame.draw.circle(window_surface, GREEN, (axisX+radius,axisY+radius), radius)
    
    # Draw boxes that bound red dots
    #pygame.draw.rect(window_surface, [125,0,0], [30,30,360,360],width=3)
    pygame.draw.rect(window_surface, [125,0,0], [30,400,360,60],width=3)
    pygame.draw.circle(window_surface, [125,0,0], (210,210),180+(radius/2),width=3)

    mouse = pygame.mouse.get_pos()

    # Zoom In & Out button highlights
    if 482 <= mouse[0] <= 482+56 and 262 <= mouse[1] <= 262+56: 
        pygame.draw.rect(window_surface,colour_light,[482,262,56,56]) 
    else: 
        pygame.draw.rect(window_surface,colour_dark,[482,262,56,56])

    if 482 <= mouse[0] <= 482+56 and 322 <= mouse[1] <= 322+56: 
        pygame.draw.rect(window_surface,colour_light,[482,322,56,56]) 
    else: 
        pygame.draw.rect(window_surface,colour_dark,[482,322,56,56])

    # Display Zoom In & Zoom Out text inside their buttons
    window_surface.blit(zoomINtext, (500, 278))
    window_surface.blit(zoomOUTtext, (491, 338))

    pygame.display.update()

    clk.tick(40)