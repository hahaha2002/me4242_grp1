#include <SoftwareSerial.h>

unsigned int Bluetooth_TX = 0;
unsigned int Bluetooth_RX = 1;

// Pin Assignment
#define rightFin  3
#define leftTail  9
#define rightTail  10
#define leftFin  11
#define pump     5
#define trig     18
#define echo     19
#define led      2

int leftTailForward = 1900;
int rightTailForward = 2000;
int leftTailTurnLeft = 900;
int rightTailTurnLeft = 1400;
int leftTailTurnRight = 1500;
int rightTailTurnRight = 700;
int stopTime = 2200;

int pumpStrength = 250;

SoftwareSerial BTserial(Bluetooth_TX, Bluetooth_RX);

void setup() {
    
    pinMode(rightFin, OUTPUT);
    pinMode(leftTail, OUTPUT);
    pinMode(rightTail, OUTPUT);
    pinMode(leftFin, OUTPUT);
    pinMode(pump, OUTPUT);
    pinMode(led, OUTPUT);
    pinMode(trig, OUTPUT);
    pinMode(echo, INPUT);
       
    BTserial.begin(9600);  

    digitalWrite(rightFin, LOW);
    digitalWrite(leftTail, LOW);
    digitalWrite(rightTail, LOW);
    digitalWrite(leftFin, LOW);
    analogWrite(pump, 0);
    digitalWrite(led, LOW);
}

long getDistance() {
    digitalWrite(trig, LOW);
    delayMicroseconds(2);
    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);
    long duration = pulseIn(echo, HIGH);
    long distance = duration * 0.034 / 2;

    return distance;
}

void pumpOn() {
  analogWrite(pump, pumpStrength);
}

void pumpOff() {
  analogWrite(pump, 0);
}

void forwardLoop() {
    resetAllValves();
    pumpOn();
    digitalWrite(rightTail, LOW);
    digitalWrite(leftTail, HIGH);
    delay(leftTailForward);
    digitalWrite(rightTail, HIGH);
    digitalWrite(leftTail, LOW);
    delay(rightTailForward);
    resetAllValves();
}

void leftLoop() {
    resetAllValves();
    digitalWrite(rightTail, LOW);
    digitalWrite(leftTail, HIGH);
    digitalWrite(leftFin, LOW);
    delay(leftTailTurnLeft);
    digitalWrite(rightTail, HIGH);
    digitalWrite(leftTail, LOW);
    digitalWrite(leftFin, HIGH);
    delay(rightTailTurnLeft);
    resetAllValves();
}

void rightLoop() {
    resetAllValves();
    digitalWrite(rightTail, LOW);
    digitalWrite(leftTail, HIGH);
    digitalWrite(rightFin, HIGH);
    delay(leftTailTurnRight);
    digitalWrite(rightTail, HIGH);
    digitalWrite(leftTail, LOW);
    digitalWrite(rightFin, LOW);
    delay(rightTailTurnRight);
    resetAllValves();
}

void stopAction() {
    resetAllValves();
    digitalWrite(leftFin, HIGH);
    digitalWrite(rightFin, HIGH);
    delay(stopTime);
    digitalWrite(leftFin, LOW);
    digitalWrite(rightFin, LOW);
    digitalWrite(pump, LOW);
    BTserial.println("stop");
    resetAllValves();
}

void resetAllValves() {
    digitalWrite(rightFin, LOW);
    digitalWrite(leftTail, LOW);
    digitalWrite(rightTail, LOW);
    digitalWrite(leftFin, LOW);
}

void shutdownSeq() {
    resetAllValves();
    pumpOff();
    digitalWrite(led, LOW);   
}

void loop() {
    if (BTserial.available()) {  
        char receivedCharacter = (char)BTserial.read();

        // Individual Commands
        if (receivedCharacter == '1') digitalWrite(rightTail, HIGH);
        if (receivedCharacter == 'a') digitalWrite(rightTail, LOW);
        if (receivedCharacter == '2') digitalWrite(leftTail, HIGH);
        if (receivedCharacter == 'b') digitalWrite(leftTail, LOW);
        if (receivedCharacter == '3') digitalWrite(rightFin, HIGH);
        if (receivedCharacter == 'c') digitalWrite(rightFin, LOW);
        if (receivedCharacter == '4') digitalWrite(leftFin, HIGH);
        if (receivedCharacter == 'd') digitalWrite(leftFin, LOW);
        if (receivedCharacter == '5') digitalWrite(pump, HIGH);
        if (receivedCharacter == 'e') digitalWrite(pump, LOW);
        if (receivedCharacter == '6') digitalWrite(led, HIGH);
        if (receivedCharacter == 'f') digitalWrite(led, LOW);

        // New Commands for Loops
        if (receivedCharacter == 'F') forwardLoop();
        if (receivedCharacter == 'L') leftLoop();
        if (receivedCharacter == 'R') rightLoop();
        if (receivedCharacter == 'S') stopAction();
        if (receivedCharacter == 'O') shutdownSeq(); 
    }
    
    // Send Distance Data
    long distance = getDistance();
    BTserial.println(distance);
    if (distance < 60) {
        digitalWrite(led, HIGH);
    } else {
        digitalWrite(led, LOW);
    }
}