/*
  Code adapted from isaac879 by Colin Bradburne.
  
  Big thanks to Tony McGuire for all his help testing the LANC control.

  To use a PS4 DualShock controller with the Pan-Tilt-Mount in stand-alone mode, this is what you’ll need.

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

  LANC Pins:
  cmdPin 5
  lancPin 18

  Note: When programming either board, you must disconnect the link between TX and RX.
  Also, when programming the ESP32 via Arduino IDE, and the IDE says "Connecting", press and hold the "BOOT" button on the ESP32 until the upload starts.

  When trying to connect your DualShock4 to your ESP32, press the PS button and if it doesn't connect keep trying, it can be a little temperamental :)

  Pan & Tilt                                        -       Right Stick
  Slider                                            -       L2 & R2 (Left and Right)

  Increase Slider Speed                             -       R1
  Decrease Slider Speed                             -       L1

  Set Slider to Max Speed                           -       R1 + R3
  Set Slider to Min Speed                           -       L1 + L3

  First element                                     -       D-Pad UP
  Last element                                      -       D-Pad DOWN
  Step back                                         -       D-Pad LEFT
  Step forwards                                     -       D-Pad RIGHT

  Clear Array                                       -       PS Button

  Execute moves array                               -       Triangle
  Edit current position                             -       Circle
  Save current position as new keyframe             -       Cross
  Calculate intercept point of first 2 keyframes    -       Square

  LANC Commands:
  lancCommand(REC)                                  -       TouchPad Button
  lancCommand(FOCUS_NEAR)                           -       Share Button
  lancCommand(FOCUS_FAR)                            -       Option Button
  
  Zoom speeds:
  lancCommand(ZOOM_OUT_0)                           -       Left Stick Down
  through
  lancCommand(ZOOM_OUT_7)

  lancCommand(ZOOM_IN_0)                            -       Left Stick Up
  through
  lancCommand(ZOOM_IN_7)

*/

#include <PS4Controller.h>

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

float in_min = -128;          // PS4 DualShock analogue stick Far Left
float in_max = 128;           // PS4 DualShock analogue stick Far Right
float out_min = -255;
float out_max = 255;

int Xspeed = 10;                                                            // Initial speed
int speedInc = 10;                                                          // Set for increment value
int minXspeed = 10;                                                         // Set to minimum X speed
int maxXspeed = 150;                                                        // Set to maximum X speed

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
bool buttonL2 = false;
bool buttonR2 = false;
bool buttonL3 = false;
bool buttonR3 = false;

bool l1andl3 = false;
bool r1andr3 = false;

bool buttonSH = false;
bool buttonOP = false;
bool buttonPS = false;
bool buttonTP = false;

bool firstRun = true;

//int L2 = 0;
//int R2 = 0;
int LYmapped = 0;
int zoomCase = 8;
int oldLY = 0;

long previousMillis = 0;
long currentMillis;
const int LED_Interval = 250;
char instruction = '0';

#define LED 2

//LANC
#define cmdPin 5
#define lancPin 18
int cmdRepeatCount;
int bitDuration = 104; //Duration of one LANC bit in microseconds.

//LANC commands byte 0 + byte 1

//Start-stop video recording
boolean REC[] = {LOW, LOW, LOW, HIGH, HIGH, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, LOW, LOW, HIGH, HIGH}; //18 33

//Zoom in from slowest to fastest speed
boolean ZOOM_IN_0[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW};    //28 00
boolean ZOOM_IN_1[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW};   //28 02
boolean ZOOM_IN_2[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, LOW};   //28 04
boolean ZOOM_IN_3[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, LOW};  //28 06
boolean ZOOM_IN_4[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, LOW, LOW};   //28 08
boolean ZOOM_IN_5[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, HIGH, LOW};  //28 0A
boolean ZOOM_IN_6[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, LOW, LOW};  //28 0C
boolean ZOOM_IN_7[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, LOW}; //28 0E

