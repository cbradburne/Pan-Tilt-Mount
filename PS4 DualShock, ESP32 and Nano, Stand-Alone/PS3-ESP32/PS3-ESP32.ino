/*
  Code adapted from isaac879 by Colin Bradburne

  To use a Ps3 DualShock controller with the Pan-Tilt-Mount in stand-alone mode, this is what you’ll need.

  ESP32 Dev Kit board - like this one https://www.amazon.co.uk/gp/product/B071JR9WS9
  DualShock 4 controller

  install ESP32 boards into Arduino IDE, follow this guide:
  https://www.hackster.io/abdularbi17/how-to-install-esp32-board-in-arduino-ide-1cd571

  NOTE: Thanks to YouTuber kingjust627, it's been noted that ESP32 DevKitC is incompatible with the code. 
  ALSO, you need to install version 1.0.4 of the ESP32 library in the Arduino board manager.

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
  Also, when programming the ESP32 via Arduino IDE, and the IDE says "Connecting", press and hold the "BOOT" button on the ESP32 until the upload starts.

  When trying to connect your DualShock4 to your ESP32, press the PS button and if it doesn't connect keep trying, it can be a little temperamental :)
*/

#include <Ps3Controller.h>

#define INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED 4
#define INPUT_DEADZONE 40

bool DEBUG = false;

int rN = 0;                   // Normal colours (when connected)
int gN = 0;
int bN = 255;

int rS = 0;                   // Colours when 'Set Keyframe' complete
int gS = 255;
int bS = 0;

int rC = 255;                 // Colours when 'Clear All Keyframes' complete
int gC = 255;
int bC = 0;

int rT = 150;                 // Colours when 'Tangent' complete
int gT = 150;
int bT = 0;

float in_min = -127;          // Ps3 DualShock analogue stick Far Left
float in_max = 127;           // Ps3 DualShock analogue stick Far Right
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
char instruction = '0';

#define LED 2

void setup()
{
  pinMode(LED, OUTPUT);
  Serial.begin(57600);
  Ps3connect();
}

void Ps3connect() {
  Ps3.begin("e8:9e:b4:a9:3b:74");                   //("8c:2d:aa:49:78:46");          // **** insert your DualShock4 MAC address here ****
  while (!Ps3.isConnected()) {
    currentMillis = millis();
    if (currentMillis - previousMillis > LED_Interval)
    {
      previousMillis = currentMillis;
      digitalWrite(LED, !(digitalRead(LED)));
    }
  }
}

