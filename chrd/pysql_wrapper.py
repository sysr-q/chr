# -*- coding: utf-8 -*-
# Copyright (C) 2012 Christopher Carter <chris@gibsonsec.org>
# Licensed under the MIT License.
# Modified for use with chr url shortener.

class pysql_wrapper:
	_instance = None

	def __init__(self, debug=False, **kwargs):
		# Are we gonna print various debugging messages?
		self.debug = debug

		# The internal database connection.
		# Can be either MySQL or sqlite, it doesnt matter.
		self._dbc = None

		# The database cursor. We'll use this to actually query stuff.
		self._cursor = None
		
		# The finalised query string to send to the dbc.
		self._query = ""
		self._query_type = ""
		
		# A dictionary of 'field' => 'value' which are used in the WHERE clause.
		self._where = {}
		
		# An internal counter of modified rows from the last statement.
		self._affected_rows = 0
		
		# Stuff we won't need unless we're using MySQL.
		self._db_host = None
		self._db_user = None
		self._db_pass = None
		self._db_name = None
		# Stuff we won't need unless we're using sqlite3
		self._db_path = None

		# Just so we know stuff worked after the connection.
		self._db_version = "SOMETHING WENT WRONG!"
		self._db_type = 'DEFAULT'

		# This is so you can easily add extra database types.
		self._db_connectors = {
			'sqlite': self._connect_sqlite,
			'mysql': self._connect_mysql
		}

		# Do some checks depending on what we're doing.
		if 'db_type' in kwargs:
			_db_type = kwargs['db_type']
			if _db_type.lower() == 'mysql':
				for db in ('db_host', 'db_user', 'db_pass', 'db_name'):
					if db not in kwargs:
						# If they miss something, we can't connect to MySQL.
						raise ValueError('No {0} was passed to pysql_wrapper.'.format(db))
					else:
						# We only want strings!
						if type(kwargs.get(db)) != str:
							raise TypeError('{0} was passed, but it isn\'t a string.')
				self._db_host = kwargs.get('db_host')
				self._db_user = kwargs.get('db_user')
				self._db_pass = kwargs.get('db_pass')
				self._db_name = kwargs.get('db_name')
				self._db_type = 'mysql'
			elif _db_type.lower() in ('sqlite', 'sqlite3'):
				self._db_type = 'sqlite'
				if 'db_path' not in kwargs:
					self._debug('Using sqlite and not given db_path.')
					raise ValueError('sqlite was selected, but db_path was not specified.')
				else:
					self._db_path = kwargs.get('db_path')
					if not isinstance(self._db_path, str):
						self._debug('Given', self._db_path, 'of type', type(self._db_path), 'which isn\'t a string.')
						raise TypeError("db_path was passed, but isn't a string.")

		try:
			# Try to grab the connector.
			connector = self._db_connectors[self._db_type]
			connector()
		except KeyError as e:
			self._debug('Given', self._db_type, 'as database_type, not supported.')
			raise Exception('The given database type is not supported.')

		# Let's knock it up a notch.. BAM!
		pysql_wrapper._instance = self

	def _debug(self, *stuff):
		if not self.debug:
			return
		print '[ ? ]', ' '.join(stuff)

	def __del__(self):
		# If this isn't called, it shouldn't really matter anyway.
		# If it is, let's tear down our connections.
		if self._dbc:
			self._dbc.close()

	def _sqlite_dict_factory(self, cursor, row):
		d = {}
		for idx, col in enumerate(cursor.description):
			d[col[0]] = row[idx]
		return d

	def _connect_sqlite(self, force=False):
		"""Connect to the sqlite database.

			This function also grabs the cursor and updates the _db_version
		"""
		import sqlite3
		self._dbc = sqlite3.connect(self._db_path)
		self._dbc.row_factory = self._sqlite_dict_factory
		self._cursor = self._dbc.cursor()
		self._cursor.execute('SELECT SQLITE_VERSION()')
		self._db_version = self._cursor.fetchone()
		self._db_type = 'sqlite'

	def _connect_mysql(self, force=False):
		"""Connect to the MySQL database.

			This function also grabs the cursor and updates the _db_version 
		"""
		import MySQLdb
		self._dbc = MySQLdb.connect(self._db_host, self._db_user, self._db_pass, self._db_name)
		self._cursor = self._dbc.cursor(MySQLdb.cursors.DictCursor)
		self._cursor.execute('SELECT VERSION()')
		self._db_version = self._cursor.fetchone()
		self._db_type = 'mysql'

	def _reset(self):
		"""Reset the given bits and pieces after each query.
			chr: kill the connection
		"""
		self._where = {}
		self._query = ""
		self._query_type = ""
		self.__del__()
		return None

	def row(self):
		"""Return last modified row id.
		"""
		return self._cursor.lastrowid

	def where(self, field, value):
		"""Add a conditional WHERE statement. You can chain multiple where() calls together.

			Example: pysql.where('id', 1).where('foo', 'bar')
			Param: 'field' The name of the database field.
			Param: 'value' The value of the database field.
			Return: Instance of self for chaining where() calls
		"""
		self._where[field] = value
		return self

	def get(self, table_name, num_rows=False):
		"""SELECT some data from a table.

			Example: pysql.get('table', 1) - Select one row
			Param: 'table_name' The name of the table to SELECT from.
			Param: 'num_rows' The (optional) amount of rows to LIMIT to.
			Return: The results of the SELECT.
		"""
		self._query_type = 'select'
		self._query = "SELECT * FROM `{0}`".format(table_name)
		stmt, data = self._build_query(num_rows=num_rows)
		res  = self._execute(stmt, data)
		self._reset()
		return res

	def insert(self, table_name, table_data):
		"""INSERT data into a table.

			Example: pysql.insert('table', {'id': 1, 'foo': 'bar'})
			Param: 'table_name' The table to INSERT into.
			Param: 'table_data' A dictionary of key/value pairs to insert.
			Return: The results of the query.
		"""
		self._query_type = 'insert'
		self._query = "INSERT INTO `{0}`".format(table_name)
		stmt, data = self._build_query(table_data=table_data)
		res  = self._execute(stmt, data)
		if self._affected_rows > 0:
			res = True
		else:
			res = False
		self._reset()
		return res

	def update(self, table_name, table_data, num_rows = False):
		"""UPDATE a table. where() must be called first.

			Example: pysql.where('id', 1).update('table', {'foo': 'baz'})
			Param: 'table_name' The name of the table to UPDATE.
			Param: 'table_data' The key/value pairs to update. (SET `KEY` = 'VALUE')
			Param: 'num_rows' The (optional) amount of rows to LIMIT to.
			return True/False, indicating success.
		"""
		if len(self._where) == 0:
			return False
		self._query_type = 'update'
		self._query = "UPDATE `{0}` SET ".format(table_name)
		stmt, data = self._build_query(num_rows=num_rows, table_data=table_data)
		res  = self._execute(stmt, data)
		if self._affected_rows > 0:
			res = True
		else:
			res = False
		self._reset()
		return res

	def delete(self, table_name, num_rows = False):
		"""DELETE from a table. where() must be called first.

			Example: pysql.where('id', 1).delete('table')
			Param: 'table_name' The table to DELETE from.
			Param: 'num_rows' The (optional) amount of rows to LIMIT to.
			return True/False, indicating success.
		"""
		if len(self._where) == 0:
			return False
		self._query_type = 'delete'
		self._query = "DELETE FROM `{0}`".format(table_name)
		stmt, data = self._build_query(num_rows=num_rows)
		res  = self._execute(stmt, data)
		if self._affected_rows > 0:
			res = True
		else:
			res = False
		self._reset()
		return res

	def escape(self, string):
		return self._dbc.escape_string(string)

	def query(self, q):
		"""Execute a raw query directly.

			Example: pysql.query('SELECT * FROM `posts` LIMIT 0, 15')
			Param: 'q' The query to execute.
			Return: The result of the query. Could be an array, True, False, anything, really.
		"""
		self._query_type = 'manual'
		self._query = q
		res = self._execute(self._query, data=None)
		self._reset()
		return res

	def affected_rows(self):
		"""Grab the amount of rows affected by the last query.

			Return: The amount of rows modified.
		"""
		return self._cursor.rowcount

	def _execute(self, query, data=None):
		if data is not None:
			self._cursor.execute(query, data)
		else:
			self._cursor.execute(query)
		if self._db_type == 'sqlite':
			self._dbc.commit()
		res = self._cursor.fetchall()
		self._affected_rows = int(self._cursor.rowcount)
		return res

	def _format_str(self, thing):
		"""Returns the format string for the thing.

			Due to how retarded MySQL is, this _HAS_ to be %s, or it won't work.
		"""
		if self._db_type == 'sqlite':
			return '?'
		elif self._db_type == 'mysql':
			return '%s'
		else:
			# No idea, return ?.
			return '?'

	def _build_query(self, num_rows=False, table_data=False):
		return_data = ()

		# e.g. -> UPDATE `table` SET `this` = ?, `that` = ?, `foo` = ? WHERE `id` = ?;

		# If they've supplied where() statements
		if len(self._where) > 0:
			keys = self._where.keys()
			# If they've supplied table data:
			if type(table_data == dict):
				count = 1
				# If we're calling an UPDATE
				if self._query_type == 'update':
					for key, val in table_data.iteritems():
						format = self._format_str(type)
						if count == len(table_data):
							self._query += "`{0}` = {1}".format(key, format)
						else:
							self._query += "`{0}` = {1}, ".format(key, format)
						return_data = return_data + (val,)
						count += 1
			self._query += " WHERE "
			where_clause = []
			for key, val in self._where.iteritems():
				format = self._format_str(val)
				where_clause.append("`{0}` = {1}".format(key, format))
				return_data = return_data + (val,)
			self._query += ' AND '.join(where_clause)

		# If they've supplied table data.
		if type(table_data) == dict and self._query_type == 'insert':
			keys = table_data.keys()
			vals = table_data.values()
			num  = len(table_data)
			for count, key in enumerate(keys):
				# Wrap column names in backticks.
				keys[count] = "`{0}`".format(key)
			self._query += " ({0}) ".format(', '.join(keys))
			# Append VALUES (?,?,?) however many we need.
			format = ""
			for count, val in enumerate(vals):
				format += '{0},'.format(self._format_str(val))
			format = format[:-1]

			self._query += "VALUES ({0})".format(format)
			for val in vals:
				return_data = return_data + (val,)

		# Do you want LIMIT with that, baby?!
		if num_rows:
			self._query += " LIMIT {0}".format(num_rows)
		return (self._query, return_data,)
