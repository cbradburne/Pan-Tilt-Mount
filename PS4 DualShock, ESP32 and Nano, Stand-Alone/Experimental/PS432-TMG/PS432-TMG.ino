/*
  Code adapted from isaac879 by Colin Bradburne

  Requested edition:
  Initial speed set to value of "Xspeed",
  L1 decreasing slider speed only by value of "speedInc",
  R1 increasing slider speed only by value of "speedInc",
  L1 & L3 pressed together sets speed to value of "minXspeed",
  R1 & R3 pressed together sets speed to value of "maxXspeed".

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

  Note: When programming either board, you must disconnect the link between TX and RX.
  Also, when programming the ESP32 via Arduino IDE, and the IDE says "Connecting", press and hold the "BOOT" button on the ESP32 until the upload starts.

  When trying to connect your DualShock4 to your ESP32, press the PS button and if it doesn't connect keep trying, it can be a little temperamental :)
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
bool l1andl3 = false;
bool r1andr3 = false;

bool buttonSH = false;
bool buttonOP = false;

bool firstRun = true;

bool onceonly = false;

long previousMillis = 0;
long currentMillis;
const int LED_Interval = 250;
char instruction = '0';

#define LED 2

void setup()
{
  pinMode(LED, OUTPUT);
  Serial.begin(57600);
  PS4connect();
}

void PS4connect() {
  PS4.begin("8c:85:90:c1:00:43");                       // **** insert your DualShock4 MAC address here ****
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
/*
      if ( DEBUG ) {
        Serial.print("LX: ");
        Serial.println(LX);
      }
*/
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
        sendCharArray((char *)"A");                   // Share - Home Axis
        buttonSH = true;
      }
      if ( PS4.data.button.options && !buttonOP) {
        sendCharArray((char *)"C");                   // Option - Clear Array
        buttonOP = true;
      }




      /* ----------------------------------------------- Button Release flags ----------------------------------------------- */




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

      if ( !PS4.data.button.l1 && !PS4.data.button.l3 && l1andl3)
        l1andl3 = false;
      if ( !PS4.data.button.r1 && !PS4.data.button.r3 && r1andr3)
        r1andr3 = false;

      if ( !PS4.data.button.share && buttonSH)
        buttonSH = false;
      if ( !PS4.data.button.options && buttonOP)
        buttonOP = false;
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
}

void sendSliderPanTiltStepSpeed(int command, short * arr) {
  byte data[7];                               // Data array to send

  data[0] = command;
  data[1] = (arr[0] >> 8);                    // Gets the most significant byte
  data[2] = (arr[0] & 0xFF);                  // Gets the second most significant byte
  data[3] = (arr[1] >> 8);
  data[4] = (arr[1] & 0xFF);
  data[5] = (arr[2] >> 8);
  data[6] = (arr[2] & 0xFF);                  // Gets the least significant byte

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
  int i = 0;
  if ( DEBUG ) {
    while (array[i] != 0) {
      Serial.print((uint8_t)array[i++]);
    }
    Serial.println("");
  }
  else {
    while (array[i] != 0) {
      Serial.write((uint8_t)array[i++]);    // Use with ESP32
    }
  }

  //Serial.write(array, (int)strlen(array));  // ??
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
