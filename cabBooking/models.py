from django.db import models

from django.db import models

from datetime import datetime

class CarBooking(models.Model):
    taxi_car = models.ForeignKey('TaxiCar', on_delete=models.CASCADE, null=True, blank=True)
    car_name = models.CharField(max_length=100)
    car_price = models.DecimalField(max_digits=10, decimal_places=2)  # Rate per hour

    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255, default=-1)

    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    dropoff_date = models.DateField()
    dropoff_time = models.TimeField()

    username = models.CharField(max_length=100, default=-1)

    phone = models.CharField(max_length=20, default=-1)

    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.car_name} - {self.pickup_location} to {self.dropoff_location} ({self.pickup_date})"

    @property
    def pickup_datetime(self):
        # Combine pickup date and time into a datetime object
        return datetime.combine(self.pickup_date, self.pickup_time)

    @property
    def dropoff_datetime(self):
        # Combine dropoff date and time into a datetime object
        return datetime.combine(self.dropoff_date, self.dropoff_time)

    
# models.py

class TaxiCar(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_images/')
    rate_per_hour = models.DecimalField(max_digits=7, decimal_places=2)

    # Driver Information
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    driver_license = models.CharField(max_length=50)
    driver_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)  # Rating (out of 5)

    def __str__(self):
        return self.name
