from flask import Flask, render_template, request , redirect , url_for, flash,session,jsonify,request,current_app, make_response,jsonify,session
from flask_sqlalchemy import SQLAlchemy 
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import jwt
from flask_migrate import Migrate
from datetime import datetime
from flask_restful import Api, Resource
import json
from decimal import Decimal
from sqlalchemy import ForeignKey,Text
from sqlalchemy.orm import relationship
import json


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
api = Api(app)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "app.db") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['SECRET_KEY'] = 'hello'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
login_manager = LoginManager() 
login_manager.init_app(app) 
login_manager.login_view = 'userlogin' 

def custom_output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=CustomJSONEncoder), code)
    resp.headers.extend(headers or {})
    resp.headers['Content-Type'] = 'application/json'
    return resp

api.representations['application/json'] = custom_output_json

class Userdata(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False , default='user')



    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200))
    license_number = db.Column(db.String(100), nullable=False)
    rooms_available = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    room_types = db.Column(db.JSON)
    user_id = db.Column(db.Integer, nullable=False)  
    

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)



@login_manager.user_loader
def load_user(user_id):
    if session.get("role") == "admin":
        return Admin.query.get(int(user_id))
    else:
        return Userdata.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



with app.app_context():
    db.create_all()

@app.route("/usersignup", methods=["GET", "POST"])
def usersignup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirmpassword = request.form.get("confirm-password")
        role = request.form.get("role", "user") 
        if password != confirmpassword:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("usersignup"))

        if Userdata.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("usersignup"))

        if Userdata.query.filter_by(phone=phone).first():
            flash("Phone number already registered. Please use a different one.", "danger")
            return redirect(url_for("usersignup"))

        new_user = Userdata(
            name=name,
            email=email,
            phone=phone,
            password=password,
            role=role
        )

        new_user.set_password(password)

 
        db.session.add(new_user)
        db.session.commit()

        flash("User signed up successfully!", "success")
        return redirect(url_for("userlogin"))

    return render_template('usersignup.html')





@app.route('/')
def home():
    return render_template("index.html")

@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        

        user = Userdata.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            session["user_id"] = user.id
            session["role"] = user.role 
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))


        flash("Invalid credentials!", "danger")
        return redirect(url_for("userlogin"))

    return render_template("userlogin.html")


UPLOAD_FOLDER = 'static/images' 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os, json

@app.route('/list-property', methods=['GET', 'POST'])
def list_property():
    if request.method == 'POST':
        hotel_name = request.form.get('property_name')
        location = request.form.get('property_location')
        license_number = request.form.get('license_number')
        rooms_available = request.form.get('rooms_available')
        price = request.form.get('price')
        description = request.form.get('property_description')
        user_id = session['user_id']


        image_file = request.files.get('property_image')
        image_filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        image_url = url_for('static', filename=f'images/{image_filename}', _external=True)

        room_types = {}
        for key in request.form:
            if key.startswith("room_types["):
                room_type = key[11:-1]  
                count = request.form.get(key)
                if count and count.isdigit():
                    room_types[room_type] = int(count)


        new_property = Property(
            hotel_name=hotel_name,
            location=location,
            image=image_filename,
            license_number=license_number,
            rooms_available=int(rooms_available),
            price=float(price),
            description=description,
            room_types=room_types,  
            user_id=user_id
        )
        db.session.add(new_property)
        db.session.commit()

        flash("Property listed successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('listProperty.html')




@app.route('/properties')
def properties():
    properties_list = Property.query.all() 
    return render_template('hotels.html', properties=properties_list)

@app.route('/book/<int:property_id>', methods=["GET", "POST"])
def book_property(property_id):
    property = Property.query.get_or_404(property_id)
    if request.method == "POST":
        user_name = request.form.get("user-name")
        user_phone = request.form.get("user-phone")
        user_email = request.form.get("user-email")


        new_booking = Booking(
            user_name=user_name,
            user_phone=user_phone,
            user_email=user_email,
            property_id=property.id
        )

 
        db.session.add(new_booking)
        db.session.commit()

        flash("Booking Successful!", "success")
        return redirect(url_for('bookings')) 

    return render_template('book_property.html', property=property)

@app.route("/admin_dashboard")
def admin_dashboard():
  
    if "role" not in session or session["role"] != "admin":
        flash("You must be an admin to access this page.", "danger")
        return redirect(url_for("userlogin"))
    

    return render_template("admin_dashboard.html")



@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/list_users")
@login_required
def list_users():
    if session.get("role") != "admin":
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for("userlogin"))
    

    users = Userdata.query.all()
    return render_template("list_users.html", users=users)



