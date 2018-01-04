#!/usr/bin/env python3
# coding: utf-8


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import PagesConstructors as PCons
from GestionFIchier import SaveOrder
from GestionFIchier import RecupData
from time import *
import General as g

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
    def __init__(self,product_name="produit",product_abbreviation="prod",product_variety="",product_position="1",product_vrac=True,product_variety_table=None,product_stock=0,product_available=False,product_icon=None,product_price=0):
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
        self.graphique=None
        self.set_graphique()
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
        self.graphique.set_name(name)
        
    def copy(self):
        nv=ProduitEnVente()
        for key in self.__dict__:
            if key=="graphique":
                nv.__dict__[key]=ProduitEnVenteGtk(idnb=nv.idnb)
            elif (key!="nom" and key!="idnb"):
                nv.__dict__[key]=self.__dict__[key]   
        nv.set_nom(self.__dict__["nom"])
        return nv
    
    def set_graphique(self):
        self.graphique=ProduitEnVenteGtk(self.idnb,self.nom,self.icon)

        


class ProduitEnVenteGtk():
    
    def __init__(self,idnb=0,nom="produit",icon=None):
        self.idnb=idnb
        self.nom=nom
        self.product=None
        self.button_admin1=self.create_button(nom,icon)
        self.button_admin2=self.create_button(nom,icon)
        self.button_choix=self.create_button(nom,icon)
        self.dico_param={}
        self.page_admin2=None
        self.page_choix=None
        
        self.button_admin1.connect("clicked",self.create_page_admin1)
        self.button_admin2.connect("clicked",self.create_page_recharg)
        self.button_choix.connect("clicked",self.choix_quantite_click)


    def set_name(self,name):
        self.nom=name
        self.button_admin1.set_label(name)
        self.button_admin2.set_label(name)
        self.button_choix.set_label(name)
        
    
    def create_button(self,nom,icon=None):
        but=Gtk.Button(label=nom)
        if icon!=None:
            but.set_image(icon)
        but.set_image_position(2)
        but.set_alignment(0.5,0.9)
        but.props.always_show_image=True
        return but
    
    def choix_quantite_click(self,widget):
        self.product=produit_dict[self.idnb]
        g.order.set_product_from_id(self.idnb)
        if self.product.vrac:
            PCons.go_page_fct("",["Choix de la quantité vrac"])
        else:
            PCons.go_page_fct("",["Choix de la quantité non vrac"])
        
    def create_page_recharg(self,widget):
        if self.product==None:
            self.product=produit_dict[self.idnb]
        dialogue = Gtk.Dialog("Recharger ce produit: "+self.nom, None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
        #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
        titre=Gtk.Label("Recharger de produit: "+self.nom)
        dialogue.vbox.pack_start(titre,False,False,20)
        
        boiteH = Gtk.Box(orientation=0,spacing=5)
        entry=Gtk.Label(" "+str(self.product.stock)+" ")
        label=Gtk.Label(" Stock actuel : ")
        label.set_name("label_avec_fond")
        label.set_halign(1)
        boiteH.pack_start(label,False,False,20)
        boiteH.pack_start(entry,False,False,20)
        dialogue.vbox.pack_start(boiteH,False,False,20)
        
        boiteH = Gtk.Box(orientation=0,spacing=5)
        entry1=Gtk.Label()
        entry1.set_text("0")
        label=Gtk.Label(" Quantité que vous rajoutez: ")
        label.set_name("label_avec_fond")
        label.set_halign(1)
        boiteH.pack_start(label,False,False,20)
        boiteH.pack_start(entry1,False,False,20)
        dialogue.vbox.pack_start(boiteH,False,False,20)
         #La boîte déjà créée contient les boutons
        
        clavier=PCons.clavier(entry1)
        dialogue.vbox.pack_start(clavier,False,False,20)
        
        dialogue.show_all() #Pour afficher tous les widgets du dialogue
        
        reponse = dialogue.run()
        if reponse == Gtk.ResponseType.OK: #Si l'on clique sur le bouton OK
            d=self.product.__dict__
            d["stock"]=float(d["stock"])+float(entry1.get_text())
        dialogue.destroy()
    
    
    def create_page_admin1(self,widget):
        if self.product==None:
            self.product=produit_dict[self.idnb]
        dialogue = Gtk.Dialog("Propriete de "+self.nom, None, Gtk.DialogFlags.MODAL, ("Supprimer", Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
        #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
        boiteH = self.create_box_admin1()
        titre=Gtk.Label("Propriete du produit:")
        dialogue.vbox.pack_start(titre,False,False,20)
        dialogue.vbox.pack_start(boiteH,False,False,20) #La boîte déjà créée contient les boutons
        
        dialogue.show_all() #Pour afficher tous les widgets du dialogue
        
        reponse = dialogue.run()
        if reponse == Gtk.ResponseType.OK: #Si l'on clique sur le bouton OK
            self.save_data_admin1(widget)
        elif reponse == Gtk.ResponseType.CANCEL:
            
            self.supprimer()
            g.window.set_dico_prod()
        dialogue.destroy()


    
    def create_box_admin1(self):
        box2=Gtk.Grid()
        box2.set_row_homogeneous(True)
        box2.set_column_homogeneous(True)
        box2.set_name("grid_avec_fond")
        dic_placement={"stock":7,"prix":8,"nom":0,"abbreviation":1,"position":2,"vrac":3,"disponible":4,"variete":5}
        i=len(dic_placement)+1
        for cle in self.product.__dict__:
            if cle in dic_placement.keys():
                j=dic_placement[cle]
            else:
                j=i
                i+=1
            if cle!="idnb":
                if (type(self.product.__dict__[cle])==str or type(self.product.__dict__[cle])==int or type(self.product.__dict__[cle])==float):
                    entry=Gtk.Entry()
                    entry.set_text(str(self.product.__dict__[cle]))
                    label=Gtk.Label(" "+cle+" :")
                    label.set_name("label_avec_fond")
                    label.set_halign(1)
                    box2.attach(label,0,j,1,1)
                    box2.attach(entry,1,j,1,1)
                    self.dico_param[cle]=(entry,"Entry")


                elif type(self.product.__dict__[cle])==bool:
                    entry=Gtk.CheckButton("Vrai?")
                    entry.set_active(self.product.__dict__[cle])
                    label=Gtk.Label(" "+cle+" :")
                    label.set_name("label_avec_fond")
                    label.set_halign(1)
                    box2.attach(label,0,j,1,1)
                    box2.attach(entry,1,j,1,1)
                    self.dico_param[cle]=(entry,"CheckButton")

                elif type(self.product.__dict__[cle])==list:
                    for k in range(2):
                        if len(self.product.__dict__[cle])-k>=1:
                            entry=Gtk.Entry()
                            entry.set_text(str(self.product.__dict__[cle][k]))
                            label=Gtk.Label(" "+cle+str(k+1)+" :")
                            label.set_name("label_avec_fond")
                            label.set_halign(1)
                            box2.attach(label,0,j+k,1,1)
                            box2.attach(entry,1,j+k,1,1)
                            self.dico_param[cle]=(entry,"Entry")
                        else:
                            entry=Gtk.Entry()
                            label=Gtk.Label(" "+cle+str(k+1)+" :")
                            label.set_name("label_avec_fond")
                            label.set_halign(1)
                            box2.attach(label,0,j+k,1,1)
                            box2.attach(entry,1,j+k,1,1)
                            self.dico_param[cle]=(entry,"Entry")
        return box2
    
    def supprimer(self):
        dialogue = Gtk.Dialog("Propriete de "+self.nom, None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
        #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
        titre=Gtk.Label("Etes vous sur de vouloir supprimer ce produit ?")
        dialogue.vbox.pack_start(titre,False,False,20)
        
        dialogue.show_all() #Pour afficher tous les widgets du dialogue
        
        reponse = dialogue.run()
        if reponse == Gtk.ResponseType.OK: #Si l'on clique sur le bouton OK
            del(produit_dict[self.idnb])
            del(self.product)
            del(self)

        dialogue.destroy()
        
        
        
    def save_data_admin1(self,widget):
        if not(self.dico_param["nom"][0].get_text() in ProduitEnVente.liste_des_noms) or self.dico_param["nom"][0].get_text()==self.nom:
            d=self.product.__dict__
            for key in self.dico_param.keys():
                if key=="nom":
                    self.product.set_nom(self.dico_param[key][0].get_text())
                    self.set_name(self.dico_param[key][0].get_text())
                else:
                    if self.dico_param[key][1]=='Entry':
                        d[key]=self.dico_param[key][0].get_text()
                        if type(d[key])==float:
                            try:
                                d[key]=float(self.dico_param[key][0].get_text())
                            except:
                                pass
                        elif type(d[key])==int:
                            try:
                                d[key]=int(self.dico_param[key][0].get_text())
                            except:
                                pass
                        else:
                            d[key]=self.dico_param[key][0].get_text()
                    elif self.dico_param[key][1]=='CheckButton':
                        d[key]=self.dico_param[key][0].get_active()
            g.window.set_dico_prod()
        else:
            dialogue = Gtk.Dialog("Probleme avec le Nom", None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
            #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
            #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
            boiteH = Gtk.HBox()
            expli=Gtk.Label("Le nom que vous avez rentré est déjà utilisé, veuillez en entrer un autre:")
            dialogue.vbox.pack_start(expli,False,False,20)
            dialogue.vbox.pack_start(boiteH,False,False,20) #La boîte déjà créée contient les boutons
            zoneTexte1 = Gtk.Entry()
            zoneTexte1.set_text("Ecrivez le bon nom ici")
            boiteH.pack_start(zoneTexte1, False,False,10)
            
            dialogue.show_all() #Pour afficher tous les widgets du dialogue
            
            reponse = dialogue.run()
            
            if reponse == Gtk.ResponseType.OK: #Si l'on clique sur le bouton OK
                self.dico_param["nom"][0].set_text(zoneTexte1.get_text())
                self.save_data_admin1(widget)
            dialogue.destroy()
        

class Commande():
    id_order_suivant=0
    fichier_backup="Historique_de_commande.txt"
    def __init__(self,ordered_product_idnb=-1,quantity_ordered=0,modepaiement=""):
        last_order=RecupData(Commande.fichier_backup)
        if last_order!={}:
            Commande.id_order_suivant=last_order["id_order"]
        Commande.id_order_suivant+=1
        self.id_order=Commande.id_order_suivant
        self.product_idnb=ordered_product_idnb
        if ordered_product_idnb!=-1:
            self.isvrac=produit_dict[self.product_idnb].vrac
            self.product_name=produit_dict[self.product_idnb].nom
            self.product_variety=produit_dict[self.product_idnb].variete
            self.price_per_unit=float(produit_dict[self.product_idnb].prix)
        else:
            self.isvrac=True
            self.product_name=""
            self.product_variety=""
            self.price_per_unit=0
        self.product_quantity=quantity_ordered
        self.price=self.product_quantity*self.price_per_unit
        self.mode_de_paiement=modepaiement
        self.product_destination=0
        self.is_paye=False
        self.date=None
        self.time=None
    
    def __str__(self):
        return "Commande numero {} \n {} , {} \n Produit : {} \n Prix au kg/Unité : {}\n Quantité : {}\n Prix : {} \n Mode de Paiement : {}".format(self.id_order,self.date,self.time,self.get_product_name(), self.price_per_unit,self.product_quantity,self.price,self.mode_de_paiement)
    
    def set_destination(self,dest):
        self.product_destination=dest
        g.arduino.set_destination(dest)
    
    def set_id_order_next(self,i):
        Commande.id_order_suivant=i

    def set_date_time(self):
        now=localtime()
        if now[3] < 10:
            heures = "0" + str(now[3])
        else:
            heures = str(localtime()[3])
        if localtime()[4] < 10:
            minutes = "0" + str(now[4])
        else:
            minutes = str(now[4])
        if now[5] < 10:
            secondes = "0" + str(now[5])
        else:
            secondes = str(now[5])
        self.time=heures+":"+minutes+":"+secondes
        self.date=str(now[2])+"/"+ str(now[1]) + "/" + str(now[0])
        self.ispaye=True
        produit_dict[self.product_idnb].stock=float(produit_dict[self.product_idnb].stock)-float(self.product_quantity)
    
    def get_product_name(self):
        return (produit_dict[self.product_idnb].nom+" "+produit_dict[self.product_idnb].variete)
    
    def get_product_position(self):
        return produit_dict[self.product_idnb].position
    
    def is_quantity_dispo(self,quantity):
        return produit_dict[self.product_idnb].stock>=quantity
    
    def get_quantity_max(self):
        return produit_dict[self.product_idnb].stock
    
    def set_quantity(self,quantity):
        self.product_quantity=float(quantity)
        self.price=self.product_quantity*self.price_per_unit
        g.arduino.set_masse(objectif=quantity)
    
    def next_order(self,i=-1):
        if self.product_idnb!=-1:
            SaveOrder(Commande.fichier_backup,self.__dict__)
            Commande.id_order_suivant+=1
        self.id_order=Commande.id_order_suivant
        self.product_idnb=i
        if i!=-1:
            self.isvrac=produit_dict[self.product_idnb].vrac
            self.product_name=produit_dict[self.product_idnb].nom
            self.product_variety=produit_dict[self.product_idnb].variete
            self.price_per_unit=float(produit_dict[self.product_idnb].prix)
        else:
            self.isvrac=True
            self.product_name=""
            self.product_variety=""
            self.price_per_unit=0
        self.product_quantity=0
        self.price=self.product_quantity*self.price_per_unit
        self.mode_de_paiement=""
        self.date=None
        self.time=None
        self.ispaye=False

    def set_product_from_id(self,i):
        self.product_idnb=i
        self.isvrac=produit_dict[self.product_idnb].vrac
        self.product_name=produit_dict[self.product_idnb].nom
        self.product_variety=produit_dict[self.product_idnb].variete
        self.price_per_unit=float(produit_dict[self.product_idnb].prix)
        self.price=self.product_quantity*self.price_per_unit
        g.arduino.set_produit(produit_dict[self.product_idnb].position)
    
if __name__=='__main__':
    
    prod1=ProduitEnVente("1")
    prod2=ProduitEnVente("2")
    print(produit_dict)
    
    order1=Commande()
