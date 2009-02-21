import gconf


class Config:
	def __init__(self):
		self.client = gconf.client_get_default()
		self.base = "/apps/gnomeCatalog/"
#		self.client.add_dir("/apps/gnomecatalog", gconf.CLIENT_PRELOAD_NONE)
		if not self.get("database"):
			self.__initConfig()
	
	def get(self, data):
		return self.client.get_string(self.base + data)	
	
	def save(self, data, value):
		self.client.set_string(self.base + data, str(value))

	
	def __initConfig(self):
		self.save("source", "/cdrom")	
		self.save("database", "gnomeCatalog.db")	
		self.save("height", 500)		
		self.save("width", 800)		
		self.save("top", 100)		
		self.save("left", 100)		
