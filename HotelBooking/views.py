from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Booking
import jwt
from django.conf import settings 
import requests
import json
from datetime import datetime
from decimal import Decimal
from django.http import Http404

api = "http://127.0.0.1:5000/api/"
FLASK_SECRET_KEY = settings.FLASK_SECRET_KEY

def home(request):
  
    destinations = [
        {"name": "New Delhi", "img": static("images/humayuns-tomb.jpg")},
        {"name": "Bangalore", "img": static("images/Bengaluru.jpg")},
        {"name": "Pune", "img": static("images/pune.jpg")},
        {"name": "Chennai", "img": static("images/Shimla.jpg")},
        {"name": "Hyderabad", "img": static("images/hyderabad.jpg")},
        {"name": "Mumbai", "img": static("images/mumbai3.jpg")},
    ]


    rooms = [
        {"img": "IMG-20250213-WA0012.jpg", "name": "Treebo Corporate Park", "place": "New Delhi", "price": "₹ 8,594"},
        {"img": "IMG-20250213-WA0007.jpg", "name": "Quality Inn Elite, Amritsar", "place": "Amritsar", "price": "₹ 5,670"},
        {"img": "images.jpg", "name": "Aachman Valley Resort Shimla", "place": "Shimla", "price": "₹ 2,608"},
        {"img": "IMG-20250213-WA0009.jpg", "name": "Hotel Airport Residency", "place": "New Delhi", "price": "₹ 7,260"},
        {"img": "IMG-20250213-WA0011.jpg", "name": "Hotel Airport Residency", "place": "New Delhi", "price": "₹ 7,260"},
        {"img": "IMG-20250213-WA0008.jpg", "name": "Hotel Airport Residency", "place": "New Delhi", "price": "₹ 7,260"},
    ]

    return render(request, "index.html", {
        "destinations": destinations,
        "rooms": rooms
    })


