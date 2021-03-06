#ifndef PANTILTMOUNT_H
#define PANTILTMOUNT_H

/*------------------------------------------------------------------------------------------------------------------------------------------------------*/

#define BAUD_RATE 38400              //115200            //57600
// Different Boards                 ESP32         Nano
//#define PIN_SHUTTER_TRIGGER //    // --         //A1
#define PIN_PAN_HALL 6              //32          //A3
#define PIN_TILT_HALL 7             //33          //A4
#define PIN_SLIDER_HALL 16          //4           //2
//#define PIN_INPUT_VOLTAGE //      // --         //A5
#define PIN_ENABLE 2 //8            //23          //12
#define PIN_MS1 3 //9               //22          //11
#define PIN_MS2 4 //10              //26          //10
#define PIN_STEP_SLIDER 18          //17          //4
#define PIN_DIRECTION_SLIDER 17     //16          //3
#define PIN_STEP_TILT 20            //18          //6
#define PIN_DIRECTION_TILT 19       //5           //5
#define PIN_STEP_PAN  22            //21          //8
#define PIN_DIRECTION_PAN 21        //19          //7

#define HALF_STEP 2
#define QUARTER_STEP 4
#define EIGHTH_STEP 8
#define SIXTEENTH_STEP 16

#define SLIDER_PULLEY_TEETH 36.0
#define PAN_GEAR_RATIO 8.4705882352941176470588235294118 //144/17 teeth
//Used with the belt driven tilt axis.
//#define TILT_GEAR_RATIO 7.6875 //123/16 teeth
//Used with herringbone gears
#define TILT_GEAR_RATIO 3.047619047619047619047619047619 //64/21 teeth

#define MAX_STRING_LENGTH 10
#define KEYFRAME_ARRAY_LENGTH 35

#define SHUTTER_DELAY 200

#define INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED 4

#define INSTRUCTION_STEP_MODE 'm'
#define INSTRUCTION_ENABLE 'g'
#define INSTRUCTION_ACCEL_ENABLE 'l'

#define INSTRUCTION_PAN_DEGREES 'p'
#define INSTRUCTION_TILT_DEGREES 't'
#define INSTRUCTION_SLIDER_MILLIMETRES 'x'

#define INSTRUCTION_PAN_DEGREES_REL 'P'
#define INSTRUCTION_TILT_DEGREES_REL 'T'
#define INSTRUCTION_SLIDER_MILLIMETRES_REL 'L'

#define INSTRUCTION_SET_PAN_SPEED 's'
#define INSTRUCTION_SET_TILT_SPEED 'S'
#define INSTRUCTION_SET_SLIDER_SPEED 'X'

#define INSTRUCTION_SET_PAN_SPEED_SLOW 'o'
#define INSTRUCTION_SET_TILT_SPEED_SLOW 'O'
#define INSTRUCTION_SET_SLIDER_SPEED_SLOW 'M'

#define INSTRUCTION_INVERT_PAN 'i'
#define INSTRUCTION_INVERT_TILT 'I'
#define INSTRUCTION_INVERT_SLIDER 'j'

#define INSTRUCTION_PAN_ACCEL_INCREMENT_DELAY 'q'
#define INSTRUCTION_TILT_ACCEL_INCREMENT_DELAY 'Q'
#define INSTRUCTION_SLIDER_ACCEL_INCREMENT_DELAY 'w'

#define INSTRUCTION_SET_FAST_SPEED 'V'
#define INSTRUCTION_SET_SLOW_SPEED 'v'

#define INSTRUCTION_DEBUG_STATUS 'R'
#define INSTRUCTION_POSITION_STATUS 'r'
#define INSTRUCTION_RESET_LEDS 'W'
#define INSTRUCTION_CLEAR_ARRAY 'Y'
#define INSTRUCTION_SAVE_TO_EEPROM 'U'

#define INSTRUCTION_SET_ZERO_POS 'h'
#define INSTRUCTION_SET_HOMING 'H'
#define INSTRUCTION_ORIBIT_POINT '@'
#define INSTRUCTION_CALCULATE_TARGET_POINT 'G'

