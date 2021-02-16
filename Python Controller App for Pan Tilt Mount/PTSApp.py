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

clk = pygame.time.Clock()

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
textBoxJoystickName = None
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
mouseBorder = 360
radius = 15
mouseMoving = False

resolution = (1200, 660)
fullscreen = False

pygame.init()
pygame.display.set_caption("PTSApp")

def sendClearArray():
    temp='C'
    sendSerial(temp)

def sendAddPos():
    temp='#'
    sendSerial(temp)

def sendEditPos():
    temp='E'
    sendSerial(temp)

def sendGOFirst():
    temp='['
    sendSerial(temp)

def sendGOBack():
    temp='<'
    sendSerial(temp)

def sendGOFwd():
    temp='>'
    sendSerial(temp)

def sendGOLast():
    temp=']'
    sendSerial(temp)

def sendExecMoves():
    temp=';1'
    sendSerial(temp)

def sendOrbitPoint():
    temp='@1'
    sendSerial(temp)

def sendTimelapse():
    temp='l'
    sendSerial(temp)

def sendPanoramicLapse():
    temp='L'
    sendSerial(temp)

def sendREPORTall():
    temp='R'
    sendSerial(temp)

def sendREPORTpos():
    temp='r'
    sendSerial(temp)

def serialPort_changed():
    global ser
    global baudRate
    serialPortSelect = drop_down_serial.selected_option
    ser = Serial(serialPortSelect , baudRate, timeout=0, writeTimeout=0)
    readSerial()

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

def serialPortTextBox():
    global textBoxSerial
    textBoxSerial = UITextBox(serialText,
                                        pygame.Rect((620, 130), (560, 510)),
                                        ui_manager,
                                        wrap_to_height=False,
                                        object_id="#text_box_1")
    ui_manager.set_focus_set(textBoxSerial.get_focus_set())

def textBoxJoystickName():
    global joystickName
    global textBoxJoystickName
    textBoxJoystickName = UITextBox(joystickName,
                                        pygame.Rect((620, 30), (560, 35)),
                                        ui_manager,
                                        object_id="#text_box_1")

def readSerial():
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
                textBoxSerial.kill()
                #serialText += serBuffer
                serialText = serBuffer + serialText
                serialPortTextBox()     # check this
                serBuffer = ''                                  # empty the buffer
            else:
                serBuffer += c                                  # add to the buffer

def sendSerial(sendValue):
    global ser
    global serialText
    if (ser == ''):                                             # Checks to see if com port has been selected
        serialNotSel = 'Serial port not selected!<br>'
        textBoxSerial.kill()
        serialText = serialNotSel + serialText
        serialPortTextBox()
        serial_text_entry.focus()
        #textOUTPUT.insert(END, 'Serial port not selected!\n')
        #textOUTPUT.see(END)
    else:
        ser.write(sendValue.encode())                           # Send button value to coneected com port
        serial_text_entry.focus()
        
def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
    
def initialiseJoysticks():
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

def int_to_bytes(number: int) -> bytes:
    return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)

all_joysticks = initialiseJoysticks()

if fullscreen:
    window_surface = pygame.display.set_mode(resolution,
                                                    pygame.FULLSCREEN)
else:
    window_surface = pygame.display.set_mode(resolution)

background_surface = None

base_path = Path(__file__).parent
file_path = (base_path / "./theme.json").resolve()
ui_manager = UIManager(resolution, file_path)

font_file_path = (base_path / "./Montserrat-Regular.ttf").resolve()
ui_manager.add_font_paths(font_name= 'montserrat', regular_path= font_file_path)
ui_manager.preload_fonts([{'name': 'montserrat', 'point_size': 12, 'style': 'regular'}])

#rel_button_L1 = None
#rel_button_L10 = None
#rel_button_R1 = None
#rel_button_R10 = None
#rel_button_U1 = None
#rel_button_U10 = None
#rel_button_D1 = None
#rel_button_D10 = None
#rel_button_GO1 = None
rel_button_Clear = None
rel_button_AddPos = None
rel_button_EditPos = None
rel_button_ExecMoves = None
rel_button_OrbitPoint = None
rel_button_Timelapse = None
rel_button_PANORAMICLAPSE = None
rel_button_GOFirst = None
rel_button_GOBack = None
rel_button_GOFwd = None
rel_button_GOLast = None
rel_button_REPORT = None
rel_button_REPORTPOS = None
serial_text_entry = None
drop_down_serial = None

