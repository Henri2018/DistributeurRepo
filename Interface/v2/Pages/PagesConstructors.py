#!/usr/bin/env python3
# coding: utf-8

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from os import path as os_path
from time import *
import General as g

empty_box=Gtk.Box()

class PrincipalBox(Gtk.Box):
    
    def __init__(self,list_floors=[empty_box]*2,space=10,size_top=60,size_bottom=150,body_homogeneous=True):
        Gtk.Box.__init__(self,orientation=1,spacing=space)
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


class ProductBox(Gtk.FlowBox):
    
    def __init__(self,title="Liste des Produits Disponibles",list_button=[],max_child=6):
        Gtk.FlowBox.__init__(self)
        self.set_max_children_per_line(max_child)
        self.set_row_spacing(5)
        self.set_column_spacing(5)
        self.set_selection_mode(1)
        self.set_homogeneous(True)
        self.unselect_all()
        self.label_list={}
        
        self.set_list_button(list_button,0)
    
    def set_list_button(self,list_child,etat):
        place_list=[]
        present=self.label_list.copy()
        for child in list_child:
            if child[0].get_label() in present.keys():
                present[child[0].get_label()]=True
        for key in present.keys():
            if not(present[key]==True):
                pl=self.label_list[key]
                flowchild=self.get_child_at_index(pl)
                place_list.append(pl-1)
                self.remove(flowchild)
        fin=len(self.label_list.keys())
        place_list.append(fin)
        for child in list_child:
            place_list.append(place_list[-1]+1)
            place=place_list.pop(0)
            if not(child[0].get_label() in self.label_list.keys()):
                
                if etat==0:
                    if child[1]:
                        self.label_list[child[0].get_label()]=place
                        self.insert(child[0],place)
                elif etat==1:
                    if child[1]==False:
                        self.label_list[child[0].get_label()]=place
                        self.insert(child[0],place)
                elif etat==2:
                    self.label_list[child[0].get_label()]=place
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
    
    
    
    
    def __init__(self,title_label="Titre",time1=Gtk.Label("time1"),date1=Gtk.Label("date1"),mode=False):
        Gtk.Box.__init__(self,orientation=0,spacing=10)
        self.set_name("HeaderBox")
        self.time=time1
        self.date=date1
        
        
        path=os_path.abspath(os_path.split(__file__)[0])
        filepath= path+"/Image/GO_BACK_BUTTON.png"
        pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_size(filepath,50,50)
        previous_icon = Gtk.Image.new_from_pixbuf(pixbuf)
        
        self.mode_admin=mode
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
        if self.mode_admin:
            self.pack_start(self.admin_button,False,False,10)
        self.pack_start(self.date,False,False,10)
        self.pack_start(self.time,False,False,10)
        
        self.previous_button.connect("clicked",go_back_fct,self)
        self.admin_button.connect("clicked",go_page_fct,["Admin_p1"])


class CompteurNombre(Gtk.Box):
    
    def __init__(self,initial=0):
        Gtk.Box.__init__(self,orientation=1,spacing=15)
        self.nombre_affiche=initial
        self.buttonplus=Gtk.Button("+")
        self.buttonplus.set_size_request(100,100)
        self.buttonmoins=Gtk.Button("-")
        self.buttonmoins.set_size_request(100,100)
        self.afficheur=Gtk.Label(str(self.nombre_affiche))
        self.afficheur.set_name("label_avec_fond")
        
        self.pack_start(self.buttonplus,False,False,10)
        self.pack_start(self.afficheur,True,True,10)
        self.pack_start(self.buttonmoins,False,False,10)
        
        
        self.buttonplus.connect("clicked",self.plus)
        self.buttonmoins.connect("clicked",self.moins)
    def plus(self,widget):
        self.set_nombre(1)
    
    def moins(self,widget):
        self.set_nombre(-1)
    
    def set_nombre(self,increment):
        self.nombre_affiche=(self.nombre_affiche+increment)%10
        self.afficheur.set_text(str(self.nombre_affiche))

def go_back_fct(widget,self):
    if g.previous_pages:
        g.set_current_page(g.previous_pages.pop())
    
def go_page_fct(widget,page):
    page=page[0]
    if g.window.notebook.get_current_page()==0:
        g.session_begin()
    if not g.previous_pages:
        g.previous_pages.append(g.window.notebook.get_current_page())
        g.set_current_page(page)
    elif g.window.notebook.get_current_page()!=g.previous_pages[-1]:
        pr=g.window.notebook.get_current_page()
        g.set_current_page(page)
        if g.window.notebook.get_current_page() in g.previous_pages:
            g.previous_pages.remove(g.window.notebook.get_current_page())
        g.previous_pages.append(pr)

def clavier(output):
    res=Gtk.Box(orientation=1,spacing=10)
    ligne=Gtk.Box(orientation=0,spacing=5)
    for i in range(1,10):
        but=Gtk.Button(str(i))
        but.connect("clicked",clavier_click,output)
        ligne.pack_start(but,False,False,5)
        
        if i%3==0:
            res.pack_start(ligne,False,False,5)
            ligne=Gtk.Box(orientation=0,spacing=5)
    but=Gtk.Button("0")
    but.connect("clicked",clavier_click,output)
    ligne.pack_start(but,False,False,5)
    but=Gtk.Button("-")
    but.connect("clicked",clavier_click,output)
    ligne.pack_start(but,False,False,5)
    but=Gtk.Button("Corriger")
    but.connect("clicked",clavier_click,output)
    ligne.pack_start(but,True,True,5)
    res.pack_start(ligne,False,False,5)
    return res
     
def clavier_click(widget,output):
    v=widget.get_label()
    if (v=="Corriger"):
        output.set_text(output.get_text()[:-1])
        if output.get_text()=="":
            output.set_text("0")
    elif (v=="-"):
        if output.get_text()=="0":
            output.set_text("-")
    elif output.get_text()=="0":
        output.set_text(v)
    else:
        output.set_text(output.get_text()+v)
    
if __name__=="__main__":
    win=Gtk.Window()
    hbox=Gtk.Box(orientation=1)
    lab=Gtk.Label("0")
    clav=clavier(lab)
    hbox.pack_start(lab,False,False,5)
    hbox.pack_start(clav,False,False,5)
    win.add(hbox)
    
    win.show_all()
    win.connect("delete-event",Gtk.main_quit)
    Gtk.main()