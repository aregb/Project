#include "FastLED.h"
#define NUM_LEDS 790
#define DATA_PIN 33
#define BAUDRATE 1000000


// BUFFER AND VARIABLES FOR RECEIVING A BYTEARRAY
uint8_t buffer[NUM_LEDS * 3]; // Each led has 3 bytes of data (One for each color value)
boolean gotData = false;   // Got all data we needed to set leds

// INITIALIZE LEDS
CRGB leds[NUM_LEDS];


// SETUP LEDS AND SERIAL COMMUINICATION
void setup() {
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
  Serial.begin(BAUDRATE, SERIAL_8N1);     //Starting serial communication, 8 data bits, no parity, 1 stop bit
}

void loop() {
  receiveSerialData();
  setLedsFromBuffer(); 
}


void receiveSerialData() {
  static boolean recvInProgress = false;
  static int index =0;
  uint8_t startMarker = 254;
  uint8_t endMarker = 255;
  uint8_t rb;
  
  while (Serial.available() > 0 && gotData==false) {
    rb = Serial.read();

    if (recvInProgress==true) {
      if (rb != endMarker) {
        buffer[index] = rb;
        index++;
      }
      else {
        recvInProgress = false;
        index = 0;
        gotData = true;
      }
    }
    else if (rb == startMarker) {
      recvInProgress = true;
    }
  }
}


// SETTING LEDS FROM RECEIVED DATA
void setLedsFromBuffer() {
    if(gotData == true){  
        int colorCount = 0;
        int ledCount = 0;
        for (int i = 0; i < NUM_LEDS * 3; i++) {
            switch (colorCount) {
            case 0:
                leds[ledCount].r = buffer[i];
                break;
            case 1:
                leds[ledCount].g = buffer[i];
                break;
            case 2:
                leds[ledCount].b = buffer[i];
                break;
            }
        colorCount++;
    if (colorCount == 3) {
      colorCount = 0;
      ledCount++;
    }
  }
  FastLED.show();
  gotData = false;
  }
}

void setLedsFromBuffer2(){
 if(gotData == true){
    for (int i=0; i<NUM_LEDS*3; i+=3){
        leds[i/3].r = buffer[i];
        leds[i/3].g = buffer[i+1];
        leds[i/3].b = buffer[i+2];
    }
    FastLED.show();
    gotData = false;
 }
}