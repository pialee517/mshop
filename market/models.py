from market import db, bcrypt
from flask_login import UserMixin

class Product(db.Model):
    __tablename__='product'
    id = db.Column(db.Integer(), db.Identity(start=100001, increment=1), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    barcode = db.Column(db.String(8), nullable=False, unique=True)
    image = db.Column(db.String(50), default='default.png')
    description = db.Column(db.String(1024))
    userid = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def buy(self, user):
        self.userid = user.id
        user.budget -= self.price
        db.session.commit()

    def sell(self, user):
        self.userid = None
        user.budget += self.price
        db.session.commit()

class User(db.Model, UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer(), db.Identity(start=10000001, increment=1), primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    budget = db.Column(db.Numeric(12,2), nullable=False, default=1000.00)
    items = db.relationship('Product', backref='user', primaryjoin='User.id==Product.userid', lazy=True)

    def can_buy(self, product_object):
        return self.budget >= product_object.price

    def can_sell(self, product_object):
        return product_object in self.items

    @property
    def get_budget(self):
        if len(str(self.budget)) >= 4:
            number_with_commas = "{:,}".format(self.budget)
            return number_with_commas

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, text_password):
        self.password_hash = bcrypt.generate_password_hash(text_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
