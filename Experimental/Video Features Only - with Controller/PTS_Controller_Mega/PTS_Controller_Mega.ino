#define INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED 4

bool DEBUG = false;

const int XdeadRangeLow  = 512 - 60;
const int XdeadRangeHigh = 512 + 60;
const int YdeadRangeLow  = 512 - 60;
const int YdeadRangeHigh = 512 + 60;
const int ZdeadRangeLow  = 512 - 5;
const int ZdeadRangeHigh = 512 + 5;

const int ledPin1r = 27;
const int ledPin1g = 25;
const int swPin1r = 23;
const int swPin1s = 29;

const int ledPin2r = 35;
const int ledPin2g = 33;
const int swPin2r = 31;
const int swPin2s = 37;

const int ledPin3r = 43;
const int ledPin3g = 41;
const int swPin3r = 39;
const int swPin3s = 45;

const int ledPin4r = 26;
const int ledPin4g = 24;
const int swPin4r = 22;
const int swPin4s = 28;

const int ledPin5r = 34;
const int ledPin5g = 32;
const int swPin5r = 30;
const int swPin5s = 36;

const int ledPin6r = 42;
const int ledPin6g = 40;
const int swPin6r = 38;
const int swPin6s = 44;

const int ledPinSlow = 47;
const int ledPinFast = 51;
const int swPinSlow = 49;
const int swPinFast = 53;

//const int ledPinLeft = 46;
//const int ledPinRight = 50;
const int swPinLeft = 48;
const int swPinRight = 52;

const int swPinZoomIn = 46;
const int swPinZoomOut = 50;

int reading1;
int reading2;
int reading3;
int reading4;
int reading5;
int reading6;
int reading7;
int reading8;
int reading9;
int reading10;
int reading11;
int reading12;
int reading13;
int reading14;
int reading15;
int reading16;
int reading17;
int reading18;

bool pos1set = false;
bool pos2set = false;
bool pos3set = false;
bool pos4set = false;
bool pos5set = false;
bool pos6set = false;

bool pos1run = false;
bool pos2run = false;
bool pos3run = false;
bool pos4run = false;
bool pos5run = false;
bool pos6run = false;

bool speedFast = true;
bool speedFastSet = true;

bool notMoving = true;
bool sliderPressed = false;

bool zoomPressed = false;
bool notZooming = true;

int buttonState1;
int buttonState2;
int buttonState3;
int buttonState4;
int buttonState5;
int buttonState6;
int buttonState7;
int buttonState8;
int buttonState9;
int buttonState10;
int buttonState11;
int buttonState12;
int buttonState13;
int buttonState14;
int buttonState15;
int buttonState16;
int buttonState17;
int buttonState18;

int lastButtonState1 = HIGH;
int lastButtonState2 = HIGH;
int lastButtonState3 = HIGH;
int lastButtonState4 = HIGH;
int lastButtonState5 = HIGH;
int lastButtonState6 = HIGH;
int lastButtonState7 = HIGH;
int lastButtonState8 = HIGH;
int lastButtonState9 = HIGH;
int lastButtonState10 = HIGH;
int lastButtonState11 = HIGH;
int lastButtonState12 = HIGH;
int lastButtonState13 = HIGH;
int lastButtonState14 = HIGH;
int lastButtonState15 = HIGH;
int lastButtonState16 = HIGH;
int lastButtonState17 = HIGH;
int lastButtonState18 = HIGH;

unsigned long lastDebounceTime1 = 0;
unsigned long lastDebounceTime2 = 0;
unsigned long lastDebounceTime3 = 0;
unsigned long lastDebounceTime4 = 0;
unsigned long lastDebounceTime5 = 0;
unsigned long lastDebounceTime6 = 0;
unsigned long lastDebounceTime7 = 0;
unsigned long lastDebounceTime8 = 0;
unsigned long lastDebounceTime9 = 0;
unsigned long lastDebounceTime10 = 0;
unsigned long lastDebounceTime11 = 0;
unsigned long lastDebounceTime12 = 0;
unsigned long lastDebounceTime13 = 0;
unsigned long lastDebounceTime14 = 0;
unsigned long lastDebounceTime15 = 0;
unsigned long lastDebounceTime16 = 0;
unsigned long lastDebounceTime17 = 0;
unsigned long lastDebounceTime18 = 0;

