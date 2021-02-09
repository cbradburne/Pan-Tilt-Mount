import random
import os
import pygame
import pygame_gui
import time

from pathlib import Path

from collections import deque

from pygame_gui import UIManager, PackageResource

from pygame_gui.elements import UIWindow
from pygame_gui.elements import UIButton
#from pygame_gui.elements import UIHorizontalSlider
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.elements import UIScreenSpaceHealthBar
from pygame_gui.elements import UILabel
from pygame_gui.elements import UIImage
from pygame_gui.elements import UIPanel
from pygame_gui.elements import UISelectionList
from pygame_gui.elements.ui_text_box import UITextBox

from pygame_gui.windows import UIMessageWindow

from serial import *
from threading import Timer
import serial.tools.list_ports

import pygame

baudRate = 38400
ser = ''
serBuffer = ''
serialText = ''
joystick = ''
joystickName = ''
buttonXPressed = None
buttonSquPressed = None
buttonTriPressed = None
buttonCirPressed = None
buttonL1Pressed = None
buttonR1Pressed = None
buttonL2Pressed = None
buttonR2Pressed = None
buttonL3Pressed = None
buttonR3Pressed = None
buttonShaPressed = None
buttonOptPressed = None
arr = []
oldAxisX = 0
oldAxisY = 0
oldAxisZ = 0
data = bytearray(7)
hat = ()
oldHatX = 0
oldHatY = 0
previousTime = 0

class Options:
    def __init__(self):
        self.resolution = (1200, 600)
        self.fullscreen = False

