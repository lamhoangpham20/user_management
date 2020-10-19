from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from datetime import datetime
import os

#Initialize app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#database config
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#mashmallow init
ma = Marshmallow(app)

#change datetime format
class MyDateTime(db.TypeDecorator):
    impl = db.DateTime
    
    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value

#event model
class Event(db.Model):
    __tablename__ = "events"
    idevents = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(20))
    starting_time = db.Column(MyDateTime)
    ending_time = db.Column(MyDateTime)
    image = db.Column(db.String(100))
    discount_rate = db.Column(db.Integer)
    discount_rules = db.Column(db.Integer)
    price = db.Column(db.Integer)
    def create(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def __init__(self,event_name,starting_time,ending_time,image,discount_rate,discount_rules,price):
        self.event_name = event_name
        self.starting_time = starting_time
        self.ending_time = ending_time
        self.image = image
        self.discount_rate = discount_rate
        self.discount_rules = discount_rules
        self.price = price
    def __repr__(self):
        return '' % self.idevents

#schema
class EventSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Event
        sqla_session = db.session
    idevents = fields.Number(dump_only=True)
    event_name = fields.String(required=True)
    starting_time = fields.String(required=True)
    ending_time = fields.String(required=True)
    image = fields.String(required=True)
    discount_rate = fields.Number(required=True)
    discount_rules = fields.Number(required=True)
    price = fields.Number(required=True)


#Get request
#get all events
@app.route('/events', methods=['GET'])
def get_all_events():
    get_events = Event.query.all()
    event_schema = EventSchema(many=True)
    events = event_schema.dump(get_events)
    return make_response(jsonify({"event": events}))

# get event by id
@app.route('/events/<id>', methods=['GET'])
def get_event_by_id(id):
    get_events = Event.query.get(id)
    event_schema = EventSchema()
    events = event_schema.dump(get_events)
    return make_response(jsonify({"event": events}))

# add new event to db
@app.route('/events', methods=['POST'])
def add_new_event():
    event_name = request.json['event_name']
    starting_time = request.json['starting_time']
    ending_time = request.json['ending_time']
    image = request.json['image']
    discount_rate = request.json['discount_rate']
    discount_rules = request.json['discount_rules']
    price = request.json['price']
    new_event = Event(event_name,starting_time,ending_time,image,discount_rate,discount_rules,price)
    new_event.create()
    return jsonify({'msg':'add success'})

#delete
@app.route('/events/<id>', methods=['DELETE'])
def delete_event(id):
    event = Event.query.get(id)
    event.delete()
    return jsonify({'msg':'delete success'})

#update
@app.route('/events/<id>', methods=['PUT'])
def update_event(id):
    event = Event.query.get(id)
    
    event_name = request.json['event_name']
    starting_time = request.json['starting_time']
    ending_time = request.json['ending_time']
    image = request.json['image']
    discount_rate = request.json['discount_rate']
    discount_rules = request.json['discount_rules']
    price = request.json['price']

    event.event_name = event_name
    event.starting_time = starting_time
    event.ending_time = ending_time
    event.image = image
    event.discount_rate = discount_rate
    event.discount_rules = discount_rules
    event.price = price

    db.session.commit()
    event_schema = EventSchema()
    events = event_schema.dump(event)
    return make_response(jsonify({"event": events}))

@app.route('/events/count/<id>', methods=['GET'])
def count(id):
    events = Event.query.filter_by(idevents= id).count()
    return jsonify({'msg':events})

#Run server
if __name__ == '__main__':
    app.run(debug=True)