//Zoom out from slowest to fastest speed
boolean ZOOM_OUT_0[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, LOW, LOW, LOW};    //28 10
boolean ZOOM_OUT_1[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, LOW, HIGH, LOW};   //28 12
boolean ZOOM_OUT_2[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, HIGH, LOW, LOW};   //28 14
boolean ZOOM_OUT_3[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, LOW, HIGH, HIGH, LOW};  //28 16
boolean ZOOM_OUT_4[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, LOW, LOW, LOW};   //28 18
boolean ZOOM_OUT_5[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, LOW, HIGH, LOW};  //28 1A
boolean ZOOM_OUT_6[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, LOW, LOW};  //28 1C
boolean ZOOM_OUT_7[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, LOW, HIGH, HIGH, HIGH, HIGH, LOW}; //28 1E

//Focus control. Camera must be switched to manual focus
boolean FOCUS_NEAR[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, HIGH, LOW, LOW, LOW, HIGH, HIGH, HIGH}; //28 47
boolean FOCUS_FAR[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, HIGH, LOW, LOW, LOW, HIGH, LOW, HIGH};   //28 45

boolean FOCUS_AUTO[] = {LOW, LOW, HIGH, LOW, HIGH, LOW, LOW, LOW, LOW, HIGH, LOW, LOW, LOW, LOW, LOW, HIGH}; //28 41

//boolean POWER_OFF[] = {LOW,LOW,LOW,HIGH,HIGH,LOW,LOW,LOW,   LOW,HIGH,LOW,HIGH,HIGH,HIGH,HIGH,LOW}; //18 5E
//boolean POWER_ON[] = {LOW,LOW,LOW,HIGH,HIGH,LOW,LOW,LOW,   LOW,HIGH,LOW,HIGH,HIGH,HIGH,LOW,LOW}; //18 5C  Doesn't work because there's no power supply from the LANC port when the camera is off
//boolean POWER_OFF2[] = {LOW,LOW,LOW,HIGH,HIGH,LOW,LOW,LOW,   LOW,LOW,HIGH,LOW,HIGH,LOW,HIGH,LOW}; //18 2A Turns the XF300 off and then on again
//boolean POWER_SAVE[] = {LOW,LOW,LOW,HIGH,HIGH,LOW,LOW,LOW,   LOW,HIGH,HIGH,LOW,HIGH,HIGH,LOW,LOW}; //18 6C Didn't work


void setup()
{
  pinMode(lancPin, INPUT); //listens to the LANC line
  pinMode(cmdPin, OUTPUT); //writes to the LANC line

  digitalWrite(cmdPin, LOW);     //set LANC line to +5V
  delay(5000);                   //Wait for camera to power up completly
  bitDuration = bitDuration - 8; //Writing to the digital port takes about 8 microseconds so only 96 microseconds are left for each bit
  pinMode(LED, OUTPUT);
  Serial.begin(57600);
  PS4connect();
}

