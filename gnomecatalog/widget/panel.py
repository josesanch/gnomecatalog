# -*- coding: UTF-8 -*-
import gtk, gobject

class Information_panel(gtk.VBox):
	__gsignals__ = {
        'comment_changed' : (gobject.SIGNAL_RUN_FIRST,
                        None,
		                (gobject.TYPE_PYOBJECT,))
        }


	current_file = None
	def __init__(self):

		gtk.VBox.__init__(self)

		self.set_size_request(200, -1)

		# Creation of toolbar
		icon_theme = gtk.icon_theme_get_default()
		image = gtk.Image()
		image.set_from_pixbuf(icon_theme.load_icon("window-close", 24, 0))
		toolbar = gtk.Toolbar()
		toolbar.append_item(
					_("Close panel"),
					_("Closes this panel"),
					"Private",         # tooltip private info
					image,
					self.__close)
		toolbar.show()
		self.pack_start(toolbar, False, False)

		self.pane = gtk.VPaned()

		# Creation of the textview for display information
		self.text_info = gtk.TextView()
		self.text_info.show()
		self.text_info.set_size_request(-1, 400)
		self.pane.add(self.text_info)

		vbox = gtk.VBox()
		vbox.show()

		# Creation of the comment label
		label = gtk.Label()
		label.set_markup(_('<b>Comment</b>'))
		label.set_alignment(0.1, 0.5)
		label.show()
		vbox.pack_start(label, False, False, 5)

		# Creation of the comment textview
		self.comment = gtk.TextView()
		self.comment.connect("focus-out-event", self.__update_comment)
		self.comment.show()
		vbox.pack_start(self.comment, True, True, 0)

		self.pane.add(vbox)
		self.pack_start(self.pane)

		self.pane.show()

		self.text_info.set_left_margin(10)
		self.text_info.set_right_margin(10)
		self.text_info.set_editable(False)
		self.text_info.set_wrap_mode(gtk.WRAP_WORD)

		self.text_info_buffer = self.text_info.get_buffer()
		self.text_info_tagtable = self.text_info_buffer.get_tag_table()

		tag = gtk.TextTag("title")
		tag.set_property("font","sans 10")
		tag.set_property("weight", 900)
		tag.set_property("foreground","#202020")
		self.text_info_tagtable.add(tag)

		tag = gtk.TextTag("normal")
		tag.set_property("font","sans 10")
		tag.set_property("foreground","#505050")
		self.text_info_tagtable.add(tag)

		tag = gtk.TextTag("normal_bold")
		tag.set_property("font","sans 9")
		tag.set_property("weight", 700)
		tag.set_property("foreground","#404040")
		self.text_info_tagtable.add(tag)



	def show_info(self, item):
		self.__update_comment()
		self.current_file = item
		self.text_info_buffer.delete(self.text_info_buffer.get_start_iter(), self.text_info_buffer.get_end_iter())
		self.insert("\n")
		self.text_info_buffer.insert_pixbuf(self.text_info_buffer.get_end_iter(), item.get_icon())
		self.insert("\n\n")
		self.insert(item.name + "\n\n", "title")
		if(item.date): self.insert_field(_("Last modification"), item.date)
		if not item.is_dir() and item.size:
			self.insert_field(_("Size"), item.get_size())
		if item.get_duration():
			self.insert_field(_("Duration"), item.get_duration())

		for row in item.metadata:
			self.insert_field(row.key, row.value)
		self.comment.get_buffer().delete(self.comment.get_buffer().get_start_iter(), self.comment.get_buffer().get_end_iter())
		if item.comment:
			self.comment.get_buffer().set_text(item.comment)


	def insert(self, text, tag_name = 'normal'):
		self.text_info_buffer.insert_with_tags_by_name(self.text_info_buffer.get_end_iter(), text, tag_name)

	def insert_field(self, field_name, field_text):
		self.insert(field_name + ": ", 'normal_bold')
		self.insert(str(field_text) + "\n", 'normal')

	def __close(self, widget):
		self.hide()

	def __update_comment(self, widget = None, p = None):

		try:
			if self.current_file.comment != self.comment.get_buffer().get_text(self.comment.get_buffer().get_start_iter(), self.comment.get_buffer().get_end_iter()):
				self.current_file.comment = self.comment.get_buffer().get_text(self.comment.get_buffer().get_start_iter(), self.comment.get_buffer().get_end_iter())
				self.emit("comment-changed" , self.current_file)
		except Exception:
			pass
