#include <Servo.h>
Servo myservo; 
String inByte;
int pos;

void setup() {
 
  myservo.attach(5);
  Serial.begin(9600);
}

void loop()
{    
  if(Serial.available())
    { 
    inByte = Serial.readStringUntil('\n');
    pos = inByte.toInt();          
    myservo.write(2000);
    delay(1.4*pos);
    myservo.write(1500);
    }
    myservo.write(1500);
}