message_window = None
running = True

clock = pygame.time.Clock()
time_delta_stack = deque([])

button_response_timer = pygame.time.Clock()

ui_manager.set_window_resolution(resolution)
ui_manager.clear_and_reset()

background_surface = pygame.Surface(resolution)
background_surface.fill(ui_manager.get_theme().get_colour('dark_bg'))

rel_button_Clear = UIButton(pygame.Rect((110, 500),
                                            (60, 60)),
                                            'Clear',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_AddPos = UIButton(pygame.Rect((180, 500),
                                            (60, 60)),
                                            'ADD',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_EditPos = UIButton(pygame.Rect((250, 500),
                                            (60, 60)),
                                            'EDIT',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_GOFirst = UIButton(pygame.Rect((85, 560),
                                            (60, 60)),
                                            '< <',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_GOBack = UIButton(pygame.Rect((145, 560),
                                            (60, 60)),
                                            '<',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_GOFwd = UIButton(pygame.Rect((215, 560),
                                            (60, 60)),
                                            '>',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_GOLast = UIButton(pygame.Rect((275, 560),
                                            (60, 60)),
                                            '> >',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_ExecMoves = UIButton(pygame.Rect((430, 120),
                                            (160, 60)),
                                            'Exec. Moves',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_OrbitPoint = UIButton(pygame.Rect((430, 180),
                                            (160, 60)),
                                            'Orbit Point',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_Timelapse = UIButton(pygame.Rect((430, 240),
                                            (160, 60)),
                                            'Timelapse',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_PANORAMICLAPSE = UIButton(pygame.Rect((430, 300),
                                            (160, 60)),
                                            'Panoramiclapse',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_REPORT = UIButton(pygame.Rect((460, 440),
                                            (100, 60)),
                                            'Report All',
                                            ui_manager,
                                            object_id='#everything_button')

rel_button_REPORTPOS = UIButton(pygame.Rect((460, 500),
                                            (100, 60)),
                                            'Report Pos',
                                            ui_manager,
                                            object_id='#everything_button')

joystick_label = UILabel(pygame.Rect(540, 10,
                                            230, 24),
                                            "Joystick",
                                            ui_manager,
                                            object_id='#main_text_entry')

serial_text_entry = UITextEntryLine(pygame.Rect((930, 95),
                                            (250, 35)),
                                            ui_manager,
                                            object_id='#main_text_entry')

serial_text_entry.focus()

serial_port_label = UILabel(pygame.Rect(550, 70,
                                            230, 24),
                                            "Serial Port",
                                            ui_manager,
                                            object_id='#main_text_entry')

serial_command_label = UILabel(pygame.Rect(870, 70,
                                            230, 24),
                                            "Serial Command",
                                            ui_manager,
                                            object_id='#main_text_entry')

current_serialPort = ' - '
ports = serial.tools.list_ports.comports()
available_ports = []
for p in ports:
    available_ports.append(p.device)                        # Append each found serial port to array available_ports

drop_down_serial = UIDropDownMenu(available_ports,
                                            current_serialPort,
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

    

def process_events():
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
    global joyCircle_draging
    global sliderCircle_draging
    global offset_x
    global offset_y
    global sliderOffset_x
    global sliderOffset_y
    global running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        ui_manager.process_events(event)
        deadRangeLow = -0.2
        deadRangeHigh = 0.2
        if joystick != '':
            joyXread = joystick.get_axis(0)
            joyYread = -(joystick.get_axis(1))
            joyZread = joystick.get_axis(2)

            if (joyXread < deadRangeLow):
                axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-254,0)))
            elif (joyXread > deadRangeHigh):
                axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
            else:
                axisX = 0

            if (joyYread < deadRangeLow):
                axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-254,0)))
            elif (joyYread > deadRangeHigh):
                axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
            else:
                axisY = 0

            if (joyZread < deadRangeLow):
                axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-254,0)))
            elif (joyZread > deadRangeHigh):
                axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
            else:
                axisZ = 0
            
            hat = joystick.get_hat(0)
            hatX = hat[0]
            hatY = hat[1]
            if (hatX != oldHatX):
                oldHatX = hatX
                if hatX == 1:                                        # RIGHT
                    sendGOFwd()
                if hatX == -1:                                       # LEFT
                    sendGOBack()

            if (hatY != oldHatY):
                oldHatY = hatY
                if hatY == 1:                                        # UP
                    sendGOLast()
                if hatY == -1:                                       # DOWN
                    sendGOFirst()

            if event.type == pygame.JOYBUTTONDOWN:
                if (joystick.get_button(0) and not buttonSquPressed):
                    buttonSquPressed = True
                    sendEditPos()
                    #print("0") 
                elif (joystick.get_button(1) and not buttonXPressed):
                    buttonXPressed = True
                    sendAddPos()
                    #print("1")                    
                elif (joystick.get_button(2) and not buttonCirPressed):
                    buttonCirPressed = True
                    sendREPORTpos()
                    #print("2")
                elif (joystick.get_button(3) and not buttonTriPressed):
                    buttonTriPressed = True
                    sendClearArray()
                    #print("3")
                elif (joystick.get_button(6) and not buttonL2Pressed):
                    buttonL2Pressed = True
                    sendREPORTpos()
                    ##print("6")
                elif (joystick.get_button(7) and not buttonR2Pressed):
                    buttonR2Pressed = True
                    sendREPORTpos()
                    #print("7")
                elif (joystick.get_button(8) and not buttonShaPressed):
                    buttonShaPressed = True
                    sendREPORTpos()
                    #print("8")
                elif (joystick.get_button(9) and not buttonOptPressed):
                    buttonOptPressed = True
                    sendREPORTpos()
                    #print("9")
                elif (joystick.get_button(10) and not buttonL3Pressed):
                    buttonL3Pressed = True
                    sendREPORTpos()
                    #print("10")
                elif (joystick.get_button(11) and not buttonR3Pressed):
                    buttonR3Pressed = True
                    sendREPORTpos()
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
                sendSerial(event.text)
                serial_text_entry.set_text('')

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == rel_button_Clear:
                    sendClearArray()
                elif event.ui_element == rel_button_AddPos:
                    sendAddPos()
                elif event.ui_element == rel_button_EditPos:
                    sendEditPos()
                elif event.ui_element == rel_button_GOFirst:
                    sendGOFirst()
                elif event.ui_element == rel_button_GOBack:
                    sendGOBack()
                elif event.ui_element == rel_button_GOFwd:
                    sendGOFwd()
                elif event.ui_element == rel_button_GOLast:
                    sendGOLast()
                elif event.ui_element == rel_button_ExecMoves:
                    sendExecMoves()
                elif event.ui_element == rel_button_OrbitPoint:
                    sendOrbitPoint()
                elif event.ui_element == rel_button_Timelapse:
                    sendTimelapse()
                elif event.ui_element == rel_button_PANORAMICLAPSE:
                    sendPanoramicLapse()
                elif event.ui_element == rel_button_REPORT:
                    sendREPORTall()
                elif event.ui_element == rel_button_REPORTPOS:
                    sendREPORTpos()

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
                    #mouseMoving = True

                if sliderCircle.collidepoint(event.pos):
                    sliderCircle_draging = True
                    mouse_x, mouse_y = event.pos
                    sliderOffset_x = sliderCircle.x - mouse_x
                    sliderOffset_y = sliderCircle.y - mouse_y
                    #mouseMoving = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:            
                joyCircle_draging = False
                joyCircle.x = 195
                joyCircle.y = 195

                sliderCircle_draging = False
                sliderCircle.x = 195
                sliderCircle.y = 415

                axisX = int(0)
                axisY = int(0)
                axisZ = int(0)

                mouseMoving = False

        if event.type == pygame.MOUSEMOTION:
            if joyCircle_draging:
                mouseMoving = True
                mouse_x, mouse_y = event.pos
                joyCircle.x = mouse_x
                joyCircle.y = mouse_y
                if ((mouse_x + offset_x) > mouseBorder) and ((mouse_y + offset_y) > mouseBorder):
                    joyCircle.x = mouseBorder
                    joyCircle.y = mouseBorder
                    #print("test1")

                elif (((mouse_x + offset_x) > mouseBorder) and ((mouse_y + offset_y) < 30)):
                    joyCircle.x = mouseBorder
                    joyCircle.y = 30
                    #print("test2")

                elif (((mouse_x + offset_x) < 30) and ((mouse_y + offset_y) > mouseBorder)):
                    joyCircle.x = 30
                    joyCircle.y = mouseBorder
                    #print("test3")

                elif (((mouse_x + offset_x) < 30) and ((mouse_y + offset_y) < 30)):
                    joyCircle.x = 30
                    joyCircle.y = 30
                    #print("test4")

                elif ((mouse_x + offset_x) > (mouseBorder)):
                    joyCircle.x = mouseBorder
                    joyCircle.y = mouse_y + offset_y
                    #print("test5")

                elif ((mouse_x + offset_x) < 30):#-offset_x):
                    joyCircle.x = 30
                    joyCircle.y = mouse_y + offset_y
                    #print("test6")

                elif ((mouse_y + offset_y) > (mouseBorder)):
                    joyCircle.y = mouseBorder
                    joyCircle.x = mouse_x + offset_x
                    #print("test7")

                elif ((mouse_y + offset_y) < 30):
                    joyCircle.y = 30
                    joyCircle.x = mouse_x + offset_x
                    #print("test8")

                else:
                    joyCircle.x = mouse_x + offset_x
                    joyCircle.y = mouse_y + offset_y

                axisX = int(scale((joyCircle.x), (30,mouseBorder), (-254,255)))
                axisY = -(int(scale((joyCircle.y), (30,mouseBorder), (-255,254))))
                axisZ = int(0)
                
            if sliderCircle_draging:
                mouseMoving = True
                mouse_x, mouse_y = event.pos
                sliderCircle.x = mouse_x
                sliderCircle.y = 420
                if ((mouse_x + sliderOffset_x) > mouseBorder):
                    sliderCircle.x = mouseBorder

                elif ((mouse_x + sliderOffset_x) < 30):
                    sliderCircle.x = 30

                else:
                    sliderCircle.x = mouse_x + sliderOffset_x
                    
                axisX = int(0)
                axisY = int(0)
                axisZ = int(scale((sliderCircle.x), (30,mouseBorder), (-254,255)))

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
                    axisXDOT = scale(joyXreadDOT, (-1.0,deadRangeLow), (-1.0,0.0))
                elif (joyXread > deadRangeHigh):
                    axisXDOT = scale(joyXreadDOT, (deadRangeHigh,1.0), (0.0,1.0))
                else:
                    axisXDOT = 0

                if (joyYreadDOT < deadRangeLow):
                    axisYDOT = scale(joyYreadDOT, (-1.0,deadRangeLow), (-1.0,0.0))
                elif (joyYreadDOT > deadRangeHigh):
                    axisYDOT = scale(joyYreadDOT, (deadRangeHigh,1.0), (0.0,1.0))
                else:
                    axisYDOT = 0

                if (joyZreadDOT < deadRangeLow):
                    axisZDOT = scale(joyZreadDOT, (-1.0,deadRangeLow), (-1.0,0.0))
                elif (joyZreadDOT > deadRangeHigh):
                    axisZDOT = scale(joyZreadDOT, (deadRangeHigh,1.0), (0.0,1.0))
                else:
                    axisZDOT = 0
                
                joyCircle.x = (axisXDOT*165)+210-radius
                joyCircle.y = (axisYDOT*165)+210-radius
                sliderCircle.x = (axisZDOT*165)+210-radius

while running:
    pygame.event.pump()
    time_delta = clock.tick() / 1000.0
    time_delta_stack.append(time_delta)
    
    process_events()                                               # check for input

    if (((axisX != oldAxisX) or (axisY != oldAxisY) or (axisZ != oldAxisZ)) and ((time.time() - previousTime) > 0.1)):
        previousTime = time.time()
        oldAxisX = axisX
        oldAxisY = axisY
        oldAxisZ = axisZ
        axisXh = tohex(axisX, 16)
        axisYh = tohex(axisY, 16)
        axisZh = tohex(axisZ, 16)

        arr = [4, axisZh, axisXh, axisYh]
        sendJoystick(arr)

    readSerial()

    ui_manager.update(time_delta)                                  # respond to input

    window_surface.blit(background_surface, (0, 0))           # draw graphics

    ui_manager.draw_ui(window_surface)

    pygame.draw.circle(window_surface, RED, (joyCircle.x+15,joyCircle.y+radius), radius)
    pygame.draw.circle(window_surface, RED, (sliderCircle.x+15,430), radius)

    pygame.draw.rect(window_surface, [125,0,0], [30,30,360,360],width=3)
    pygame.draw.rect(window_surface, [125,0,0], [30,400,360,60],width=3)

    pygame.display.update()

    clk.tick(40)