def decode_jwt(token):
    try:
        return jwt.decode(token, FLASK_SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        payload = {
            "email": email,
            "password": password
        }

        try:
            url = f"{api}userlogin"
            response = requests.post(url, json=payload)
            data = response.json()

            if data.get("status") == "success":
                token = data.get("token")

              
                user_data = decode_jwt(token)
                if not user_data:
                    messages.error(request, "Invalid or expired token.")
                    return render(request, "userlogin.html")

                actual_role = user_data.get("role")
                if actual_role != selected_role:
                    messages.error(request, "Incorrect role selected.")
                    return render(request, "userlogin.html")

              
                request.session["token"] = token  
                request.session["user_id"] = user_data.get("user_id")
                request.session["name"] = user_data.get("name")
                request.session["email"] = user_data.get("email")
                request.session["phone"] = user_data.get("phone")
                request.session["role"] = actual_role
                request.session["is_authenticated"] = True

                print(f"User session data after login: {dict(request.session.items())}")

                
                if actual_role == "admin":
                    return redirect("owner_dashboard")
                else:
                    return redirect("home")

            else:
                messages.error(request, data.get("message"))
                return render(request, "userlogin.html")

        except requests.exceptions.RequestException:
            messages.error(request, "Unable to connect to Flask server.")
            return render(request, "userlogin.html")

    return render(request, "userlogin.html")

def signup(request):

    FLASK_API_URL = f'{api}register'
    if request.method == 'POST':
     
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

      
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

      
        data = {
            'name': name,
            'email': email,
            'phone': phone,
            'password': password,
        }

        try:
         
            response = requests.post(FLASK_API_URL, json=data)

            if response.status_code == 201:
                messages.success(request, 'User registered successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Failed to create user in Flask API.')
                return redirect('signup')
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error connecting to Flask API: {e}')
            return redirect('signup')

    return render(request, 'usersignup.html')




def owner_dashboard(request):

    if not request.session.get('is_authenticated') or request.session.get('role') != 'admin':
        messages.error(request, "You're not authorized to access this page!")
        return redirect('home')

    owner_id = request.session.get('user_id') 

    flask_api_url = f"{api}owner/{owner_id}/bookings"

    try:
        response = requests.get(flask_api_url)
        if response.status_code != 200:
            raise Http404("Unable to fetch bookings from Flask API.")

        bookings = response.json() 
        context = {
            'bookings': bookings
        }
        return render(request, 'owner_dashboard.html', context)

    except requests.exceptions.RequestException as e:
        raise Http404(f"Error communicating with Flask API: {e}")




def forgot(request):
    return render(request, "userforgot.html")

def user_logout(request):
    logout(request)         
    request.session.flush()   
    messages.success(request, "You have been logged out.")
    return redirect('login')
def privacy(request):
    return render(request, "privacy.html")

def contact(request):
    return render(request, "contact_us.html")



def about_us(request):
    return render(request, 'about_us.html')


def search_properties(request):
    location_to_search = request.GET.get("location_to_search")
    properties = []

    if location_to_search:

        flask_api_url = f'{api}search_properties?location={location_to_search}'

        try:
            response = requests.get(flask_api_url)
         
            if response.status_code == 200:
                properties = response.json() 
            else:
          
                print(f"Failed to fetch properties from Flask. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error while requesting data from Flask: {e}")

    return render(request, 'search_results.html', {'properties': properties})
import requests
import json
from django.shortcuts import render
from django.contrib import messages

def available_properties(request):
    api_url = f"{api}properties"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            properties = response.json()

            for prop in properties:
                print("Django received:", prop)  

             
                if isinstance(prop.get("room_types"), str):
                    try:
                        prop["room_types"] = json.loads(prop["room_types"])
                    except json.JSONDecodeError:
                        prop["room_types"] = {}

            return render(request, 'hotels.html', {'properties': properties})
        else:
            messages.error(request, "Failed to fetch properties from backend.")
            return render(request, 'hotels.html', {'properties': []})
    except requests.exceptions.RequestException as e:
        print("Request error:", e)
        messages.error(request, "API server is unreachable.")
        return render(request, 'hotels.html', {'properties': []})







def book(request, id):
    flask_api_url = f'{api}properties/{id}'

    try:
        response = requests.get(flask_api_url)
        response.raise_for_status()
        property_obj = response.json()

        room_type_counts_raw = property_obj.get('room_types', '{}')
        if isinstance(room_type_counts_raw, str):
            try:
                room_type_counts = json.loads(room_type_counts_raw)
            except json.JSONDecodeError:
                room_type_counts = {}
        else:
            room_type_counts = room_type_counts_raw or {}

        if request.method == 'POST':
            user_id = request.session.get('user_id') 
            if not user_id:
                messages.error(request, "You must be logged in to book.")
                return redirect('login')

            user_name = request.POST.get('user-name')
            user_email = request.POST.get('user-email')
            user_phone = request.POST.get('user-phone')
            checkin_date = request.POST.get('checkin-date')
            checkout_date = request.POST.get('checkout-date')
            rooms = request.POST.get('rooms')
            room_type = request.POST.get('room-type')

            if not all([user_name, user_email, user_phone, checkin_date, checkout_date, rooms, room_type]):
                messages.error(request, "Please fill all required fields.")
                return redirect('book', id=id)

            try:
                checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d')
                checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d')
                if checkin_date >= checkout_date:
                    messages.error(request, "Check-out date must be after the check-in date.")
                    return redirect('booking_confirmation_hotelio', id=id)
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return redirect('book', id=id)

            rooms_requested = int(rooms)
            available_rooms = int(room_type_counts.get(room_type, 0))

            if rooms_requested > available_rooms:
                messages.error(request, f"Only {available_rooms} rooms available for {room_type}.")
                return redirect('booking_confirmation_hotelio', id=id)

         
            booking_data = {
                'user_id': user_id,
                'property_id': property_obj['id'],
                'user_name': user_name,
                'user_email': user_email,
                'user_phone': user_phone,
                'checkin_date': checkin_date.strftime('%Y-%m-%d'),
                'checkout_date': checkout_date.strftime('%Y-%m-%d'),
                'rooms_booked': rooms_requested,
                'room_type': room_type
            }

            flask_booking_url = f'{api}bookingAPI'
            try:
                book_response = requests.post(flask_booking_url, json=booking_data)
                if book_response.status_code == 201:
                    booking_id = book_response.json().get('booking_id')
                    return redirect('booking_confirmation_hotelio', booking_id=booking_id)
                else:
                    messages.error(request, "Booking failed through Flask API.")
                    return redirect('book', id=id)
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error connecting to booking API: {e}")
                return redirect('book', id=id)

        return render(request, 'book_property.html', {
            'property': property_obj,
            'room_type_counts': room_type_counts
        })

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Failed to connect to Flask API: {e}")
        return redirect('home')

    
def user_bookings(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "User not logged in.")
        return redirect('login')

    try:
        response = requests.get(f'{api}all/{user_id}')
        if response.status_code == 200:
            data = response.json()
            bookings = data.get('bookings', [])
            return render(request, 'bookings.html', {'bookings': bookings})
        else:
            messages.error(request, 'Failed to fetch bookings from server.')
    except requests.exceptions.RequestException as e:
        messages.error(request, f'Connection error: {e}')

    return render(request, 'bookings.html', {'bookings': []})

def cancel_booking_hotel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        booking.delete()
        messages.success(request, "Your booking has been successfully cancelled.")
        return redirect('user_bookings')  

    messages.error(request, "Invalid request method.")
    return redirect('user_bookings')

from django.contrib.auth import logout


@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  
        user.delete()    
        messages.success(request, "Your profile has been deleted successfully.")
        return redirect('home')  

    return render(request, 'delete_profile.html')


def dashboard(request):
 
    required_keys = ['name', 'email', 'phone', 'role']
    missing_keys = [key for key in required_keys if key not in request.session]

    if missing_keys:
     
        return redirect('login')


    return render(request, 'dashboard.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def edit_profile(request):
    if request.method == 'POST':
        

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name or not email or not phone:
            messages.error(request, "All fields are required.")
            return redirect('edit_profile')


        FLASK_API_URL = f'{api}update_profile'  
        flask_id = request.session.get('user_id')
        data = {
            'user_id': flask_id,
            'name': name,
            'email': email,
            'phone': phone
        }
        try:
            response = requests.post(
                FLASK_API_URL,
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                messages.success(request, 'Profile updated successfully!')

                request.session['name'] = name
                request.session['email'] = email
                request.session['phone'] = phone

                return redirect('dashboard')

            else:
                error_msg = response.json().get("error", "Unknown error occurred")
                messages.error(request, f'Failed to update profile: {error_msg}')
                return redirect('edit_profile')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'Error connecting to Flask API: {str(e)}')
            return redirect('edit_profile')

    return render(request, 'edit_profile.html', {'user': request.user})

def booking_confirmation_hotelio(request, booking_id):

    flask_api_url = f'{api}bookingAPI/{booking_id}' 

    try:
        response = requests.get(flask_api_url)
        if response.status_code != 200:
            raise Http404("Booking not found in Flask API")
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise Http404(f"Error fetching booking from backend: {e}")

    try:
        user_name = data['user_name']
        user_email = data['user_email']
        user_phone = data['user_phone']
        property_data = data['property'] 
        room_type = data['room_type']
        checkin_date = data['checkin_date']
        checkout_date = data['checkout_date']
        rooms_booked = int(data['rooms_booked'])

    
        from datetime import datetime
        checkin = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        checkout = datetime.strptime(checkout_date, '%Y-%m-%d').date()
        days = (checkout - checkin).days or 1

        price_per_room = Decimal(str(property_data['price']))
        total_price = price_per_room * rooms_booked * days

   
        code = request.GET.get('code', '').strip().upper()
        valid_codes = {'HOTELIO10': 10, 'GET20': 20, 'WELCOME5': 5}
        discount = valid_codes.get(code, 0)
        discount_amount = (total_price * Decimal(discount) / 100).quantize(Decimal('0.01'))
        final_price = total_price - discount_amount
        invalid_code = bool(code and code not in valid_codes)

        context = {
            'booking_id': booking_id,
            'property': property_data,
            'user_name': user_name,
            'user_email': user_email,
            'user_phone': user_phone,
            'checkin_date': checkin,
            'checkout_date': checkout,
            'room_type': room_type,
            'rooms_booked': rooms_booked,
            'days': days,
            'price_per_room': price_per_room,
            'total_price': total_price.quantize(Decimal('0.01')),
            'discount': discount,
            'discount_amount': discount_amount,
            'final_price': final_price.quantize(Decimal('0.01')),
            'invalid_code': invalid_code,
            'coupon_code': code,
            'request': request,
        }

        return render(request, 'booking_con_hotelio.html', context)

    except KeyError as e:
        raise Http404(f"Incomplete booking data received: {e}")



from django.views.decorators.csrf import csrf_exempt


def show_property_form(request):
    return render(request, 'listProperty.html')

import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
import requests

@csrf_exempt
def post_property_to_flask(request):
    if request.method == 'POST':
   
        image = request.FILES.get('property_image')
        image_filename = ''

   
        if image:
        
            image_filename = image.name  

            image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename)

      
            with open(image_path, 'wb') as f:
                for chunk in image.chunks(): 
                    f.write(chunk)

        hotel_name = request.POST.get('property_name')
        location = request.POST.get('property_location')
        license_number = request.POST.get('license_number')
        rooms_available = int(request.POST.get('rooms_available'))
        price = float(request.POST.get('price'))
        description = request.POST.get('property_description')

      
        room_types = {
            "AC": int(request.POST.get('room_types[AC]', 0)),
            "Non-AC": int(request.POST.get('room_types[Non-AC]', 0)),
            "Deluxe": int(request.POST.get('room_types[Deluxe]', 0)),
            "Duplex": int(request.POST.get('room_types[Duplex]', 0)),
            "Triplex": int(request.POST.get('room_types[Triplex]', 0)),
        }


        flask_user_id = request.session.get('user_id')
        if not flask_user_id:
            messages.error(request, "User is not authenticated via Flask.")
            return redirect('login') 

        flask_data = {
            'hotel_name': hotel_name,
            'location': location,
            'license_number': license_number,
            'rooms_available': rooms_available,
            'price': str(price),
            'description': description,
            'room_types': room_types,
            'user_id': flask_user_id, 
            'image': image_filename  
        }

        try:
            response = requests.post('http://127.0.0.1:5000/api/propertyAPI', json=flask_data)
            
            if response.status_code == 201:
                messages.success(request, 'Property created and sent to Flask successfully.')
            else:
                messages.error(request, 'Failed to send property data to Flask.')

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error sending data to Flask: {str(e)}")

  
        return redirect('owner_dashboard')

    return render(request, 'listProperty.html')

