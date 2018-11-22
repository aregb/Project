#include "FastLED.h"
const uint16_t  NUM_LEDS = 791;
const uint8_t DATA_PIN = 33;
const int BAUDRATE = 1000000;


// BUFFER AND VARIABLES FOR RECEIVING A BYTEARRAY
uint8_t buffer[NUM_LEDS * 3]; // Each led has 3 bytes of data (one for each color value)
boolean gotData = false;   

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
  static uint16_t index =0;
  static uint8_t startMarker = 254;
  static uint8_t endMarker = 255;
  static uint8_t rb;
  
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
void setLedsFromBuffer(){
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
