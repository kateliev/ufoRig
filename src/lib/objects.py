# MODULE: ufoRig / lib / objects
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

__version__ = 1.0

# - Classes -------------------------------------------------
def data_collector(object):
	def __init__(self, var_name, var_value=None, export_type=None):
		self.name = var_name
		self.value = var_value
		self.__export_type = export_type if not isinstance(export_type, str) else(eval(export_type))
		self.__data = []

	def append(self, data):
		self.__data.append(data)

	def export(self, evaluate=True):
		if self.__export_type is None:
			return_value = eval(self.value) if evaluate else self.value
			return (self.name, return_value)
		else:
			return self.__export_type(self.__data)