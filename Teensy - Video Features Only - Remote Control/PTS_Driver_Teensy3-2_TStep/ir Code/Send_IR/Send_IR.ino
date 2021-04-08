#include <IRLibSendBase.h>
#include <IRLib_P02_Sony.h>   
#include <IRLibCombo.h>

IRsend mySender;

void setup() {
  Serial.begin(9600);
  delay(2000); while (!Serial); //delay for Leonardo
  Serial.println(F("Every time you press a key is a serial monitor we will send."));
}

void loop() {
  if (Serial.read() != -1) {
    mySender.send(SONY,0xC81, 12);
    Serial.println(F("Sent signal."));
  }
}