void loop() {
  if (!Ps3.isConnected()) {
    Ps3connect();
  }

  if (Ps3.isConnected()) {
    if (firstRun) {
      firstRun1();
    }
    else {

      float LX = (Ps3.data.analog.stick.lx);            // Get left analog stick X value
      float LY = (Ps3.data.analog.stick.ly);            // Get left analog stick Y value
      float RX = (Ps3.data.analog.stick.rx);            // Get right analog stick X value
      float RY = (Ps3.data.analog.stick.ry);            // Get right analog stick Y value

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
          RYShort = map(RY, 0, in_max, 15, (out_max * (scaleSpeed * 4)));   // Compensate for no movement between 00 & 0F
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
          LXShort = map(LX, 0, in_max, 15, (out_max * (scaleSpeed * 4)));   // Compensate for no movement between 00 & 0F
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

      if ( Ps3.data.button.up && !buttonUP) {
        sendCharArray((char *)"[");                   // Up - First element
        buttonUP = true;
      }
      if ( Ps3.data.button.down && !buttonDOWN) {
        sendCharArray((char *)"]");                   // Down - Last element
        buttonDOWN = true;
      }
      if ( Ps3.data.button.left && !buttonLEFT) {
        sendCharArray((char *)"<");                   // Left - Step back
        buttonLEFT = true;
      }
      if ( Ps3.data.button.right && !buttonRIGHT) {
        sendCharArray((char *)">");                   // Right - Step forwards
        buttonRIGHT = true;
      }

      if ( Ps3.data.button.triangle && !buttonTRI) {
        sendCharArray((char *)";1");                  // Triangle - Execute moves array
        buttonTRI = true;
      }
      if ( Ps3.data.button.circle && !buttonCIR) {
        sendCharArray((char *)"E");                   // Circle - Edit current position
        buttonCIR = true;
      }
      if ( Ps3.data.button.cross && !buttonCRO) {
        sendCharArray((char *)"#");                   // Cross - Save current position as new keyframe
        buttonCRO = true;
      }
      if ( Ps3.data.button.square && !buttonSQU) {
        sendCharArray((char *)"T");                   // Square - Calculate intercept point of first 2 keyframes
        buttonSQU = true;
      }

      if ( Ps3.data.button.l1 && !buttonL1) {         // L1 - Set slow speed
        scaleSpeed = scaleSpeedSlow;
        if ( DEBUG ) {
          Serial.println("L1");
        }
        buttonL1 = true;
      }
      if ( Ps3.data.button.r1 && !buttonR1) {         // R1 - Set fast speed
        scaleSpeed = scaleSpeedFast;
        if ( DEBUG ) {
          Serial.println("R1");
        }
        buttonR1 = true;
      }

      if ( Ps3.data.button.select && !buttonSH) {
        sendCharArray((char *)"A");                   // Share - Home Axis
        buttonSH = true;
      }
      if ( Ps3.data.button.start && !buttonOP) {
        sendCharArray((char *)"C");                   // Option - Clear Array
        buttonOP = true;
      }

      if ( !Ps3.data.button.up && buttonUP)           // Button Release flags
        buttonUP = false;
      if ( !Ps3.data.button.down && buttonDOWN)
        buttonDOWN = false;
      if ( !Ps3.data.button.left && buttonLEFT)
        buttonLEFT = false;
      if ( !Ps3.data.button.right && buttonRIGHT)
        buttonRIGHT = false;

      if ( !Ps3.data.button.triangle && buttonTRI)
        buttonTRI = false;
      if ( !Ps3.data.button.circle && buttonCIR)
        buttonCIR = false;
      if ( !Ps3.data.button.cross && buttonCRO)
        buttonCRO = false;
      if ( !Ps3.data.button.square && buttonSQU)
        buttonSQU = false;

      if ( !Ps3.data.button.l1 && buttonL1)
        buttonL1 = false;
      if ( !Ps3.data.button.r1 && buttonR1)
        buttonR1 = false;

      if ( !Ps3.data.button.select && buttonSH)
        buttonSH = false;
      if ( !Ps3.data.button.start && buttonOP)
        buttonOP = false;
    }
    /*                                        // Experimental - Flash if Nano received data
    if (Serial.available() > 0) {
      instruction = Serial.read();
    }
    switch (instruction) {
      case 'a': {                             // Set Keyframe
          Ps3.setLed(rS, gS, bS);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rN, gN, bN);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rS, gS, bS);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rN, gN, bN);
          Ps3.sendToController();
          if ( DEBUG ) {
            Serial.println("Key Frame Set");
          }
          instruction = '0';
        }
        break;
      case 'b': {                             // Clear All Keyframes
          Ps3.setLed(rC, gC, bC);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rN, gN, bN);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rC, gC, bC);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rN, gN, bN);
          Ps3.sendToController();
          if ( DEBUG ) {
            Serial.println("Clear All Key Frame");
          }
          instruction = '0';
        }
        break;
      case 'c': {                             // Set first 2 keyframes to tangent point
          Ps3.setLed(rT, gT, bT);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rN, gN, bN);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rT, gT, bT);
          Ps3.sendToController();
          delay(100);
          Ps3.setLed(rN, gN, bN);
          Ps3.sendToController();
          if ( DEBUG ) {
            Serial.println("Calculate Tangent from first 2 Key Frames");
          }
          instruction = '0';
        }
        break;
    }
    */
  }
}

void sendSliderPanTiltStepSpeed(int command, short * arr) {
  byte data[7];                           // Data array to send

  data[0] = command;
  data[1] = (arr[0] >> 8);                // Gets the most significant byte
  data[2] = (arr[0] & 0xFF);               // Gets the second most significant byte
  data[3] = (arr[1] >> 8);
  data[4] = (arr[1] & 0xFF);
  data[5] = (arr[2] >> 8);
  data[6] = (arr[2] & 0xFF);               // Gets the least significant byte

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
  //Ps3.setLed(255, 0, 0);
  //Ps3.sendToController();
  //delay(100);
  //Ps3.setLed(0, 0, 0);
  //Ps3.sendToController();
  //delay(100);
  //Ps3.setLed(255, 0, 0);
  //Ps3.sendToController();
  //delay(100);
  //Ps3.setLed(0, 0, 0);
  //Ps3.sendToController();
  //delay(100);
  //Ps3.setLed(rN, gN, bN);
  //Ps3.sendToController();
  //delay(300);
  Ps3.setPlayer(1);
  if ( DEBUG ) {
    Serial.println("\n\n");
    Serial.println("Controller Connected.");
  }
}
