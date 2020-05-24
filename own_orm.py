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

# gets all tables on sqlite
SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"

class Database:
  def __init__(self, path):
    self.conn = sqlite3.Connection(path)

  # to  execute sql code
  def _execute(self, sql):
    return self.conn.execute(sql)

  @property
  def tables(self):
    return [ row[0] for row in self._execute(SELECT_TABLES_SQL).fetchall()]

  def create(self, table):
    self._execute(table._get_create_sql())


class Table:
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
class Column:
  def __init__(self, type):
    self.type = type

  @property
  def sql_type(self):
    return SQLITE_TYPE_MAP[self.type]

class ForeignKey:
  def __init__(self, table):
    self.table = table
