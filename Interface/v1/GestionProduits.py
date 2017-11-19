#!/usr/bin/env python3
# coding: utf-8


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

produit_dict={}
id_suivant=0

class MetaProduitEnVente(type):

    def __new__(metacls,nom,bases,dict):
        return type.__new__(metacls,nom,bases,dict)
        
    def __init__(cls,nom,bases,dict):
        
        type.__init__(cls,nom,bases,dict)
        global id_suivant
        produit_dict[id_suivant]=cls



class ProduitEnVente(metaclass=MetaProduitEnVente):
    liste_des_noms=[]
    def __init__(self,product_name="produit",product_abbreviation="prod",product_variety=[],product_position="v1",product_vrac=True,product_variety_table=None,product_stock=0,product_available=False,product_icon=None,product_price=0):
        global id_suivant
        self.nom=product_name
        self.abbreviation=product_abbreviation
        id_suivant+=1
        self.idnb=id_suivant
        self.variete=product_variety
        self.position=product_position
        self.vrac=product_vrac
        self.tableau_variete=product_variety_table
        self.stock=product_stock
        self.disponible=product_available
        self.icon=product_icon
        self.button_admin1=self.create_button()
        self.button_admin2=self.create_button()
        self.button_choix=self.create_button()
        self.prix=product_price
        produit_dict[self.idnb]=self
        
        ProduitEnVente.liste_des_noms.append(product_name)

    def __str__(self):
        try:
            return "produit : {},stock :{},id:{}".format(self.nom,self.stock,self.idnb)
        except AttributeError:
            print("Attribut : name, inventory, idnb inexistant")
            return str(self)
        
    def get_nb_produit(self):
        return len(produit_dict)
    
    def add_product(self,quantite=0):
        self.stock+=quantite
    
    def sell_product(self,quantite=0,verif=10):
        self.stock-=quantite
        return (self.stock>=verif)
    
    def create_button(self):
        but=Gtk.Button(label=self.nom)
        if self.icon!=None:
            but.set_image(self.icon)
        but.set_image_position(2)
        but.set_alignment(0.5,0.9)
        but.props.always_show_image=True
        return but
        
    def set_nom(self,name):
        ProduitEnVente.liste_des_noms.remove(self.nom)
        ProduitEnVente.liste_des_noms.append(name)
        self.nom=name
        self.button_admin1.set_label(name)
        self.button_admin2.set_label(name)
        self.button_choix.set_label(name)
        
    def copy(self):
        nv=ProduitEnVente()
        for key in self.__dict__:
            if key[:6]=="button":
                nv.__dict__[key]=self.create_button()
            elif key!="nom":
                nv.__dict__[key]=self.__dict__[key]
           
        nv.set_nom(self.__dict__["nom"])
        return nv

class Commande():
    
    def __init__(self,ordered_product_idnb,quantity_ordered=0):
        pass

if __name__=='__main__':
    
    prod1=ProduitEnVente("1")
    prod2=ProduitEnVente("2")
    print(produit_dict)
