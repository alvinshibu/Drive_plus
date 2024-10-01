from django.contrib.auth.models import User
from django.db import models

from django.utils import timezone 


# Model to store predefined locations
class Location(models.Model):
    name = models.CharField(max_length=255)
    

    def __str__(self):
        return self.name

# Model to store information about drivers
class Driver(models.Model):
    name = models.CharField(max_length=15,default="driver")
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=20)
    address = models.TextField()
    rating = models.FloatField(default=0.0)  # Driver rating
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

# Model to store information about vehicles
class Vehicle(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20)  # e.g., Car, Bike, Auto
    vehicle_model = models.CharField(max_length=50)
    registration_number = models.CharField(max_length=20, unique=True)
    seating_capacity = models.IntegerField()
    color = models.CharField(max_length=30)
    available = models.BooleanField(default=True)  # To indicate if the vehicle is available
    fare_per_km = models.DecimalField(max_digits=10, decimal_places=2,default=0) 
    def __str__(self):
        return f"{self.vehicle_model} - {self.registration_number}"

# Model to store information about trips
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='trips_from')  # Using predefined locations
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='trips_to')  # Using predefined locations
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'), 
        ('ONGOING', 'Ongoing'), 
        ('COMPLETED', 'Completed'), 
        ('CANCELLED', 'Cancelled')
    ], default='PENDING')

    def __str__(self):
        return f"Trip {self.id} by {self.user.username} - {self.status}"

# Model to store booking information
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    number_of_passengers = models.IntegerField()

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for {self.number_of_passengers} passengers"
