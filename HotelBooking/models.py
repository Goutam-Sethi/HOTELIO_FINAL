from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings



class AppUserManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is mandatory')  
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, name, phone, password, **extra_fields)

class AppUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    username = None
    objects = AppUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.email


from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.db import models

class Property(models.Model):
    ROOM_CHOICES = [
        ('STANDARD', 'Standard Room'),
        ('DELUXE', 'Deluxe Room'),
        ('AC', 'AC Room'),
        ('NON_AC', 'Non-AC Room'),
        ('DUPLEX', 'Duplex Suite'),
        ('TRIPLEX', 'Triplex Suite'),
    ]

    hotel_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')
    license_number = models.CharField(max_length=100)
    rooms_available = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    # This now stores a dictionary like {'AC': 3, 'Deluxe': 2, ...}
    room_types = models.JSONField(default=dict)

    owner = models.ForeignKey("AppUser", on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.hotel_name



class Booking(models.Model):
    ROOM_TYPE_CHOICES = [
        ('AC', 'AC Room'),
        ('NON_AC', 'Non-AC Room'),
        ('DUPLEX', 'Duplex Suite'),
        ('TRIPLEX', 'Triplex Suite'),
        ('DELUXE', 'Deluxe Room'),
        ('STANDARD', 'Standard Room'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    user_name = models.CharField(max_length=100)
    user_phone = models.CharField(max_length=15)
    user_email = models.EmailField()
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    rooms_booked = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='STANDARD')
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.property.hotel_name} ({self.room_type}) on {self.booked_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        # Ensure rooms are available before saving the booking
        if self.rooms_booked <= self.property.rooms_available:
            self.property.rooms_available -= self.rooms_booked
            self.property.save()  # Save the updated property after booking
            super(Booking, self).save(*args, **kwargs)
        else:
            raise ValueError("Not enough rooms available for this booking.")
