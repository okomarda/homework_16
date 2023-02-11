from datetime import datetime
import prettytable
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import data
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db: SQLAlchemy = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, )
    first_name = db.Column(db.Text(100))
    last_name = db.Column(db.Text(100))
    age = db.Column(db.Integer)
    email = db.Column(db.Text(100))
    role = db.Column(db.Text(100))
    phone = db.Column (db.Text (100))


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column (db.Integer, db.ForeignKey ('user.id'))
    user = db.relationship('User')
    order = db.relationship('Order')

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text(100))
    description = db.Column(db.Text(300))
    start_date = db.Column(db.Text(15))
    end_date = db.Column(db.Text(15))
    address = db.Column(db.Text(100))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))

db.create_all()

for user_data in data.users:
    new_user = User(**user_data)
    db.session.add(new_user)
    db.session.commit()

for order_data in data.orders:
    order_data['start_date'] = datetime.strptime(order_data['start_date'], '%m/%d/%Y').date()
    order_data['end_date'] = datetime.strptime(order_data['end_date'], '%m/%d/%Y').date()
    new_order = Order(**order_data)
    db.session.add(new_order)
    db.session.commit()

for offer_data in data.offers:
    new_offer = Offer(**offer_data)
    db.session.add(new_offer)
    db.session.commit()


