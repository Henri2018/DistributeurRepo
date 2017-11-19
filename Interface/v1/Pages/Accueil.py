#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from os import path as os_path

import PagesConstructors as PConstruct


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
        
        self.hello_button.connect("clicked",self.hello_button_fct)
    
    def hello_button_fct(self,widget):
        win=self.get_toplevel()
        win.previous_page.append(win.notebook.get_current_page())
        win.notebook.set_current_page(win.dico_pagenb["Choix du produit"])
        
    def actualise(self,liste_produit=[],liste_rapid=[]):
        self.footer.set_list_button(liste_rapid,0)
        
            
            
    
