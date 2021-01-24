#include "PanTiltMount.h"
#include <Iibrary.h> //A library I created for Arduino that contains some simple functions I commonly use. Library available at: https://github.com/isaac879/Iibrary
#include "TeensyStep.h"
#include <EEPROM.h> //To be able to save values when powered off
#include <IRremote.h>

/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/

//Global scope

Stepper stepper_pan(PIN_STEP_PAN, PIN_DIRECTION_PAN);
Stepper stepper_tilt(PIN_STEP_TILT, PIN_DIRECTION_TILT);
Stepper stepper_slider(PIN_STEP_SLIDER, PIN_DIRECTION_SLIDER);

StepControl multi_stepper;

StepControl step_stepperP;
StepControl step_stepperT;
StepControl step_stepperS;

RotateControl rotate_stepperP;
RotateControl rotate_stepperT;
RotateControl rotate_stepperS;

IRsend irsend;

KeyframeElement keyframe_array[6];

bool DEBUG1 = false;

int keyframe_elements = 0;
int current_keyframe_index = -1;
char stringText[MAX_STRING_LENGTH + 1];
float pan_steps_per_degree = (200.0 * SIXTEENTH_STEP * PAN_GEAR_RATIO) / 360.0; //Stepper motor has 200 steps per 360 degrees
float tilt_steps_per_degree = (200.0 * SIXTEENTH_STEP * TILT_GEAR_RATIO) / 360.0; //Stepper motor has 200 steps per 360 degrees
float slider_steps_per_millimetre = (200.0 * SIXTEENTH_STEP) / (SLIDER_PULLEY_TEETH * 2); //Stepper motor has 200 steps per 360 degrees, the timing pully has 36 teeth and the belt has a pitch of 2mm
float step_mode = SIXTEENTH_STEP;
bool enable_state = true; //Stepper motor driver enable state
float hall_pan_offset_degrees = 0; //Offset to make the pan axis home position centred. This is required because the Hall sensor triggers before being centred on the magnet.
float hall_tilt_offset_degrees = 0; //Offset to make the tilt axis home position centred. This is required because the Hall sensor triggers before being centred on the magnet.
byte invert_pan = 0; //Variables to invert the direction of the axis. Note: These value gets set from the saved EEPROM value on startup.
byte invert_tilt = 0;
byte invert_slider = 0;
byte homing_mode = 0; //Note: Gets set from the saved EEPROM value on startup
float pan_max_speed = 20;     //degrees/second. Note: Gets set from the saved EEPROM value on startup.
float tilt_max_speed = 20;    //degrees/second.
float slider_max_speed = 40;  //mm/second.
float pan_fast_speed = 20;    //degrees/second.
float tilt_fast_speed = 20;   //degrees/second.
float slider_fast_speed = 60; //mm/second.
float pan_slow_speed = 5;    //degrees/second.
float tilt_slow_speed = 5;   //degrees/second.
float slider_slow_speed = 20; //mm/second.
long target_position[3]; //Array to store stepper motor step counts
long start_position[3];
float final_position[3];
float degrees_per_picture = 0.5; //Note: Gets set from the saved EEPROM value on startup.
//unsigned long delay_ms_between_pictures = 1000; //Note: Gets set from the saved EEPROM value on startup.
float delay_ms_between_pictures = 1000; //Note: Gets set from the saved EEPROM value on startup.
float pan_accel_increment_us = 6000;
float tilt_accel_increment_us = 6000;
float slider_accel_increment_us = 6000;
byte acceleration_enable_state = 1;
FloatCoordinate intercept;

bool motorRunning = false;

