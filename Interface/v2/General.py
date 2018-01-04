#!/usr/bin/env python3
# coding: utf-8

import time
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject

import Pages.Accueil as Accueil
import Pages.ChoixProduit as ChoixProduit
import Pages.Administrateur as Admin
import Pages.Quantite as Quant
import Pages.Paiement as Paie
import Indisponible as Indispo
import GestionProduits as GProd
import GestionFIchier as GFichier


def new_page(nom):
    b=True
    while b:
        page=Accueil.PageAccueil()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=ChoixProduit.PageChoixProduit()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Admin.PageAdmin()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Admin.PageRechargement()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Admin.PageAdminProd()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Admin.PageAddProduct()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Quant.PageChoixQuantiteVrac()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Quant.PageChoixQuantiteNonVrac()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Paie.PageChoixPaiement()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Paie.PageMonnaie()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Paie.PageCarte()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Paie.PageAttenteVrac()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Paie.PageFinale()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        page=Indispo.PageIndisponible()
        if nom==page.page_name:
            dico_pages[nom]=page
            break
        b=False
    if not b:
        print("Page non trouvée")

arduino=""

centrale_de_paiement=""

window=""
taille_x=0
taille_y=0
bottom_size=150
header_size=80
spacing=10
mode_admin=True

liste_pages=["Accueil","Admin_p1","Rechargement","Admin Produit","Ajouter un produit","Choix du produit","Choix Mode de Paiement","Paiement par Pièces / Billets","Paiement par Carte Bancaire"
             ,"Choix de la quantité non vrac","Choix de la quantité vrac","Servez-vous !","Attente Produit Vrac","Problème"]
dico_pages={}
new_page(liste_pages[0])
dico_pagenb={}
previous_pages=[]
number_pages=len(dico_pages)
current_page_nb=0
time_switch_page=0
time_begin_paiement=0
timeout_paiement=60
time_begin_produit=0
timeout_produit=240
time_session_begin=0
timeout_session=1200
timeout_inactive_session=300
affiche_page_probleme=False

dico_prod={}
list_button_prod_choix=[]
list_button_prod_admin1=[]
list_button_prod_admin2=[]
list_rapid=[]

rapid_choice_quantity=[2.5,5,10]
m_min=1.5
m_max=25

order=GProd.Commande()
masseactuelle=0
massefinale=0
credit=0
delivered=False
fin=True

monnaiedispo=True
cartedispo=True

def actualise_page(nomcurrent):
    return dico_pages[nomcurrent].actualise()
    
def set_current_page(nom):
    if type(nom)==str:
        if not(nom in dico_pages.keys()):
            new_page(nom)
            number_pages=len(dico_pages)
            for key in dico_pages.keys():
                if not (key in dico_pagenb.keys()):
                    dico_pagenb[nom]=window.notebook.insert_page(dico_pages[nom],None,-1)
        window.actualiser_pages()
        window.notebook.set_current_page(dico_pagenb[nom])
    elif type(nom)==int:
        window.actualiser_pages()
        window.notebook.set_current_page(nom)
    

def delete_page(nom):
    if not(nom in previous_pages):
        dico_pages.pop(nom)
        dico_pagenb.pop(nom)
        number_pages=len(dico_pages)
    else:
        print("Page présente dans les pages précédentes")

def get_size(axe,pourcentage):
    if (axe==0 or axe=='h'):
        return pourcentage*taille_y
    if (axe==1 or axe=="l"):
        return pourcentage*taille_x

def set_size():
    couple=window.get_size()
    if couple==(0,0):
        return True
    else:
        global taille_x
        global taille_y
        global spacing
        global bottom_size
        global header_size
        taille_x=couple[0]
        taille_y=couple[1]
        spacing=taille_y*0.05
        bottom_size=taille_y*0.2
        header_size=taille_y*0.1
        return False

def session_begin():
    time_session_begin=time.time()
    GObject.idle_add(check_session_timeout)

def check_session_timeout():
    #TODO a faire si page actuelle différente de accueil et si mode admin=False et si mode indispo =False
    if (time.time()-time_session_begin)>timeout_session:
        #TODO
        return False
    if (itme.time()-time_switch_page)>timeout_inactive_session:
        #TODO
        return False
    return True
    