#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from os import path as os_path

import PagesConstructors as PConstruct
import General as g


class PageIndisponible(Gtk.Box):
    def __init__(self):
        self.page_name="Problème"
        
        path=os_path.abspath(os_path.split(__file__)[0])
        filepath= path+"/Image/Potato_icon.png"
        icon = Gtk.Image.new_from_file(filepath)
        self.message=Gtk.Label("Nous sommes désolé mais nous rencontrons un problème technique \n Merci de bien vouloir nous excuser. \n Nous tentns de résoudre ce problème le plus rapidement possible")
        
        self.body=Gtk.Box()
        self.body.pack_start(icon,True,True,10)
        self.body.pack_start(self.message,True,True,10)
        self.body.set_center_widget()
    
    def actualise(self):
        return False
        
            
            
    

