//-- Verin A --
int ENA=10; //Connecté à Arduino pin 10(sortie pwm)
int IN1=9; //Connecté à Arduino pin 9
int IN2=8; //Connecté à Arduino pin 8


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(ENA,OUTPUT);//Configurer les broches comme sortie
  pinMode(IN1,OUTPUT);
  pinMode(IN2,OUTPUT);
  digitalWrite(ENA,LOW);// Moteur A - Ne pas tourner (désactivation moteur)

  // Direction du Moteur A
  digitalWrite(IN1,LOW); 
  digitalWrite(IN2,LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()>0){
    char text=Serial.read();
    if (text=='G'){
      digitalWrite(IN1,LOW); 
      digitalWrite(IN2,HIGH);
      analogWrite(ENA,255);
      Serial.println("Start Gauche");
    }
    else if (text=='D'){
      digitalWrite(IN1,HIGH); 
      digitalWrite(IN2,LOW);
      analogWrite(ENA,255);
      Serial.println("Start Droite");
    }
    else{
      digitalWrite(IN1,LOW); 
      digitalWrite(IN2,LOW);
      analogWrite(ENA,0);
      Serial.println("Stop");
    }
  }
}
