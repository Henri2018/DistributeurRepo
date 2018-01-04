//-------------------------------------------------------------------------------------
// HX711_ADC.h
// Arduino master library for HX711 24-Bit Analog-to-Digital Converter for Weigh Scales
// Olav Kallhovd sept2017
// Tested with      : HX711 asian module on channel A and YZC-133 3kg load cell
// Tested with MCU  : Arduino Nano
//-------------------------------------------------------------------------------------
/* This is an example sketch on how to find correct calibration factor for your HX711:
   - Power up the scale and open Arduino serial terminal
   - After stabelizing and tare is complete, put a known weight on the load cell
   - Observe values on serial terminal
   - Adjust the calibration factor until output value is same as your known weight:
      - Sending 'l' from the serial terminal decrease factor by 1.0
      - Sending 'L' from the serial terminal decrease factor by 10.0
      - Sending 'h' from the serial terminal increase factor by 1.0
      - Sending 'H' from the serial terminal increase factor by 10.0
      - Sending 't' from the serial terminal call tare function
   - Observe and note the value of the new calibration factor
   - Use this new calibration factor in your sketch
*/

#include <HX711_ADC.h>

//HX711 constructor (dout pin, sck pin)
HX711_ADC LoadCell_1(4, 5);
HX711_ADC LoadCell_2(6, 7); //HX711 2

long t;
float moyenne=0;
int nb;

void setup() {
  Serial.begin(9600);
  Serial.println("Wait...");
  LoadCell_1.begin();
  LoadCell_2.begin();
  long stabilisingtime = 2000; // tare preciscion can be improved by adding a few seconds of stabilising time
  byte loadcell_1_rdy = 0;
  byte loadcell_2_rdy = 0;
  while ((loadcell_1_rdy + loadcell_2_rdy) < 2) { //run startup, stabilization and tare, both modules simultaniously
    if (!loadcell_1_rdy) loadcell_1_rdy = LoadCell_1.startMultiple(stabilisingtime);
    if (!loadcell_2_rdy) loadcell_2_rdy = LoadCell_2.startMultiple(stabilisingtime);
  }
  LoadCell_1.setCalFactor(108550.0); // user set calibration factor (float)
  LoadCell_2.setCalFactor(112450.0);
  Serial.println("Startup + tare is complete");
}

void loop() {
  //update() should be called at least as often as HX711 sample rate; >10Hz@10SPS, >80Hz@80SPS
  //longer delay in scetch will reduce effective sample rate (be carefull with delay() in loop)
  LoadCell_1.update();
  LoadCell_2.update();

  //get smoothed value from data set + current calibration factor
  if (millis() > t + 250) {
    float i_1 = LoadCell_1.getData();
    float v_1 = LoadCell_1.getCalFactor();
    float i_2 = LoadCell_2.getData();
    float v_2 = LoadCell_2.getCalFactor();
    float i_s=i_1+i_2;
    float v_s=(v_1+v_2)/2;
    if (moyenne==0) {
      moyenne=i_s;
      nb+=1;
      }
    else{
      moyenne=(moyenne*nb+i_s)/(nb+1);
      nb+=1;
      }
    Serial.println();
    Serial.print("Load_cell_1 output val: ");
    Serial.print(i_1);
    Serial.print("      Load_cell_2 output val: ");
    Serial.print(i_2);
    Serial.print("      Sum output val: ");
    Serial.print(i_s);
    Serial.print("      Moy output val: ");
    Serial.println(moyenne);
    Serial.print("Load_cell_1 calFactor: ");
    Serial.print(v_1);
    Serial.print("      Load_cell_2 calFactor: ");
    Serial.print(v_2);
    Serial.print("      Sum calFactor: ");
    Serial.println(v_s);
    t = millis();
  }

  //receive from serial terminal
  if (Serial.available() > 0) {
    float i;
    char inByte = Serial.read();
    if (inByte == 'l') i = -1.0;
    else if (inByte == 'm') moyenne = 0.0;
    else if (inByte == 'L') i = -10.0;
    else if (inByte == 'h') i = 1.0;
    else if (inByte == 'H') i = 10.0;
    else if (inByte == 't') {
      LoadCell_1.tareNoDelay();
      LoadCell_2.tareNoDelay();
    }
    if (i != 't') {
      float v1 = LoadCell_1.getCalFactor() + i;
      LoadCell_1.setCalFactor(v1);
      float v2 = LoadCell_2.getCalFactor() + i;
      LoadCell_2.setCalFactor(v2);
    }
  }

  //check if last tare operation is complete
  if (LoadCell_1.getTareStatus() == true && LoadCell_2.getTareStatus() == true) {
    Serial.println("Tare complete");
  }

}