@app.route('/search')
def search_properties():
    location_to_search = request.args.get("location_to_search")
    if location_to_search:
        properties = Property.query.filter(
            Property.location.ilike(f"%{location_to_search}%")
        ).all()
    else:
        properties = []

    return render_template('search_results.html', properties=properties)



class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
   
    user_id = db.Column(db.Integer, db.ForeignKey('userdata.id'), nullable=False)
    user = db.relationship('Userdata', backref=db.backref('bookings', lazy=True))

    user_name = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(15), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    property = db.relationship('Property', backref=db.backref('bookings', lazy=True))

    room_type = db.Column(db.String(50), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    rooms_booked = db.Column(db.Integer, nullable=False)
    
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Booking {self.user_name} booked {self.rooms_booked} room(s) at {self.property.name}>"
    

with app.app_context():
    db.create_all()


@app.route("/logout")
@login_required
def logout():
    print(f"Before logout: {current_user.is_authenticated}") 
    logout_user()  
    session.clear()  
    print(f"After logout: {current_user.is_authenticated}")
    flash("You have been logged out.", "info")
    return redirect(url_for("userlogin"))

#############      API        ###################

class PropertyAPI(Resource):
    def post(self):
        data = request.get_json()

        new_property = Property(
            hotel_name=data['hotel_name'],
            location=data['location'],
            image=data.get('image', ''),
            license_number=data['license_number'],
            rooms_available=data['rooms_available'],
            price=data['price'],
            description=data.get('description', ''),
            room_types=data.get('room_types', {}),
            user_id=data['user_id']
        )

        db.session.add(new_property)
        db.session.commit()

        return {'id': new_property.id, 'message': 'Booking created'}, 201


class SearchProperties(Resource):
    def get(self):
        location = request.args.get('location')
        if location:
            properties = Property.query.filter(Property.location.ilike(f'%{location}%')).all()
            property_list = []

            for prop in properties:
                image_url = (
                    url_for('static', filename=f'images/{prop.image}', _external=True)
                    if prop.image else None
                )

                property_list.append({
                    'id': prop.id,
                    'hotel_name': prop.hotel_name,
                    'location': prop.location,
                    'image': image_url, 
                    'license_number': prop.license_number,
                    'rooms_available': prop.rooms_available,
                    'price': str(prop.price),
                    'description': prop.description,
                    'room_types': prop.room_types
                })

            return property_list, 200

        return [], 200


class RegisterAPI(Resource):
    def post(self):
        try:
            data = request.get_json()

            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            password = data.get('password')

            if not all([name, email, phone, password]):
                return {'error': 'All fields are required'}, 400

            if Userdata.query.filter((Userdata.email == email) | (Userdata.phone == phone)).first():
                return {'error': 'User with this email or phone already exists'}, 400

            user = Userdata(name=name, email=email, phone=phone)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            return {'message': 'User registered successfully'}, 201

        except Exception as e:
            return {'error': str(e)}, 500



class ProtectedAPI(Resource):
    def get(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'error': 'Token is missing!'}, 403

        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = Userdata.query.get(user_id)

            if not user:
                return {'error': 'User not found!'}, 404

            return {'message': f'Hello, {user.name}!'}, 200

        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}, 401


