#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from os import path as os_path

import PagesConstructors as PConstruct

class PageChoixProduit(PConstruct.PrincipalBox):
    def __init__(self):
        self.page_name="Choix du produit"
        
        self.label_titre=Gtk.Label("<big><b>Choississez votre produit :</b></big>\nCliquez sur le bouton correspondant.")
        self.label_titre.set_use_markup(True)
        self.label_titre.set_alignment(0,0)
        self.label_titre.set_name("body_title")
        self.body=PConstruct.ProductBox()
        
        self.rapid_buttons=[(Gtk.Button("Pomme de terre \n MARABEL 5kg"),True),(Gtk.Button("Pomme de terre \n MARABEL 2.5kg"),True),(Gtk.Button("Pomme de terre \n MARABEL 10kg"),True)]
        self.footer=PConstruct.RapidFooterBox(self.rapid_buttons)
        PConstruct.PrincipalBox.__init__(self,[self.label_titre,self.body,self.footer],body_homogeneous=False)
        
    def actualise(self,liste_produit=[],liste_rapid=[]):
        self.body.set_list_button(liste_produit,0)
        self.footer.set_list_button(liste_rapid,0)
