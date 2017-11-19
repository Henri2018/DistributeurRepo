#!/usr/bin/env python3
# coding: utf-8

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,GdkPixbuf



class TestGdkPixbuf(Gtk.Window):
    Cover= "Image/Potato_icon.png"
    Cover2= "Image/GO_BACK_BUTTON.png"

    def __init__(self):
        Gtk.Window.__init__(self, title="TestGdkPixbuf")
        self.connect("delete-event",Gtk.main_quit)
        mainLayout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)


        self.image = GdkPixbuf.Pixbuf.new_from_file_at_size(self.Cover, 250, 250)
        self.image_renderer = Gtk.Image.new_from_pixbuf(self.image)

        button = Gtk.Button(label='Change')
        button.connect('clicked', self.editPixbuf)

        mainLayout.pack_start(self.image_renderer, True, True, 0)
        mainLayout.pack_start(button, True, True, 0)

        self.add(mainLayout)

    def editPixbuf(self, button):
        self.image = GdkPixbuf.Pixbuf.new_from_file_at_size(self.Cover2, 250, 250)
        self.image_renderer.set_from_pixbuf (self.image)
        print(self.Cover2)

win=TestGdkPixbuf()
win.show_all()
Gtk.main()
