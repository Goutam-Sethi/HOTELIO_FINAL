from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('listProperty/',views.show_property_form,name='listProperty'),
    path('submit-property/', views.post_property_to_flask, name='post_property_to_flask'),
   path('login/',views.user_login,name="login"),
    path('signup/',views.signup,name="signup"),
    path('forgot/',views.forgot,name='forgot'),
    path('privacy/',views.privacy,name="privacy"),
    path('contact_us/',views.contact,name="contact_us"),
    path('search/', views.search_properties, name='search_properties'),
    path('properties/', views.available_properties, name='available_properties'),
    path('bookProperty/<int:id>/', views.book, name='book'),
    path('my-bookings/', views.user_bookings, name='user_bookings'),
    path('delete-profile/', views.delete_profile, name='delete_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('about/', views.about_us, name='about_us'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking_hotel, name='cancel_booking_hotel'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation_hotelio, name='booking_confirmation_hotelio'),
]