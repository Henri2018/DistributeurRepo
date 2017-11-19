#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import PagesConstructors as PConstruct
import GestionProduits as GProd

class PageAdmin(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self,orientation=0,spacing=15)
        self.page_name="Admin_p1"
        self.inventory_button=Gtk.Button("Gérer les Stocks")
        self.product_button=Gtk.Button("Gérer les produits disponibles")
        self.paiement_button=Gtk.Button("Gérer les modes de paiement")
        
        self.pack_start(self.inventory_button,False,False,10)
        self.pack_start(self.product_button,False,False,10)
        self.pack_start(self.paiement_button,False,False,10)
        
        self.inventory_button.connect("clicked",self.go_PageRechargement)
        self.product_button.connect("clicked",self.go_PageGestionProd)
    
    def go_PageRechargement(self,widget):
        win=self.get_toplevel()
        if not win.previous_page:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Rechargement"])
        elif win.notebook.get_current_page()!=win.previous_page[-1]:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Rechargement"])
    
    def go_PageGestionProd(self,widget):
        win=self.get_toplevel()
        if not win.previous_page:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Admin Produit"])
        elif win.notebook.get_current_page()!=win.previous_page[-1]:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Admin Produit"])

class PageRechargement(PConstruct.PrincipalBox):
    
    def __init__(self):
        self.page_name="Rechargement"
        
        self.label_titre=Gtk.Label("<big><b>Choississez votre produit :</b></big>\nCliquez sur le bouton correspondant.")
        self.label_titre.set_use_markup(True)
        self.label_titre.set_alignment(0,0)
        self.label_titre.set_name("body_title")
        self.body=PConstruct.ProductBox()
        
        PConstruct.PrincipalBox.__init__(self,[self.label_titre,self.body],body_homogeneous=False)
        
        
class PageAdminProd(PConstruct.PrincipalBox):
    
    def __init__(self):
        self.page_name="Admin Produit"
        
        self.label_titre=Gtk.Label("<big><b>Choississez votre produit :</b></big>\nCliquez sur le bouton correspondant.")
        self.label_titre.set_use_markup(True)
        self.label_titre.set_alignment(0,0)
        self.label_titre.set_name("body_title")
        self.add_button=Gtk.Button(stock=Gtk.STOCK_ADD)
        self.body=PConstruct.ProductBox()
        self.footer=self.add_button
        
        PConstruct.PrincipalBox.__init__(self,[self.label_titre,self.body,self.footer],body_homogeneous=False)

        self.add_button.connect("clicked",self.go_PageAddProd)
        
    def go_PageAddProd(self,widget):
        win=self.get_toplevel()
        if not win.previous_page:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Ajouter un produit"])
        elif win.notebook.get_current_page()!=win.previous_page[-1]:
            win.previous_page.append(win.notebook.get_current_page())
            win.notebook.set_current_page(win.dico_pagenb["Ajouter un produit"])
    
    def actualise(self,liste_produit=[],liste_rapid=[]):
        self.body.set_list_button(liste_produit,2)

class PageAddProduct(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self,orientation=0,spacing=15)
        self.page_name="Ajouter un produit"
        self.box1=Gtk.Box(orientation=1, spacing=5)
        
        self.box2=Gtk.Grid()
        self.box2.set_row_homogeneous(True)
        self.box2.set_column_homogeneous(True)
        self.box2.set_name("grid_avec_fond")
        self.pack_start(self.box2,True,True,10)
        self.pack_start(self.box1,True,True,10)
        self.product=GProd.ProduitEnVente()
        self.dico_param={}
        self.create_box2()
        self.save_button.connect("clicked",self.save_data_fct)
        
        
    
    def create_box2(self):
        dic_placement={"stock":7,"prix":8,"nom":0,"abbreviation":1,"position":2,"vrac":3,"disponible":4,"variete":5}
        i=len(dic_placement)+1
        for cle in self.product.__dict__:
            if cle in dic_placement.keys():
                j=dic_placement[cle]
            else:
                j=i
                i+=1
            if (type(self.product.__dict__[cle])==str or type(self.product.__dict__[cle])==int or type(self.product.__dict__[cle])==float):
                entry=Gtk.Entry()
                entry.set_text(str(self.product.__dict__[cle]))
                label=Gtk.Label(" "+cle+" :")
                label.set_name("label_avec_fond")
                label.set_halign(1)
                self.box2.attach(label,0,j,1,1)
                self.box2.attach(entry,1,j,1,1)
                self.dico_param[cle]=(entry,"Entry")


            elif type(self.product.__dict__[cle])==bool:
                entry=Gtk.CheckButton("Vrai?")
                entry.set_active(self.product.__dict__[cle])
                label=Gtk.Label(" "+cle+" :")
                label.set_name("label_avec_fond")
                label.set_halign(1)
                self.box2.attach(label,0,j,1,1)
                self.box2.attach(entry,1,j,1,1)
                self.dico_param[cle]=(entry,"CheckButton")

            elif type(self.product.__dict__[cle])==list:
                for k in range(2):
                    if len(self.product.__dict__[cle])-k>=1:
                        entry=Gtk.Entry()
                        entry.set_text(str(self.product.__dict__[cle][k]))
                        label=Gtk.Label(" "+cle+str(k+1)+" :")
                        label.set_name("label_avec_fond")
                        label.set_halign(1)
                        self.box2.attach(label,0,j+k,1,1)
                        self.box2.attach(entry,1,j+k,1,1)
                        self.dico_param[cle]=(entry,"Entry")
                    else:
                        entry=Gtk.Entry()
                        label=Gtk.Label(" "+cle+str(k+1)+" :")
                        label.set_name("label_avec_fond")
                        label.set_halign(1)
                        self.box2.attach(label,0,j+k,1,1)
                        self.box2.attach(entry,1,j+k,1,1)
                        self.dico_param[cle]=(entry,"Entry")
                
                
        self.save_button=Gtk.Button("Enregistrez les modifications")
        self.box2.attach(self.save_button,0,i,2,2)
    
        
        
    def save_data_fct(self,widget):
        print(self.dico_param["nom"][0].get_text())
        print(GProd.ProduitEnVente.liste_des_noms)
        if not(self.dico_param["nom"][0].get_text() in GProd.ProduitEnVente.liste_des_noms):
            nv_produit=GProd.ProduitEnVente()
            d=nv_produit.__dict__
            for key in self.dico_param.keys():
                if key=="nom":
                    nv_produit.set_nom(self.dico_param[key][0].get_text())
                else:
                    if self.dico_param[key][1]=='Entry':
                        d[key]=self.dico_param[key][0].get_text()
                    elif self.dico_param[key][1]=='CheckButton':
                        d[key]=self.dico_param[key][0].get_active()
            self.product.button=self.product.create_button()
            win=self.get_toplevel()
            win.set_dico_prod()
        
        
        
        
        
        
