# -*- coding: UTF-8 -*-
import gtk
import gnomecatalog


class MainMenu(gtk.UIManager):
	def __init__(self, mainApp):
		self.mainApp = mainApp
		gtk.UIManager.__init__(self)
		ag = gtk.ActionGroup('GnomeCatalog')

		ag.add_actions([

                        ('File', None, _('File')),
                        ('New', gtk.STOCK_NEW, _('New File')),
						('Open', gtk.STOCK_OPEN, _('Open File')),
						('Save', gtk.STOCK_SAVE, _('Save File')),
						('SaveAs', gtk.STOCK_SAVE_AS, _('Save As')),
						('NewDisk', gtk.STOCK_ADD, _('New disk')),
						('NewCatalog', gtk.STOCK_DIRECTORY, _('New catalog')),
						('Import', None, _('Import')),
						('Export', None, _('Export')),
						('Quit', gtk.STOCK_QUIT, _('Quit'), None, '', self.mainApp.quit),
                        ('View', None, _('View')),
#   						('InformationPanel', gtk.STOCK_DIALOG_INFO, _('Information panel'), 'F9', '', self.mainApp.on_menu_information_panel),
   						('Preferences', gtk.STOCK_PREFERENCES, _('Preferences'), None, '', self.mainApp.on_toolbutton_preferencias_clicked),
						('Help', None, _('_Help')),
						('About', gtk.STOCK_ABOUT, _('_About'), None ,"", self.open_about_dialog)
						])
		ag.add_toggle_actions([('InformationPanel', None, _('_Information panel'), "F9", None, self.mainApp.on_menu_information_panel)])

		self.add_ui_from_string(self.get_menu())
		self.mainApp.mainApp.add_accel_group(self.get_accel_group())
  		self.insert_action_group(ag, -1)


	def get_menu(self):
		return """
			<ui>
				<menubar name="MenuBar">
					<menu action="File">
						<menuitem action="New"/>
						<menuitem action="Open"/>
						<menuitem action="Save"/>
						<menuitem action="SaveAs"/>
						<separator />
						<menuitem action="NewDisk"/>
						<menuitem action="NewCatalog"/>
						<separator />
						<menuitem action="Import"/>
						<menuitem action="Export"/>
						<separator />
						<menuitem action="Quit"/>
					</menu>
					<menu action="View">
						<menuitem action="InformationPanel"/>
						<menuitem action="Preferences"/>
					</menu>

					<menu action="Help">
						<menuitem action="About"/>
					</menu>
				</menubar>
			</ui>
			"""

	def open_about_dialog(self):
		print "about"

	def preferences(self):
		print "preferences"

class MenuDisks(gtk.UIManager):

	def __init__(self):
#		self.mainApp = mainApp
		gtk.UIManager.__init__(self)
		ag = gtk.ActionGroup('GnomeCatalog')

		ag.add_actions([
                        ('Rename', gtk.STOCK_EDIT, _('Rename'), 'F2', '', self.on_rename),
                        ('Information', gtk.STOCK_INFO, _('Information'), None, '', self.on_information),
                        ])

		menu = """
		<ui>
			<popup>
					<menuitem action="Rename"/>
					<menuitem action="Information"/>

			</popup>
		</ui>
		"""

		self.add_ui_from_string(menu)
#		self.mainApp.mainApp.add_accel_group(self.get_accel_group())
  		self.insert_action_group(ag, -1)

  	def on_rename(self, widget):
  		print "rename"

  	def on_information(self, widget):
		app = gnomecatalog.GnomecatalogApp.instance
		item = app.treeDisks.get_selected()
