#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from os import path as os_path

import PagesConstructors as PConstruct
import General as g


class PageAccueil(PConstruct.PrincipalBox):
    def __init__(self):
        self.hello_button=Gtk.Button(label="Bonjour!\nCliquez ICI !")
        self.page_name="Accueil"
        
        path=os_path.abspath(os_path.split(__file__)[0])
        filepath= path+"/Image/Potato_icon.png"
        potato_icon = Gtk.Image.new_from_file(filepath)
        self.hello_button.set_image(potato_icon)
        self.hello_button.set_image_position(2)
        self.hello_button.set_size_request(200,200)
        self.hello_button.set_alignment(0.5,0.9)
        self.hello_button.props.always_show_image=True
        
        self.body=Gtk.Fixed()
        self.body.put(self.hello_button,400,100)
        self.rapid_buttons=[(Gtk.Button("Pomme de terre \n MARABEL 5kg"),True),(Gtk.Button("Pomme de terre \n MARABEL 2.5kg"),True),(Gtk.Button("Pomme de terre \n MARABEL 10kg"),True)]
        self.footer=PConstruct.RapidFooterBox(self.rapid_buttons)
        PConstruct.PrincipalBox.__init__(self,[self.body,self.footer])
        
        self.hello_button.connect("clicked",PConstruct.go_page_fct,["Choix du produit"])
        
    
    def actualise(self):
        self.body.move(self.hello_button,int(g.get_size("l",0.45)),int(g.get_size("h",0.2)))
        self.footer.set_list_button(g.list_rapid,0)
        return False
        
            
            
    
