# -*- coding: UTF-8 -*-
import gtk

class ScrolledWindow(gtk.ScrolledWindow):
	def __init__(self,widget,use_view_port=False,shadow=gtk.SHADOW_IN):
		super(ScrolledWindow,self).__init__()
		self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.show()
		if use_view_port:
			self.add_with_viewport(widget)
		else:
			self.add(widget)
		self.set_shadow_type(shadow)
