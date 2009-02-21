# -*- coding: UTF-8 -*-
import gtk.glade
from gnomecatalog import utils

class GladeConnect:

    def __init__(self, file, signals = None):
        gtk.glade.textdomain("gnomecatalog")

#	print file, utils.locate_file(file, "glade")
        self.glade = gtk.glade.XML(utils.locate_file(file, "glade"), domain = "gnomecatalog")
        self.connect(signals)

    def connect(self, signals = None):
        if signals == None:
            signals = self
        self.glade.signal_autoconnect(signals)

    def __getattr__(self, name):
        result = self.glade.get_widget(name)
        if result == None:
            ## On ne le trouve pas sur l'ui, il serait bon de recherche sur
            ## la fenetre de l'ui
            pass
            if result == None:
                raise AttributeError, name
        return result

    def on_exit(self, source=None, event=None):
        try:
            gtk.main_quit()
        except:
            print "Terminando ejecución..."