#define INSTRUCTION_SETPOS1 'a'
#define INSTRUCTION_GOPOS1 'A'
#define INSTRUCTION_SETPOS2 'b'
#define INSTRUCTION_GOPOS2 'B'
#define INSTRUCTION_SETPOS3 'c'
#define INSTRUCTION_GOPOS3 'C'
#define INSTRUCTION_SETPOS4 'd'
#define INSTRUCTION_GOPOS4 'D'
#define INSTRUCTION_SETPOS5 'e'
#define INSTRUCTION_GOPOS5 'E'
#define INSTRUCTION_SETPOS6 'f'
#define INSTRUCTION_GOPOS6 'F'

#define INSTRUCTION_ZOOM_IN 'Z'
#define INSTRUCTION_ZOOM_OUT 'z'
#define INSTRUCTION_STOP_ZOOM 'N'

#define EEPROM_ADDRESS_HOMING_MODE 0
#define EEPROM_ADDRESS_MODE 4
#define EEPROM_ADDRESS_ACCELERATION_ENABLE 8
#define EEPROM_ADDRESS_PAN_FAST_SPEED 12
#define EEPROM_ADDRESS_TILT_FAST_SPEED 16
#define EEPROM_ADDRESS_SLIDER_FAST_SPEED 20
#define EEPROM_ADDRESS_PAN_SLOW_SPEED 24
#define EEPROM_ADDRESS_TILT_SLOW_SPEED 28
#define EEPROM_ADDRESS_SLIDER_SLOW_SPEED 32
#define EEPROM_ADDRESS_INVERT_PAN 36
#define EEPROM_ADDRESS_INVERT_TILT 40
#define EEPROM_ADDRESS_INVERT_SLIDER 44
#define EEPROM_ADDRESS_PAN_ACCEL_INCREMENT_DELAY 48
#define EEPROM_ADDRESS_TILT_ACCEL_INCREMENT_DELAY 56
#define EEPROM_ADDRESS_SLIDER_ACCEL_INCREMENT_DELAY 64

#define VERSION_NUMBER "Version: 1.0.0\n"

/*------------------------------------------------------------------------------------------------------------------------------------------------------*/

struct KeyframeElement {
    long panStepCount = 0;
    float panSpeed = 0;
    long tiltStepCount = 0;
    float tiltSpeed = 0;
    long sliderStepCount = 0;
    float sliderSpeed = 0;
    int msDelay = 0;
};

struct FloatCoordinate {
    float x;
    float y;
    float z;
};

struct LinePoints {
    float x0;
    float y0;
    float x1;
    float y1;
};

/*------------------------------------------------------------------------------------------------------------------------------------------------------*/

void initPanTilt(void);
void Serial1Flush(void);
void enableSteppers(void);
void setStepMode(int);
void Serial1Data(void);
void mainLoop(void);
void panDegrees(float);
void tiltDegrees(float);
void debugReport(void);
bool findHome(void);
float getBatteryVoltage(void);
float getBatteryPercentage(void);
float boundFloat(float, float, float);
float panDegreesToSteps(float);
float tiltDegreesToSteps(float);
float panStepsToDegrees(long);
float panStepsToDegrees(float);
float tiltStepsToDegrees(long);
float tiltStepsToDegrees(float);
int addPosition(void);
void clearKeyframes(void);
void executeMoves(int);
void moveToIndex(int);
void gotoFirstKeyframe(void);
void gotoLastKeyframe(void);
void editKeyframe(void);
void addDelay(unsigned int ms);
void editDelay(unsigned int ms);
void printKeyframeElements(void);
void saveEEPROM(void);
void printEEPROM(void);
void setEEPROMVariables(void);
void invertPanDirection(bool);
void invertTiltDirection(bool);
int setTargetPositions(float, float, float);
void toggleAutoHoming(void);
//void triggerCameraShutter(void);
//void panoramiclapseInterpolation(float, float, float, float, float, float, float, unsigned long);
//void panoramiclapse(float, unsigned long, int);
long sliderMillimetresToSteps(float);
float sliderStepsToMillimetres(long);
void sliderMoveTo(float);
void invertSliderDirection(bool);
//void timelapse(unsigned int, unsigned long);
//bool calculateTargetCoordinate(void);
//void interpolateTargetPoint(FloatCoordinate);
void toggleAcceleration(void);
void scaleKeyframeSpeed(float);

/*------------------------------------------------------------------------------------------------------------------------------------------------------*/

#endif
