from flask import Flask ,make_response,render_template,url_for,request,redirect
from peewee import *
import datetime
from hashlib import md5

app = Flask(__name__)


DATABASE = 'twit.db'
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta():
        database = database


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email    = CharField(unique=True)
    join_at  = DateTimeField(default=datetime.datetime.now())

    def following(self):
        return (User.select()
                .join(Relationship,on = Relationship.to_user)
                .where(Relationship.from_user == self)
                .order_by(User.username)
                )
    def followers(self):
        return (User.select()
                .join(Relationship,on = Relationship.from_user)
                .where(Relationship.to_user == self)
                .order_by(User.username)
                )


class Message(BaseModel):
    user        = ForeignKeyField(User,backref='message')
    content     = TextField()
    publish_at  = DateTimeField(default=datetime.datetime.now())

class Relationship(BaseModel):
    from_user   = ForeignKeyField(User,backref='relationship')
    to_user     = ForeignKeyField(User,backref='relation_to')
    class Meta():
        Indexes = (
            (('from_user','to_user',True))
        )


@app.before_request
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response


def create_tables():
    with database:
        database.create_tables([User,Relationship,Message])


# ================================================================
# CODE FOR ROUTE
# ================================================================


@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('/login.html')

@app.route('/register',methods=['GET','POST'])
def regis():
    if request.method == 'POST' and request.form['email']:
        try:
            with database.atomic():
                user = User.create(
                    username    = request.form['username'],
                    password    = md5(request.form['password'].encode('utf-8')).hexdigest(),
                    email       = request.form['email']
                )

            return redirect(url_for('homepage'))

        except IntegrityError:
            return 'ada kesalahan'




    return render_template('/register.html')


