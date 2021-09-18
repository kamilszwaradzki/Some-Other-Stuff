#!/usr/bin/env python
"""
how to run the script with a doubleclick? (work with Gnome)

> sudo apt install dconf-editor (if it is not installed.)
> dconf-editor
> org -> gnome -> nautilus -> preferences -> executable-text-activation
> use default value -> off
> other value -> launch

install required packages(on Ubuntu)
sudo apt install python3-bs4 python3-gi gobject-introspection gir1.2-gtk-3.0
"""

from bs4 import BeautifulSoup
import requests
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

soup = BeautifulSoup(requests.get(r"https://lowcygier.pl/darmowe/").text,"html.parser")

class LinkButtonWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="List of free games")
        self.set_border_width(10)
        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box_outer.pack_start(listbox, True, True, 0)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(vbox, True, True, 0)
        
        y = {x.text:x.get('href') for x in soup.find_all("a") if  "darmo" in str(x)}
        y = { x:y[x] for x in y.keys()  if ('Store' in x or 'GOG' in x or 'Steam' in x) and 'darmowy' not in x and 'Darmowy' not in x}
        for x in y.keys():
            vbox.pack_start(Gtk.LinkButton(y[x], x,  xalign=0), True, True, 0)
        listbox.add(row)

win = LinkButtonWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
