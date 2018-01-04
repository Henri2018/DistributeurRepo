int Relais[8]={14,15,16,17,3,2,1,0};
boolean etatRelais[8]={true,true,true,true,true,true,true,true};


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i=0;i<8;i++){
    pinMode(Relais[i],OUTPUT);
    digitalWrite(Relais[i],etatRelais[i]);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  communicationSerie();
  for (int i=0;i<8;i++){
    digitalWrite(Relais[i],etatRelais[i]);
  }
}

void communicationSerie(void){
  if (Serial.available()>0){
    while (Serial.available()>0){
      char text = Serial.read();
      switch (text){
        case 'R':
          long num = Serial.parseInt();
          if ('='==Serial.read()){
            if (1==Serial.parseInt()){
              etatRelais[num-1]=false;
            } 
            else {
              etatRelais[num-1]=true;
            }
          }
      }
    }
  }
}