unsigned long debounceDelay = 10;

short shortVals[3] = {0, 0, 0};
short XShort = 0;
short YShort = 0;
short ZShort = 0;
short oldShortVal0 = 0;
short oldShortVal1 = 0;
short oldShortVal2 = 0;

int X_max = 1023;
int Y_max = 1023;
int Z_max = 1023;

int out_min = -254;
int out_max = 254;

int joyXread;
int joyX;
int joyYread;
int joyY;
int joyZread;
int joyZ;

void setup() {
  //Serial.begin(115200);
  //Serial3.begin(115200);
  Serial.begin(38400);
  Serial3.begin(38400);

  pinMode(ledPin1r, OUTPUT);
  pinMode(ledPin1g, OUTPUT);
  pinMode(swPin1s, INPUT_PULLUP);
  pinMode(swPin1r, INPUT_PULLUP);

  pinMode(ledPin2r, OUTPUT);
  pinMode(ledPin2g, OUTPUT);
  pinMode(swPin2s, INPUT_PULLUP);
  pinMode(swPin2r, INPUT_PULLUP);

  pinMode(ledPin3r, OUTPUT);
  pinMode(ledPin3g, OUTPUT);
  pinMode(swPin3s, INPUT_PULLUP);
  pinMode(swPin3r, INPUT_PULLUP);

  pinMode(ledPin4r, OUTPUT);
  pinMode(ledPin4g, OUTPUT);
  pinMode(swPin4s, INPUT_PULLUP);
  pinMode(swPin4r, INPUT_PULLUP);

  pinMode(ledPin5r, OUTPUT);
  pinMode(ledPin5g, OUTPUT);
  pinMode(swPin5s, INPUT_PULLUP);
  pinMode(swPin5r, INPUT_PULLUP);

  pinMode(ledPin6r, OUTPUT);
  pinMode(ledPin6g, OUTPUT);
  pinMode(swPin6s, INPUT_PULLUP);
  pinMode(swPin6r, INPUT_PULLUP);

  pinMode(ledPinSlow, OUTPUT);
  pinMode(ledPinFast, OUTPUT);
  pinMode(swPinSlow, INPUT_PULLUP);
  pinMode(swPinFast, INPUT_PULLUP);

  //pinMode(swPinLeft, INPUT_PULLUP);
  //pinMode(swPinRight, INPUT_PULLUP);

  pinMode(swPinZoomIn, INPUT_PULLUP);
  pinMode(swPinZoomOut, INPUT_PULLUP);

  digitalWrite(ledPinSlow, LOW);
  digitalWrite(ledPinFast, HIGH);
}

