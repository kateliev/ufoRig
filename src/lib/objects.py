# MODULE: ufoRig / lib / objects
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

__version__ = 1.0

# - Classes -------------------------------------------------
class data_collector(object):
	def __init__(self, var_name, var_value=None, export_type=None):
		self.name = var_name
		self.value = var_value
		self.__export_type = export_type if not isinstance(export_type, str) else (eval(export_type))
		self.__data = []

	def append(self, data):
		self.__data.append(data)

	def export(self, evaluate=True):
		if self.__export_type is None:
			return_value = eval(self.value) if evaluate else self.value
			return (self.name, return_value)
		else:
			if len(self.__data):
				return (self.name, self.__export_type(self.__data))
			else:
				return (self.name, self.__export_type(self.value))


if __name__ == "__main__":
	a = data_collector('int', '5', int)
	b = data_collector('list', None, list)
	b2 = data_collector('list2', None, list)
	c = data_collector('dict', None, dict)
	b.append(a.export())
	b2.append(a.export())
	c.append(b.export())
	c.append(b2.export())
	print(a.export())
	print(b.export())
	print(c.export())