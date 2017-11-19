#!/usr/bin/env python3
# coding: utf-8

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,GObject, GdkPixbuf
from os import path as os_path
from time import *


empty_box=Gtk.Box()

class PrincipalBox(Gtk.Box):
    
    def __init__(self,list_floors=[empty_box]*2,spacing=10,size_top=60,size_bottom=150,body_homogeneous=True):
        Gtk.Box.__init__(self,orientation=1,spacing=10)
        self.nb_floors=len(list_floors)
        self.floors=list_floors
        
        self.pack_start(self.floors[0],body_homogeneous,body_homogeneous,0)
        self.floors[0].set_xalign=0.5
        self.floors[0].set_yalign=0.5
    
        if(self.nb_floors>1):
            for i in range (1,self.nb_floors-1):
                self.pack_start(self.floors[i],True,True,0)
                self.floors[i].set_xalign=0.5
                self.floors[i].set_yalign=0.5
        
        self.floors[-1].set_size_request(0,size_bottom)
        self.pack_start(self.floors[-1],False,True,0)

classic_button1=Gtk.Button()
classic_button2=Gtk.Button()
class ProductBox(Gtk.FlowBox):
    
    def __init__(self,title="Liste des Produits Disponibles",list_button=[],max_child=6):
        Gtk.FlowBox.__init__(self)
        self.set_max_children_per_line(max_child)
        self.set_row_spacing(5)
        self.set_column_spacing(5)
        self.set_selection_mode(1)
        self.set_homogeneous(True)
        self.unselect_all()
        self.label_list=[]
        
        self.set_list_button(list_button,0)
    
    def set_list_button(self,list_child,etat):
        for child in list_child:
            place=len(self.get_children())
            if not(child[0].get_label() in self.label_list):
                
                if etat==0:
                    if child[1]:
                        self.label_list.append(child[0].get_label())
                        self.insert(child[0],place)
                elif etat==1:
                    if child[1]==False:
                        self.label_list.append(child[0].get_label())
                        self.insert(child[0],place)
                elif etat==2:
                    self.label_list.append(child[0].get_label())
                    self.insert(child[0],place)
                    

class RapidFooterBox(Gtk.Box):
    
    def __init__(self,list_rapid_button=[]):
        Gtk.Box.__init__(self,orientation=0,spacing=5)
        self.set_name("RapidFooterBox")
        self.label_list=[]

        self.set_list_button(list_rapid_button,0)
        
    def set_list_button(self,list_child,etat):
        
        for i in range(min(4,len(list_child))):
            child=list_child[i]
            if not(child[0].get_label() in self.label_list):
                
                if etat==0:
                    if child[1]:
                        self.label_list.append(child[0].get_label())
                        self.pack_start(child[0],False,True,5)
                elif etat==1:
                    if child[1]==False:
                        self.label_list.append(child[0].get_label())
                        self.pack_start(child[0],False,True,5)
                elif etat==2:
                    self.label_list.append(child[0].get_label())
                    self.pack_start(child[0],False,True,5)
        


class HeaderBox(Gtk.Box):
    
    
    
    
    def __init__(self,title_label="Titre",time1=Gtk.Label("time1"),date1=Gtk.Label("date1")):
        Gtk.Box.__init__(self,orientation=0,spacing=10)
        self.set_name("HeaderBox")
        self.time=time1
        self.date=date1
        
        
        path=os_path.abspath(os_path.split(__file__)[0])
        filepath= path+"/Image/GO_BACK_BUTTON.png"
        pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_size(filepath,50,50)
        previous_icon = Gtk.Image.new_from_pixbuf(pixbuf)
        
        self.admin_button=Gtk.Button(stock=Gtk.STOCK_EDIT)
        
        self.previous_button=Gtk.Button()
        self.previous_button.set_image(previous_icon)
        self.previous_button.set_border_width(3)
        
        self.title=Gtk.Label(title_label)
        
        #Puisque la fonction localtime() donne des chiffres, il faut les convertir en mots gràce à ces tuples
        self.jours = ('Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche')
        self.mois = ('', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre')
        
        if localtime()[4] < 10: #Si les minutes sont inférieurs à 10, on ajoute un 0 pour que l'affichage soit comme ceci 13:01.05 au lieu de 13:1.5
            minutes = "0" + str(localtime()[4])
        else:
            minutes = str(localtime()[4])

        
        self.time.set_text(str(localtime()[3])+":"+minutes)
        self.date.set_text(self.jours[localtime()[6]]+" "+str(localtime()[2])+" "+ self.mois[localtime()[1]] + " " + str(localtime()[0]))
        
        self.pack_start(self.previous_button,False,False,0)
        self.pack_start(self.title,True,True,0)
        self.pack_start(self.admin_button,False,False,10)
        self.pack_start(self.date,False,False,10)
        self.pack_start(self.time,False,False,10)
        
        self.previous_button.connect("clicked",self.go_back_fct)
        self.admin_button.connect("clicked",self.go_admin_fct)
        
    def go_back_fct(self,widget):
        win=self.get_toplevel()
        if win.previous_page:
            win.notebook.set_current_page(win.previous_page.pop())
    
    def go_admin_fct(self,widget):
        win=self.get_toplevel()
        if not win.previous_page:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Admin_p1"])
        elif win.notebook.get_current_page()!=win.previous_page[-1]:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Admin_p1"])
        
    
