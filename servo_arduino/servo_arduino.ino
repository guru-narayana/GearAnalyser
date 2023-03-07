#include <Servo.h>
Servo myservo; 
String inByte;
int pos;
unsigned long previousMillis = 0;
void setup() {
 
  myservo.attach(5);
  Serial.begin(9600);
}

void loop()
{
  bool x  = false;
  if(Serial.available())
    { 
    inByte = Serial.readStringUntil('\n');
    pos = inByte.toInt();
    x = true;          
    }
   if(x){
    myservo.write(2000);
    delay(1.6*pos);
   }
    myservo.write(1500);
}
