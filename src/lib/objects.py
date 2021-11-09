# MODULE: ufoRig / lib / objects
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

__version__ = 1.2

# - Classes -------------------------------------------------
class data_collector(object):
	def __init__(self, var_name, var_value=None, export_type=None):
		self.name = var_name
		self.value = var_value
		self.__export_type = export_type if not isinstance(export_type, str) else (eval(export_type))
		self.__data = []

	def __smart_return(self, value):
		if self.name is not None:
			return (self.name, value)
		else:
			return value

	def append(self, data):
		self.__data.append(data)

	def export(self, evaluate=False):
		if len(self.__data) and self.__export_type is not None:
			return self.__smart_return(self.__export_type(self.__data))
		else:
			if self.__export_type is None or evaluate:
				try:
					return self.__smart_return(eval(self.value))
				except (NameError, SyntaxError):
					return self.__smart_return(self.value)
			else:
				return self.__smart_return(self.__export_type(self.value))


if __name__ == "__main__":
	a = data_collector('int', '5', int)
	b = data_collector('list', None, list)
	b2 = data_collector('list2', '[1,2,3]', list)
	c = data_collector('dict', None, dict)
	b.append(a.export())
	c.append(b.export())
	c.append(b2.export(True))
	print(a.export())
	print(b.export())
	print(c.export())