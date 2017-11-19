#!/usr/bin/env python3
# coding: utf-8

import pickle

def SaveData(mon_fichier,data):
    with open(mon_fichier,'wb') as fichier:
        mon_pickler = pickle.Pickler(fichier)
        mon_pickler.dump(data)


def RecupData(mon_fichier):
    with open(mon_fichier,'rb') as fichier:
        mon_depickler = pickle.Unpickler(fichier)
        data=mon_depickler.load()
    return data