void loop() {

  if (Serial.available()) {
    int inByte = Serial.read();
    Serial3.write(inByte);
  }

  //if (Serial3.available()) {        // If anything comes in Serial1 (pins 0 & 1)
  //  Serial.write(Serial3.read());   // read it and send it out Serial (USB)
  //}

  if (Serial3.available()) {
    char instruction = Serial3.read();
    if (instruction == '#') {
      int count = 0;
      while (Serial3.available() < 1) {                       //  Wait for 6 bytes to be available. Breaks after ~20ms if bytes are not received.
        delayMicroseconds(200);
        count++;
        if (count > 100) {
          SerialFlush();                                     //  Clear the Serial1 buffer
          break;
        }
      }
      instruction = Serial3.read();
      switch (instruction) {
        case 'v': {                       // speed set slow
            speedFastSet = false;
            doLEDs();
          }
          break;
        case 'V': {                       // speed set fast
            speedFastSet = true;
            doLEDs();
          }
          break;
      }
    }
    else {
      //Serial.write(Serial3.read());
      Serial.write(instruction);
    }
  }

  /* ------------------------------------------------- Calculate Joystick ------------------------------------------------- */

  joyXread = analogRead(A0);
  if (joyXread < XdeadRangeLow) {
    XShort = map(joyXread, 0, XdeadRangeLow, out_min, 0);
  }
  else if (joyXread > XdeadRangeHigh) {
    XShort = map(joyXread, XdeadRangeHigh, X_max, 0, out_max);
  }
  else {
    XShort = 0; // deadzone around center value
  }

  joyYread = analogRead(A1);
  if (joyYread < YdeadRangeLow) {
    YShort = map(joyYread, 0, YdeadRangeLow, out_min, 0);
  }
  else if (joyYread > YdeadRangeHigh) {
    YShort = map(joyYread, YdeadRangeHigh, Y_max, 0, out_max);
  }
  else {
    YShort = 0; // deadzone around center value
  }

  joyZread = analogRead(A2);
  if (joyZread < ZdeadRangeLow) {
    ZShort = map(joyZread, 0, ZdeadRangeLow, out_min, 0);
  }
  else if (joyZread > ZdeadRangeHigh) {
    ZShort = map(joyZread, ZdeadRangeHigh, Z_max, 0, out_max);
  }
  else {
    ZShort = 0; // deadzone around center value
  }
  
  /* ------------------------------------------------- Buttons ------------------------------------------------- */

  reading1 = digitalRead(swPin1s);
  if (reading1 != lastButtonState1) {
    lastDebounceTime1 = millis();
  }

  if ((millis() - lastDebounceTime1) > debounceDelay) {
    if (reading1 != buttonState1) {
      buttonState1 = reading1;
      if (buttonState1 == LOW) {
        sendCharArray((char *)"a");
        pos1set = true;
        pos1run = true;
        pos2run = false;
        pos3run = false;
        pos4run = false;
        pos5run = false;
        pos6run = false;
        doLEDs();
      }
    }
  }
  lastButtonState1 = reading1;

  reading2 = digitalRead(swPin1r);
  if (reading2 != lastButtonState2) {
    lastDebounceTime2 = millis();
  }

  if ((millis() - lastDebounceTime2) > debounceDelay) {
    if (reading2 != buttonState2) {
      buttonState2 = reading2;
      if (buttonState2 == LOW) {
        if (pos1set && !pos1run) {
          sendCharArray((char *)"A");
          pos1run = true;
          pos2run = false;
          pos3run = false;
          pos4run = false;
          pos5run = false;
          pos6run = false;
          doLEDs();
        }
      }
    }
  }
  lastButtonState2 = reading2;

  reading3 = digitalRead(swPin2s);
  if (reading3 != lastButtonState3) {
    lastDebounceTime3 = millis();
  }

  if ((millis() - lastDebounceTime3) > debounceDelay) {
    if (reading3 != buttonState3) {
      buttonState3 = reading3;
      if (buttonState3 == LOW) {
        sendCharArray((char *)"b");
        pos2set = true;
        pos1run = false;
        pos2run = true;
        pos3run = false;
        pos4run = false;
        pos5run = false;
        pos6run = false;
        doLEDs();
      }
    }
  }
  lastButtonState3 = reading3;

  reading4 = digitalRead(swPin2r);
  if (reading4 != lastButtonState4) {
    lastDebounceTime4 = millis();
  }

  if ((millis() - lastDebounceTime4) > debounceDelay) {
    if (reading4 != buttonState4) {
      buttonState4 = reading4;
      if (buttonState4 == LOW) {
        if (pos2set && !pos2run) {
          sendCharArray((char *)"B");
          pos1run = false;
          pos2run = true;
          pos3run = false;
          pos4run = false;
          pos5run = false;
          pos6run = false;
          doLEDs();
        }
      }
    }
  }
  lastButtonState4 = reading4;

  reading5 = digitalRead(swPin3s);
  if (reading5 != lastButtonState5) {
    lastDebounceTime5 = millis();
  }

  if ((millis() - lastDebounceTime5) > debounceDelay) {
    if (reading5 != buttonState5) {
      buttonState5 = reading5;
      if (buttonState5 == LOW) {
        sendCharArray((char *)"c");
        pos3set = true;
        pos1run = false;
        pos2run = false;
        pos3run = true;
        pos4run = false;
        pos5run = false;
        pos6run = false;
        doLEDs();
      }
    }
  }
  lastButtonState5 = reading5;

  reading6 = digitalRead(swPin3r);
  if (reading6 != lastButtonState6) {
    lastDebounceTime6 = millis();
  }

  if ((millis() - lastDebounceTime6) > debounceDelay) {
    if (reading6 != buttonState6) {
      buttonState6 = reading6;
      if (buttonState6 == LOW) {
        if (pos3set && !pos3run) {
          sendCharArray((char *)"C");
          pos1run = false;
          pos2run = false;
          pos3run = true;
          pos4run = false;
          pos5run = false;
          pos6run = false;
          doLEDs();
        }
      }
    }
  }
  lastButtonState6 = reading6;

  reading7 = digitalRead(swPin4s);
  if (reading7 != lastButtonState7) {
    lastDebounceTime7 = millis();
  }

  if ((millis() - lastDebounceTime7) > debounceDelay) {
    if (reading7 != buttonState7) {
      buttonState7 = reading7;
      if (buttonState7 == LOW) {
        sendCharArray((char *)"d");
        pos4set = true;
        pos1run = false;
        pos2run = false;
        pos3run = false;
        pos4run = true;
        pos5run = false;
        pos6run = false;
        doLEDs();
      }
    }
  }
  lastButtonState7 = reading7;

  reading8 = digitalRead(swPin4r);
  if (reading8 != lastButtonState8) {
    lastDebounceTime8 = millis();
  }

  if ((millis() - lastDebounceTime8) > debounceDelay) {
    if (reading8 != buttonState8) {
      buttonState8 = reading8;
      if (buttonState8 == LOW) {
        if (pos4set && !pos4run) {
          sendCharArray((char *)"D");
          pos1run = false;
          pos2run = false;
          pos3run = false;
          pos4run = true;
          pos5run = false;
          pos6run = false;
          doLEDs();
        }
      }
    }
  }
  lastButtonState8 = reading8;

  reading9 = digitalRead(swPin5s);
  if (reading9 != lastButtonState9) {
    lastDebounceTime9 = millis();
  }

  if ((millis() - lastDebounceTime9) > debounceDelay) {
    if (reading9 != buttonState9) {
      buttonState9 = reading9;
      if (buttonState9 == LOW) {
        sendCharArray((char *)"e");
        pos5set = true;
        pos1run = false;
        pos2run = false;
        pos3run = false;
        pos4run = false;
        pos5run = true;
        pos6run = false;
        doLEDs();
      }
    }
  }
  lastButtonState9 = reading9;

  reading10 = digitalRead(swPin5r);
  if (reading10 != lastButtonState10) {
    lastDebounceTime10 = millis();
  }

  if ((millis() - lastDebounceTime10) > debounceDelay) {
    if (reading10 != buttonState10) {
      buttonState10 = reading10;
      if (buttonState10 == LOW) {
        if (pos5set && !pos5run) {
          sendCharArray((char *)"E");
          pos1run = false;
          pos2run = false;
          pos3run = false;
          pos4run = false;
          pos5run = true;
          pos6run = false;
          doLEDs();
        }
      }
    }
  }
  lastButtonState10 = reading10;

  reading11 = digitalRead(swPin6s);
  if (reading11 != lastButtonState11) {
    lastDebounceTime11 = millis();
  }

  if ((millis() - lastDebounceTime11) > debounceDelay) {
    if (reading11 != buttonState11) {
      buttonState11 = reading11;
      if (buttonState11 == LOW) {
        sendCharArray((char *)"f");
        pos6set = true;
        pos1run = false;
        pos2run = false;
        pos3run = false;
        pos4run = false;
        pos5run = false;
        pos6run = true;
        doLEDs();
      }
    }
  }
  lastButtonState11 = reading11;

  reading12 = digitalRead(swPin6r);
  if (reading12 != lastButtonState12) {
    lastDebounceTime12 = millis();
  }

  if ((millis() - lastDebounceTime12) > debounceDelay) {
    if (reading12 != buttonState12) {
      buttonState12 = reading12;
      if (buttonState12 == LOW) {
        if (pos6set && !pos6run) {
          sendCharArray((char *)"F");
          pos1run = false;
          pos2run = false;
          pos3run = false;
          pos4run = false;
          pos5run = false;
          pos6run = true;
          doLEDs();
        }
      }
    }
  }
  lastButtonState12 = reading12;


  /* ------------------------------------------------- Speed, L&R ------------------------------------------------- */


  reading13 = digitalRead(swPinSlow);
  reading14 = digitalRead(swPinFast);

  if (reading13 != lastButtonState13) {
    lastDebounceTime13 = millis();
  }

  if ((millis() - lastDebounceTime13) > debounceDelay) {
    if (reading13 != buttonState13) {
      buttonState13 = reading13;
      if (buttonState13 == LOW) {
        if (1==1) {                                    // If Fast is set, Send SLOW  (speedFast)
          /*
          sendCharArray((char *)"s10");
          delay(50);
          sendCharArray((char *)"S10");
          delay(50);
          sendCharArray((char *)"X30");
          speedFast = false;
          doLEDs();
          */
          sendCharArray((char *)"v");
        }
      }
    }
  }
  lastButtonState13 = reading13;

  if (reading14 != lastButtonState14) {
    lastDebounceTime14 = millis();
  }

  if ((millis() - lastDebounceTime14) > debounceDelay) {
    if (reading14 != buttonState13) {
      buttonState14 = reading14;
      if (buttonState14 == LOW) {
        if (1==1) {                                   // If Slow is set, Send FAST  (!speedFast)
          /*
          sendCharArray((char *)"s30");
          delay(50);
          sendCharArray((char *)"S30");
          delay(50);
          sendCharArray((char *)"X60");
          speedFast = true;
          doLEDs();
          */
          sendCharArray((char *)"V");
        }
      }
    }
  }
  lastButtonState14 = reading14;

  /* --------------------------------------------- Send Move Slider Left / Right -------------------------------------------- */
/*
  reading15 = digitalRead(swPinLeft);
  reading16 = digitalRead(swPinRight);
  if (!reading15 && reading16 && !sliderPressed) {
    sliderPressed = true;
    notMoving = false;
    ZShort = -127;                                          // Go Left
  }
  else if (reading15 && !reading16 && !sliderPressed) {
    sliderPressed = true;
    notMoving = false;
    ZShort = 127;                                           // Go Right
  }
  if (reading15 && reading16 && !notMoving && sliderPressed) {
    sliderPressed = false;
    notMoving = true;
    ZShort = 0;                                             // Stop L&R
  }
*/
  /* --------------------------------------------- Send Zoom In / Out -------------------------------------------- */

  reading17 = digitalRead(swPinZoomIn);
  reading18 = digitalRead(swPinZoomOut);
  if (!reading17 && reading18 && !zoomPressed) {
    zoomPressed = true;
    notZooming = false;
    sendCharArray((char *)"Z");                             // Zoom In
  }
  else if (reading17 && !reading18 && !zoomPressed) {
    zoomPressed = true;
    notZooming = false;
    sendCharArray((char *)"z");                             // Zoom In
  }
  if (reading17 && reading18 && !notZooming && zoomPressed) {
    zoomPressed = false;
    notZooming = true;                                      //
  }

  /* --------------------------------------------- Send Joystick & Left / Right -------------------------------------------- */

  shortVals[0] = ZShort;
  shortVals[1] = XShort;
  shortVals[2] = YShort;

  if (shortVals[0] != oldShortVal0 || shortVals[1] != oldShortVal1 || shortVals[2] != oldShortVal2) {   // IF input has changed
    sendSliderPanTiltStepSpeed(INSTRUCTION_BYTES_SLIDER_PAN_TILT_SPEED, shortVals);                     // Send the combned values

    oldShortVal0 = shortVals[0];      // Store as old values
    oldShortVal1 = shortVals[1];      // Store as old values
    oldShortVal2 = shortVals[2];      // Store as old values

    delay(20);
    if ( DEBUG ) {
      Serial.print(XShort, DEC);
      Serial.print(" - ");
      Serial.print(YShort, DEC);
      Serial.print(" - ");
      Serial.println(ZShort);
    }
  }
}

