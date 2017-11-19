#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gdk,Gio

class AccueilBox(Gtk.Box):
    def __init__(self):
		Gtk.Box.__init__(self,orientation=1,spacing=20)
		
		hello_button=Gtk.Button(label="Bonjour !")
		
		Rapid1_button=Gtk.Button(label="Choix Rapide 1")
		Rapid1_button.set_size_request(0,150)
		box1=Gtk.Box()
		box1.set_size_request(0,150)
		version_label=Gtk.Label("Version 1.0")
		version_label.set_xalign(0)
		version_label.set_yalign(0)
		info_label=Gtk.Label("Marabel : 4€ les 5 kg")
		self.pack_start(box1,False,True,0)
		self.set_size_request(0,150)
		self.pack_start(hello_button,True,True,0)
		self.pack_start(Rapid1_button,False,True,0)
		

class MainWindow(Gtk.Window):
	
	def __init__(self):
		Gtk.Window.__init__(self,title="Distributeur_v1")

		style_provider=Gtk.CssProvider()
		background_file_css=Gio.File.new_for_path("AccueilStyle_v1.css")
		style_provider.load_from_file(background_file_css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


		self.connect("delete-event",Gtk.main_quit)

		self.notebook=Gtk.Notebook()
		self.notebook.set_show_tabs(False)
		self.add(self.notebook)

		self.page1=AccueilBox()
		self.notebook.append_page(self.page1, Gtk.Label('Page1'))
		self.page2 = Gtk.Box()
		self.page2.set_border_width(10)
		self.page2.add(Gtk.Label('A page with an image for a Title.'))
		self.notebook.append_page(
			self.page2,
			Gtk.Image.new_from_icon_name(
				"help-about",
				Gtk.IconSize.MENU
			)
		)

		self.show_all()
		
win=MainWindow()
win.show_all()
Gtk.main()