@app.route('/users', methods=['GET', 'POST'])
def get_users():
    '''Загрузка страницы со списком пользователей '''
    if request.method == 'GET':
        user_list = User.query.all()
        user_answer = []
        for user in user_list:
            user_answer.append(
            {
            "id": user.id,
            "first_name": user.first_name,
            "last_name":user.last_name,
            "age":user.age,
            "email":user.email,
            "role": user.role,
            "phone": user.phone
            }
        )
        return jsonify(user_answer), 200, {'content-Type': 'application/json; charset utf-8'}

    elif request.method == 'POST':
        data = request.json
        user = User(
           id =data.get ('id'),
           first_name = data.get('first_name'),
           last_name=data.get ('last_name'),
           age=data.get ('age'),
           email=data.get('email'),
           role=data.get ('role'),
           phone=data.get('phone')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify ({
            "id": user.id,
            "first_name": user.first_name,
            "last_name":user.last_name,
            "age":user.age,
            "email":user.email,
            "role": user.role,
            "phone": user.phone
            })

@app.route('/users/<int:sid>')
def get_user(sid:int):
    '''Загрузка главной страницы со списком пользователя по номеру идентификатора'''
    user = User.query.get(sid)
    if user is None:
        return "Такого пользователя не существует"

    return jsonify({
            "id": user.id,
            "first_name": user.first_name,
            "last_name":user.last_name,
            "age":user.age,
            "email":user.email,
            "role": user.role,
            "phone": user.phone
            }), {'content-Type': 'application/json; charset utf-8' }

@app.route('/users/<int:sid>/delete')
def delete_user(sid):
    user = User.query.get(sid)
    db.session.delete(user)
    db.session.commit()
    return jsonify("")

@app.route('/users/<int:sid>/put')
def update_user(sid):
    user_data = json.loads(request.data)
    user = User.query.get (sid)
    user.id = user_data['id']
    user.first_name = user_data['first_name']
    user.last_name = user_data['last_name']
    user.age = user_data['age']
    user.email = user_data['email']
    user.role = user_data['role']
    user.phone = user_data['phone']

    db.session.add (user)
    db.session.commit ( )
    return jsonify ("")


@app.route('/orders', methods = ['GET', 'POST'])
def get_orders():
    '''Загрузка страницы со списком заказов '''
    if request.method == 'GET':
        order_list = Order.query.all()
        order_answer = []
        for order in order_list:
            order_answer.append(
            {
            "id": order.id,
            "name": order.name,
            "description":order.description,
            "start_date":str(order.start_date),
            "end_date":str(order.end_date),
            "address": order.address,
            "price": order.price,
            "customer_id": order.customer_id,
            "executor_id": order.executor_id
            }
        )
        return jsonify(order_answer), {'content-Type': 'application/json; charset utf-8' }

    elif request.method == 'POST':
        data = request.json
        order = Order(
           id =data.get ('id'),
           name = data.get('name'),
           description=data.get ('description'),
           start_date=str(data.get ('start_date')),
           end_date=str(data.get('end_date')),
           address=data.get ('address'),
           price=data.get('price'),
           customer_id=data.get('customer_id'),
           executor_id=data.get ('executor_id')
        )
        db.session.add(order)
        db.session.commit()
        return jsonify ({
            "id": order.id,
            "name": order.name,
            "description":order.description,
            "start_date":str(order.start_date),
            "end_date":str(order.end_date),
            "address": order.address,
            "price": order.price,
            "customer_id" : order.customer_id,
            "executor_id" : order.executor_id,
            })

@app.route('/orders/<int:sid>')
def get_order(sid:int):
    '''Загрузка главной страницы с заказом по номеру идентификатора'''
    order = Order.query.get(sid)
    if order is None:
        return "Такого заказа не существует"
    return json.dumps({
            "id": order.id,
            "name": order.name,
            "description":order.description,
            "start_date":str(order.start_date),
            "end_date":str(order.end_date),
            "address": order.address,
            "price": order.price,
            "customer_id": order.customer_id,
            "executor_id": order.executor_id
            }), {'content-Type': 'application/json; charset utf-8' }

@app.route('/orders/<int:sid>/delete')
def delete_order(sid):
    order = Order.query.get(sid)
    db.session.delete(order)
    db.session.commit()
    return jsonify("")

@app.route('/orders/<int:sid>/put')
def update_order(sid):
    order_data = json.loads(request.data)
    order = Order.query.get (sid)
    order.id = order_data['id']
    order.name = order_data['name']
    order.description = order_data['description']
    order.start_date = order_data['start_date']
    order.end_date = order_data['end_date']
    order.address = order_data['address']
    order.price = order_data['price']
    order.customer_id = order_data['customer_id']
    order.executor_id = order_data['executor_id']

    db.session.add (order)
    db.session.commit ( )
    return jsonify ("")

@app.route('/offers', methods=['GET', 'POST'])
def get_offers():
    '''Загрузка страницы со списком заказов '''
    if request.method == 'GET':
        offer_list = Offer.query.all()
        offer_answer = []
        for offer in offer_list:
            offer_answer.append(
            {
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id
            }
        )
        return jsonify(offer_answer), {'content-Type': 'application/json; charset utf-8' }
    elif request.method == 'POST':
        data = request.json
        offer = Offer(
            id = data.get('id'),
            order_id = data.get('order_id'),
            executor_id = data.get('executor_id')
        )
        db.session.add(offer)
        db.session.commit()
        return jsonify({
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id
            })


@app.route('/offers/<int:sid>')
def get_offer(sid:int):
    '''Загрузка главной страницы с заказом по номеру идентификатора'''
    offer = Offer.query.get(sid)
    if offer is None:
        return "Такого заказа не существует"
    return json.dumps({
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id
            }), {'content-Type': 'application/json; charset utf-8' }

@app.route('/offers/<int:sid>/delete')
def delete_offer(sid):
    offer = Offer.query.get(sid)
    db.session.delete(offer)
    db.session.commit()
    return jsonify("")

@app.route('/offers/<int:sid>/put')
def update_offer(sid):
    offer_data = json.loads(request.data)
    offer = Offer.query.get (sid)
    offer.id = offer_data['id']
    offer.order_id = offer_data['order_id']
    offer.executor_id = offer_data['executor_id']

    db.session.add(offer)
    db.session.commit()
    return jsonify("")


#session = db.session()

#cursor_user = session.execute("SELECT * from user").cursor
#mytable1 = prettytable.from_db_cursor(cursor_user)
#cursor_offer = session.execute("SELECT * from offer").cursor
#mytable2 = prettytable.from_db_cursor(cursor_offer)
#cursor_order = session.execute("SELECT * from orders").cursor
#mytable3 = prettytable.from_db_cursor(cursor_order)

#if __name__ == '__main__':
 #   print(mytable1)
  #  print(mytable2)
   # print(mytable3)

if __name__ == '__main__':
    app.run (debug=True)