/* ------------------------------------------------- Set LEDs ------------------------------------------------- */

void doLEDs() {
  if (pos1set && !pos1run) {
    digitalWrite(ledPin1r, HIGH);
    digitalWrite(ledPin1g, LOW);
    if ( DEBUG ) {
      Serial.println(", 1 - Red, ");
    }
  }
  if (pos2set && !pos2run) {
    digitalWrite(ledPin2r, HIGH);
    digitalWrite(ledPin2g, LOW);
    if ( DEBUG ) {
      Serial.println(", 2 - Red, ");
    }
  }

  if (pos3set && !pos3run) {
    digitalWrite(ledPin3r, HIGH);
    digitalWrite(ledPin3g, LOW);
    if ( DEBUG ) {
      Serial.println(", 3 - Red, ");
    }
  }
  if (pos4set && !pos4run) {
    digitalWrite(ledPin4r, HIGH);
    digitalWrite(ledPin4g, LOW);
    if ( DEBUG ) {
      Serial.println(", 4 - Red, ");
    }
  }
  if (pos5set && !pos5run) {
    digitalWrite(ledPin5r, HIGH);
    digitalWrite(ledPin5g, LOW);
    if ( DEBUG ) {
      Serial.println(", 5 - Red, ");
    }
  }
  if (pos6set && !pos6run) {
    digitalWrite(ledPin6r, HIGH);
    digitalWrite(ledPin6g, LOW);
    if ( DEBUG ) {
      Serial.println(", 6 - Red, ");
    }
  }
  if (pos1run) {
    digitalWrite(ledPin1r, LOW);
    digitalWrite(ledPin1g, HIGH);
    if ( DEBUG ) {
      Serial.println(", 1 - Green, ");
    }
  }
  if (pos2run) {
    digitalWrite(ledPin2r, LOW);
    digitalWrite(ledPin2g, HIGH);
    if ( DEBUG ) {
      Serial.println(", 2 - Green, ");
    }
  }
  if (pos3run) {
    digitalWrite(ledPin3r, LOW);
    digitalWrite(ledPin3g, HIGH);
    if ( DEBUG ) {
      Serial.println(", 3 - Green, ");
    }
  }
  if (pos4run) {
    digitalWrite(ledPin4r, LOW);
    digitalWrite(ledPin4g, HIGH);
    if ( DEBUG ) {
      Serial.println(", 4 - Green, ");
    }
  }
  if (pos5run) {
    digitalWrite(ledPin5r, LOW);
    digitalWrite(ledPin5g, HIGH);
    if ( DEBUG ) {
      Serial.println(", 5 - Green, ");
    }
  }
  if (pos6run) {
    digitalWrite(ledPin6r, LOW);
    digitalWrite(ledPin6g, HIGH);
    if ( DEBUG ) {
      Serial.println(", 6 - Green, ");
    }
  }
  if (speedFastSet) {
    digitalWrite(ledPinSlow, LOW);
    digitalWrite(ledPinFast, HIGH);
  }
  else if (!speedFastSet) {
    digitalWrite(ledPinSlow, HIGH);
    digitalWrite(ledPinFast, LOW);
  }
}

void SerialFlush(void) {
  while (Serial.available() > 0) {
    char c = Serial.read();
  }
}

void sendCharArray(char *array) {
  int i = 0;
  while (array[i] != 0)
    if ( DEBUG ) {
      Serial.write((uint8_t)array[i++]);
    }
    else {
      Serial3.write((uint8_t)array[i++]);
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
    Serial3.write(data, sizeof(data));        // Send the command and the 6 bytes of data
  }
}
