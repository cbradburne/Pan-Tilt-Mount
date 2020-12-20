/*
  Code adapted from isaac879 by Colin Bradburne
  
  To use a PS4 DualShock controller with the Pan-Tilt-Mount in stand-alone mode, this is what you’ll need.

  ESP32 Dev Kit board - like this one https://www.amazon.co.uk/gp/product/B071JR9WS9
  DualShock 4 controller

  You'll need to get your DualShock4's Bluetooth MAC Address.
  To get the MAC address use the program "SixaxisPairTool", https://dancingpixelstudios.com/sixaxis-controller/sixaxispairtool/.
  I've included the file as thier website seems to be down at the moment.

  I was able to use it on a Mac via a virtual machine running Windows 10 on Parallels Deskptop.
  Make sure you connect your DualShock4 to your computer via USB and not by BlueTooth.

  Wiring:

  NANO  --  12vPSU  --  ESP32

  GND---------GND---------GND
  Vin---------12v---------Vin
  TX----------------------RX0
  RX----------------------TX0

  Note: When programming either board, you must disconnect the link between TX and RX.
  Also, when programming the ESP32 via Arduino IDE, and when the IDE says "Connecting", press and hold the "BOOT" button on the ESP32 until the upload starts.

  When trying to connect your DualShock4 to your ESP32, press the PS button and if it doesn't connect keep trying, it can be a little temperamental :)
*/

#include <PS4Controller.h>

#define INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED 4
#define INPUT_DEADZONE 40

bool DEBUG = false;

float in_min = -127;          // PS4 DualShock analogue stick Far Left
float in_max = 127;           // PS4 DualShock analogue stick Far Right
float out_min = -255;
float out_max = 255;

float scaleSpeed = 1;
const float scaleSpeedFast = 1;
const float scaleSpeedSlow = 0.02;

short shortVals[3] = {0, 0, 0};
short LXShort = 0;
short RXShort = 0;
short RYShort = 0;
short oldShortVal0 = 0;
short oldShortVal1 = 0;
short oldShortVal2 = 0;

bool buttonUP = false;
bool buttonDOWN = false;
bool buttonLEFT = false;
bool buttonRIGHT = false;

bool buttonTRI = false;
bool buttonCIR = false;
bool buttonCRO = false;
bool buttonSQU = false;

bool buttonL1 = false;
bool buttonR1 = false;

bool buttonSH = false;
bool buttonOP = false;

bool firstRun = true;

long previousMillis = 0;
long currentMillis;
const int LED_Interval = 250;

#define LED 2

void setup()
{
  pinMode(LED, OUTPUT);
  Serial.begin(57600);
  PS4connect();
}

void PS4connect() {
  PS4.begin("8c:2d:aa:49:78:46");                       // **** insert your DualShock4 MAC address here ****
  while (!PS4.isConnected()) {
    currentMillis = millis();
    if (currentMillis - previousMillis > LED_Interval)
    {
      previousMillis = currentMillis;
      digitalWrite(LED, !(digitalRead(LED)));
    }
  }
}

