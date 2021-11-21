# MODULE: ufoRig / lib / objects
# -----------------------------------------------------------
# (C) Vassil Kateliev, 2021 		(http://www.kateliev.com)
# ------------------------------------------------------------
# https://github.com/kateliev

from collections import defaultdict

__version__ = 1.53

# - Objects -------------------------------------------------
class data_collector(object):
	'''Table parser that turns string values into actual datatypes'''

	def __init__(self, var_name, var_value=None, export_type=None):
		self.name = var_name
		self.value = var_value
		self.__export_type = export_type if not isinstance(export_type, str) else (eval(export_type))
		self.__data = []

	def __smart_return(self, value):
		'''Dumb helper that returns key, value pairs for making dicts if needed'''
		if self.name is not None:
			return (self.name, value)
		else:
			return value

	def append(self, data):
		self.__data.append(data)

	def export(self, evaluate=False):
		'''Overly complicated string evaluator'''
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

class dictextractor:
	'''A collection of dicionary value extractors'''

	@staticmethod
	def extract(obj, search):
		'''Pull all values of specified key (search)
		
		Attributes:
			search (Str): Search string

		Returns:
			generator
		'''
		
		def extract_helper(obj, search):
			if isinstance(obj, dict):
				for key, value in obj.items():
					if key == search:
						yield value
					else:	
						if isinstance(value, (dict, list)):
							for result in extract_helper(value, search):
								yield result

			elif isinstance(obj, list):
				for item in obj:
					for result in extract_helper(item, search):
						yield result

		return extract_helper(obj, search)

	@staticmethod
	def find(obj, search, search_type=None):
		'''Pull all objects that contain keys of specified search.
		
		Attributes:
			search (Str): Search string
			search_type (type) : Value type
		Returns:
			generator
		'''
		def isisntance_plus(entity, test_type):
			if test_type is not None:
				return isinstance(entity, test_type)
			else:
				return True

		def where_helper(obj, search):
			if isinstance(obj, dict):
				for key, value in obj.items():
					if key == search and isisntance_plus(value, search_type):
						yield obj
					else:	
						if isinstance(value, (dict, list)):
							for result in where_helper(value, search):
								yield result

			elif isinstance(obj, list):
				for item in obj:
					for result in where_helper(item, search):
						yield result

		return where_helper(obj, search)

	@staticmethod
	def where(obj, search_value, search_key=None):
		'''Pull all objects that contain values of specified search.
		
		Attributes:
			search_value (Str): Search value
			search_key (Str) : Search for specific key that contains above value
		Returns:
			generator
		'''
		def eq_plus(test, pass_test):
			if pass_test is not None:
				return test
			else:
				return True

		def where_helper(obj, search_value):
			if isinstance(obj, dict):
				for key, value in obj.items():
					if value == search_value and eq_plus(key==search_key, search_key):
						yield obj
					else:	
						if isinstance(value, (dict, list)):
							for result in where_helper(value, search_value):
								yield result

			elif isinstance(obj, list):
				for item in obj:
					for result in where_helper(item, search_value):
						yield result

		return where_helper(obj, search_value)

	@staticmethod
	def contains(obj, search, search_type=None):
		'''Does the object contain ANY value or nested object with given name (search)
		
		Attributes:
			search (Str): Search string
			search_type (type) : Value type

		Returns:
			Bool
		'''
		def isisntance_plus(entity, test_type):
			if test_type is not None:
				return isinstance(entity, test_type)
			else:
				return True
		
		def contains_helper(obj, search):
			if isinstance(obj, dict):
				for key, value in obj.items():
					if search in key and isisntance_plus(value, search_type):
						yield True
					else:
						if isinstance(value, (dict, list)):
							for result in contains_helper(value, search):
								yield result

			elif isinstance(obj, list):
				for item in obj:
					for result in contains_helper(item, search):
						yield result
			
			
		return any(list(contains_helper(obj, search)))

class attribdict(defaultdict):
	'''	Default dictionary where keys can be accessed as attributes	'''
	def __init__(self, *args, **kwdargs):
		super(attribdict, self).__init__(attribdict, *args, **kwdargs)

	def __getattribute__(self, name):
		try:
			return object.__getattribute__(self, name)
		except AttributeError:
			try:
				return self[name]
			except KeyError:
				raise AttributeError(name)
		
	def __setattr__(self, name, value):
		if name in self.keys():
			self[name] = value
			return value
		else:
			object.__setattr__(self, name, value)

	def __delattr__(self, name):
		try:
			return object.__delattr__(self, name)
		except AttributeError:
			return self.pop(name, None)
					
	def __repr__(self):
		return '<%s: %s>' %(self.__class__.__name__, len(self.keys()))

	def __hash__(self):
		import copy
		
		def hash_helper(obj):
			if isinstance(obj, (set, tuple, list)):
				return tuple([hash_helper(element) for element in obj])    

			elif not isinstance(obj, dict):
				return hash(obj)

			new_obj = {}

			for key, value in obj.items():
				new_obj[key] = hash_helper(value)

			return hash(tuple(frozenset(sorted(new_obj.items()))))

		return hash_helper(self)

	def dir(self):
		tree_map = ['   .%s\t%s' %(key, type(value)) for key, value in self.items()]
		print('Attributes (Keys) map:\n%s' %('\n'.join(tree_map).expandtabs(30)))

	def factory(self, factory_type):
		self.default_factory = factory_type

	def lock(self):
		self.default_factory = None

	def extract(self, search):
		'''Pull all values of specified key (search)
		
		Attributes:
			search (Str): Search string

		Returns:
			generator
		'''
		return dictextractor.extract(self, search)
				
	def find(self, search, search_type=None):
		'''Pull all objects that contain keys of specified search.
		
		Attributes:
			search (Str): Search string
			search_type (type) : Value type
		Returns:
			generator
		'''
		return dictextractor.find(self, search, search_type)

	def where(self, search_value, search_key=None):
		'''Pull all objects that contain values of specified search.
		
		Attributes:
			search_value (Str): Search value
			search_key (Str) : Search for specific key that contains above value
		Returns:
			generator
		'''
		return dictextractor.where(self, search_value, search_key)

	def contains(self, search, search_type=None):
		'''Does the object contain ANY value or nested object with given name (search)
		
		Attributes:
			search (Str): Search string
			search_type (type) : Value type

		Returns:
			Bool
		'''
		return dictextractor.contains(self, search, search_type)

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
	
	d = {'a_dict':{'a_key':['a_value', 'b_value']}, 'a_list':[1,2,3,4,5], 'a_int':3, 'a_sting':'hamburgefonts'}
	attr_d = attribdict(d)
	print(attr_d.dir())