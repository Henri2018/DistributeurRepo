#!/usr/bin/env python3
# coding: utf-8

import sys
import os.path
import glob

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

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject
import MainWindow as MW
import GestionFIchier as GF

win=MW.MainWindow()
win.ouvrir_appli_prod()

#win.fullscreen()
win.show_all()
Gtk.main()