constexpr unsigned PID_Interval = 10; // ms
constexpr float P = 0.01;             // (P)roportional constant of the regulator needs to be adjusted (depends on speed and acceleration setting)


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void initPanTilt(void) {
  Serial1.setTX(1);
  Serial1.begin(BAUD_RATE);
  pinMode(PIN_MS1, OUTPUT);
  pinMode(PIN_MS2, OUTPUT);
  pinMode(PIN_ENABLE, OUTPUT);
  pinMode(PIN_DIRECTION_PAN, OUTPUT);
  pinMode(PIN_STEP_PAN, OUTPUT);
  pinMode(PIN_DIRECTION_TILT, OUTPUT);
  pinMode(PIN_STEP_TILT, OUTPUT);
  pinMode(PIN_DIRECTION_SLIDER, OUTPUT);
  pinMode(PIN_STEP_SLIDER, OUTPUT);
  pinMode(PIN_PAN_HALL, INPUT_PULLUP);
  pinMode(PIN_TILT_HALL, INPUT_PULLUP);
  pinMode(PIN_SLIDER_HALL, INPUT_PULLUP);
  setEEPROMVariables();
  setStepMode(step_mode); //steping mode
  stepper_pan.setMaxSpeed(panDegreesToSteps(pan_max_speed));
  stepper_tilt.setMaxSpeed(tiltDegreesToSteps(tilt_max_speed));
  stepper_slider.setMaxSpeed(sliderMillimetresToSteps(slider_max_speed));
  stepper_pan.setAcceleration(pan_accel_increment_us);
  stepper_tilt.setAcceleration(tilt_accel_increment_us);
  stepper_slider.setAcceleration(slider_accel_increment_us);
  invertPanDirection(invert_pan);
  invertTiltDirection(invert_tilt);
  invertSliderDirection(invert_slider);
  delay(200);
  Serial1.println(String("Pan max           : ") + panDegreesToSteps(pan_max_speed) + String(" steps/s"));
  Serial1.println(String("Tilt max          : ") + tiltDegreesToSteps(tilt_max_speed) + String(" steps/s"));
  Serial1.println(String("Slider max        : ") + sliderMillimetresToSteps(slider_max_speed) + String(" steps/s"));
  Serial1.println("");
  digitalWrite(PIN_ENABLE, LOW);          //Enable the stepper drivers
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void Serial1Flush(void) {
  while (Serial1.available() > 0) {
    char c = Serial1.read();
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void enableSteppers(void) {
  if (enable_state == false) {
    digitalWrite(PIN_ENABLE, LOW); //Enable the stepper drivers
    enable_state = true;
    Serial1.println(String("Enabled"));
  }
  else {
    digitalWrite(PIN_ENABLE, HIGH); //Disabe the stepper drivers
    enable_state = false;
    Serial1.println(String("Disabled"));
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void setStepMode(int newMode) { //Step modes for the TMC2208
  float stepRatio = (float)newMode / (float)step_mode; //Ratio between the new step mode and the previously set one.
  if (newMode == HALF_STEP) {
    digitalWrite(PIN_MS1, HIGH);
    digitalWrite(PIN_MS2, LOW);
  }
  else if (newMode == QUARTER_STEP) {
    digitalWrite(PIN_MS1, LOW);
    digitalWrite(PIN_MS2, HIGH);
  }
  else if (newMode == EIGHTH_STEP) {
    digitalWrite(PIN_MS1, LOW);
    digitalWrite(PIN_MS2, LOW);
  }
  else if (newMode == SIXTEENTH_STEP) {
    digitalWrite(PIN_MS1, HIGH);
    digitalWrite(PIN_MS2, HIGH);
  }
  else { //If an invalid step mode was entered.
    Serial1.println(String("Invalid mode. Enter 2, 4, 8 or 16"));
    return;
  }

  Serial1.println(newMode);

  //Scale current step to match the new step mode
  stepper_pan.setPosition(stepper_pan.getPosition() * stepRatio);
  stepper_tilt.setPosition(stepper_tilt.getPosition() * stepRatio);
  stepper_slider.setPosition(stepper_slider.getPosition() * stepRatio);

  pan_steps_per_degree = (200.0 * (float)newMode * PAN_GEAR_RATIO) / 360.0; //Stepper motor has 200 steps per 360 degrees
  tilt_steps_per_degree = (200.0 * (float)newMode * TILT_GEAR_RATIO) / 360.0; //Stepper motor has 200 steps per 360 degrees
  slider_steps_per_millimetre = (200.0 * (float)newMode) / (SLIDER_PULLEY_TEETH * 2.0); //Stepper motor has 200 steps per 360 degrees, the timing pully has 36 teeth and the belt has a pitch of 2mm

  stepper_pan.setMaxSpeed(panDegreesToSteps(pan_max_speed));
  stepper_tilt.setMaxSpeed(tiltDegreesToSteps(tilt_max_speed));
  stepper_slider.setMaxSpeed(sliderMillimetresToSteps(slider_max_speed));
  step_mode = (float)newMode;
  Serial1.println(String("Set to ") + step_mode + (" step mode."));
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void panDegrees(float angle) {
  target_position[0] = panDegreesToSteps(angle);
  if (acceleration_enable_state == 0) {
    Serial1.println(String("Current Pan Position   : ") + stepper_pan.getPosition());
    Serial1.println(String("Target  Pan Position   : ") + target_position[0]);

    stepper_pan.setTargetAbs(target_position[0]);
    step_stepperP.move(stepper_pan);
  }
  else {
    Serial1.println(String("Current Pan Position   : ") + stepper_pan.getPosition());
    Serial1.println(String("Target  Pan Position   : ") + target_position[0]);

    stepper_pan.setTargetAbs(target_position[0]);
    step_stepperP.move(stepper_pan);
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void tiltDegrees(float angle) {
  target_position[1] = tiltDegreesToSteps(angle);
  if (acceleration_enable_state == 0) {
    Serial1.println(String("Current Tilt Position  : ") + stepper_tilt.getPosition());
    Serial1.println(String("Target  Tilt Position  : ") + target_position[1]);

    stepper_tilt.setTargetAbs(target_position[1]);
    step_stepperT.move(stepper_tilt);
  }
  else {
    Serial1.println(String("Current Tilt Position  : ") + stepper_tilt.getPosition());
    Serial1.println(String("Target  Tilt Position  : ") + target_position[1]);

    stepper_tilt.setTargetAbs(target_position[1]);
    step_stepperT.move(stepper_tilt);
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float panDegreesToSteps(float angle) {
  return pan_steps_per_degree * angle;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float tiltDegreesToSteps(float angle) {
  return tilt_steps_per_degree * angle;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


long sliderMillimetresToSteps(float mm) {
  return round(mm * slider_steps_per_millimetre);
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float sliderStepsToMillimetres(long steps) {
  return (float)steps / slider_steps_per_millimetre;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void sliderMoveTo(float mm) {
  target_position[2] = sliderMillimetresToSteps(mm);
  if (acceleration_enable_state == 0) {
    Serial1.println(String("Current Slider Position: ") + stepper_slider.getPosition());
    Serial1.println(String("Target Slider Position : ") + target_position[2]);

    stepper_slider.setTargetAbs(target_position[2]);
    step_stepperS.move(stepper_slider);
  }
  else {
    Serial1.println(String("Current Slider Position: ") + stepper_slider.getPosition());
    Serial1.println(String("Target Slider Position : ") + target_position[2]);

    stepper_slider.setTargetAbs(target_position[2]);
    step_stepperS.move(stepper_slider);
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void printKeyframeElements(void) {
  int row = 0;
  do {
    Serial1.println(String("Keyframe index: ") + row); //, F("\t|"));
    delay(200);
    Serial1.print(String("Pan   : ") + panStepsToDegrees(keyframe_array[row].panStepCount) + String("º\t"));
    Serial1.print(String("Tilt  : ") + tiltStepsToDegrees(keyframe_array[row].tiltStepCount) + String("º\t"));
    Serial1.print(String("Slider: ") + sliderStepsToMillimetres(keyframe_array[row].sliderStepCount) + String("mm\t"));
    delay(200);
    Serial1.print(String("Pan Speed   : ") + panStepsToDegrees(keyframe_array[row].panSpeed) + String(" º/s\t"));
    Serial1.print(String("Tilt Speed  : ") + tiltStepsToDegrees(keyframe_array[row].tiltSpeed) + String(" º/s\t"));
    Serial1.println(String("Slider Speed: ") + sliderStepsToMillimetres(keyframe_array[row].sliderSpeed) + String(" mm/s"));
    delay(200);
    row++;
  } while (row < 6);
  Serial1.println(String(""));
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void debugReport(void) {
  Serial1.println(String("Step mode      : ") + step_mode);
  delay(200);
  Serial1.println(String(""));
  Serial1.println(String("Pan angle         : ") + panStepsToDegrees(stepper_pan.getPosition()) + String("º"));
  delay(200);
  Serial1.println(String("Tilt angle        : ") + tiltStepsToDegrees(stepper_tilt.getPosition()) + String("º"));
  Serial1.println(String("Slider position   : ") + sliderStepsToMillimetres(stepper_slider.getPosition()) + String(" mm\n"));
  delay(200);
  Serial1.println(String("Pan max           : ") + panDegreesToSteps(pan_max_speed) + String(" steps/s"));
  Serial1.println(String("Tilt max          : ") + tiltDegreesToSteps(tilt_max_speed) + String(" steps/s"));
  delay(200);
  Serial1.println(String("Slider max        : ") + sliderMillimetresToSteps(slider_max_speed) + String(" steps/s\n"));
  Serial1.println(String("Pan max speed     : ") + pan_max_speed + String("º/s"));
  delay(200);
  Serial1.println(String("Tilt max speed    : ") + tilt_max_speed + String("º/s"));
  Serial1.println(String("Slider max speed  : ") + slider_max_speed + String("mm/s\n"));
  delay(200);
  Serial1.println(String("Pan Accel         : ") + pan_accel_increment_us + String(" steps/s²"));
  Serial1.println(String("Tilt Accel        : ") + tilt_accel_increment_us + String(" steps/s²"));
  delay(200);
  Serial1.println(String("Slider Accel      : ") + slider_accel_increment_us + String(" steps/s²\n"));
  delay(100);

  printEEPROM();
  printKeyframeElements();
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void positionReport(void) {
  Serial1.println(String("Position Report   : "));
  Serial1.println(String("Pan angle         : ") + panStepsToDegrees(stepper_pan.getPosition()) + String("º"));
  delay(200);
  Serial1.println(String("Tilt angle        : ") + tiltStepsToDegrees(stepper_tilt.getPosition()) + String("º"));
  Serial1.println(String("Slider position   : ") + sliderStepsToMillimetres(stepper_slider.getPosition()) + String(" mm\n"));
  delay(200);
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float panStepsToDegrees(long steps) {
  return steps / pan_steps_per_degree;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float panStepsToDegrees(float steps) {
  return steps / pan_steps_per_degree;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float tiltStepsToDegrees(long steps) {
  return steps / tilt_steps_per_degree;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


float tiltStepsToDegrees(float steps) {
  return steps / tilt_steps_per_degree;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


int addPosition(void) {
  if (keyframe_elements >= 0 && keyframe_elements < KEYFRAME_ARRAY_LENGTH) {
    keyframe_array[keyframe_elements].panStepCount = stepper_pan.getPosition();
    keyframe_array[keyframe_elements].tiltStepCount = stepper_tilt.getPosition();
    keyframe_array[keyframe_elements].sliderStepCount = stepper_slider.getPosition();
    keyframe_array[keyframe_elements].panSpeed = panDegreesToSteps(pan_max_speed);
    keyframe_array[keyframe_elements].tiltSpeed = tiltDegreesToSteps(tilt_max_speed);
    keyframe_array[keyframe_elements].sliderSpeed = sliderMillimetresToSteps(slider_max_speed);
    keyframe_array[keyframe_elements].msDelay = 0;
    current_keyframe_index = keyframe_elements;
    keyframe_elements++;                            //increment the index
    Serial1.println(String("Added at index: ") + current_keyframe_index);
    return 0;
  }
  else {
    Serial1.println(String("Max number of keyframes reached"));
  }
  return -1;
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void moveToIndex(int index) {

  stepper_pan.setTargetAbs(keyframe_array[index].panStepCount);
  stepper_tilt.setTargetAbs(keyframe_array[index].tiltStepCount);
  stepper_slider.setTargetAbs(keyframe_array[index].sliderStepCount);

  //float initialPanSpeed = panDegreesToSteps(pan_max_speed);
  //float initialTiltSpeed = tiltDegreesToSteps(tilt_max_speed);
  //float initialSliderSpeed = sliderMillimetresToSteps(slider_max_speed);

  //stepper_pan.setMaxSpeed(keyframe_array[index].panSpeed);
  //stepper_tilt.setMaxSpeed(keyframe_array[index].tiltSpeed);
  //stepper_slider.setMaxSpeed(keyframe_array[index].sliderSpeed);

  Serial1.println(String("\nMove to Index: ") + index);
  delay(200);
  Serial1.println(String("panStepCount   : ") + keyframe_array[index].panStepCount);
  Serial1.println(String("tiltStepCount  : ") + keyframe_array[index].tiltStepCount);
  Serial1.println(String("sliderStepCount: ") + keyframe_array[index].sliderStepCount);

  multi_stepper.move(stepper_pan, stepper_tilt, stepper_slider);

  //stepper_pan.setMaxSpeed(initialPanSpeed);
  //stepper_tilt.setMaxSpeed(initialTiltSpeed);
  //stepper_slider.setMaxSpeed(initialSliderSpeed);


}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void executeMoves(int repeat) {
  for (int i = 0; i < repeat; i++) {
    for (int row = 0; row < keyframe_elements; row++) {
      moveToIndex(row);
    }
  }
}

/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void editKeyframe(int keyframeEdit) {
  keyframe_array[keyframeEdit].panStepCount = stepper_pan.getPosition();
  keyframe_array[keyframeEdit].tiltStepCount = stepper_tilt.getPosition();
  keyframe_array[keyframeEdit].sliderStepCount = stepper_slider.getPosition();
  keyframe_array[keyframeEdit].panSpeed = panDegreesToSteps(pan_max_speed);
  keyframe_array[keyframeEdit].tiltSpeed = tiltDegreesToSteps(tilt_max_speed);
  keyframe_array[keyframeEdit].sliderSpeed = sliderMillimetresToSteps(slider_max_speed);

  Serial1.println(String("Edited index: ") + keyframeEdit);
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void invertPanDirection(bool invert) {
  Serial1.println(String("Pan inversion: ") + invert);
  invert_pan = invert;
  if (invert_pan == 1) {
    stepper_pan.setInverseRotation(true);
  }
  else {
    stepper_pan.setInverseRotation(false);
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void invertTiltDirection(bool invert) {
  Serial1.println(String("Tilt inversion: ") + invert);
  invert_tilt = invert;
  if (invert_tilt == 1) {
    stepper_tilt.setInverseRotation(true);
  }
  else {
    stepper_tilt.setInverseRotation(false);
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void invertSliderDirection(bool invert) {
  Serial1.println(String("Slider inversion: ") + invert);
  invert_slider = invert;
  if (invert_slider == 1) {
    stepper_slider.setInverseRotation(true);
  }
  else {
    stepper_slider.setInverseRotation(false);
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void saveEEPROM(void) {
  EEPROM.put(EEPROM_ADDRESS_HOMING_MODE, homing_mode);
  EEPROM.put(EEPROM_ADDRESS_MODE, step_mode);
  EEPROM.put(EEPROM_ADDRESS_PAN_MAX_SPEED, pan_max_speed);
  EEPROM.put(EEPROM_ADDRESS_TILT_MAX_SPEED, tilt_max_speed);
  EEPROM.put(EEPROM_ADDRESS_SLIDER_MAX_SPEED, slider_max_speed);
  EEPROM.put(EEPROM_ADDRESS_HALL_PAN_OFFSET, hall_pan_offset_degrees);
  EEPROM.put(EEPROM_ADDRESS_HALL_TILT_OFFSET, hall_tilt_offset_degrees);
  EEPROM.put(EEPROM_ADDRESS_INVERT_PAN, invert_pan);
  EEPROM.put(EEPROM_ADDRESS_INVERT_TILT, invert_tilt);
  EEPROM.put(EEPROM_ADDRESS_INVERT_SLIDER, invert_slider);
  //EEPROM.put(EEPROM_ADDRESS_DEGREES_PER_PICTURE, degrees_per_picture);
  //EEPROM.put(EEPROM_ADDRESS_PANORAMICLAPSE_DELAY, delay_ms_between_pictures);
  EEPROM.put(EEPROM_ADDRESS_ACCELERATION_ENABLE, acceleration_enable_state);
  EEPROM.put(EEPROM_ADDRESS_PAN_ACCEL_INCREMENT_DELAY, pan_accel_increment_us);
  EEPROM.put(EEPROM_ADDRESS_TILT_ACCEL_INCREMENT_DELAY, tilt_accel_increment_us);
  EEPROM.put(EEPROM_ADDRESS_SLIDER_ACCEL_INCREMENT_DELAY, slider_accel_increment_us);
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void printEEPROM(void) {
  float ftemp;
  delay(200);
  EEPROM.get(EEPROM_ADDRESS_MODE, ftemp);
  Serial1.println(String("EEPROM:\nStep mode         : ") + ftemp + String("\n"));
  EEPROM.get(EEPROM_ADDRESS_PAN_MAX_SPEED, ftemp);
  Serial1.println(String("Pan max           : ") + ftemp + String("º/s"));
  delay(200);
  EEPROM.get(EEPROM_ADDRESS_TILT_MAX_SPEED, ftemp);
  Serial1.println(String("Tilt max          : ") + ftemp + String("º/s"));
  EEPROM.get(EEPROM_ADDRESS_SLIDER_MAX_SPEED, ftemp);
  Serial1.println(String("Slider max        : ") + ftemp + String("mm/s\n"));
  delay(200);
  Serial1.println(String("Pan invert        : ") + EEPROM.read(EEPROM_ADDRESS_INVERT_PAN));
  Serial1.println(String("Tilt invert       : ") + EEPROM.read(EEPROM_ADDRESS_INVERT_TILT));
  delay(200);
  Serial1.println(String("Slider invert     : ") + EEPROM.read(EEPROM_ADDRESS_INVERT_SLIDER) + String("\n"));
  EEPROM.get(EEPROM_ADDRESS_PAN_ACCEL_INCREMENT_DELAY, ftemp);
  Serial1.println(String("Pan accel delay   : ") + ftemp + String(" steps/s²"));
  delay(200);
  EEPROM.get(EEPROM_ADDRESS_TILT_ACCEL_INCREMENT_DELAY, ftemp);
  Serial1.println(String("Tilt accel delay  : ") + ftemp + String(" steps/s²"));
  EEPROM.get(EEPROM_ADDRESS_SLIDER_ACCEL_INCREMENT_DELAY, ftemp);
  Serial1.println(String("Slider accel delay: ") + ftemp + String(" steps/s²\n"));
  delay(500);
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void setEEPROMVariables(void) {
  EEPROM.get(EEPROM_ADDRESS_MODE, step_mode);
  EEPROM.get(EEPROM_ADDRESS_PAN_MAX_SPEED, pan_max_speed);
  EEPROM.get(EEPROM_ADDRESS_TILT_MAX_SPEED, tilt_max_speed);
  EEPROM.get(EEPROM_ADDRESS_SLIDER_MAX_SPEED, slider_max_speed);
  EEPROM.get(EEPROM_ADDRESS_HALL_PAN_OFFSET, hall_pan_offset_degrees);
  EEPROM.get(EEPROM_ADDRESS_HALL_TILT_OFFSET, hall_tilt_offset_degrees);
  //EEPROM.get(EEPROM_ADDRESS_DEGREES_PER_PICTURE, degrees_per_picture);
  //EEPROM.get(EEPROM_ADDRESS_PANORAMICLAPSE_DELAY, delay_ms_between_pictures);
  EEPROM.get(EEPROM_ADDRESS_PAN_ACCEL_INCREMENT_DELAY, pan_accel_increment_us);
  EEPROM.get(EEPROM_ADDRESS_TILT_ACCEL_INCREMENT_DELAY, tilt_accel_increment_us);
  EEPROM.get(EEPROM_ADDRESS_SLIDER_ACCEL_INCREMENT_DELAY, slider_accel_increment_us);
  EEPROM.get(EEPROM_ADDRESS_INVERT_PAN, invert_pan);
  EEPROM.get(EEPROM_ADDRESS_INVERT_TILT, invert_tilt);
  EEPROM.get(EEPROM_ADDRESS_INVERT_SLIDER, invert_slider);
  EEPROM.get(EEPROM_ADDRESS_HOMING_MODE, homing_mode);
  EEPROM.get(EEPROM_ADDRESS_ACCELERATION_ENABLE, acceleration_enable_state);
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/

//From the first two keyframes the intercept of where the camera is directed is calculated.
//The first kayframe's x pan and tilt positions are used to calculate a 3D vector. The second keyframe's x and pan position are used to calculate a vertical plane. (It wuld be almost impossible for 2 3D vectors to intercept due to floating point precision issues.)
//The intercept of the vectorand plane are then calculated to give the X, Y, Z coordinates of the point the camera was pointed at in both keyframes. (The second keyframe will ignore the tilt value and calculate it based on the first keyframes vector.)
bool calculateTargetCoordinate(void) {
  float m1, c1, m2, c2;

  LinePoints line0;
  line0.x0 = sliderStepsToMillimetres(keyframe_array[0].sliderStepCount);
  line0.y0 = 0;
  line0.x1 = line0.x0 + cos(degToRads(panStepsToDegrees(keyframe_array[0].panStepCount)));
  line0.y1 = sin(degToRads(panStepsToDegrees(keyframe_array[0].panStepCount)));

  LinePoints line1;
  line1.x0 = sliderStepsToMillimetres(keyframe_array[1].sliderStepCount);
  line1.y0 = 0;
  line1.x1 = line1.x0 + cos(degToRads(panStepsToDegrees(keyframe_array[1].panStepCount)));
  line1.y1 = sin(degToRads(panStepsToDegrees(keyframe_array[1].panStepCount)));

  if ((line0.x1 - line0.x0) != 0) {
    m1 = (line0.y1 - line0.y0) / (line0.x1 - line0.x0);
    c1 = line0.y1 - m1 * line0.x1;
  }

  if ((line1.x1 - line1.x0) != 0) {
    m2 = (line1.y1 - line1.y0) / (line1.x1 - line1.x0);
    c2 = line1.y1 - m2 * line1.x1;
  }

  if ((line0.x1 - line0.x0) == 0) {
    intercept.x = line0.x0;
    intercept.y = m2 * intercept.x + c2;
  }
  else if ((line1.x1 - line1.x0) == 0) {
    intercept.x = line1.x0;
    intercept.y = m1 * intercept.x + c1;
  }
  else {
    if (m1 == m2) { //If the angle of the slope of both lines are the same they are parallel and cannot intercept.
      Serial1.println(String("Positions do not intersect."));
      return false;
    }
    intercept.x = (c2 - c1) / (m1 - m2);
    intercept.y = m1 * intercept.x + c1;
  }
  intercept.z = tan(degToRads(tiltStepsToDegrees(keyframe_array[0].tiltStepCount))) * sqrt(pow(intercept.x - sliderStepsToMillimetres(keyframe_array[0].sliderStepCount), 2) + pow(intercept.y, 2));
  if (((panStepsToDegrees(keyframe_array[0].panStepCount) > 0 && panStepsToDegrees(keyframe_array[1].panStepCount) > 0) && intercept.y < 0)
      || ((panStepsToDegrees(keyframe_array[0].panStepCount) < 0 && panStepsToDegrees(keyframe_array[1].panStepCount) < 0) && intercept.y > 0) || intercept.y == 0) { //Checks that the intercept point is in the direction the camera was pointing and not on the opposite side behind the camera.
    Serial1.println(String("Invalid intercept.\n"));
    return false;
  }
  return true;
}

/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void interpolateTargetPoint(FloatCoordinate targetPoint, int repeat) { //The first two keyframes are interpolated between while keeping the camera pointing at previously calculated intercept point.
  if (keyframe_elements < 1) {
    Serial1.println(String("Not enough keyframes recorded\n"));
    return; //check there are posions to move to
  }

  //float sliderStartPos = sliderStepsToMillimetres(keyframe_array[0].sliderStepCount); //slider start position
  //float sliderEndPos = sliderStepsToMillimetres(keyframe_array[1].sliderStepCount);
  float panAngle = 0;
  float tiltAngle = 0;
  float x = targetPoint.x - sliderStepsToMillimetres(keyframe_array[0].sliderStepCount);
  float ySqared = pow(targetPoint.y, 2);
  //float sliderTravel = sliderStepsToMillimetres(keyframe_array[1].sliderStepCount) - sliderStepsToMillimetres(keyframe_array[0].sliderStepCount);
  //int numberOfIncrements = abs(sliderTravel);
  //float increment = sliderTravel / numberOfIncrements;//size of interpolation increments in mm

  float currentSliderPosMM = sliderStepsToMillimetres(stepper_slider.getPosition());
  float previousSliderPosMM = 0;
  //multi_stepper.rotateAsync(stepper_slider);

  final_position[0] = keyframe_array[1].panStepCount;
  final_position[1] = keyframe_array[1].tiltStepCount;
  final_position[2] = keyframe_array[1].sliderStepCount;

  rotate_stepperS.rotateAsync(stepper_slider);
  rotate_stepperP.rotateAsync(stepper_pan);
  rotate_stepperT.rotateAsync(stepper_tilt);

  rotate_stepperS.overrideSpeed(1.0f);
  rotate_stepperP.overrideSpeed(0.0f);
  rotate_stepperT.overrideSpeed(0.0f);

  //for (int j = 0; (j < repeat || (repeat == 0 && j == 0)); j++) {
  //for (int i = 0; i <= numberOfIncrements; i++) {
  while (stepper_pan.getPosition() != final_position[0] || stepper_tilt.getPosition() != final_position[1] || stepper_slider.getPosition() != final_position[2]) {
    currentSliderPosMM = sliderStepsToMillimetres(stepper_slider.getPosition());
    if (currentSliderPosMM != previousSliderPosMM) {
      previousSliderPosMM = currentSliderPosMM;

      //x = targetPoint.x - (sliderStartPos + increment * i);
      panAngle = radsToDeg(atan2(targetPoint.y, x));
      tiltAngle = radsToDeg(atan2(targetPoint.z, sqrt(pow(x, 2) + ySqared)));

      //setTargetPositions(panAngle, tiltAngle, sliderStartPos + increment * i);
      stepper_pan.setTargetAbs(panDegreesToSteps(panAngle));
      stepper_tilt.setTargetAbs(tiltDegreesToSteps(tiltAngle));

      float deltaP = ((panAngle - panStepsToDegrees(stepper_pan.getPosition())) * (P / PID_Interval));  // This implements a simple P regulator (can be extended to a PID if necessary)
      float factorP = std::max(-1.0f, std::min(1.0f, deltaP)); // limit to -1.0..1.0

      float deltaT = ((tiltAngle - tiltStepsToDegrees(stepper_tilt.getPosition())) * (P / PID_Interval));  // This implements a simple P regulator (can be extended to a PID if necessary)
      float factorT = std::max(-1.0f, std::min(1.0f, deltaT)); // limit to -1.0..1.0

      rotate_stepperP.overrideSpeed(factorP); // set new speed
      rotate_stepperT.overrideSpeed(factorT); // set new speed

      //multi_stepper.runSpeedToPosition();//blocking move to the next position
    }
  }
  rotate_stepperS.stopAsync();
  rotate_stepperP.stopAsync();
  rotate_stepperT.stopAsync();
  /*
    x = targetPoint.x - sliderEndPos;
    panAngle = radsToDeg(atan2(targetPoint.y, x));
    tiltAngle = radsToDeg(atan2(targetPoint.z, sqrt(pow(x, 2) + ySqared)));
    //setTargetPositions(panAngle, tiltAngle, sliderEndPos);
    //multi_stepper.runSpeedToPosition();//blocking move to the next position

    for (int i = numberOfIncrements; (i >= 0 && repeat > 0); i--) {
    x = targetPoint.x - (sliderStartPos + increment * i);
    panAngle = radsToDeg(atan2(targetPoint.y, x));
    tiltAngle = radsToDeg(atan2(targetPoint.z, sqrt(pow(x, 2) + ySqared)));
    //setTargetPositions(panAngle, tiltAngle, sliderStartPos + increment * i);
    //multi_stepper.runSpeedToPosition();//blocking move to the next position
    }
    if (repeat > 0) {
    //setTargetPositions(panAngle, tiltAngle, sliderStartPos);
    //multi_stepper.runSpeedToPosition();//blocking move to the next position
    }

    }*/
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void toggleAcceleration(void) {
  if (acceleration_enable_state == 0) {
    acceleration_enable_state = 1;
    Serial1.println(String("Accel enabled."));
  }
  else {
    acceleration_enable_state = 0;
    Serial1.println(String("Accel disabled."));
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void Serial1Data(void) {
  char instruction = Serial1.read();
  if (instruction == INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED) {
    int count = 0;
    while (Serial1.available() < 6) {                       //  Wait for 6 bytes to be available. Breaks after ~20ms if bytes are not received.
      delayMicroseconds(200);
      count++;
      if (count > 100) {
        Serial1Flush();                                     //  Clear the Serial1 buffer
        break;
      }
    }
    short sliderStepSpeed = (Serial1.read() << 8) + Serial1.read();
    short panStepSpeed = (Serial1.read() << 8) + Serial1.read();
    short tiltStepSpeed = (Serial1.read() << 8) + Serial1.read();

    if ( DEBUG1 ) {
      Serial1.print(String("sliderStepSpeed - ") + sliderStepSpeed);
      Serial1.print(String(" , "));
      Serial1.print(String("panStepSpeed - ") + panStepSpeed);
      Serial1.print(String(" , "));
      Serial1.println(String("tiltStepSpeed - ") + tiltStepSpeed);
    }

    float sliderStepSpeed2 = map(sliderStepSpeed, -255, 255, -(sliderMillimetresToSteps(slider_max_speed)), sliderMillimetresToSteps(slider_max_speed));
    float panStepSpeed2 = map(panStepSpeed, -255, 255, -(panDegreesToSteps(pan_max_speed)), panDegreesToSteps(pan_max_speed));
    float tiltStepSpeed2 = map(tiltStepSpeed, -255, 255, -(tiltDegreesToSteps(tilt_max_speed)), tiltDegreesToSteps(tilt_max_speed));

    float speedFactorP = panStepSpeed2 / 2000.0f;
    float speedFactorT = tiltStepSpeed2 / 2000.0f;
    float speedFactorS = sliderStepSpeed2 / 2000.0f;

    if (speedFactorS == 0) {
      rotate_stepperS.stopAsync();
    }
    else {
      //Serial1.println(String("speedFactorS - ") + speedFactorS);
      rotate_stepperS.rotateAsync(stepper_slider);
      rotate_stepperS.overrideAcceleration(10);
      rotate_stepperS.overrideSpeed(speedFactorS);
    }

    if (speedFactorP == 0) {
      rotate_stepperP.stopAsync();
    }
    else {
      //Serial1.println(String("speedFactorP - ") + speedFactorP);
      rotate_stepperP.rotateAsync(stepper_pan);
      rotate_stepperP.overrideAcceleration(100);
      rotate_stepperP.overrideSpeed(speedFactorP);
    }

    if (speedFactorT == 0) {
      rotate_stepperT.stopAsync();
    }
    else {
      //Serial1.println(String("speedFactorT - ") + speedFactorT);
      rotate_stepperT.rotateAsync(stepper_tilt);
      rotate_stepperT.overrideAcceleration(100);
      rotate_stepperT.overrideSpeed(speedFactorT);
    }
  }

  delay(2);                                               //wait to make sure all data in the Serial1 message has arived
  memset(&stringText[0], 0, sizeof(stringText));          //clear the array
  while (Serial1.available()) {                            //set elemetns of stringText to the Serial1 values sent
    char digit = Serial1.read();                         //read in a char
    strncat(stringText, &digit, 1);                     //add digit to the end of the array
  }
  Serial1Flush();                                          //Clear any excess data in the Serial1 buffer
  int Serial1CommandValueInt = atoi(stringText);           //converts stringText to an int
  float Serial1CommandValueFloat = atof(stringText);       //converts stringText to a float
  if (instruction == '+') {                               //The Bluetooth module sends a message starting with "+CONNECTING" which should be discarded.
    delay(100);                                         //wait to make sure all data in the Serial1 message has arived
    Serial1Flush();                                      //Clear any excess data in the Serial1 buffer
    return;
  }

  switch (instruction) {
    case INSTRUCTION_SETPOS1: {
        editKeyframe(0);
      }
      break;
    case INSTRUCTION_GOPOS1: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          moveToIndex(0);
        }
      }
      break;
    case INSTRUCTION_SETPOS2: {
        editKeyframe(1);
      }
      break;
    case INSTRUCTION_GOPOS2: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          moveToIndex(1);
        }
      }
      break;
    case INSTRUCTION_SETPOS3: {
        editKeyframe(2);
      }
      break;
    case INSTRUCTION_GOPOS3: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          moveToIndex(2);
        }
      }
      break;
    case INSTRUCTION_SETPOS4: {
        editKeyframe(3);
      }
      break;
    case INSTRUCTION_GOPOS4: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          moveToIndex(3);
        }
      }
      break;
    case INSTRUCTION_SETPOS5: {
        editKeyframe(4);
      }
      break;
    case INSTRUCTION_GOPOS5: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          moveToIndex(4);
        }
      }
      break;
    case INSTRUCTION_SETPOS6: {
        editKeyframe(5);
      }
      break;
    case INSTRUCTION_GOPOS6: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          moveToIndex(5);
        }
      }
      break;
    case INSTRUCTION_SET_FAST_SPEED: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          stepper_pan.setMaxSpeed(panDegreesToSteps(pan_fast_speed));
          stepper_tilt.setMaxSpeed(panDegreesToSteps(tilt_fast_speed));
          stepper_slider.setMaxSpeed(sliderMillimetresToSteps(slider_fast_speed));
          Serial1.println(String("#V"));
        }
      }
      break;
    case INSTRUCTION_SET_SLOW_SPEED: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          stepper_pan.setMaxSpeed(panDegreesToSteps(pan_slow_speed));
          stepper_tilt.setMaxSpeed(panDegreesToSteps(tilt_slow_speed));
          stepper_slider.setMaxSpeed(sliderMillimetresToSteps(slider_slow_speed));
          Serial1.println(String("#v"));
        }
      }
      break;
    case INSTRUCTION_PAN_ACCEL_INCREMENT_DELAY: {
        pan_accel_increment_us = (Serial1CommandValueInt >= 0) ? Serial1CommandValueInt : 0;
        stepper_pan.setAcceleration(pan_accel_increment_us);
        Serial1.println(String("Pan accel delay: ") + pan_accel_increment_us + String(" steps/s²"));
      }
      break;
    case INSTRUCTION_TILT_ACCEL_INCREMENT_DELAY: {
        tilt_accel_increment_us = (Serial1CommandValueInt >= 0) ? Serial1CommandValueInt : 0;
        stepper_tilt.setAcceleration(tilt_accel_increment_us);
        Serial1.println(String("Tilt accel delay: ") + tilt_accel_increment_us + String(" steps/s²"));
      }
      break;
    case INSTRUCTION_SLIDER_ACCEL_INCREMENT_DELAY: {
        slider_accel_increment_us = (Serial1CommandValueInt >= 0) ? Serial1CommandValueInt : 0;
        stepper_slider.setAcceleration(slider_accel_increment_us);
        Serial1.println(String("Slider accel delay: ") + slider_accel_increment_us + String(" steps/s²"));
      }
      break;
    case INSTRUCTION_ACCEL_ENABLE: {
        toggleAcceleration();
      }
      break;
    case INSTRUCTION_SLIDER_MILLIMETRES: {
        //if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
        sliderMoveTo(Serial1CommandValueFloat);
        //}
      }
      break;
    case INSTRUCTION_INVERT_SLIDER: {
        invertSliderDirection(Serial1CommandValueInt);
      }
      break;
    case INSTRUCTION_INVERT_TILT: {
        invertTiltDirection(Serial1CommandValueInt);
      }
      break;
    case INSTRUCTION_INVERT_PAN: {
        invertPanDirection(Serial1CommandValueInt);
      }
      break;
    case INSTRUCTION_SAVE_TO_EEPROM: {
        saveEEPROM();
        Serial1.println(String("Saved to EEPROM"));
      }
      break;
    case INSTRUCTION_DEBUG_STATUS: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          debugReport();
        }
      }
      break;
    case INSTRUCTION_POSITION_STATUS: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          positionReport();
        }
      }
      break;
    case INSTRUCTION_PAN_DEGREES: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          panDegrees(Serial1CommandValueFloat);
        }
      }
      break;
    case INSTRUCTION_TILT_DEGREES: {
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          tiltDegrees(Serial1CommandValueFloat);
        }
      }
      break;
    case INSTRUCTION_ENABLE: {
        enableSteppers();
      }
      break;
    case INSTRUCTION_STEP_MODE: {
        setStepMode(Serial1CommandValueInt);
      }
      break;
    case INSTRUCTION_SET_PAN_SPEED: {
        Serial1.println(String("Max pan speed: ") + Serial1CommandValueFloat + String("º/s."));
        pan_max_speed = Serial1CommandValueFloat;
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          stepper_pan.setMaxSpeed(panDegreesToSteps(pan_max_speed));
        }
        Serial1.println(String("Max pan speed set as: ") + panDegreesToSteps(pan_max_speed) + String("\n\n"));
      }
      break;
    case INSTRUCTION_SET_TILT_SPEED: {
        Serial1.println(String("Max tilt speed: ") + Serial1CommandValueFloat + String("º/s."));
        tilt_max_speed = Serial1CommandValueFloat;
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          stepper_tilt.setMaxSpeed(tiltDegreesToSteps(tilt_max_speed));
        }
        Serial1.println(String("Max tilt speed set as: ") + tiltDegreesToSteps(tilt_max_speed) + String("\n\n"));
      }
      break;
    case INSTRUCTION_SET_SLIDER_SPEED: {
        Serial1.println(String("Max slider speed: ") + Serial1CommandValueFloat + String("mm/s."));
        slider_max_speed = Serial1CommandValueFloat;
        if (!multi_stepper.isRunning() && !step_stepperP.isRunning() && !rotate_stepperP.isRunning() && !step_stepperT.isRunning() && !rotate_stepperT.isRunning() && !step_stepperS.isRunning() && !rotate_stepperS.isRunning()) {
          stepper_slider.setMaxSpeed(sliderMillimetresToSteps(slider_max_speed));
        }
        Serial1.println(String("Max slider speed set as: ") + sliderMillimetresToSteps(slider_max_speed) + String("\n\n"));
      }
      break;
    case INSTRUCTION_CALCULATE_TARGET_POINT: {
        if (calculateTargetCoordinate()) {
          Serial1.println(String("Target:\tx: ") + intercept.x + String("\t"));
          Serial1.println(String("y: ") + intercept.y + String("\t"));
          Serial1.println(String("z: ") + intercept.z + String("mm\n"));
        }
      }
      break;
    case INSTRUCTION_ORIBIT_POINT: {
        if (calculateTargetCoordinate()) {
          interpolateTargetPoint(intercept, Serial1CommandValueInt);
        }
      }
      break;
    case INSTRUCTION_ZOOM_IN: {
        irsend.sendSony(0x2C9B, 12);
        delay(20);
        irsend.sendSony(0x2C9B, 12);
        delay(20);
        irsend.sendSony(0x2C9B, 12);
        delay(20);

        Serial1.println(String("Zoom IN"));
      }
      break;
    case INSTRUCTION_ZOOM_OUT: {
        irsend.sendSony(0x6C9B, 12);   // test with hi-fi 0x481  // camera zoom out 0x6C9B
        delay(20);
        irsend.sendSony(0x6C9B, 12);
        delay(20);
        irsend.sendSony(0x6C9B, 12);
        delay(20);

        Serial1.println(String("Zoom OUT"));
      }
      break;
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/


void mainLoop(void) {
  while (1) {
    if (Serial1.available()) Serial1Data();
  }
}


/*--------------------------------------------------------------------------------------------------------------------------------------------------------*/
