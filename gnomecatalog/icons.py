import gtk
import utils
icon_size = w = h = 24
icon_theme = gtk.icon_theme_get_default()


icons = {
					"directory" : icon_theme.load_icon("folder", icon_size, 0),
					"audio": icon_theme.load_icon("audio-x-generic", icon_size, 0),
					"video": icon_theme.load_icon("video-x-generic", icon_size, 0),
					"image": icon_theme.load_icon("image-x-generic", icon_size, 0),
					"package": icon_theme.load_icon("gnome-package", icon_size, 0),
					"default": icon_theme.load_icon("document", icon_size, 0),
					"loading": icon_theme.load_icon("gnome-fs-loading-icon", icon_size, 0),
					"catalog": icon_theme.load_icon("folder", icon_size, 0),
					"cdrom": icon_theme.load_icon("media-optical", icon_size, 0),
					"star_on" : gtk.gdk.pixbuf_new_from_file_at_size(utils.locate_file("star_set.png", "icons"), 16,16),
                    "star_off" : gtk.gdk.pixbuf_new_from_file_at_size(utils.locate_file("star_unset.png", "icons"), 16,16)
		}