void PS4connect() {
  PS4.begin("8c:85:90:c1:00:43");                   //("8c:2d:aa:49:78:46");          // **** insert your DualShock4 MAC address here ****
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
      //float LX = (PS4.data.analog.stick.lx);            // Get left analog stick X value
      //float LY = (PS4.data.analog.stick.ly);            // Get left analog stick Y value
      float RX = (PS4.data.analog.stick.rx);            // Get right analog stick X value
      float RY = (PS4.data.analog.stick.ry);            // Get right analog stick Y value

      float L2 = (PS4.data.analog.button.l2);
      float R2 = (PS4.data.analog.button.r2);

      //RX = ((RX - in_min) * (out_max - out_min) / ((in_max - in_min) + out_min));       // Note: "map" alternative

      //LX = map(LX, in_min, in_max, out_min, out_max);   // Map DualShock values to (-255 to 255, FF)
      //LY = map(LY, in_min, in_max, out_min, out_max);
      RX = map(RX, in_min, in_max, out_min, out_max);
      RY = map(RY, in_min, in_max, out_min, out_max);

      L2 = map(L2, 0, 255, 0, out_min);
      R2 = map(R2, 0, 255, 0, out_max);
      float Z2 = L2 + R2;

      float magnitudeRX = sqrt(RX * RX);                // Get magnitude of Right stick movement to test for DeadZone
      float magnitudeRY = sqrt(RY * RY);                // Get magnitude of Right stick movement to test for DeadZone
      //float magnitudeLX = sqrt(LX * LX);                // Get magnitude of Left stick movement to test for DeadZone

      float magnitudeZ2 = sqrt(Z2 * Z2);

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

      if (magnitudeRX > INPUT_DEADZONE) {                                   // check if the controller is outside of the axis dead zone
        if (RX > 0) {
          RXShort = map(RX, INPUT_DEADZONE, out_max, 0, out_max);
        }
        else if (RX < 0) {
          RXShort = map(RX, -INPUT_DEADZONE, out_min, 0, out_min);
        }
      }
      else {
        RXShort = 0;                                                        // if in DeadZone, send 0, Don't move
      }

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/

      if (magnitudeRY > INPUT_DEADZONE) {
        if (RY > 0) {
          RYShort = map(RY, INPUT_DEADZONE, out_max, 0, out_max);
        }
        else if (RY < 0) {
          RYShort = map(RY, -INPUT_DEADZONE, out_min, 0, out_min);
        }
      }
      else {
        RYShort = 0;
      }

      /*------------------------------------------------------------------------------------------------------------------------------------------------------*/
      /*
            if (magnitudeLX > INPUT_DEADZONE) {
              if (LX > 0) {
                LXShort = map(LX, INPUT_DEADZONE, out_max, 0, out_max);
              }
              else if (LX < 0) {
                LXShort = map(LX, -INPUT_DEADZONE, out_min, 0, out_min);
              }
            }
            else {
              LXShort = 0;
            }
      */

      if (magnitudeZ2 > INPUT_DEADZONE) {
        if (Z2 > 0) {
          LXShort = map(Z2, INPUT_DEADZONE, out_max, 0, out_max);
        }
        else if (Z2 < 0) {
          LXShort = map(Z2, -INPUT_DEADZONE, out_min, 0, out_min);
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

      if ( PS4.data.button.l1 && !buttonL1) {                                       // L1 - decrease slider speed by 10
        Xspeed -= speedInc;
        if (Xspeed <= minXspeed) {
          Xspeed = minXspeed;                                                       // Limit Xspeed to minXspeed
        }
        char a[24] = "X";
        char tmp[6];
        sendCharArray((char *)(strcat(a, itoa(Xspeed, tmp, 10))));
        if ( DEBUG ) {
          Serial.print("L1 - X Speed: ");
          Serial.println(Xspeed);
        }
        buttonL1 = true;
      }
      if ( PS4.data.button.r1 && !buttonR1) {                                       // R1 - increase slider speed by 10
        Xspeed += speedInc;
        if (Xspeed >= maxXspeed) {
          Xspeed = maxXspeed;                                                       // Limit Xspeed to maxXspeed
        }
        char a[24] = "X";
        char tmp[6];
        sendCharArray((char *)(strcat(a, itoa(Xspeed, tmp, 10))));
        if ( DEBUG ) {
          Serial.print("R1 - X Speed: ");
          Serial.println(Xspeed);
        }
        buttonR1 = true;
      }
      if ( PS4.data.button.l1 && PS4.data.button.l3 && !l1andl3) {
        Xspeed = minXspeed;
        char a[24] = "X";
        char tmp[6];
        sendCharArray((char *)(strcat(a, itoa(Xspeed, tmp, 10))));               // Set Xspeed to minXspeed
        if ( DEBUG ) {
          Serial.print("L1 + L3 - X Speed: ");
          Serial.println(minXspeed);
        }
        l1andl3 = true;
      }
      if ( PS4.data.button.r1 && PS4.data.button.r3 && !r1andr3) {
        Xspeed = maxXspeed;
        char a[24] = "X";
        char tmp[6];
        sendCharArray((char *)(strcat(a, itoa(Xspeed, tmp, 10))));               // Set Xspeed to maxXspeed
        if ( DEBUG ) {
          Serial.print("R1 + R3 - X Speed: ");
          Serial.println(maxXspeed);
        }
        r1andr3 = true;
      }

      if ( PS4.data.button.share && !buttonSH) {
        lancCommand(FOCUS_NEAR);
        //sendCharArray((char *)"A");                   // Share - Home Axis
        buttonSH = true;
      }
      if ( PS4.data.button.options && !buttonOP) {
        lancCommand(FOCUS_FAR);
        //sendCharArray((char *)"C");                   // Option - Clear Array
        buttonOP = true;
      }

      if ( PS4.data.button.ps && !buttonPS) {
        if ( DEBUG ) {
          Serial.println("PS Button");
        }
        sendCharArray((char *)"C");                   // Option - Clear Array
        buttonPS = true;
      }
      if ( PS4.data.button.touchpad  && !buttonTP) {
        if ( DEBUG ) {
          Serial.println("Touch Pad Button");
        }
        lancCommand(REC);
        buttonTP = true;
      }

      int LY = (PS4.data.analog.stick.ly);
      float magnitudeLY = sqrt(LY * LY);

      if (magnitudeLY > INPUT_DEADZONE) {
        if (LY > 0) {
          LYmapped = map(LY, INPUT_DEADZONE, 127, 8, 16);
        }
        else if (LY < 0) {
          LYmapped = map(LY, -INPUT_DEADZONE, -128, 8, 0);
        }
      }
      else {
        LYmapped = 8;
      }

      if (LYmapped != zoomCase) {
        if ( DEBUG ) {
          Serial.print("LYmapped - ");
          Serial.println(LYmapped);
          zoomCase = LYmapped;
        }

        if (LYmapped == 0) {
          lancCommand(ZOOM_OUT_7);
          zoomCase = 0;
        }
        else if (LYmapped == 1) {
          lancCommand(ZOOM_OUT_6);
          zoomCase = 1;
        }
        else if (LYmapped == 2) {
          lancCommand(ZOOM_OUT_5);
          zoomCase = 2;
        }
        else if (LYmapped == 3) {
          lancCommand(ZOOM_OUT_4);
          zoomCase = 3;
        }
        else if (LYmapped == 4) {
          lancCommand(ZOOM_OUT_3);
          zoomCase = 4;
        }
        else if (LYmapped == 5) {
          lancCommand(ZOOM_OUT_2);
          zoomCase = 5;
        }
        else if (LYmapped == 6) {
          lancCommand(ZOOM_OUT_1);
          zoomCase = 6;
        }
        else if (LYmapped == 7) {
          lancCommand(ZOOM_OUT_0);
          zoomCase = 7;
        }
        else if (LYmapped == 8) {
          //                                      DO NOTHING!
          zoomCase = 8;
        }
        else if (LYmapped == 9) {
          lancCommand(ZOOM_IN_0);
          zoomCase = 9;
        }
        else if (LYmapped == 10) {
          lancCommand(ZOOM_IN_1);
          zoomCase = 10;
        }
        else if (LYmapped == 11) {
          lancCommand(ZOOM_IN_2);
          zoomCase = 11;
        }
        else if (LYmapped == 12) {
          lancCommand(ZOOM_IN_3);
          zoomCase = 12;
        }
        else if (LYmapped == 13) {
          lancCommand(ZOOM_IN_4);
          zoomCase = 13;
        }
        else if (LYmapped == 14) {
          lancCommand(ZOOM_IN_5);
          zoomCase = 14;
        }
        else if (LYmapped == 15) {
          lancCommand(ZOOM_IN_6);
          zoomCase = 15;
        }
        else if (LYmapped == 16) {
          lancCommand(ZOOM_IN_7);
          zoomCase = 16;
        }
      }

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

    if ( !PS4.data.button.l1 && !PS4.data.button.l3 && l1andl3)
      l1andl3 = false;
    if ( !PS4.data.button.r1 && !PS4.data.button.r3 && r1andr3)
      r1andr3 = false;

    if ( !PS4.data.button.ps && buttonPS)
      buttonPS = false;
    if ( !PS4.data.button.touchpad && buttonTP)
      buttonTP = false;
    if ( !PS4.data.button.l2 && buttonL2)
      buttonL2 = false;
    if ( !PS4.data.button.r2 && buttonR2)
      buttonR2 = false;
  }
  /*                                        // Experimental - Flash if Nano received data
    if (Serial.available() > 0) {
    instruction = Serial.read();
    }
    switch (instruction) {
    case 'a': {                             // Set Keyframe
        PS4.setLed(rS, gS, bS);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rN, gN, bN);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rS, gS, bS);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rN, gN, bN);
        PS4.sendToController();
        if ( DEBUG ) {
          Serial.println("Key Frame Set");
        }
        instruction = '0';
      }
      break;
    case 'b': {                             // Clear All Keyframes
        PS4.setLed(rC, gC, bC);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rN, gN, bN);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rC, gC, bC);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rN, gN, bN);
        PS4.sendToController();
        if ( DEBUG ) {
          Serial.println("Clear All Key Frame");
        }
        instruction = '0';
      }
      break;
    case 'c': {                             // Set first 2 keyframes to tangent point
        PS4.setLed(rT, gT, bT);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rN, gN, bN);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rT, gT, bT);
        PS4.sendToController();
        delay(100);
        PS4.setLed(rN, gN, bN);
        PS4.sendToController();
        if ( DEBUG ) {
          Serial.println("Calculate Tangent from first 2 Key Frames");
        }
        instruction = '0';
      }
      break;
    }
  */

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
  PS4.setLed(255, 0, 0);
  PS4.sendToController();
  delay(100);
  PS4.setLed(0, 0, 0);
  PS4.sendToController();
  delay(100);
  PS4.setLed(255, 0, 0);
  PS4.sendToController();
  delay(100);
  PS4.setLed(0, 0, 0);
  PS4.sendToController();
  delay(100);
  PS4.setLed(rN, gN, bN);
  PS4.sendToController();
  delay(300);
  if ( DEBUG ) {
    Serial.println("\n\n");
    Serial.println("Controller Connected.");
  }
}

void lancCommand(boolean lancBit[])
{

  cmdRepeatCount = 0;

  while (cmdRepeatCount < 5)
  { //repeat 5 times to make sure the camera accepts the command

    while (pulseIn(lancPin, HIGH) < 5000)
    {
      //"pulseIn, HIGH" catches any 0V TO +5V TRANSITION and waits until the LANC line goes back to 0V
      //"pulseIn" also returns the pulse duration so we can check if the previous +5V duration was long enough (>5ms) to be the pause before a new 8 byte data packet
      //Loop till pulse duration is >5ms
    }

    //LOW after long pause means the START bit of Byte 0 is here
    delayMicroseconds(bitDuration); //wait START bit duration

    //Write the 8 bits of byte 0
    //Note that the command bits have to be put out in reverse order with the least significant, right-most bit (bit 0) first
    for (int i = 7; i > -1; i--)
    {
      digitalWrite(cmdPin, lancBit[i]); //Write bits.
      delayMicroseconds(bitDuration);
    }

    //Byte 0 is written now put LANC line back to +5V
    digitalWrite(cmdPin, LOW);
    delayMicroseconds(10); //make sure to be in the stop bit before byte 1

    while (digitalRead(lancPin))
    {
      //Loop as long as the LANC line is +5V during the stop bit
    }

    //0V after the previous stop bit means the START bit of Byte 1 is here
    delayMicroseconds(bitDuration); //wait START bit duration

    //Write the 8 bits of Byte 1
    //Note that the command bits have to be put out in reverse order with the least significant, right-most bit (bit 0) first
    for (int i = 15; i > 7; i--)
    {
      digitalWrite(cmdPin, lancBit[i]); //Write bits
      delayMicroseconds(bitDuration);
    }

    //Byte 1 is written now put LANC line back to +5V
    digitalWrite(cmdPin, LOW);

    cmdRepeatCount++; //increase repeat count by 1

    /*Control bytes 0 and 1 are written, now don’t care what happens in Bytes 2 to 7
      and just wait for the next start bit after a long pause to send the first two command bytes again.*/

  } //While cmdRepeatCount < 5
}
