#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import PagesConstructors as PConstruct
import General as g

class PageChoixQuantiteVrac(PConstruct.PrincipalBox):
    
    def __init__(self,name="Produit",variety="/"):
        self.page_name="Choix de la quantité vrac"
        self.m_min=g.m_min
        self.m_max=g.m_max
        self.label_titre=Gtk.Label("")
        self.label_titre.set_alignment(0,0)
        self.label_titre.set_name("body_title")
        self.set_label_titre()
        
        self.rapid_buttons=[]
        self.set_rapid_choice(g.rapid_choice_quantity)
        self.body1=PConstruct.RapidFooterBox(self.rapid_buttons)
        self.inter_label=Gtk.Label("")
        self.set_max_min()
        self.body2=Gtk.Box(orientation=0,spacing=1)
        self.g10=PConstruct.CompteurNombre()
        self.g100=PConstruct.CompteurNombre()
        self.vir=Gtk.Label(",")
        self.vir.set_name("label_avec_fond")
        self.kg1=PConstruct.CompteurNombre()
        self.kg10=PConstruct.CompteurNombre()
        self.val=Gtk.Button("Valider")
        self.val.connect("clicked",self.validate_mass_click)
        self.body2.pack_start(self.g10,False,False,1)
        self.body2.pack_start(self.g100,False,False,1)
        self.body2.pack_start(self.vir,False,False,0)
        self.body2.pack_start(self.kg1,False,False,1)
        self.body2.pack_start(self.kg10,False,False,1)
        self.body2.pack_start(self.val,False,False,5)
        
        PConstruct.PrincipalBox.__init__(self,[self.label_titre,self.body1,self.inter_label,self.body2],body_homogeneous=False)
        
    def set_label_titre(self):
        self.label_titre.set_markup("<big><b>Produit demandé : "+g.order.product_name+"\nVariété demandée : "+g.order.product_variety+"</b></big>\n<big><b>Choississez la quantité désirée :</b></big>\nCliquez sur le bouton correspondant ou Rentrez manuellement la masse désirée.")

    def set_rapid_choice(self,choices):
        self.rapid_buttons=[]
        for m in choices:
            self.rapid_buttons.append((Gtk.Button(str(m)+" kg "),True))
        for but in self.rapid_buttons:
            but[0].connect("clicked",self.rapid_button_clik)
    
    def actualise(self):
        self.set_label_titre()
        self.set_max_min()
        return False
    
    def rapid_button_clik(self,widget):
        lab=widget.get_label()
        quantity=float(lab[:lab.find(" ")])
        self.validate_mass(quantity)
        
    
    def validate_mass_click(self,widget):
        nb=""
        nb+=self.g10.afficheur.get_text()
        nb+=self.g100.afficheur.get_text()
        nb+="."
        nb+=self.kg1.afficheur.get_text()
        nb+=self.kg10.afficheur.get_text()
        nb=float(nb)
        self.validate_mass(masse)
    
    def validate_mass(self,masse):
        self.m_max=float(g.order.get_quantity_max())
        if self.m_max<self.m_min:
            self.m_min=0
        if masse>self.m_max:
            self.verif()
        elif masse<self.m_min:
            self.verif()
        else:
            g.order.set_quantity(masse)
            PConstruct.go_page_fct("",["Choix Mode de Paiement"])
    
    def set_max_min(self):
        self.m_max=min(self.m_max,float(g.order.get_quantity_max()))
        self.m_min=g.m_min
        if self.m_max<self.m_min:
            self.m_min=0
        self.inter_label.set_markup("\n<big><b>Si vous désirez une autre masse, veuillez la rentrer si après</b></big> (masse minimale : "+str(self.m_min)+" kg masse maximale : "+str(self.m_max)+" kg )")
    
    def verif(self):
        dialogue = Gtk.Dialog("Problème avec la masse", None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
        #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
        titre=Gtk.Label("La masse que vous avez saisie n'est pas disponibles")
        dialogue.vbox.pack_start(titre,False,False,20)
        
        titre=Gtk.Label("Rappel : masse minimale : "+str(self.m_min)+" kg masse maximale : "+str(self.m_max)+" kg ")
        dialogue.vbox.pack_start(titre,False,False,20)
        
        dialogue.show_all() #Pour afficher tous les widgets du dialogue
        
        reponse = dialogue.run()
        dialogue.destroy()
    
    
class PageChoixQuantiteNonVrac(PConstruct.PrincipalBox):
    
    def __init__(self,name="Produit",variety="/",rapid_choice=[2.5,5,10],m_min=2.5,m_max=25):
        self.page_name="Choix de la quantité non vrac"
        self.product_name=name
        self.product_variety=variety
        self.m_min=m_min
        self.m_max=m_max
        self.label_titre=Gtk.Label("")
        self.label_titre.set_alignment(0,0)
        self.label_titre.set_name("body_title")
        self.set_label_titre()
        
        self.rapid_buttons=[]
        self.set_rapid_choice(rapid_choice)
        self.body1=PConstruct.RapidFooterBox(self.rapid_buttons)
        self.inter_label=Gtk.Label("</b></big>\n<big><b>Si vous désirez une autre masse, veuillez la rentrer si après</b></big> (masse minimale : "+str(self.m_min)+" masse maximale : "+str(self.m_max)+")")
        self.body2=Gtk.Box(orientation=0,spacing=50)
        self.g10=PConstruct.CompteurNombre()
        self.g100=PConstruct.CompteurNombre()
        self.vir=Gtk.Label(",")
        self.vir.set_name("label_avec_fond")
        self.kg1=PConstruct.CompteurNombre()
        self.kg10=PConstruct.CompteurNombre()
        self.val=Gtk.Button("Valider")
        self.val.connect("clicked",self.validate_mass_click)
        self.body2.pack_start(self.g10,False,False,1)
        self.body2.pack_start(self.g100,False,False,1)
        self.body2.pack_start(self.vir,False,False,0)
        self.body2.pack_start(self.kg1,False,False,1)
        self.body2.pack_start(self.kg10,False,False,1)
        self.body2.pack_start(self.val,False,False,5)
        
        PConstruct.PrincipalBox.__init__(self,[self.label_titre,self.body1,self.inter_label,self.body2],body_homogeneous=False)
        
    def set_label_titre(self):
        self.label_titre.set_markup("<big><b>Produit demandé : "+self.product_name+"\nVariété demandée : "+self.product_variety+"</b></big>\n<big><b>Choississez la quantité désirée :</b></big>\nCliquez sur le bouton correspondant ou Rentrez manuellement la masse désirée.")
    
    def set_rapid_choice(self,choices):
        self.rapid_buttons=[]
        for m in choices:
            self.rapid_buttons.append((Gtk.Button(str(m)+" kg "),True))
        for but in self.rapid_buttons:
            but[0].connect("clicked",self.rapid_button_clik)
    
    def actualise(self):
        self.set_label_titr()
        return False
    
    def rapid_button_clik(self,widget):
        lab=widget.get_label()
        quantity=float(lab[:lab.find(" ")])
    
    def validate_mass_click(self,widget):
        nb=""
        nb+=self.g10.afficheur.get_text()
        nb+=self.g100.afficheur.get_text()
        nb+="."
        nb+=self.kg1.afficheur.get_text()
        nb+=self.kg10.afficheur.get_text()
        nb=float(nb)
        if nb>self.m_max:
            pass
        elif nb<self.m_min:
            pass
        else:
            print(nb)

if __name__=="__main__":
    win=Gtk.Window()
    win.add(PageChoixQuantite())
    win.connect("delete-event",Gtk.main_quit)
    win.show_all()
    Gtk.main()