class OptionsUIApp:
    def __init__(self):
        global previousTime
        pygame.init()
        pygame.display.set_caption("PTSApp")

        self.all_joysticks = self.initialiseJoysticks()
        self.options = Options()
        if self.options.fullscreen:
            self.window_surface = pygame.display.set_mode(self.options.resolution,
                                                          pygame.FULLSCREEN)
        else:
            self.window_surface = pygame.display.set_mode(self.options.resolution)

        self.background_surface = None

        base_path = Path(__file__).parent
        file_path = (base_path / "./theme.json").resolve()
        self.ui_manager = UIManager(self.options.resolution, file_path)

        self.test_button = None
        self.test_button_2 = None
        self.test_button_3 = None
        self.rel_button_L1 = None
        self.rel_button_L10 = None
        self.rel_button_R1 = None
        self.rel_button_R10 = None
        self.rel_button_U1 = None
        self.rel_button_U10 = None
        self.rel_button_D1 = None
        self.rel_button_D10 = None
        self.rel_button_SET1 = None
        self.rel_button_SET2 = None
        self.rel_button_SET3 = None
        self.rel_button_SET4 = None
        self.rel_button_SET5 = None
        self.rel_button_SET6 = None
        self.rel_button_GO1 = None
        self.rel_button_GO2 = None
        self.rel_button_GO3 = None
        self.rel_button_GO4 = None
        self.rel_button_GO5 = None
        self.rel_button_GO6 = None
        self.rel_button_SLOW = None
        self.rel_button_FAST = None
        self.rel_button_REPORT = None
        self.rel_button_REPORTPOS = None
        self.serial_text_entry = None
        self.drop_down_serial = None
        self.panel = None
        self.disable_toggle = None
        self.hide_toggle = None

        self.message_window = None

        self.recreate_ui()

        self.clock = pygame.time.Clock()
        self.time_delta_stack = deque([])

        self.button_response_timer = pygame.time.Clock()
        self.running = True
        self.debug_mode = False

        self.all_enabled = True
        self.all_shown = True

        previousTime = time.time()

    def recreate_ui(self):
        global current_serialPort
        
        self.ui_manager.set_window_resolution(self.options.resolution)
        self.ui_manager.clear_and_reset()

        self.background_surface = pygame.Surface(self.options.resolution)
        self.background_surface.fill(self.ui_manager.get_theme().get_colour('dark_bg'))

        self.rel_button_L1 = UIButton(pygame.Rect((120, 180),
                                                  (60, 60)),
                                      '.5',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_L10 = UIButton(pygame.Rect((60, 180),
                                                  (60, 60)),
                                      '10',
                                      self.ui_manager,
                                      object_id='#everything_button')
                                      
        self.rel_button_R1 = UIButton(pygame.Rect((240, 180),
                                                  (60, 60)),
                                      '.5',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_R10 = UIButton(pygame.Rect((300, 180),
                                                  (60, 60)),
                                      '10',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_U1 = UIButton(pygame.Rect((180, 120),
                                                  (60, 60)),
                                      '.5',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_U10 = UIButton(pygame.Rect((180, 60),
                                                  (60, 60)),
                                      '10',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_D1 = UIButton(pygame.Rect((180, 240),
                                                  (60, 60)),
                                      '.5',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_D10 = UIButton(pygame.Rect((180, 300),
                                                  (60, 60)),
                                      '10',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_set0 = UIButton(pygame.Rect((190, 190),
                                                  (40, 40)),
                                      '0',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SL10 = UIButton(pygame.Rect((145, 360),
                                                  (60, 60)),
                                      '10',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SL100 = UIButton(pygame.Rect((85, 360),
                                                  (60, 60)),
                                      '100',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SR10 = UIButton(pygame.Rect((215, 360),
                                                  (60, 60)),
                                      '10',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SR100 = UIButton(pygame.Rect((275, 360),
                                                  (60, 60)),
                                      '100',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SET1 = UIButton(pygame.Rect((30, 500),
                                                  (60, 60)),
                                      'SET 1',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SET2 = UIButton(pygame.Rect((90, 500),
                                                  (60, 60)),
                                      'SET 2',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SET3 = UIButton(pygame.Rect((150, 500),
                                                  (60, 60)),
                                      'SET 3',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SET4 = UIButton(pygame.Rect((210, 500),
                                                  (60, 60)),
                                      'SET 4',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SET5 = UIButton(pygame.Rect((270, 500),
                                                  (60, 60)),
                                      'SET 5',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SET6 = UIButton(pygame.Rect((330, 500),
                                                  (60, 60)),
                                      'SET 6',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_GO1 = UIButton(pygame.Rect((30, 440),
                                                  (60, 60)),
                                      'GO 1',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_GO2 = UIButton(pygame.Rect((90, 440),
                                                  (60, 60)),
                                      'GO 2',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_GO3 = UIButton(pygame.Rect((150, 440),
                                                  (60, 60)),
                                      'GO 3',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_GO4 = UIButton(pygame.Rect((210, 440),
                                                  (60, 60)),
                                      'GO 4',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_GO5 = UIButton(pygame.Rect((270, 440),
                                                  (60, 60)),
                                      'GO 5',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_GO6 = UIButton(pygame.Rect((330, 440),
                                                  (60, 60)),
                                      'GO 6',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_SLOW = UIButton(pygame.Rect((450, 100),
                                                  (60, 60)),
                                      'SLOW',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_FAST = UIButton(pygame.Rect((450, 160),
                                                  (60, 60)),
                                      'FAST',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_ZOOMin = UIButton(pygame.Rect((450, 260),
                                                  (60, 60)),
                                      'IN',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_ZOOMout = UIButton(pygame.Rect((450, 320),
                                                  (60, 60)),
                                      'OUT',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_REPORT = UIButton(pygame.Rect((510, 440),
                                                  (100, 60)),
                                      'Report All',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.rel_button_REPORTPOS = UIButton(pygame.Rect((510, 500),
                                                  (100, 60)),
                                      'Report Pos',
                                      self.ui_manager,
                                      object_id='#everything_button')

        self.joystick_label = UILabel(pygame.Rect(540, 10,
                                                    230, 24),
                                                    "Joystick",
                                                    self.ui_manager,
                                                    object_id='#main_text_entry')

        self.serial_text_entry = UITextEntryLine(pygame.Rect((930, 95),
                                                    (250, 35)),
                                                    self.ui_manager,
                                                    object_id='#main_text_entry')

        self.serial_port_label = UILabel(pygame.Rect(550, 70,
                                                    230, 24),
                                                    "Serial Port",
                                                    self.ui_manager,
                                                    object_id='#main_text_entry')

        self.serial_command_label = UILabel(pygame.Rect(870, 70,
                                                    230, 24),
                                                    "Serial Command",
                                                    self.ui_manager,
                                                    object_id='#main_text_entry')

        current_serialPort = ' - '
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for p in ports:
            available_ports.append(p.device)                        # Append each found serial port to array available_ports

        self.drop_down_serial = UIDropDownMenu(available_ports,
                                                    current_serialPort,
                                                    pygame.Rect((620,95),
                                                    (250, 25)),
                                                    self.ui_manager)

        self.serialPortTextBox()
        self.textBoxJoystickName()

    def sendUP1(self):
        temp='T1'
        self.sendSerial(temp)

    def sendDOWN1(self):
        temp='T-1'
        self.sendSerial(temp)

    def sendLEFT1(self):
        temp='P-0.5'
        self.sendSerial(temp)

    def sendRIGHT1(self):
        temp='P0.5'
        self.sendSerial(temp)

    def sendUP10(self):
        temp='T10'
        self.sendSerial(temp)

    def sendDOWN10(self):
        temp='T-10'
        self.sendSerial(temp)

    def sendLEFT10(self):
        temp='P-10'
        self.sendSerial(temp)

    def sendRIGHT10(self):
        temp='P10'
        self.sendSerial(temp)

    def sendRESETpos(self):
        temp='h'
        self.sendSerial(temp)

    def sendSR1(self):
        temp='L10'
        self.sendSerial(temp)

    def sendSR10(self):
        temp='L100'
        self.sendSerial(temp)

    def sendSL1(self):
        temp='L-10'
        self.sendSerial(temp)

    def sendSL10(self):
        temp='L-100'
        self.sendSerial(temp)

    def sendZOOMin(self):
        temp='Z'
        self.sendSerial(temp)

    def sendZOOMout(self):
        temp='z'
        self.sendSerial(temp)

    def sendSET1(self):
        temp='a'
        self.sendSerial(temp)

    def sendSET2(self):
        temp='b'
        self.sendSerial(temp)

    def sendSET3(self):
        temp='c'
        self.sendSerial(temp)

    def sendSET4(self):
        temp='d'
        self.sendSerial(temp)

    def sendSET5(self):
        temp='e'
        self.sendSerial(temp)

    def sendSET6(self):
        temp='f'
        self.sendSerial(temp)

    def sendGO1(self):
        temp='A'
        self.sendSerial(temp)

    def sendGO2(self):
        temp='B'
        self.sendSerial(temp)

    def sendGO3(self):
        temp='C'
        self.sendSerial(temp)

    def sendGO4(self):
        temp='D'
        self.sendSerial(temp)

    def sendGO5(self):
        temp='E'
        self.sendSerial(temp)

    def sendGO6(self):
        temp='F'
        self.sendSerial(temp)

    def sendSPEEDfast(self):
        temp='V'
        self.sendSerial(temp)

    def sendSPEEDslow(self):
        temp='v'
        self.sendSerial(temp)

    def sendREPORTall(self):
        temp='R'
        self.sendSerial(temp)

    def sendREPORTpos(self):
        temp='r'
        self.sendSerial(temp)

    def serialPort_changed(self):
        global ser
        global baudRate
        serialPortSelect = self.drop_down_serial.selected_option
        ser = Serial(serialPortSelect , baudRate, timeout=0, writeTimeout=0)
        self.readSerial()

    def sendSerial(self, sendValue):
        global ser
        global serialText
        if (ser == ''):                                             # Checks to see if com port has been selected
            serialText = 'Serial port not selected!'
            self.serialPortTextBox()
            #textOUTPUT.insert(END, 'Serial port not selected!\n')
            #textOUTPUT.see(END)
        else:
            ser.write(sendValue.encode())                           # Send button value to coneected com port

    def tohex(self, val, nbits):
        return hex((val + (1 << nbits)) % (1 << nbits))

    def sendJoystick(self, arr):
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

    def serialPortTextBox(self):
        self.textBoxSerial = UITextBox(serialText,
                                            pygame.Rect((620, 130), (560, 450)),
                                            self.ui_manager,
                                            object_id="#text_box_1")

    def textBoxJoystickName(self):
        global joystickName
        self.textBoxJoystickName = UITextBox(joystickName,
                                            pygame.Rect((620, 30), (560, 35)),
                                            self.ui_manager,
                                            object_id="#text_box_1")

    def readSerial(self):
        global ser
        global serBuffer
        if (ser == ''):
            return
        else:
            while True:
                c = ser.read()

                if len(c) == 0:
                    break

                if (c == b'\xb0'):                                  # Change / remove characters that cause error
                    c = '°'
                elif (c == b'\xb2'):
                    c = '²'
                elif (c == b'\xba') or (c == b'\xc2') or (c == b'\xc9'):
                    c = ''
                else:
                    c = c.decode('ascii') 

                if c == '\r':                                       # check if character is a delimeter
                    c = ''                                          # don't want returns. chuck it
                    
                if c == '\n':
                    serBuffer += '<br>'                              # replace \n with HTML <br>
                    #textOUTPUT.insert(END, serBuffer)               #add the line to the TOP of the log
                    #textOUTPUT.see(END)
                    global serialText
                        
                    serialText=serialText+serBuffer
                    self.serialPortTextBox()     # check this
                    #self.serialPortTextBox.redraw_from_text_block()
                    serBuffer = ''                                  # empty the buffer
                else:
                    serBuffer += c                                  # add to the buffer
           
    def scale(self, val, src, dst):
        """
        Scale the given value from the scale of src to the scale of dst.
        """
        return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
        
    def initialiseJoysticks(self):
        global joystick
        global joystickName
        """Initialise all joysticks, returning a list of pygame.joystick.Joystick"""
        available_joysticks = []                                            # for returning
        
        pygame.joystick.init()                                              # Initialise the Joystick sub-module

        joystick_count = pygame.joystick.get_count()                        # Get count of joysticks
        
        for i in range( joystick_count ):                                   # For each joystick:
            joystick = pygame.joystick.Joystick( i )
            joystick.init()
            available_joysticks.append( joystick )

        if ( len( available_joysticks ) == 0 ):

            print( "No joysticks found" )
        else:
            for i,joystk in enumerate( available_joysticks ):
                print("Joystick %d is named [%s]" % ( i, joystk.get_name() ) )
                joystickName = joystk.get_name()

        return available_joysticks

    def int_to_bytes(self, number: int) -> bytes:
        return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)

    def process_events(self):
        global arr
        global joystick
        global buttonXPressed
        global buttonSquPressed
        global buttonTriPressed
        global buttonCirPressed
        global buttonL1Pressed
        global buttonR1Pressed
        global buttonL2Pressed
        global buttonR2Pressed
        global buttonL3Pressed
        global buttonR3Pressed
        global buttonShaPressed
        global buttonOptPressed
        global oldAxisX
        global oldAxisY
        global oldAxisZ
        global oldHatX
        global oldHatY
        global previousTime
        axisXb = 'text'

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.ui_manager.process_events(event)
            deadRangeLow = -0.2
            deadRangeHigh = 0.2
            if joystick != '':
                joyXread = joystick.get_axis(0)
                joyYread = -(joystick.get_axis(1))
                joyZread = joystick.get_axis(2)

                if (joyXread < deadRangeLow):
                    axisX = int(self.scale(joyXread, (-1.0,deadRangeLow), (-254,0)))
                elif (joyXread >deadRangeHigh):
                    axisX = int(self.scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                else:
                    axisX = 0

                if (joyYread < deadRangeLow):
                    axisY = int(self.scale(joyYread, (-1.0,deadRangeLow), (-254,0)))
                elif (joyYread > deadRangeHigh):
                    axisY = int(self.scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                else:
                    axisY = 0

                if (joyZread < deadRangeLow):
                    axisZ = int(self.scale(joyZread, (-1.0,deadRangeLow), (-254,0)))
                elif (joyZread > deadRangeHigh):
                    axisZ = int(self.scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                else:
                    axisZ = 0

                if (((axisX != oldAxisX) or (axisY != oldAxisY) or (axisZ != oldAxisZ)) and ((time.time() - previousTime) > 0.1)):
                    previousTime = time.time()
                    oldAxisX = axisX
                    oldAxisY = axisY
                    oldAxisZ = axisZ
                    axisXh = self.tohex(axisX, 16)
                    axisYh = self.tohex(axisY, 16)
                    axisZh = self.tohex(axisZ, 16)
                    arr = [4, axisZh, axisXh, axisYh]
                    self.sendJoystick(arr)

                #if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                #    self.debug_mode = False if self.debug_mode else True
                #    self.ui_manager.set_visual_debug_mode(self.debug_mode)

                #if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                #    print("self.ui_manager.focused_set:", self.ui_manager.focused_set)
                
                hat = joystick.get_hat(0)
                hatX = hat[0]
                hatY = hat[1]
                if (hatX != oldHatX):
                    oldHatX = hatX
                    if hatX == 1:                                        # RIGHT
                        self.sendSET1()
                    if hatX == -1:                                       # LEFT
                        self.sendSET2()

                if (hatY != oldHatY):
                    oldHatY = hatY
                    if hatY == 1:                                        # UP
                        self.sendSET3()
                    if hatY == -1:                                       # DOWN
                        self.sendSET4()

                if event.type == pygame.JOYBUTTONDOWN:
                    
                    if (joystick.get_button(0) and not buttonSquPressed):
                        buttonSquPressed = True
                        self.sendGO2()
                        #print("0") 
                    elif (joystick.get_button(1) and not buttonXPressed):
                        buttonXPressed = True
                        self.sendGO4()
                        #print("1")                    
                    elif (joystick.get_button(2) and not buttonCirPressed):
                        buttonCirPressed = True
                        self.sendGO1()
                        #print("2")
                    elif (joystick.get_button(3) and not buttonTriPressed):
                        buttonTriPressed = True
                        self.sendGO3()
                        #print("3")
                    elif (joystick.get_button(4) and not buttonL1Pressed):
                        buttonL1Pressed = True
                        self.sendSPEEDslow()
                        #print("4")
                    elif (joystick.get_button(5) and not buttonR1Pressed):
                        buttonR1Pressed = True
                        self.sendSPEEDfast()
                        #print("5")
                    elif (joystick.get_button(6) and not buttonL2Pressed):
                        buttonL2Pressed = True
                        self.sendREPORTpos()
                        ##print("6")
                    elif (joystick.get_button(7) and not buttonR2Pressed):
                        buttonR2Pressed = True
                        self.sendREPORTpos()
                        #print("7")
                    elif (joystick.get_button(8) and not buttonShaPressed):
                        buttonShaPressed = True
                        self.sendREPORTpos()
                        #print("8")
                    elif (joystick.get_button(9) and not buttonOptPressed):
                        buttonOptPressed = True
                        self.sendREPORTpos()
                        #print("9")
                    elif (joystick.get_button(10) and not buttonL3Pressed):
                        buttonL3Pressed = True
                        self.sendREPORTpos()
                        #print("10")
                    elif (joystick.get_button(11) and not buttonR3Pressed):
                        buttonR3Pressed = True
                        self.sendREPORTpos()
                        #print("11")

            if event.type == pygame.JOYBUTTONUP:
                if (buttonSquPressed and not joystick.get_button(0)):
                    buttonSquPressed = False
                elif (buttonXPressed and not joystick.get_button(1)):
                    buttonXPressed = False
                elif (buttonCirPressed and not joystick.get_button(2)):
                    buttonCirPressed = False
                elif (buttonTriPressed and not joystick.get_button(3)):
                    buttonTriPressed = False
                elif (buttonL1Pressed and not joystick.get_button(4)):
                    buttonL1Pressed = False
                elif (buttonR1Pressed and not joystick.get_button(5)):
                    buttonR1Pressed = False
                elif (buttonL2Pressed and not joystick.get_button(6)):
                    buttonL2Pressed = False
                elif (buttonR2Pressed and not joystick.get_button(7)):
                    buttonR2Pressed = False
                elif (buttonShaPressed and not joystick.get_button(8)):
                    buttonShaPressed = False
                elif (buttonOptPressed and not joystick.get_button(9)):
                    buttonOptPressed = False
                elif (buttonL3Pressed and not joystick.get_button(10)):
                    buttonL3Pressed = False
                elif (buttonR3Pressed and not joystick.get_button(11)):
                    buttonR3Pressed = False

            if event.type == pygame.USEREVENT:
                if (event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                        event.ui_object_id == '#main_text_entry'):
                    self.sendSerial(event.text)
                    print(event.text)
                    self.serial_text_entry.set_text('')

                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.rel_button_L1:
                        self.sendLEFT1()
                    elif event.ui_element == self.rel_button_L10:
                        self.sendLEFT10()
                    elif event.ui_element == self.rel_button_R1:
                        self.sendRIGHT1()
                    elif event.ui_element == self.rel_button_R10:
                        self.sendRIGHT10()
                    elif event.ui_element == self.rel_button_U1:
                        self.sendUP1()
                    elif event.ui_element == self.rel_button_U10:
                        self.sendUP10()
                    elif event.ui_element == self.rel_button_D1:
                        self.sendDOWN1()
                    elif event.ui_element == self.rel_button_D10:
                        self.sendDOWN10()
                    elif event.ui_element == self.rel_button_set0:
                        self.sendRESETpos()
                    elif event.ui_element == self.rel_button_SR10:
                        self.sendSR1()
                    elif event.ui_element == self.rel_button_SR100:
                        self.sendSR10()
                    elif event.ui_element == self.rel_button_SL10:
                        self.sendSL1()
                    elif event.ui_element == self.rel_button_SL100:
                        self.sendSL10()
                    elif event.ui_element == self.rel_button_U10:
                        self.sendZOOMin()
                    elif event.ui_element == self.rel_button_D1:
                        self.sendZOOMout()
                    elif event.ui_element == self.rel_button_SET1:
                        self.sendSET1()
                    elif event.ui_element == self.rel_button_SET2:
                        self.sendSET2()
                    elif event.ui_element == self.rel_button_SET3:
                        self.sendSET3()
                    elif event.ui_element == self.rel_button_SET4:
                        self.sendSET4()
                    elif event.ui_element == self.rel_button_SET5:
                        self.sendSET5()
                    elif event.ui_element == self.rel_button_SET6:
                        self.sendSET6()
                    elif event.ui_element == self.rel_button_GO1:
                        self.sendGO1()
                    elif event.ui_element == self.rel_button_GO2:
                        self.sendGO2()
                    elif event.ui_element == self.rel_button_GO3:
                        self.sendGO3()
                    elif event.ui_element == self.rel_button_GO4:
                        self.sendGO4()
                    elif event.ui_element == self.rel_button_GO5:
                        self.sendGO5()
                    elif event.ui_element == self.rel_button_GO6:
                        self.sendGO6()
                    elif event.ui_element == self.rel_button_SLOW:
                        self.sendSPEEDslow()
                    elif event.ui_element == self.rel_button_FAST:
                        self.sendSPEEDfast()
                    elif event.ui_element == self.rel_button_REPORT:
                        self.sendREPORTall()
                    elif event.ui_element == self.rel_button_REPORTPOS:
                        self.sendREPORTpos()

                if (event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
                    and event.ui_element == self.drop_down_serial):
                        self.serialPort_changed()

    def run(self):
        while self.running:
            time_delta = self.clock.tick() / 1000.0
            self.time_delta_stack.append(time_delta)
            if len(self.time_delta_stack) > 2000:
                self.time_delta_stack.popleft()
            
            self.process_events()                                               # check for input

            self.readSerial()

            self.ui_manager.update(time_delta)                                  # respond to input

            self.window_surface.blit(self.background_surface, (0, 0))           # draw graphics
            self.ui_manager.draw_ui(self.window_surface)

            #pygame.display.update()
            pygame.display.flip()

if __name__ == '__main__':
    app = OptionsUIApp()
    app.run()
