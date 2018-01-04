#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from time import time

import PagesConstructors as PCons
import General as g

class PageChoixPaiement(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self,orientation=1, spacing=50)
        self.page_name="Choix Mode de Paiement"
        self.prix=g.order.price
        self.affichage=Gtk.Label("Vous devez payez "+str(g.order.price)+" €, pour " + str(g.order.product_quantity) + "kg/unité de "+g.order.product_name)
        self.pack_start(self.affichage,True,True,50)
        self.box2=Gtk.Box(orientation=0,spacing=50)
        self.pack_start(self.box2,True,True,10)
        self.choix1=Gtk.Button("Pièces / Billets")
        self.choix2=Gtk.Button("Carte Bancaire")
        self.dispo1=g.monnaiedispo
        self.dispo2=g.cartedispo
        self.choix1.connect("clicked",self.clickChoix1)
        self.choix2.connect("clicked",self.clickChoix2)
        self.set_choix()
        
    def set_choix(self):
        if self.dispo1:
            self.box2.pack_start(self.choix1,True,True,10)
        if self.dispo2:
            self.box2.pack_end(self.choix2,True,True,10)
        
    def clickChoix1(self,button):
        g.order.mode_de_paiement="Pièces / Billets"
        PCons.go_page_fct(button,["Paiement par Pièces / Billets"])
    
    def clickChoix2(self,button):
        g.order.mode_de_paiement="Carte Bancaire"
        PCons.go_page_fct(button,["Paiement par Carte Bancaire"])
        g.time_begin_paiement=time()
        
    def actualise(self):
        if (self.dispo1!=g.monnaiedispo or self.dispo1!=g.centrale_de_paiement.coinInited or self.dispo1!=g.centrale_de_paiement.billInited):
            if (self.dispo1==True and self.dispo1!=g.monnaiedispo):
                self.box2.remove(self.choix1)
                self.dispo1=False
            elif g.centrale_de_paiement.coinInited and g.centrale_de_paiement.billInited:
                self.box2.pack_start(self.choix1,True,True,10)
                self.dispo1=True
            else:
                self.dispo1=False
                try:
                    self.box2.remove(self.choix1)
                except:
                    pass
                print("Problème d'initialisation du mode de paiement par pièce et par billet")
                print("Etat billet : ",g.centrale_de_paiement.billInited)
                print("Etat pièce : ",g.centrale_de_paiement.coinInited)
            
        if (self.dispo2!=g.cartedispo or self.dispo2!=g.centrale_de_paiement.cashlessInited):
            if (self.dispo2==True and self.dispo2!=g.cartedispo):
                self.box2.remove(self.choix2)
                self.dispo2=False
            elif g.centrale_de_paiement.cashlessInited:
                self.box2.pack_end(self.choix2,True,True,10)
                self.dispo2=True
            else:
                self.dispo2=False
                try:
                    self.box2.remove(self.choix2)
                except:
                    pass
                print("Problème d'initialisation du mode de paiement par carte")
                print("Etat cashless : ",g.centrale_de_paiement.cashlessInited)
                
        self.affichage.set_text("Vous devez payez "+str(g.order.price)+" €, pour " + str(g.order.product_quantity) + "kg/unité de "+g.order.product_name)
        return False

