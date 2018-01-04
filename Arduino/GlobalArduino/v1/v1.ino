//Global
boolean globalState=false;
boolean balanceFull=false;
boolean destination=0;
long tfin;

//Balance
#include <HX711_ADC.h>

//HX711 constructor (dout pin, sck pin)
HX711_ADC LoadCell_1(4, 5); //HX711 1
HX711_ADC LoadCell_2(6, 7); //HX711 2
long t;
float limMasse=0;
float actuMasse=0;
float deltaSeuil1=0.05;
float deltaSeuil2=0.1;
long dureeStableBalance=251;
long tseuil;
float videBalance=0.1;

//Verin
int EN[2]={10,11};
int IN1[2]={9,12};
int IN2[2]={8,13};
int etatVerin[2]={0,0};
int commandeVerin[2]={0,0};
long numV=1;
long touv;
long dureeImpulsionOuv=7000;
long dureeImpulsionFerm=8500;
long dureeOuverture=1000;

//Moteur
int Relais[8]={14,15,16,17,3,2,1,0};
boolean etatRelais[8]={true,true,true,true,true,true,true,true};
long numM=1;

void setup() {
  // put your setup code here, to run once:
  //Serie
  Serial.begin(115200);
  Serial.println("En attente ...");
  //Balance
  initialiseBalance();
  
  //Verin
  for (int i=0;i<2;i++){
    pinMode(EN[i],OUTPUT);
    pinMode(IN1[i],OUTPUT);
    pinMode(IN2[i],OUTPUT);
    digitalWrite(EN[i],LOW);
    digitalWrite(IN1[i],LOW); 
    digitalWrite(IN2[i],LOW);
  }
  
  //Moteur
  for (int i=0;i<8;i++){
    pinMode(Relais[i],OUTPUT);
    digitalWrite(Relais[i],etatRelais[i]);
  }
  Serial.println("Initialisation terminee");
}

void loop() {
  // put your main code here, to run repeatedly:
  communicationSerie();
  if (globalState){
    actualiseBalance();
    actualiseEtatMoteur();
    actualiseMoteur();
    if (balanceFull){
      actualiseVerin();
    }
  }
  else{
    if (commandeVerin[0]==1){
      commandeVerin[0]=2;
    }
    if (commandeVerin[1]==1){
      commandeVerin[1]=2;
    }
    for (int i=0;i<8;i++){
      etatRelais[i]=true;
    }
    actualiseBalance();
    actualiseMoteur();
    actualiseVerin();
  }
}


void initialiseBalance(void){
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
  LoadCell_2.setCalFactor(112450.0); // user set calibration factor (float)
  
  //check if last tare operation is complete
  if (LoadCell_1.getTareStatus() == true) {
    Serial.println("Tare load cell 1 complete");
  }
  if (LoadCell_2.getTareStatus() == true) {
    Serial.println("Tare load cell 2 complete");
  }
}

void actualiseBalance(void){
  //update() should be called at least as often as HX711 sample rate; >10Hz@10SPS, >80Hz@80SPS
  //longer delay in scetch will reduce effective sample rate (be carefull with delay() in loop)
  LoadCell_1.update();
  LoadCell_2.update();
  
  if (millis() > t + 250) {
    actuMasse = LoadCell_1.getData() + LoadCell_2.getData();
    if (globalState){
      Serial.print("MasseActuelle=");Serial.println(actuMasse);
    }
    t = millis();
  }
  
  //check if last tare operation is complete
  if (LoadCell_1.getTareStatus() == true) {
    Serial.println("Tare load cell 1 complete");
  }
  if (LoadCell_2.getTareStatus() == true) {
    Serial.println("Tare load cell 2 complete");
  }
}

