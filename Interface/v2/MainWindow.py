#!/usr/bin/env python3
# coding: utf-8

from os import path as os_path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gio,Gdk,GObject
from os import path as os_path
from time import *
from Pages.PagesConstructors import HeaderBox

import General as g
import GestionProduits as GProd
import GestionFIchier as GFichier

class MainWindow(Gtk.Window):
    
    def __init__(self,space=15):
        super(MainWindow, self).__init__()
        self.set_title("Distributeur v1")
        self.maximize()
        self.connect("delete-event",self.quitter_appli)
        
        #
        self.notebook=Gtk.Notebook()
        self.header=HeaderBox(mode=g.mode_admin)
        self.header.set_size_request=g.header_size
        self.header.set_xalign=0
        self.header.set_yalign=0
        #self.header.set_size_request(100,-1)
        
        
        self.box1=Gtk.Box(orientation=1,spacing=g.spacing)
        
        
        self.box1.pack_start(self.header,False,False,0)
        self.set_style()

        
        #Create Notebook to handle the different pages
        
        self.notebook.set_show_tabs(False)
        self.box1.pack_start(self.notebook,True,True,0)
        self.notebook.set_border_width(10)

        self.add(self.box1)
        
        
        #Add pages to the Notebook
        i=0
        for key in g.dico_pages.keys():
            g.dico_pagenb[key]=i
            self.notebook.append_page(g.dico_pages[key], Gtk.Label(key))
            i+=1
        
        self.set_dico_prod()
        self.notebook.connect("switch-page",self.change_page_fct)
        GObject.timeout_add(60000,self.metAJourTemps)
        GObject.timeout_add(3600000,self.sauver_appli)
        GObject.idle_add(g.set_size)
        self.show_all()
        g.time_switch_page=time()
        self.notebook.set_current_page(g.dico_pagenb["Accueil"])
        self.header.title.set_text("Accueil")
    
    def actualiser_pages(self):
        #new_pages=self.creer_pages(False)
        try:
            g.dico_pages["Admin Produit"].actualise()
        except:
            pass
        try:
            g.dico_pages["Rechargement"].actualise()
        except:
            pass
        try:
            g.dico_pages["Accueil"].actualise()
        except:
            pass
        try:
            g.dico_pages["Choix du produit"].actualise()
        except:
            pass
        self.show_all()
        
    def set_style(self,fichier="Window/ApplicationStyle.css"):
        style_provider=Gtk.CssProvider()
        path=os_path.abspath(os_path.split(__file__)[0])
        background_file_css=Gio.File.new_for_path(path+"/"+fichier)
        style_provider.load_from_file(background_file_css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
    def change_page_fct(self,widget,arg1,arg2):
        self.header.title.set_text(arg1.page_name)
        GObject.idle_add(g.actualise_page,arg1.page_name)
        g.time_switch_page=time()
        
    def metAJourTemps(self):
        if localtime()[3] < 10:
            heures = "0" + str(localtime()[3])
        else:
            heures = str(localtime()[3])
        if localtime()[4] < 10:
            minutes = "0" + str(localtime()[4])
        else:
            minutes = str(localtime()[4])
        '''
        if localtime()[5] < 10:
            secondes = "0" + str(localtime()[5])
        else:
            secondes = str(localtime()[5])
        self.header.time.set_text(str(localtime()[3])+":"+minutes+"."+secondes)
        '''
        self.header.time.set_text(heures+":"+minutes)
        self.header.date.set_text(self.header.jours[localtime()[6]]+" "+str(localtime()[2])+" "+ self.header.mois[localtime()[1]] + " " + str(localtime()[0]))
        return True #Si le retour est True, la boucle continue
        
    def set_dico_prod(self):
        g.dico_prod=GProd.produit_dict
        l_choix=[]
        l_admin1=[]
        l_admin2=[]
        #l_name=[(key,str(self.dico_prod[key])) for key in self.dico_prod.keys()]
        #print(l_name)
        for key in g.dico_prod.keys():
            #print("key",key,self.dico_prod[key])
            if key>0 and g.dico_prod[key].nom!="produit":
                value=g.dico_prod[key]
                #l_name.append(value.nom)
                l_choix.append((value.graphique.button_choix,value.disponible))
                l_admin1.append((value.graphique.button_admin1,value.disponible))
                l_admin2.append((value.graphique.button_admin2,value.disponible))
        g.list_button_prod_choix=l_choix.copy()
        g.list_button_prod_admin1=l_admin1.copy()
        g.list_button_prod_admin2=l_admin2.copy()
        
        self.actualiser_pages()
    
    def ouvrir_appli_prod(self):
        dico=GFichier.RecupData("Sauvegarde_application")
        for key in dico.keys():
            if key>0 and dico[key].nom!="produit":
                nv=dico[key].copy()
                dico[key]=nv
        self.set_dico_prod()
    
    def quitter_appli(self,widget,arg1):
        g.arduino.send_stop()
        g.centrale_de_paiement.quit()
        GFichier.SaveData("Sauvegarde_application",g.dico_prod)
        Gtk.main_quit()
    
    def sauver_appli(self):
        GFichier.SaveData("Sauvegarde_application",g.dico_prod)
    
    def set_header(self):
        self.header=HeaderBox(mode=g.mode_admin)
        self.header.set_size_request=header_size
        self.header.set_xalign=0
        self.header.set_yalign=0
        #self.header.set_size_request(100,-1)
        self.header.title.set_text(self.notebook.get_nth_page(self.notebook.get_current_page()).page_name)
