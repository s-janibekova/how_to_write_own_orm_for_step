import sqlite3
import inspect

SQLITE_TYPE_MAP = {
  int: "INTEGER",
  float: "REAL",
  str: "TEXT",
  bytes: "BLOB",
  bool: "INTEGER", # 0 OR 1
}

CREATE_TABLE_SQL = "CREATE TABLE {name} ({fields});"
INSERT_SQL = 'INSERT INTO {name} ({fields}) VALUES ({placeholders});'
# gets all tables on sqlite
SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"

class Database:
  def __init__(self, path):
    self.conn = sqlite3.Connection(path)

  # to  execute sql code
  def _execute(self, sql, params=None):
    # print(sql)
    if params:
      return self.conn.execute(sql, params)
    return self.conn.execute(sql)

  @property
  def tables(self):
    return [ row[0] for row in self._execute(SELECT_TABLES_SQL).fetchall()]

  def create(self, table):
    self._execute(table._get_create_sql())

  def save(self, instance):
    sql, values = instance._get_insert_sql( )
    cursor = self._execute(sql, values)
    instance._data['id'] = cursor.lastrowid
    self.conn.commit( )


class Table:
  # здесь мы создаем объекты нашего table
  # и не знаем сколько их будет
  def __init__(self, **kwargs):
    self._data = {
      'id': None
    }
    for key, value in kwargs.items():
      self._data[key] = value

  def __getattribute__(self, key):
    _data = object.__getattribute__(self, '_data')
    if key in _data:
      return _data[key]
    return object.__getattribute__(self, key)

  @classmethod
  def _get_name(cls):
    return cls.__name__.lower()

  @classmethod
  def _get_create_sql(cls):
    fields = [
      ("id", "INTEGER PRIMARY KEY AUTOINCREMENT")
    ]

    for name, field in inspect.getmembers(cls):
      if isinstance(field, Column):
        fields.append((name, field.sql_type))
      elif isinstance(field, ForeignKey):
        fields.append((name + "_id", "INTEGER"))

    fields = [" ".join(x) for x in fields]
    return CREATE_TABLE_SQL.format(name=cls._get_name( ),
                                   fields=", ".join(fields))

  def _get_insert_sql(self):
      cls = self.__class__
      fields = []
      placeholders = []
      values = []

      for name, field in inspect.getmembers(cls):
          if isinstance(field, Column):
              fields.append(name)
              values.append(getattr(self, name))
              placeholders.append('?')
          elif isinstance(field, ForeignKey):
              fields.append(name + "_id")
              values.append(getattr(self, name).id)
              placeholders.append('?')

      sql = INSERT_SQL.format(name=cls._get_name(),
                              fields=", ".join(fields),
                              placeholders=", ".join(placeholders))

      return sql, values

class Column:
  def __init__(self, type):
    self.type = type

  @property
  def sql_type(self):
    return SQLITE_TYPE_MAP[self.type]

class ForeignKey:
  def __init__(self, table):
    self.table = table
