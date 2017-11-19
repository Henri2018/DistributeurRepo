#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gdk,Gio

class AccueilBox(Gtk.Grid):
	
	def __init(self):
		Gtk.Grid.__init__(self)
		hello_button=Gtk.Button(label="Bonjour !")

		Rapid1_button=Gtk.Button(label="Choix Rapide 1")

		version_label=Gtk.Label("Version 1.0")
		info_label=Gtk.Label("Marabel : 4€ les 5 kg")
		self.add(version_label)

		self.attach(info_label,4,1,1,1)
		self.attach(hello_button,2,2,1,1)
		self.attach(Rapid1_button,0,4,1,1)
		self.set_column_homogeneous(True)
		self.set_row_homogeneous(True)
		self.set_row_spacing(20)
		self.set_column_spacing(20)

window = Gtk.Window(title="Accueil")
style_provider=Gtk.CssProvider()
background_file_css=Gio.File.new_for_path("AccueilStyle_v1.css")
style_provider.load_from_file(background_file_css)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
grid=Gtk.Box()
sublayout=AccueilBox()
grid.pack_start(sublayout,True,True,0)
window.add(grid)
window.show_all()
window.connect("destroy", Gtk.main_quit)
Gtk.main()
