from orm import Database, Table, Column, Foreign Key


db = Database("./test.db")

class Author(Table):
  name = Column(str)
  lucky_number = Column(int)
 
class Post(Table):
  title = Column(str)
  published = Column(bool)
  author = ForeignKey(Author)
  

db.create(Author)
db.create(Post)

greg = Author(name="Greg Back",
              lucky_number=13
             )
authors = db.all(Author)
db.save(greg)

authors = db.all(Author)

bob = db.get(Author,47)

post = Post(title="Building an ORM",
            published=True,
            author = greg)
            
db.save(post)

print(db.get(Post,55).author.name)


### Testing Test 
