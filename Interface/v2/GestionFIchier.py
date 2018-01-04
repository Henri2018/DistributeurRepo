#!/usr/bin/env python3
# coding: utf-8

import pickle

def SaveData(mon_fichier,data):
    with open(mon_fichier,'wb') as fichier:
        mon_pickler = pickle.Pickler(fichier)
        mon_pickler.dump(data)


def RecupData(mon_fichier):
    try:
        with open(mon_fichier,'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            data=mon_depickler.load()
    except FileNotFoundError:
        print("fichier de sauvegarde non existant")
        data={}
    except EOFError:
        print("fichier vide")
        data={}
    return data

def SaveOrder(mon_fichier,order):
    with open(mon_fichier,'a+b') as fichier:
        mon_pickler = pickle.Pickler(fichier)
        mon_pickler.dump(order)

def RecupAllOrder(mon_fichier):
    data=[]
    try:
        with open(mon_fichier,'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            while True:
                try:
                    data.append(mon_depickler.load())
                except EOFError:
                    break
            
    except FileNotFoundError:
        print("fichier de sauvegarde non existant")
    return data


def RecupLastOrder(mon_fichier):
    try:
        with open(mon_fichier,'rb') as fichier:
            mon_depickler = pickle.Unpickler(fichier)
            data=mon_depickler.load()
    except:
        print("fichier de sauvegarde non existant")
        data={}
    return data