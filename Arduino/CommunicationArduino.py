#!/usr/bin/env python3
# coding: utf-8
import time
import serial
import sys
import string
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
import General as g

class Arduino():
    
    def __init__(self):
        try:
            print("Opening serial port to Arduino")
            self.COM = serial.Serial('/dev/ttyACM0', 115200)
            if self.COM.isOpen() == False:
                print("Cannot open serial port to Arduino")
                #TODO
                #Procedure en cas d echec de l'ouverture
                #Reessaie une fois, mise en indisponible, envoi sms d'erreur
            else:
                print("\t\t\tSerial port to Arduino opened")
        except:
            print("Error opening serial port to Arduino")
            #TODO
            #Procedure en cas d'echec de la communication

        self.derniere_ligne=""
        self.compteur=0
        self.isMasseSet=False
        self.isProduitSet=False
        self.isDestinationSet=False
        self.receivedMasseActuelle=0
        self.receivedMasseFinale=0
        self.ready=False
        self.working=False
        self.deliveredState=False
        GObject.idle_add(self.lecture3)

    def isavailable(self):
        return (self.COM.inWaiting()>0)
    
    def set_masse(self, objectif=5.00,nb_envoi=2,timeout=5):
        transmit=False
        i=0
        while ((transmit==False) and (i<nb_envoi)):
            i+=1
            self.envoi_commande("M="+str(objectif))
            tenvoi=time.time()
            trecept=tenvoi
            while (not("MasseDemandee=" in self.derniere_ligne) and (trecept-tenvoi<timeout)):
                trecept=time.time()
                self.lecture(1)
            deb=self.derniere_ligne.find("=",0)
            if objectif==float(self.derniere_ligne[deb+1:]):
                print("Consigne de Masse Transmise")
                transmit=True
                self.isMasseSet=True
        return transmit

    def set_produit(self, produit=1,nb_envoi=2,timeout=5):
        transmit=False
        i=0
        while ((transmit==False) and (i<nb_envoi)):
            i+=1
            self.envoi_commande("P"+str(produit))
            tenvoi=time.time()
            trecept=tenvoi
            while (not("EntreeMoteur=" in self.derniere_ligne) and ((trecept-tenvoi)<timeout)):
                trecept=time.time()
                self.lecture(1)
            deb=self.derniere_ligne.find("=",0)
            
            if float(produit)==float(self.derniere_ligne[deb+1:]):
                print("Consigne de Produit Transmise")
                transmit=True
                self.isProduitSet=True
        return transmit
    
    def set_destination(self, destination=0,nb_envoi=2,timeout=5):
        transmit=False
        i=0
        while ((transmit==False) and (i<nb_envoi)):
            i+=1
            self.envoi_commande("D"+str(destination))
            tenvoi=time.time()
            trecept=tenvoi
            while (not("Destination=" in self.derniere_ligne) and ((trecept-tenvoi)<timeout)):
                trecept=time.time()
                self.lecture(1)
            deb=self.derniere_ligne.find("=",0)
            if float(destination)==float(self.derniere_ligne[deb+1:]):
                print("Consigne de Destination Transmise")
                transmit=True
                self.isDestinationSet=True
        return transmit
    
    def send_start(self,nb_envoi=2,timeout=5):
        print(self.isMasseSet)
        if not(self.isMasseSet):
            self.set_masse()
        if not(self.isProduitSet):
            self.set_produit()
        if not(self.isDestinationSet):
            self.set_destination()
        transmit=False
        i=0
        while ((transmit==False) and (i<nb_envoi)):
            i+=1
            self.envoi_commande("S1")
            tenvoi=time.time()
            trecept=tenvoi
            while (not("Start" in self.derniere_ligne) and ((trecept-tenvoi)<timeout)):
                trecept=time.time()
                self.lecture(1)
            if (trecept-tenvoi)<timeout:
                print("Consigne de Demarrage Transmise")
                transmit=True
        return transmit
    
    def send_stop(self,nb_envoi=2,timeout=5):
        transmit=False
        i=0
        while ((transmit==False) and (i<nb_envoi)):
            i+=1
            self.envoi_commande("S0")
            tenvoi=time.time()
            trecept=tenvoi
            while (not("Stop" in self.derniere_ligne) and ((trecept-tenvoi)<timeout)):
                trecept=time.time()
                self.lecture(1)
            if (trecept-tenvoi)<timeout:
                print("Consigne d'Arret Transmise")
                transmit=True
        return transmit
    
    def nouvelle(self,objectif=5.00,produit=1,destination=0):
        transmit=False
        while transmit==False:
            self.envoi_commande("M="+str(objectif))
            while not("MasseDemandee=" in self.derniere_ligne):
                self.lecture(1)
            deb=self.derniere_ligne.find("=",0)
            if objectif==float(self.derniere_ligne[deb+1:]):
                print("Consigne de Masse Transmise")
                transmit=True
                self.isMasseSet=True
        transmit=False
        while transmit==False:
            self.envoi_commande("P"+str(produit))
            while not("EntreeMoteur=" in self.derniere_ligne):
                self.lecture(1)
            deb=self.derniere_ligne.find("=",0)
            if float(produit)==float(self.derniere_ligne[deb+1:]):
                print("Consigne de Produit Transmise")
                transmit=True
                self.isProduitSet=True
        transmit=False
        while transmit==False:
            self.envoi_commande("D"+str(destination))
            while not("Destination=" in self.derniere_ligne):
                self.lecture(1)
            deb=self.derniere_ligne.find("=",0)
            if float(destination)==float(self.derniere_ligne[deb+1:]):
                print("Consigne de Destination Transmise")
                transmit=True
                self.isDestinationSet=True
        transmit=False
        while transmit==False:
            self.envoi_commande("S1")
            while not("Start" in self.derniere_ligne):
                self.lecture(1)
            print("Consigne de Demarrage Transmise")
            transmit=True

    def verifdata(self):
        if self.derniere_ligne=="Fermeture Verin":
            print(self.derniere_ligne)
            self.deliveredState=True
            g.delivered=True
            self.isMasseSet=False
            self.isProduitSet=False
            self.isDestinationSet=False
        elif ("MasseFinale=" in self.derniere_ligne):
            print(self.derniere_ligne)
            deb=self.derniere_ligne.find("=",0)
            self.receivedMasseFinale=float(self.derniere_ligne[deb+1:])
            g.massefinale=self.receivedMasseFinale
        elif ("MasseActuelle=" in self.derniere_ligne):
            print(self.derniere_ligne)
            deb=self.derniere_ligne.find("=",0)
            self.receivedMasseActuelle=float(self.derniere_ligne[deb+1:])
            g.masseactuelle=self.receivedMasseActuelle
        elif self.derniere_ligne=="Initialisation terminee":
            print(self.derniere_ligne)
            self.ecriture("B1")
        elif self.derniere_ligne=="Restart":
            print(self.derniere_ligne)
            self.ready=True
        elif self.derniere_ligne=="Start":
            print(self.derniere_ligne)
            self.deliveredState=False
            g.delivered=False
            self.working=True
            self.receivedMasseFinale=0
            g.massefinale=0
        elif self.derniere_ligne=="Stop":
            print(self.derniere_ligne)
            self.working=False
        g.fin=g.delivered
            
    def envoi_commande(self,texte):
        self.ecriture(texte)
        self.lecture(1)
    
    def lecture(self,nb=1):
        i=0
        while i<nb:
            i+=1
            if self.COM.inWaiting()>0:
                try:
                    # Read data incoming on the serial line
                    data=self.COM.readline()
                    data=str(data)
                    deb=data.find("b'")
                    fin=data.find("\\r\\n")
                    self.derniere_ligne=data[deb+2:fin]
                    self.verifdata()
                except:
                    print ("Unexpected error:", sys.exc_info())
                    sys.exit()
    
    def lecture3(self):
        while self.COM.inWaiting()>0:
            try:
                # Read data incoming on the serial line
                data=self.COM.readline()
                data=str(data)
                deb=data.find("b'")
                fin=data.find("\\r\\n")
                self.derniere_ligne=data[deb+2:fin]
                self.verifdata()
            except:
                print ("Unexpected error:", sys.exc_info())
                sys.exit()
        return True

    def lecture2(self,forever=False):
        continu=True
        while continu:
            if self.COM.inWaiting()>0:
                try:
                    # Read data incoming on the serial line
                    data=self.COM.readline()
                    data=str(data)
                    deb=data.find("b'")
                    fin=data.find("\\r\\n")
                    self.derniere_ligne=data[deb+2:fin]
                    self.verifdata()
                except:
                    print ("Unexpected error:", sys.exc_info())
                    sys.exit()
                continu=True
            elif (forever==False):
                continu=False

    def ecriture(self,texte):
        self.COM.write(texte.encode())
        self.COM.flush()

if __name__=="__main__":
    arduino=Arduino()
    lecture(4)