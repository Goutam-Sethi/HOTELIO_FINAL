
from datetime import datetime
from .models import CarBooking, TaxiCar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone



def ride_book(request):
    return render(request, "taxi_index.html")


def confirm_book(request):
    return render(request, "taxi_booking.html")



from django.views.decorators.csrf import csrf_protect

@csrf_protect
def book_car_view(request):
    from django.contrib import messages
    from datetime import datetime

    if not request.session.get("is_authenticated"):
        messages.warning(request, "Please log in first to book a taxi.")
        return redirect("login")
    if request.method == "POST":
        pickup_location = request.POST.get("location")
        pickup_date = request.POST.get("pickup_date")
        pickup_time = request.POST.get("pickup_time")
        dropoff_date = request.POST.get("dropoff_date")
        dropoff_time = request.POST.get("dropoff_time")

        if not all([pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time]):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'taxi_index.html')

        cars = TaxiCar.objects.all()

        return render(request, 'taxi_detail.html', {'cars': cars, 'pickup_location': pickup_location,
                                                    'pickup_date': pickup_date, 'pickup_time': pickup_time,
                                                    'dropoff_date': dropoff_date, 'dropoff_time': dropoff_time})
    else:
        cars = TaxiCar.objects.all()
        return render(request, 'taxi_detail.html', {'cars': cars})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


def confirm_booking(request, car_id):
    from datetime import datetime
    from django.contrib import messages

  
    car = get_object_or_404(TaxiCar, id=car_id)

    if request.method == "POST":
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        pickup_location = request.POST.get("pickup_location")
        dropoff_location = request.POST.get("dropoff_location")
        pickup_datetime_str = request.POST.get("pickup_datetime")
        dropoff_datetime_str = request.POST.get("dropoff_datetime")

        if not all([username, phone, pickup_location, dropoff_location, pickup_datetime_str, dropoff_datetime_str]):
            messages.error(request, "Please fill all required fields.")
            return redirect('cab_booking')


        try:
            pickup_datetime = datetime.strptime(pickup_datetime_str, "%Y-%m-%dT%H:%M")
            dropoff_datetime = datetime.strptime(dropoff_datetime_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            messages.error(request, "Invalid date/time format.")
            return redirect('cab_booking')

        booking = CarBooking.objects.create(
            taxi_car=car,
            car_name=car.name,
            car_price=car.rate_per_hour,
            username=username,
            phone=phone,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_date=pickup_datetime.date(),
            pickup_time=pickup_datetime.time(),
            dropoff_date=dropoff_datetime.date(),
            dropoff_time=dropoff_datetime.time()
        )

        return redirect('booking_confirmation', booking_id=booking.id)  

 
    return render(request, 'taxi_booking.html', {'car': car})


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(CarBooking, id=booking_id)
    car = booking.taxi_car  # This is the linked TaxiCar object
    return render(request, 'booking_confirmation.html', {
        'booking': booking,
        'car': car
    })





def manage_bookings(request):
    bookings = CarBooking.objects.all()

    for booking in bookings:
        # Combine date and time
        dropoff_naive = datetime.combine(booking.dropoff_date, booking.dropoff_time)

        # Convert it to timezone-aware
        dropoff_datetime = timezone.make_aware(dropoff_naive)

        # Compare with current time
        booking.is_completed = dropoff_datetime <= timezone.now()

    context = {
        'bookings': bookings,
    }
    return render(request, 'taxi_manage_booking.html', context)




def cancel_booking(request, booking_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages

    booking = get_object_or_404(CarBooking, id=booking_id)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Your booking has been successfully cancelled.")
        return redirect('manage_bookings')
    messages.error(request, "Invalid request method.")
    return redirect('manage_bookings')