void loop() {
  if (!PS4.isConnected()) {
    PS4connect();
  }

  if (PS4.isConnected()) {
    if (firstRun) {
      firstRun1();
    }
    else {

      float LX = (PS4.data.analog.stick.lx);            // Get left analog stick X value
      float LY = (PS4.data.analog.stick.ly);            // Get left analog stick Y value
      float RX = (PS4.data.analog.stick.rx);            // Get right analog stick X value
      float RY = (PS4.data.analog.stick.ry);            // Get right analog stick Y value

      //RX = ((RX - in_min) * (out_max - out_min) / ((in_max - in_min) + out_min));       // Note: "map" alternative

      LX = map(LX, in_min, in_max, out_min, out_max);   // Map DualShock values to (-255 to 255, FF)
      LY = map(LY, in_min, in_max, out_min, out_max);
      RX = map(RX, in_min, in_max, out_min, out_max);
      RY = map(RY, in_min, in_max, out_min, out_max);

      float magnitudeRX = sqrt(RX * RX);                // Get magnitude of Right stick movement to test for DeadZone
      float magnitudeRY = sqrt(RY * RY);                // Get magnitude of Right stick movement to test for DeadZone
      float magnitudeLX = sqrt(LX * LX);                // Get magnitude of Left stick movement to test for DeadZone

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

      if (magnitudeRX > INPUT_DEADZONE) {                                   // check if the controller is outside of the axis dead zone
        if (RX > 0 && (scaleSpeed == scaleSpeedSlow)) {                     // Scale output
          RXShort = map(RX, 0, in_max, 15, (out_max * (scaleSpeed * 4)));
        }
        else if (RX <= 0 || (scaleSpeed == scaleSpeedFast)) {
          RXShort = scaleSpeed * RX;
        }
      }
      else {
        RXShort = 0;                                                        // if in DeadZone, send 0, Don't move
      }

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

      if (magnitudeRY > INPUT_DEADZONE) {
        if (RY > 0 && (scaleSpeed == scaleSpeedSlow)) {
          RYShort = map(RY, 0, in_max, 15, (out_max * (scaleSpeed * 4)));
        }
        else if (RY <= 0 || (scaleSpeed == scaleSpeedFast)) {
          RYShort = scaleSpeed * RY;
        }
      }
      else {
        RYShort = 0;
      }

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

      if (magnitudeLX > INPUT_DEADZONE) {
        if (LX > 0 && (scaleSpeed == scaleSpeedSlow)) {
          LXShort = map(LX, 0, in_max, 15, (out_max * (scaleSpeed * 4)));
        }
        else if (LX <= 0 || (scaleSpeed == scaleSpeedFast)) {
          LXShort = scaleSpeed * LX;
        }
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

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

      if ( PS4.data.button.up && !buttonUP) {
        sendCharArray((char *)"[");                   // Up - First element
        buttonUP = true;
      }
      if ( PS4.data.button.down && !buttonDOWN) {
        sendCharArray((char *)"]");                   // Down - Last element
        buttonDOWN = true;
      }
      if ( PS4.data.button.left && !buttonLEFT) {
        sendCharArray((char *)"<");                   // Left - Step back
        buttonLEFT = true;
      }
      if ( PS4.data.button.right && !buttonRIGHT) {
        sendCharArray((char *)">");                   // Right - Step forwards
        buttonRIGHT = true;
      }

      if ( PS4.data.button.triangle && !buttonTRI) {
        sendCharArray((char *)";1");                  // Triangle - Execute moves array
        buttonTRI = true;
      }
      if ( PS4.data.button.circle && !buttonCIR) {
        sendCharArray((char *)"E");                   // Circle - Edit current position
        buttonCIR = true;
      }
      if ( PS4.data.button.cross && !buttonCRO) {
        sendCharArray((char *)"#");                   // Cross - Save current position as new keyframe
        buttonCRO = true;
      }
      if ( PS4.data.button.square && !buttonSQU) {
        sendCharArray((char *)"T");                   // Square - Calculate intercept point of first 2 keyframes
        buttonSQU = true;
      }

      if ( PS4.data.button.l1 && !buttonL1) {         // L1 - Set slow speed
        scaleSpeed = scaleSpeedSlow;
        buttonL1 = true;
      }
      if ( PS4.data.button.r1 && !buttonR1) {         // R1 - Set fast speed
        scaleSpeed = scaleSpeedFast;
        buttonR1 = true;
      }

      if ( PS4.data.button.share && !buttonSH) {
        sendCharArray((char *)"A");                   // Share - Home Axis
        buttonSH = true;
      }
      if ( PS4.data.button.options && !buttonOP) {
        sendCharArray((char *)"C");                   // Option - Clear Array
        buttonOP = true;
      }

      if ( !PS4.data.button.up && buttonUP)           // Button Release flags
        buttonUP = false;
      if ( !PS4.data.button.down && buttonDOWN)
        buttonDOWN = false;
      if ( !PS4.data.button.left && buttonLEFT)
        buttonLEFT = false;
      if ( !PS4.data.button.right && buttonRIGHT)
        buttonRIGHT = false;

      if ( !PS4.data.button.triangle && buttonTRI)
        buttonTRI = false;
      if ( !PS4.data.button.circle && buttonCIR)
        buttonCIR = false;
      if ( !PS4.data.button.cross && buttonCRO)
        buttonCRO = false;
      if ( !PS4.data.button.square && buttonSQU)
        buttonSQU = false;

      if ( !PS4.data.button.l1 && buttonL1)
        buttonL1 = false;
      if ( !PS4.data.button.r1 && buttonR1)
        buttonR1 = false;

      if ( !PS4.data.button.share && buttonSH)
        buttonSH = false;
      if ( !PS4.data.button.options && buttonOP)
        buttonOP = false;
    }
  }
}

void sendSliderPanTiltStepSpeed(int command, short * arr) {
  byte data[7];                           // Data array to send

  data[0] = command;
  data[1] = (arr[0] >> 4);                // Gets the most significant byte
  data[2] = (arr[0] & 0xF);               // Gets the second most significant byte
  data[3] = (arr[1] >> 4);
  data[4] = (arr[1] & 0xF);
  data[5] = (arr[2] >> 4);
  data[6] = (arr[2] & 0xF);               // Gets the least significant byte

  if ( DEBUG ) {
    Serial.print(data[0], HEX);
    Serial.print(data[1], HEX);
    Serial.print(data[2], HEX);
    Serial.print(data[3], HEX);
    Serial.print(data[4], HEX);
    Serial.print(data[5], HEX);
    Serial.println(data[6], HEX);
  }
  else {
    Serial.write(data, sizeof(data));     // Send the command and the 6 bytes of data
  }
  //return 0;                             // Non-ESP32
}

void sendCharArray(char *array) {
  //Serial.write(array, (int)strlen(array));

  int i = 0;
  while (array[i] != 0)
    Serial.write((uint8_t)array[i++]);    // Use with ESP32
  //Serial.write(array, sizeof(array));   // Non-ESP32
}

void firstRun1() {
  digitalWrite(LED, LOW);
  firstRun = false;
  PS4.setLed(255, 0, 0);
  PS4.setFlashRate(0, 0);
  PS4.setRumble(0, 0);
  PS4.sendToController();
  delay(250);
  PS4.setLed(0, 0, 0);
  PS4.setFlashRate(0, 0);
  PS4.setRumble(0, 0);
  PS4.sendToController();
  delay(250);
  PS4.setLed(255, 0, 0);
  PS4.setFlashRate(0, 0);
  PS4.setRumble(0, 0);
  PS4.sendToController();
  delay(250);
  PS4.setLed(0, 0, 0);
  PS4.setFlashRate(0, 0);
  PS4.setRumble(0, 0);
  PS4.sendToController();
  delay(250);
  PS4.setLed(0, 0, 255);
  PS4.setFlashRate(0, 0);
  PS4.setRumble(0, 0);
  PS4.sendToController();
  delay(250);
  if ( DEBUG ) {
    Serial.println("Controller Connected.");
  }
}