void actualiseVerin(void){
  if ((millis()>touv+dureeOuverture)&&(etatVerin[destination]==1)){
    commandeVerin[destination]=2;
    balanceFull=false;
    globalState=false;
  }
  else if ((balanceFull)&&(etatVerin[destination]!=1)) {
    commandeVerin[destination]=1;
  }
  
  for (int i=0;i<2;i++){
    if (commandeVerin[i]==0){
      digitalWrite(IN1[i],LOW);
      digitalWrite(IN2[i],LOW);
      analogWrite(EN[i],0);
    }
    else if (commandeVerin[i]==1){
      Serial.println("Ouverture Verin");
      Serial.print("Temps depuis detection: ");Serial.println(millis()-tfin);
      digitalWrite(IN1[i],HIGH); 
      digitalWrite(IN2[i],LOW);
      analogWrite(EN[i],255);
      delay(dureeImpulsionOuv);
      analogWrite(EN[i],0);
      commandeVerin[i]=0;
      etatVerin[i]=1;
      touv = millis();
      globalState=false;
    }
    else if (commandeVerin[i]==2){
      Serial.println("Fermeture Verin");
      digitalWrite(IN1[i],LOW); 
      digitalWrite(IN2[i],HIGH);
      analogWrite(EN[i],255);
      delay(dureeImpulsionFerm);
      analogWrite(EN[i],0);
      commandeVerin[i]=0;
      etatVerin[i]=0;
    }
  }
}

boolean actualiseEtatMoteur(void){
  float delta=limMasse-actuMasse;
  if (etatRelais[numM-1]){
    if ((millis() > tfin + dureeStableBalance)&&(delta<0)){
      balanceFull=true;
      Serial.print("MasseFinale=");
      Serial.println(actuMasse);
    }
    else if (delta>=0){
      etatRelais[numM-1]=false;
      Serial.println("Masse non atteinte, moteur redemarre");
    }
  }else{
    if (delta<0){
      etatRelais[numM-1]=true;
      tfin = millis();
      Serial.println("Masse atteinte, moteur arret");
    }
    else if ((actuMasse>deltaSeuil2)&&((delta<deltaSeuil1) || (delta<deltaSeuil2))&& (millis()>tseuil+dureeStableBalance)){
      etatRelais[numM-1]=true;
      tseuil=millis();
      Serial.println("Masse seuil atteinte, moteur arret");
    }
  }
}

void actualiseMoteur(void){
  for (int i=0;i<8;i++){
    digitalWrite(Relais[i],etatRelais[i]);
  }
}

void communicationSerie(void){
  if (Serial.available()>1){
    while (Serial.available()>0){
      char text = Serial.read();
      if (text=='R'){
        Serial.println("Moteur");
        long num = Serial.parseInt();
        if ('='==Serial.read()){
          Serial.println("ok");
          if (1==Serial.parseInt()){
            etatRelais[num-1]=false;
            Serial.println("f");
          } 
          else {
            etatRelais[num-1]=true;
            Serial.println("t");
          }
        }
      }
      else if (text=='P'){
        numM = Serial.parseInt();
        Serial.print("EntreeMoteur=");Serial.println(numM);
      }
      else if (text=='V'){
        Serial.println("Verin");
        numV = Serial.parseInt();
        if ('='==Serial.read()){
          commandeVerin[numV-1]=Serial.parseInt();
        }
      }
      else if (text=='B'){
        Serial.println("Restart");
        if ('1'==Serial.parseInt()){
          setup();
        }
      }
      else if (text=='T'){
        Serial.println("Tare demandee ...");
        LoadCell_1.tareNoDelay();
        LoadCell_2.tareNoDelay();
      }
      else if (text=='M'){
        long c=Serial.read();
        if ('='==c){
          limMasse=Serial.parseFloat();
          Serial.print("MasseDemandee=");Serial.println(limMasse);
        }
        else{
          Serial.print("MasseActuelle=");Serial.println(actuMasse);
        }
      }
      else if (text=='S'){
        if (0==Serial.parseInt()){
          Serial.println("Stop");
          globalState=false;
        }
        else{
          Serial.println("Start");
          globalState=true;
          
        }
      }
      else if (text=='D'){
        if (0==Serial.parseInt()){
          Serial.println("Destination=0");
          destination=0;
        }
        else{
          Serial.println("Destination=1");
          destination=1;
        }
      }
    }
  }
}
