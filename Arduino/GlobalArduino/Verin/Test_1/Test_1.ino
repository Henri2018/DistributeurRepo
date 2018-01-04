//-- Verin A --
int ENA=10; //Connecté à Arduino pin 10(sortie pwm)
int IN1=9; //Connecté à Arduino pin 9
int IN2=8; //Connecté à Arduino pin 8

//-- Verin B --
int ENB=11; //Connecté à Arduino pin 11(Sortie pwm)
int IN3=12; //Connecté à Arduino pin 12
int IN4=13; //Connecté à Arduino pin 13

void setup() {
  // put your setup code here, to run once:
  pinMode(ENA,OUTPUT);//Configurer les broches comme sortie
  pinMode(ENB,OUTPUT);
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
  pinMode(IN3,OUTPUT);
  pinMode(IN4,OUTPUT);
  digitalWrite(ENA,LOW);// Moteur A - Ne pas tourner (désactivation moteur)
  digitalWrite(ENB,LOW);// Moteur B - Ne pas tourner (désactivation moteur)

  // Direction du Moteur A
  digitalWrite(IN1,LOW); 
  digitalWrite(IN2,HIGH);

  // Direction du Moteur B
  // NB: meme sens moteur A
  digitalWrite(IN3,LOW);
  digitalWrite(IN4,HIGH);
}

void loop() {
  // put your main code here, to run repeatedly:
  // Moteur A
  analogWrite(ENA,10);

  // Moteur B
  analogWrite(ENB,10);
}
