#include <avr/io.h>
#include <avr/interrupt.h>

volatile char trigger = 0;
int hitcount = 0;
unsigned int t_delta = 0;
unsigned long t_inhibit, t_end, t_last;

void setup() {
  Serial.begin(115200);
  
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
  pinMode(2, INPUT_PULLUP);
  pinMode(3, OUTPUT);
  
  // Setup the comparator...
  ACSR = (0<<ACD) | (0<<ACBG) | (1<<ACIE) | (0<<ACIC) | (1<<ACIS1) | (0<<ACIS0);
  
  sei();
  t_inhibit = millis();
}

void loop() {
  //wait for buttonpress
  while(digitalRead(2));
  //send that arduino is ready
  Serial.println(-1);
  hitcount = 1;
  trigger = 0;
  //wait for first trigger
  while(trigger == 0);
  t_last =  millis();
  trigger = 0;
  //send that arduino is counting
  Serial.println(-2);
  t_end = millis() + 60000;
  while(millis() < t_end) {
    if (trigger) {
      //increase count, send t_delta, light led, reset trigger
      hitcount++;
      Serial.println(t_delta);
      digitalWrite(3, HIGH);
      trigger = 0;
    }
    //light led for trigger indication
    if (millis() > t_inhibit) {
      digitalWrite(3, LOW);
    }
  }
  Serial.println(-3);
  digitalWrite(3, LOW);
}

ISR(ANALOG_COMP_vect)
{
  static unsigned long t_current;
  if (ACSR & ACO) {
  } else {
    t_current = millis();
    if (t_current > t_inhibit) {
      trigger = 1;
      t_inhibit = t_current + 15;
      t_delta = (int)(t_current - t_last);
      t_last = t_current;
    }
  }
  ACSR |= (1<<ACI);
}
