/*
  https://playground.arduino.cc/Interfacing/Python
  Using FastLED library:
  - Download the FastLED library: http://fastled.io/ as .zip.
  - In Arduino IDE: Sketch -> Include library -> Add .ZIP library
*/
#include <FastLED.h>
#define NUM_LEDS 240
#define DATA_PIN 6
#define BAUDRATE 115200

// BUFFER AND VARIABLES FOR RECEIVING A BYTEARRAY
uint8_t buffer[3];   // Each led has 3 bytes of data (One for each color value)
uint16_t numBytesRead = 0;   // How many bytes have we read into the buffer
bool gotData = false;   // Got all data we needed to set leds
uint16_t address = 0;
// INITIALIZE LEDS
CRGB leds[NUM_LEDS];


// SETUP LEDS AND SERIAL COMMUINICATION
void setup(){
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
  Serial.begin(BAUDRATE, SERIAL_8N1);     //Starting serial communication, 8 data bits, no parity, 1 stop bit
}

void loop(){
  if(gotData){
    FastLED.show();
    gotData = false;
  }
}

// SERIAL
/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
  
  https://www.arduino.cc/en/Reference/SerialEvent
  https://www.arduino.cc/en/Tutorial/SerialEvent
*/

 void serialEvent(){

  while (Serial.available() && !gotData){
    //read out and set address
    address= 256*Serial.read(); 
    address += Serial.read();
    //red out and set led-data in buffer
    buffer[0] = Serial.read();
    buffer[1] = Serial.read();
    buffer[2] = Serial.read();

    leds[address].r = buffer[0];
    leds[address].g = buffer[1];
    leds[address].b = buffer[2];

    //numPixelsRecieved++;

    //if(numPixelsRecieved == NUM_LEDS{
       // gotData=true;
       //numPixelsRecieved = 0;
    //}
  }
  gotData = true;

}
