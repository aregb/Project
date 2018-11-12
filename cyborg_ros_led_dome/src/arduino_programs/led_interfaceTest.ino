#include <FastLED.h>
#define NUM_LEDS 240
#define DATA_PIN 6
#define BAUDRATE 115200

// BUFFER AND VARIABLES FOR RECEIVING A BYTEARRAY
uint8_t buffer[NUM_LEDS*3];   // Each led has 3 bytes of data (One for each color value)
int numBytesRead = 0;   // How many bytes have we read into the buffer
int color = 1;
bool gotData = false;   // Got all data we needed to set leds
bool lastblue=false;
int *iterations = 0;

// INITIALIZE LEDS
CRGB leds[NUM_LEDS];

// SETUP LEDS AND SERIAL COMMUINICATION
void setup() {
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);

  // Board controls:
  // FastLED.setBrightness(255);
  // FastLED.setMaxPowerInVoltsAndMilliamps(5, 10000);

  FastLED.clear();
  FastLED.show();

  // TEST DEMO:
  // meteorRain(0xff,0xff,0xff,10, 64, true, 30);
}

void loop(){
  while(iterations <=26){
    if (iterations==0){
      eyes();    
    }
    else if (iterations>0 && iterations<=20){
      siren();
    }
    else if (iterations>20 && iterations <=25){
      eyes();
    }
    else{
      siren();
    }
    visualize();
    iterations++;

    FastLED.show(); 
    delay(1000);
  }
}

void visualize(){
  
  for(int i=0;i<NUM_LEDS;i++){
      leds[i].r = buffer[i*3];
      leds[i].g = buffer[i*3 +1];
      leds[i].b = buffer[i*3 +2];
    }
}

void siren(){
  Serial.println("rendering siren");
  if (lastblue==true)  {
  for(int i=0;i<NUM_LEDS;i++){
    buffer[i*3] = 50;
   }
  }
  else
  {
  for (int i=0;i<NUM_LEDS;i++)
    {
     buffer[i*3 +2]=50;
    } 
  }
    
}

void eyes(){
  Serial.println("rendering eyes");
  for (int i=0;i<NUM_LEDS;i++)
  {
    buffer[2]=50;
    buffer[5]=50;
    buffer[8]=50;
    buffer[11]=50;
    buffer[14]=50;
    buffer[17]=50;
    buffer[20]=50;
    buffer[23]=50;
    buffer[26]=50;
    buffer[29]=50;
    buffer[32]=50;
  }
}