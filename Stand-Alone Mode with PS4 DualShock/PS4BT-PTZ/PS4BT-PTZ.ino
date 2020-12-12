/*
  Example sketch for the PS4 Bluetooth library - developed by Kristian Lauszus
  For more information visit my blog: http://blog.tkjelectronics.dk/ or
  send me an e-mail:  kristianl@tkjelectronics.com

  Partial code written by isaac879
  Adapted for PS4 by Colin Bradburne
*/

#include <PS4BT.h>
#include <usbhub.h>

// Satisfy the IDE, which needs to see the include statment in the ino too.
#ifdef dobogusinclude
#include <spi4teensy3.h>
#endif
#include <SPI.h>

#define INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED 4

#define INPUT_DEADZONE 40

#define MAXIMUM_PAN_STEP_SPEED 1130.0     //steps per second
#define MAXIMUM_TILT_STEP_SPEED 410.0
#define MAXIMUM_SLIDER_STEP_SPEED 900.0

USB Usb;
//USBHub Hub1(&Usb); // Some dongles have a hub inside
BTD Btd(&Usb); // You have to create the Bluetooth Dongle instance like so

/* You can create the instance of the PS4BT class in two ways */
// This will start an inquiry and then pair with the PS4 controller - you only have to do this once
// You will need to hold down the PS and Share button at the same time, the PS4 controller will then start to blink rapidly indicating that it is in pairing mode
PS4BT PS4(&Btd, PAIR);

// After that you can simply create the instance like so and then press the PS button on the device
//PS4BT PS4(&Btd);

bool printAngle, printTouch;
uint8_t oldL2Value, oldR2Value;

float in_min = 0;         // PS4 DualShock analogue stick Far Left
float in_max = 255;       // PS4 DualShock analogue stick Far Right
float out_min = -255;
float out_max = 255;

short shortVals[3] = {0, 0, 0};
short LXShort = 0;
short RXShort = 0;
short RYShort = 0;
short oldShortVal0 = 0;
short oldShortVal1 = 0;
short oldShortVal2 = 0;

void setup() {
  Serial.begin(57600); //115200
#if !defined(__MIPSEL__)
  while (!Serial); // Wait for serial port to connect - used on Leonardo, Teensy and other boards with built-in USB CDC serial connection
#endif
  if (Usb.Init() == -1) {
    Serial.print(F("\r\nOSC did not start"));
    while (1); // Halt
  }
  //Serial.print(F("\r\nPS4 Bluetooth Library Started"));
}

void loop() {
  Usb.Task();

  if (PS4.connected()) {

    float LX = (PS4.getAnalogHat(LeftHatX));          // Get left analog stick X value (0 to 255, Left to Right)
    float LY = (PS4.getAnalogHat(LeftHatY));          // Get left analog stick Y value
    float RX = (PS4.getAnalogHat(RightHatX));         // Get right analog stick X value
    float RY = (PS4.getAnalogHat(RightHatY));         // Get right analog stick Y value

    //RX = ((RX - in_min) * (out_max - out_min) / ((in_max - in_min) + out_min));

    LX = map(LX, in_min, in_max, out_min, out_max);   // Map DualShock values to (-255 to 255)
    LY = map(LY, in_min, in_max, out_min, out_max);
    RX = map(RX, in_min, in_max, out_min, out_max);
    RY = map(RY, in_min, in_max, out_min, out_max);

    float magnitudeRX = sqrt(RX * RX);                // Get magnitude of Right stick movement to test for DeadZone
    float magnitudeRY = sqrt(RY * RY);                // Get magnitude of Right stick movement to test for DeadZone
    float magnitudeLX = sqrt(LX * LX);                // Get magnitude of Left stick movement to test for DeadZone

    /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

    if (magnitudeRX > INPUT_DEADZONE) {               // check if the controller is outside a circular dead zone
      RXShort = RX;
    }
    else {
      RXShort = 0;                                    // if in DeadZone, send 0, Don't move
    }

    /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

    if (magnitudeRY > INPUT_DEADZONE) {
      RYShort = RY;
    }
    else {
      RYShort = 0;
    }

    /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

    if (magnitudeLX > INPUT_DEADZONE) {
      LXShort = LX;
    }
    else {
      LXShort = 0;
    }

    /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

    shortVals[0] = LXShort;
    shortVals[1] = RXShort;
    shortVals[2] = RYShort;

    if (shortVals[0] != oldShortVal0 || shortVals[1] != oldShortVal1 || shortVals[2] != oldShortVal2) {   // IF input has changed
      sendSliderPanTiltStepSpeed(INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED, shortVals);                     // Send the combned values
      
      oldShortVal0 = shortVals[0];      // Store as old values
      oldShortVal1 = shortVals[1];      // Store as old values
      oldShortVal2 = shortVals[2];      // Store as old values
      
      delay(20);
    }

    if (PS4.getButtonClick(UP)) {
      sendCharArray((char *)"@");       //Up first element
    }
    if (PS4.getButtonClick(DOWN)) {
      sendCharArray((char *)"Z");       //down last element
    }
    if (PS4.getButtonClick(LEFT)) {
      sendCharArray((char *)"<");       //left step back
    }
    if (PS4.getButtonClick(RIGHT)) {
      sendCharArray((char *)">");       //right step forwards
    }
    if (PS4.getButtonClick(SHARE)) {
      sendCharArray((char *)"A");       //Menu home
    }
    if (PS4.getButtonClick(OPTIONS)) {
      sendCharArray((char *)";1");      //views execute
    }
    if (PS4.getButtonClick(TRIANGLE)) {
      sendCharArray((char *)"#");       //A save position
    }
    if (PS4.getButtonClick(CIRCLE)) {
      sendCharArray((char *)"C");       //B clear array
    }
    if (PS4.getButtonClick(CROSS)) {
      sendCharArray((char *)"E");       //X edit position
    }
    if (PS4.getButtonClick(SQUARE)) {
      sendCharArray((char *)"R");       //Y status
    }
  }
}

void sendSliderPanTiltStepSpeed(int command, short *arr) {
  byte data[7];                         //Data array to send

  data[0] = command;
  data[1] = (arr[0] >> 4);              //Gets the most significant byte
  data[2] = (arr[0] & 0xF);             //Gets the second most significant byte
  data[3] = (arr[1] >> 4);
  data[4] = (arr[1] & 0xF);
  data[5] = (arr[2] >> 4);
  data[6] = (arr[2] & 0xF);             //Gets the least significant byte

  Serial.write(data, sizeof(data));     //Send the command and the 6 bytes of data

  /*//                            FOR TESTING
    Serial.print(data[0], HEX);
    Serial.print(data[1], HEX);
    Serial.print(data[2], HEX);
    Serial.print(data[3], HEX);
    Serial.print(data[4], HEX);
    Serial.print(data[5], HEX);
    Serial.println(data[6], HEX);
  */
  return 0;
}

void sendCharArray(char *array) {
  Serial.write(array, (int)strlen(array));
}
