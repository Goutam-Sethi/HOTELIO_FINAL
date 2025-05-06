from django.urls import path
from . import views

urlpatterns = [
    path('',views.ride_book, name='cab_booking'),
    path('book/', views.book_car_view, name='car_selection'),
    path('confirmation/<int:car_id>/', views.confirm_booking, name='book_car'),
    path('confirm/', views.confirm_book, name='confirm_car'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
]