class PageMonnaie(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self,orientation=1,spacing=50)
        self.page_name="Paiement par Pièces / Billets"
        self.affichage=Gtk.Label("Introduisez votre monnaie ou vos pièces")
        self.montant=Gtk.Label("Le montant total est:"+str(g.order.price)+"€")
        self.cred=Gtk.Label("Vous avez déjà introduit :"+str(g.credit)+"€")
        self.restant=Gtk.Label("Restant à payer :"+str(g.order.price-g.credit)+"€")
        self.pack_start(self.affichage,True,True,5)
        self.pack_start(self.montant,True,True,5)
        self.pack_start(self.cred,True,True,5)
        self.pack_start(self.restant,True,True,5)
        
        
    
    def actualise(self):
        self.montant.set_text("Le montant total est:"+str(g.order.price)+"€")
        self.cred.set_text("Vous avez déjà introduit :"+str(g.credit)+"€")
        self.restant.set_text("Restant à payer :"+str(g.order.price-g.credit)+"€")
        g.window.show_all()
        if g.order.price!=0:
            #TODO
            g.credit,prob=g.centrale_de_paiement.vente_par_cash(float(g.order.price),int(g.order.get_product_position()))
        if prob:
            print("Provision non suffisante")
            #TODO
            self.paiement_imossible()
        if ((g.order.price-g.credit)<=0 and (g.order.price!=-1)):
            g.order.set_date_time()
            if g.order.isvrac:
                g.arduino.send_start()
                PCons.go_page_fct(self,["Attente Produit Vrac"])
                g.time_begin_produit=time()
            else:
                PCons.go_page_fct(self,["Servez-vous !"])
            return False
        else:
            return True
        
        def paiement_impossible(self):
            g.credit-=g.centrale_de_paiement.rendu_monnaie(g.credit)
            dialogue = Gtk.Dialog("Problème avec le paiement", None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
            #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
            #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
            titre=Gtk.Label("Il y a eu un problème avec le paiement")
            dialogue.vbox.pack_start(titre,False,False,20)
            
            titre=Gtk.Label("Vous allez être redirigé vers l'écran de choix du mode de paiement")
            dialogue.vbox.pack_start(titre,False,False,20)
            
            dialogue.show_all() #Pour afficher tous les widgets du dialogue
            
            reponse = dialogue.run()
            dialogue.destroy()
            PCons.go_page_fct(self,["Choix Mode de Paiement"])

class PageCarte(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self,orientation=1,spacing=50)
        self.page_name="Paiement par Carte Bancaire"
        self.affichage=Gtk.Label("Payez sans contact ou Insérez votre carte dans le lecteur")
        self.montant=Gtk.Label("Le montant total est:"+str(g.order.price)+"€")
        self.pack_start(self.affichage,True,True,5)
        self.pack_start(self.montant,True,True,5)
    
    def actualise(self):
        self.montant.set_text("Le montant total est:"+str(g.order.price)+"€")
        if g.order.price!=0:
            g.credit=g.centrale_de_paiement.vente_par_carte(float(g.order.price),int(g.order.get_product_position()),time()-g.time_begin_paiement>g.timeout_paiement)
        if g.credit==-1:
            print("Provision non suffisante")
            self.paiement_impossible()
            return False
        if ((g.order.price-g.credit)<=0 and (g.order.product_idnb!=-1)):
            g.credit=0
            g.order.set_date_time()
            if g.order.isvrac:
                g.arduino.send_start()
                PCons.go_page_fct(self,["Attente Produit Vrac"])
                g.time_begin_produit=time()
            else:
                PCons.go_page_fct(self,["Servez-vous !"])
            return False
        else:
            return True

    def paiement_impossible(self):
        dialogue = Gtk.Dialog("Problème avec le paiement", None, Gtk.DialogFlags.MODAL, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
        #Création d'une boîte de dialogue personalisé (Titre, parent, flag, boutons)
        #Les boutons sont créés comme ceci (STOCK, REPONSE, STOCK, REPONSE, ...)
        titre=Gtk.Label("Il y a eu un problème avec le paiement \n ou la carte que vous avez insérez ne permet pas le paiement")
        dialogue.vbox.pack_start(titre,False,False,20)
        
        titre=Gtk.Label("Vous allez être redirigé vers l'écran de choix du mode de paiement")
        dialogue.vbox.pack_start(titre,False,False,20)
        
        dialogue.show_all() #Pour afficher tous les widgets du dialogue
        
        reponse = dialogue.run()
        dialogue.destroy()
        PCons.go_page_fct(self,["Choix Mode de Paiement"])

class PageAttenteVrac(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self)
        self.page_name="Attente Produit Vrac"
        self.affichage=Gtk.Label("Votre Produit est en cours de préparation")
        self.pack_start(self.affichage,True,True,5)
        
    
    def actualise(self):
        if (g.delivered):
            if g.order.mode_de_paiement=="Pièces / Billets":
                g.credit-=g.centrale_de_paiement.rendu_monnaie(g.credit)
                g.centrale_de_paiement.conclure_vente_cash(int(g.order.get_product_position()))
                PCons.go_page_fct(self,["Servez-vous !"])
                return False

            elif g.order.mode_de_paiement=="Carte Bancaire":
                if (g.centrale_de_paiement.conclure_vente_carte(int(g.order.get_product_position()),True)):
                    PCons.go_page_fct(self,["Servez-vous !"])
                    return False
                else:
                    print("Problème avec le paiement par carte")
                    #TODO
                    #Stocker données carte bleue, délivrer produit
                    #Demander Tel pour recontacter, expliquer problème
                    return True
        elif (time()-g.time_begin_produit)>g.timeout_produit:
            #TODO
            #Explication défault
            g.centrale_de_paiement.conclure_vente_carte(int(g.order.get_product_position()),False)
            #Excuse
            #Renvoi page Distributeur non disponible
            #Envoi SMS erreur
            return False
        else:
            return True

class PageFinale(Gtk.Box):
    
    def __init__(self):
        Gtk.Box.__init__(self)
        self.page_name="Servez-vous !"
        self.affichage=Gtk.Label("Votre Produit est disponible")
        if g.order.isvrac:
            self.affichage2=Gtk.Label("N'oubliez pas de placer votre sac")
        else:
            self.affichage2=Gtk.Label("Ouvrez le casier correspondant, la lumière clignote ;)")
        self.pack_start(self.affichage,True,True,5)
        self.pack_start(self.affichage2,True,True,5)

        
    
    def actualise(self):
        if (g.fin):
            g.fin=False
            g.order.next_order(i=-1)
            PCons.go_page_fct(self,["Accueil"])
            return False
        else:
            return True 

if __name__=="__main__":
    win=Gtk.Window()
    win.add(PageChoixPaiement())
    win.connect("delete-event",Gtk.main_quit)
    win.show_all()
    Gtk.main()