class UserLoginAPI(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = Userdata.query.filter_by(email=email).first()
        if user and user.check_password(password):
            payload = {
                "user_id": user.id,
                "role": user.role,
                "name": user.name,
                "email": user.email,
                "phone": user.phone
            }
            token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
            return {
                "status": "success",
                "message": "Logged in successfully!",
                "token": token
            }, 200

        return {
            "status": "fail",
            "message": "Invalid credentials"
        }, 401


class UpdateProfileAPI(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')

        if not user_id or not name or not email or not phone:
            return {"error": "Missing required fields"}, 400

        existing_user = Userdata.query.filter_by(phone=phone).first()
        if existing_user and existing_user.id != user_id:
            return {"error": "Phone number already taken"}, 400

        user = Userdata.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        user.name = name
        user.email = email
        user.phone = phone
        db.session.commit()

        return {
            "message": "Profile updated successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone
            }
        }, 200


class AllPropertiesAPI(Resource):
    def get(self):
        properties = Property.query.all()
        properties_data = []

        for prop in properties:
            if isinstance(prop.room_types, str):
                try:
                    room_types_data = json.loads(prop.room_types)
                except json.JSONDecodeError:
                    room_types_data = {}
            else:
                room_types_data = prop.room_types or {}

            image_url = (
                url_for('static', filename=f'images/{prop.image}', _external=True)
                if prop.image else None
            )

            properties_data.append({
                'id': prop.id,
                'hotel_name': prop.hotel_name,
                'location': prop.location,
                'description': prop.description,
                'license_number': prop.license_number,
                'rooms_available': prop.rooms_available,
                'price': prop.price,
                'image_url': image_url,
                'room_types': room_types_data,
                'owner_id': prop.user_id
            })

        return properties_data, 200


class SinglePropertyAPI(Resource):
    def get(self, id):
        try:
            prop = Property.query.get_or_404(id)

            if isinstance(prop.room_types, str):
                try:
                    room_types_data = json.loads(prop.room_types)
                except json.JSONDecodeError:
                    room_types_data = {}
            else:
                room_types_data = prop.room_types or {}

            image_url = url_for('static', filename=f'images/{prop.image}', _external=True) if prop.image else None

            return {
                'id': prop.id,
                'hotel_name': prop.hotel_name,
                'location': prop.location,
                'description': prop.description,
                'license_number': prop.license_number,
                'rooms_available': prop.rooms_available,
                'price': prop.price,
                'image_url': image_url,
                'room_types': room_types_data,
                'owner_id': prop.user_id
            }, 200

        except Exception as e:
            return {'error': str(e)}, 400


class UserBookingsAPI(Resource):
    def get(self, user_id):
        print(f"Received request for user_id: {user_id}")
        user = Userdata.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
        print(f"User found: {user}")
        result = []
        for b in bookings:
            result.append({
                'id': b.id,
                'hotel_name': b.property.hotel_name if b.property else "N/A",
                'check_in': b.checkin_date.strftime('%Y-%m-%d'),
                'check_out': b.checkout_date.strftime('%Y-%m-%d'),
                'room_type': b.room_type,
                'rooms_booked': b.rooms_booked,
                'booked_at': b.booking_date.strftime('%Y-%m-%d %H:%M:%S')
            })

        return {"bookings": result}, 200

class BookingAPI(Resource):
    def get(self):
        bookings_list = Booking.query.all()
        return make_response(render_template('bookings.html', bookings=bookings_list))

    def post(self):
        try:
            data = request.get_json()

      
            user_id = data.get('user_id')
            if not user_id:
                return {'error': 'user_id is required'}, 400

        
            user_name = data.get('user_name')
            user_phone = data.get('user_phone')
            user_email = data.get('user_email')
            property_id = data.get('property_id')
            room_type = data.get('room_type')
            checkin_date = datetime.strptime(data.get('checkin_date'), '%Y-%m-%d').date()
            checkout_date = datetime.strptime(data.get('checkout_date'), '%Y-%m-%d').date()
            rooms_booked = int(data.get('rooms_booked'))

    
            prop = Property.query.get(property_id)
            if not prop:
                return {'error': 'Property not found'}, 404

       
            room_types_dict = json.loads(prop.room_types) if isinstance(prop.room_types, str) else prop.room_types
            if room_type not in room_types_dict:
                return {'error': f'Room type {room_type} not found'}, 400
            if room_types_dict[room_type] < rooms_booked:
                return {'error': f'Not enough {room_type} rooms available'}, 400
            if prop.rooms_available < rooms_booked:
                return {'error': 'Not enough total rooms available'}, 400

           
            room_types_dict[room_type] -= rooms_booked
            prop.rooms_available -= rooms_booked
            prop.room_types = room_types_dict
            db.session.commit()

           
            new_booking = Booking(
                user_id=user_id,
                user_name=user_name,
                user_phone=user_phone,
                user_email=user_email,
                property_id=property_id,
                room_type=room_type,
                checkin_date=checkin_date,
                checkout_date=checkout_date,
                rooms_booked=rooms_booked
            )
            db.session.add(new_booking)
            db.session.commit()

            return {
                'message': 'Booking created successfully',
                'booking_id': new_booking.id
            }, 201

        except Exception as e:
            return {'error': str(e)}, 400


class BookingByIdAPI(Resource):
    def get(self, booking_id):
        booking = Booking.query.get(booking_id)

        if not booking:
            return {'error': 'Booking not found'}, 404

        property_obj = booking.property
        image_url = url_for('static', filename=f'images/{property_obj.image}', _external=True)

        return {
            'id': booking.id,
            'user_name': booking.user_name,
            'user_email': booking.user_email,
            'user_phone': booking.user_phone,
            'property': {
                'id': property_obj.id,
                'name': property_obj.hotel_name,
                'price': str(property_obj.price),
                'location': property_obj.location,
                'image': image_url
            },
            'room_type': booking.room_type,
            'checkin_date': booking.checkin_date.strftime('%Y-%m-%d'),
            'checkout_date': booking.checkout_date.strftime('%Y-%m-%d'),
            'rooms_booked': booking.rooms_booked,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S')
        }, 200

class OwnerBookingsAPI(Resource):
    def get(self, user_id):
        properties = Property.query.filter_by(user_id=user_id).all()

        if not properties:
            return {'error': 'No properties found for this owner'}, 404

        all_bookings = []
        for prop in properties:
            for booking in prop.bookings:
                booking_info = {
                    'booking_id': booking.id,
                    'user_name': booking.user_name,
                    'user_email': booking.user_email,
                    'user_phone': booking.user_phone,
                    'room_type': booking.room_type,
                    'checkin_date': booking.checkin_date.strftime('%Y-%m-%d'),
                    'checkout_date': booking.checkout_date.strftime('%Y-%m-%d'),
                    'rooms_booked': booking.rooms_booked,
                    'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'property': {
                        'id': prop.id,
                        'name': prop.hotel_name,
                        'location': prop.location,
                        'price': str(prop.price),
                        'image': prop.image  
                    }
                }
                all_bookings.append(booking_info)

        return all_bookings, 200




api.add_resource(PropertyAPI, '/api/propertyAPI')
api.add_resource(SearchProperties, '/api/search_properties')
api.add_resource(RegisterAPI, '/api/register')
api.add_resource(ProtectedAPI, '/api/protected')
api.add_resource(UserLoginAPI, '/api/userlogin')
api.add_resource(UpdateProfileAPI, '/api/update_profile')
api.add_resource(AllPropertiesAPI, '/api/properties')
api.add_resource(SinglePropertyAPI, '/api/properties/<int:id>')
api.add_resource(UserBookingsAPI, '/api/all/<int:user_id>')
api.add_resource(BookingAPI, '/api/bookingAPI')
api.add_resource(BookingByIdAPI, '/api/bookingAPI/<int:booking_id>')
api.add_resource(OwnerBookingsAPI, '/api/owner/<int:user_id>/bookings')



if __name__ == "__main__":
    app.run(debug=True) 