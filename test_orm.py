import os
import unittest

DB_PATH = "./test.db"


class Test01_CreateTestDatabase(unittest.TestCase):

    def test_it(self):
        global Database, db
        from own_orm import Database

        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        db = Database(DB_PATH)

        assert db.tables == []


class Test02_DefineTables(Test01_CreateTestDatabase):

    def test_it(self):
        super().test_it()
        global Table, Column, ForeignKey
        global Author, Post

        from own_orm import Table, Column, ForeignKey

        class Author(Table):
            name = Column(str)
            lucky_number = Column(int)

        class Post(Table):
            title = Column(str)
            published = Column(bool)
            author = ForeignKey(Author)

        assert Author.name.type == str
        assert Post.author.table == Author



class Test03_CreateTables(Test02_DefineTables):
  def test_it(self):
    super().test_it()

    db.create(Author)
    db.create(Post)

    assert Author._get_create_sql() ==  "CREATE TABLE author (id INTEGER PRIMARY KEY AUTOINCREMENT, lucky_number INTEGER, name TEXT);"
    assert Post._get_create_sql( ) == "CREATE TABLE post (id INTEGER PRIMARY KEY AUTOINCREMENT, author_id INTEGER, published INTEGER, title TEXT);"

    for table in ('author', 'post'):
      assert table in db.tables


class Test04_CreateAuthorInstance(Test03_CreateTables):
  def test_it(self):
    super().test_it()
    global author

    author = Author(name="SJ", lucky_number=8)

    assert author.name == 'SJ'
    assert  author.lucky_number == 8
    assert author.id is None


class Test05_SaveAuthorInstance(Test04_CreateAuthorInstance):
  def test_it(self):
    super().test_it()
    db.save(author)

    assert author._get_insert_sql() == (
      "INSERT INTO author (lucky_number, name) VALUES (?, ?);",
      [8, "SJ"]
    )
    assert author.id == 1