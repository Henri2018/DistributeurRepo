#!/usr/bin/env python3
# coding: utf-8

import sys
import os.path
import glob
import datetime

PATH = os.path.abspath(os.path.split(__file__)[0])
def listdirectory(path):  
    subfolder=[]  
    l = glob.glob(path+'/*')
    for i in l:
        if os.path.isdir(i):
            
            subfolder.extend(listdirectory(i))
            subfolder.append(i)
    return subfolder

directories=listdirectory(PATH)
for i in directories:
    sys.path.append(i)

import UnipiInit
from Scale import Scale
import hx711_allMode as HX711
'''
Start of the script
Warning the pd_sck of each hx need to be different
'''
unipi0=UnipiInit.initialisationUnipi("Ecrire IP")

hx1=HX711.HX711Relais(unipi=unipi0,dout="Ecrire ici entree data1", pd_sck="Ecrire ici sortie1")
hx2=HX711.HX711Relais(unipi=unipi0,dout="Ecrire ici entree data2", pd_sck="Ecrire ici sortie2")

scale=Scale(source=[hx1,hx2])
#Pour tarer la machine
#scale.tare()

#Une fois obtenu placer la reference Unit
ref1=1 # a modifier
ref2=1 # a modifier
scale.setReferenceUnit([ref1,ref2])
scale.reset()
#scale.tare()

#Pour obtenir la reference unit pour la balance globale et non par capteur
#Placer une masse sur la balance puis appeler la fonction suivante avec la valeur de la masse consideree
#si vous rajouter l'element tareBefore=True, la balance va tarer avant de faire l'exercice,
#cette operation permet d'effacer l'effet du plateau de base
masse=1
refbalance=scale.calculateReferenceUnitScale(masse=masse,tareBefore=False)
ref1=hx1.calculateReferenceUnit(masse=masse,tareBefore=False)
ref2=hx2.calculateReferenceUnit(masse=masse,tareBefore=False)

print("Valeur de reference avec masse de {}: \n balance : {} \n capteur1 : {} \n capteur2 : {} ".format(masse,refbalance,ref1,ref2))

def testlectureValeurStatique(nb=1000):
    i=0
    while i<nb:
        i+=1
        try:
            valbalance = scale.getMeasure()
            val1=hx1.getWeight()
            val2=hx2.getWeight()
            print("Balance : {0: 4.4f}  ;  Balance : {0: 4.4f}  ;  Balance : {0: 4.4f}  ;".format(valbalance,val1,val2))

        except (KeyboardInterrupt, SystemExit):
            #GPIO.cleanup()
            sys.exit()

def testlectureValeurDynamique(nb=1000):
    i=0
    while i<nb:
        i+=1
        try:
            heure=datetime.now()
            valbalance = scale.getMeasure()
            delta= datetime.now()-heure
            print("Heure : {} , Balance : {0: 4.4f}  ;  valeur obtenue en {}".format(heure,valbalance,delta.total_seconds()))

        except (KeyboardInterrupt, SystemExit):
            #GPIO.cleanup()
            sys.exit()
