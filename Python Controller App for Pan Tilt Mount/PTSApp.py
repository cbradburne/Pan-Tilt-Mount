import pygame
from pygame.cursors import tri_left
import pygame_gui
import time
import serial.tools.list_ports

from collections import deque
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.elements import UILabel
from pygame_gui.elements.ui_text_box import UITextBox
from serial import *
from pathlib import Path

baudRate = 57600 #57600 or 38400
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
axisX = 0
axisY = 0
axisZ = 0
data = bytearray(7)
hat = ()
oldHatX = 0
oldHatY = 0
previousTime = 0
RED = (255, 0, 0)
mouseBorder = 360
radius = 15
mouseMoving = False

class Options:
    def __init__(self):
        self.resolution = (1200, 660)
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

        font_file_path = (base_path / "./Montserrat-Regular.ttf").resolve()
        print (file_path)
        self.ui_manager.add_font_paths(font_name= 'montserrat', regular_path= font_file_path)
        self.ui_manager.preload_fonts([{'name': 'montserrat', 'style': 'regular'}]) # 'point_size': 12,

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
        self.rel_button_GO1 = None
        self.rel_button_Clear = None
        self.rel_button_AddPos = None
        self.rel_button_EditPos = None
        self.rel_button_ExecMoves = None
        self.rel_button_OrbitPoint = None
        self.rel_button_Timelapse = None
        self.rel_button_PANORAMICLAPSE = None
        self.rel_button_GOFirst = None
        self.rel_button_GOBack = None
        self.rel_button_GOFwd = None
        self.rel_button_GOLast = None
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

        self.rel_button_Clear = UIButton(pygame.Rect((110, 500),
                                                    (60, 60)),
                                                    'Clear',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_AddPos = UIButton(pygame.Rect((180, 500),
                                                    (60, 60)),
                                                    'ADD',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_EditPos = UIButton(pygame.Rect((250, 500),
                                                    (60, 60)),
                                                    'EDIT',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_GOFirst = UIButton(pygame.Rect((85, 560),
                                                    (60, 60)),
                                                    '< <',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_GOBack = UIButton(pygame.Rect((145, 560),
                                                    (60, 60)),
                                                    '<',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_GOFwd = UIButton(pygame.Rect((215, 560),
                                                    (60, 60)),
                                                    '>',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_GOLast = UIButton(pygame.Rect((275, 560),
                                                    (60, 60)),
                                                    '> >',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_ExecMoves = UIButton(pygame.Rect((430, 120),
                                                    (160, 60)),
                                                    'Exec. Moves',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_OrbitPoint = UIButton(pygame.Rect((430, 180),
                                                    (160, 60)),
                                                    'Orbit Point',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_Timelapse = UIButton(pygame.Rect((430, 240),
                                                    (160, 60)),
                                                    'Timelapse',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_PANORAMICLAPSE = UIButton(pygame.Rect((430, 300),
                                                    (160, 60)),
                                                    'Panoramiclapse',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_REPORT = UIButton(pygame.Rect((460, 440),
                                                    (100, 60)),
                                                    'Report All',
                                                    self.ui_manager,
                                                    object_id='#everything_button')

        self.rel_button_REPORTPOS = UIButton(pygame.Rect((460, 500),
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
        self.serial_text_entry.focus()

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
                                                    (250, 30)),
                                                    self.ui_manager)

        self.serialPortTextBox()
        self.textBoxJoystickName()

        self.joyCircle = pygame.draw.circle(self.window_surface, pygame.Color("blue"), (225,225), radius)
        self.joyCircle_draging = False

        self.joyCircle.x = 195
        self.joyCircle.y = 195

        # Generate crosshair
        self.crosshair = pygame.surface.Surface((30, 30))
        self.crosshair.fill(pygame.Color("magenta"))
        pygame.draw.circle(self.crosshair, pygame.Color("blue"), (radius,radius), radius)
        self.crosshair.set_colorkey(pygame.Color("magenta"))#, pygame.RLEACCEL)
        #self.crosshair = self.crosshair.convert()

        self.sliderCircle = pygame.draw.circle(self.window_surface, pygame.Color("blue"), (225,415), radius)
        self.sliderCircle_draging = False

        self.sliderCircle.x = 195
        self.sliderCircle.y = 415

        # Generate crosshair
        self.crosshairSlider = pygame.surface.Surface((30, 30))
        self.crosshairSlider.fill(pygame.Color("magenta"))
        pygame.draw.circle(self.crosshairSlider, pygame.Color("blue"), (radius,radius), radius)
        self.crosshairSlider.set_colorkey(pygame.Color("magenta"))#, pygame.RLEACCEL)
        #self.crosshair = self.crosshair.convert()

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
        temp='X10'
        self.sendSerial(temp)

    def sendSR10(self):
        temp='X100'
        self.sendSerial(temp)

    def sendSL1(self):
        temp='X-10'
        self.sendSerial(temp)

    def sendSL10(self):
        temp='X-100'
        self.sendSerial(temp)

    def sendClearArray(self):
        temp='C'
        self.sendSerial(temp)

    def sendAddPos(self):
        temp='#'
        self.sendSerial(temp)

    def sendEditPos(self):
        temp='E'
        self.sendSerial(temp)

    def sendGOFirst(self):
        temp='['
        self.sendSerial(temp)

    def sendGOBack(self):
        temp='<'
        self.sendSerial(temp)

    def sendGOFwd(self):
        temp='>'
        self.sendSerial(temp)

    def sendGOLast(self):
        temp=']'
        self.sendSerial(temp)

    def sendExecMoves(self):
        temp=';1'
        self.sendSerial(temp)

    def sendOrbitPoint(self):
        temp='@1'
        self.sendSerial(temp)

    def sendTimelapse(self):
        temp='l'
        self.sendSerial(temp)

    def sendPanoramicLapse(self):
        temp='L'
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
            serialNotSel = 'Serial port not selected!<br>'
            self.textBoxSerial.kill()
            serialText = serialNotSel + serialText
            self.serialPortTextBox()
            self.serial_text_entry.focus()
            #textOUTPUT.insert(END, 'Serial port not selected!\n')
            #textOUTPUT.see(END)
        else:
            ser.write(sendValue.encode())                           # Send button value to coneected com port
            self.serial_text_entry.focus()

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
                                            pygame.Rect((620, 130), (560, 510)),
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
        global serialText

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

                if ((c == '\r') or (c == '\t')):                                       # check if character is a delimeter
                    c = ''                                          # don't want returns. chuck it
                    
                if c == '\n':
                    serBuffer += '<br>'                              # replace \n with HTML <br>
                    #textOUTPUT.insert(END, serBuffer)               #add the line to the TOP of the log
                    #textOUTPUT.see(END)
                    self.textBoxSerial.kill()
                    #serialText += serBuffer
                    serialText = serBuffer + serialText
                    self.serialPortTextBox()     # check this
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
        global axisX
        global axisY
        global axisZ
        global previousTime
        global mouseMoving

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
                elif (joyXread > deadRangeHigh):
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
                
                hat = joystick.get_hat(0)
                hatX = hat[0]
                hatY = hat[1]
                if (hatX != oldHatX):
                    oldHatX = hatX
                    if hatX == 1:                                        # RIGHT
                        self.sendGOFwd()
                    if hatX == -1:                                       # LEFT
                        self.sendGOBack()

                if (hatY != oldHatY):
                    oldHatY = hatY
                    if hatY == 1:                                        # UP
                        self.sendGOLast()
                    if hatY == -1:                                       # DOWN
                        self.sendGOFirst()

                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not buttonSquPressed):
                        buttonSquPressed = True
                        self.sendEditPos()
                        #print("0") 
                    elif (joystick.get_button(1) and not buttonXPressed):
                        buttonXPressed = True
                        self.sendAddPos()
                        #print("1")                    
                    elif (joystick.get_button(2) and not buttonCirPressed):
                        buttonCirPressed = True
                        self.sendREPORTpos()
                        #print("2")
                    elif (joystick.get_button(3) and not buttonTriPressed):
                        buttonTriPressed = True
                        self.sendClearArray()
                        #print("3")
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
                    self.serial_text_entry.set_text('')

                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.rel_button_Clear:
                        self.sendClearArray()
                    elif event.ui_element == self.rel_button_AddPos:
                        self.sendAddPos()
                    elif event.ui_element == self.rel_button_EditPos:
                        self.sendEditPos()
                    elif event.ui_element == self.rel_button_GOFirst:
                        self.sendGOFirst()
                    elif event.ui_element == self.rel_button_GOBack:
                        self.sendGOBack()
                    elif event.ui_element == self.rel_button_GOFwd:
                        self.sendGOFwd()
                    elif event.ui_element == self.rel_button_GOLast:
                        self.sendGOLast()
                    elif event.ui_element == self.rel_button_ExecMoves:
                        self.sendExecMoves()
                    elif event.ui_element == self.rel_button_OrbitPoint:
                        self.sendOrbitPoint()
                    elif event.ui_element == self.rel_button_Timelapse:
                        self.sendTimelapse()
                    elif event.ui_element == self.rel_button_PANORAMICLAPSE:
                        self.sendPanoramicLapse()
                    elif event.ui_element == self.rel_button_REPORT:
                        self.sendREPORTall()
                    elif event.ui_element == self.rel_button_REPORTPOS:
                        self.sendREPORTpos()

                if (event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
                    and event.ui_element == self.drop_down_serial):
                        self.serialPort_changed()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:            
                    if self.joyCircle.collidepoint(event.pos):
                        self.joyCircle_draging = True
                        mouse_x, mouse_y = event.pos
                        self.offset_x = self.joyCircle.x - mouse_x
                        self.offset_y = self.joyCircle.y - mouse_y
                        #mouseMoving = True

                    if self.sliderCircle.collidepoint(event.pos):
                        self.sliderCircle_draging = True
                        mouse_x, mouse_y = event.pos
                        self.sliderOffset_x = self.sliderCircle.x - mouse_x
                        self.sliderOffset_y = self.sliderCircle.y - mouse_y
                        #mouseMoving = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:            
                    self.joyCircle_draging = False
                    self.joyCircle.x = 195
                    self.joyCircle.y = 195

                    self.sliderCircle_draging = False
                    self.sliderCircle.x = 195
                    self.sliderCircle.y = 415

                    axisX = int(0)
                    axisY = int(0)
                    axisZ = int(0)
                        
                    axisXh = self.tohex(axisX, 16)
                    axisYh = self.tohex(axisY, 16)
                    axisZh = self.tohex(axisZ, 16)

                    mouseMoving = False

            if event.type == pygame.MOUSEMOTION:
                if self.joyCircle_draging:
                    mouseMoving = True
                    mouse_x, mouse_y = event.pos
                    self.joyCircle.x = mouse_x
                    self.joyCircle.y = mouse_y
                    if ((mouse_x + self.offset_x) > mouseBorder) and ((mouse_y + self.offset_y) > mouseBorder):
                        self.joyCircle.x = mouseBorder
                        self.joyCircle.y = mouseBorder
                        #print("test1")

                    elif (((mouse_x + self.offset_x) > mouseBorder) and ((mouse_y + self.offset_y) < 30)):
                        self.joyCircle.x = mouseBorder
                        self.joyCircle.y = 30
                        #print("test2")

                    elif (((mouse_x + self.offset_x) < 30) and ((mouse_y + self.offset_y) > mouseBorder)):
                        self.joyCircle.x = 30
                        self.joyCircle.y = mouseBorder
                        #print("test3")

                    elif (((mouse_x + self.offset_x) < 30) and ((mouse_y + self.offset_y) < 30)):
                        self.joyCircle.x = 30
                        self.joyCircle.y = 30
                        #print("test4")

                    elif ((mouse_x + self.offset_x) > (mouseBorder)):
                        self.joyCircle.x = mouseBorder
                        self.joyCircle.y = mouse_y + self.offset_y
                        #print("test5")

                    elif ((mouse_x + self.offset_x) < 30):#-self.offset_x):
                        self.joyCircle.x = 30
                        self.joyCircle.y = mouse_y + self.offset_y
                        #print("test6")

                    #elif (self.rectangle.x < 30):#-self.offset_x):
                    #    self.rectangle.x = 0
                    #    self.rectangle.y = mouse_y + self.offset_y
                        #print("test6")

                    elif ((mouse_y + self.offset_y) > (mouseBorder)):
                        self.joyCircle.y = mouseBorder
                        self.joyCircle.x = mouse_x + self.offset_x
                        #print("test7")

                    elif ((mouse_y + self.offset_y) < 30):
                        self.joyCircle.y = 30
                        self.joyCircle.x = mouse_x + self.offset_x
                        #print("test8")

                    else:
                        self.joyCircle.x = mouse_x + self.offset_x
                        self.joyCircle.y = mouse_y + self.offset_y

                    axisX = int(self.scale((self.joyCircle.x), (30,mouseBorder), (-254,255)))
                    axisY = -(int(self.scale((self.joyCircle.y), (30,mouseBorder), (-255,254))))
                    axisZ = int(0)
                  
                if self.sliderCircle_draging:
                    mouseMoving = True
                    mouse_x, mouse_y = event.pos
                    self.sliderCircle.x = mouse_x
                    self.sliderCircle.y = 420
                    if ((mouse_x + self.sliderOffset_x) > mouseBorder):
                        self.sliderCircle.x = mouseBorder

                    elif ((mouse_x + self.sliderOffset_x) < 30):
                        self.sliderCircle.x = 30

                    else:
                        self.sliderCircle.x = mouse_x + self.sliderOffset_x
                        
                    axisX = int(0)
                    axisY = int(0)
                    axisZ = int(self.scale((self.sliderCircle.x), (30,mouseBorder), (-254,255)))

            if (mouseMoving == False):
                if joystick == '':
                    pass
                else:
                    deadRangeLow = -0.2
                    deadRangeHigh = 0.2
                    joyXreadDOT = joystick.get_axis(0)
                    joyYreadDOT = joystick.get_axis(1)
                    joyZreadDOT = joystick.get_axis(2)

                    if (joyXreadDOT < deadRangeLow):
                        axisXDOT = self.scale(joyXreadDOT, (-1.0,deadRangeLow), (-1.0,0.0))
                    elif (joyXread > deadRangeHigh):
                        axisXDOT = self.scale(joyXreadDOT, (deadRangeHigh,1.0), (0.0,1.0))
                    else:
                        axisXDOT = 0

                    if (joyYreadDOT < deadRangeLow):
                        axisYDOT = self.scale(joyYreadDOT, (-1.0,deadRangeLow), (-1.0,0.0))
                    elif (joyYreadDOT > deadRangeHigh):
                        axisYDOT = self.scale(joyYreadDOT, (deadRangeHigh,1.0), (0.0,1.0))
                    else:
                        axisYDOT = 0

                    if (joyZreadDOT < deadRangeLow):
                        axisZDOT = self.scale(joyZreadDOT, (-1.0,deadRangeLow), (-1.0,0.0))
                    elif (joyZreadDOT > deadRangeHigh):
                        axisZDOT = self.scale(joyZreadDOT, (deadRangeHigh,1.0), (0.0,1.0))
                    else:
                        axisZDOT = 0
                    
                    self.joyCircle.x = (axisXDOT*165)+210-radius
                    self.joyCircle.y = (axisYDOT*165)+210-radius
                    self.sliderCircle.x = (axisZDOT*165)+210-radius

    def run(self):
        global previousTime
        global oldAxisX
        global oldAxisY
        global oldAxisZ
        global axisX
        global axisY
        global axisZ
        global mouseMoving

        while self.running:
            time_delta = self.clock.tick() / 1000.0
            self.time_delta_stack.append(time_delta)
            if len(self.time_delta_stack) > 2000:
                self.time_delta_stack.popleft()
            
            self.process_events()                                               # check for input

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

            self.readSerial()

            self.ui_manager.update(time_delta)                                  # respond to input

            self.window_surface.blit(self.background_surface, (0, 0))           # draw graphics

            pygame.draw.circle(self.window_surface, RED, (self.joyCircle.x+15,self.joyCircle.y+radius), radius)
            pygame.draw.circle(self.window_surface, RED, (self.sliderCircle.x+15,430), radius)

            pygame.draw.rect(self.window_surface, [125,0,0], [30,30,360,360],width=3)
            pygame.draw.rect(self.window_surface, [125,0,0], [30,400,360,60],width=3)

            self.ui_manager.draw_ui(self.window_surface)

            pygame.display.update()

if __name__ == '__main__':
    app = OptionsUIApp()
    app.run()
