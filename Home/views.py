from django.shortcuts import render, redirect
from .forms import CustomUserForm
from django.contrib.auth import authenticate,logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .models import *
from django.utils import timezone 
from django.contrib.auth.decorators import login_required
import google.generativeai as genai

# Home view
def home(request):
    return render(request, 'home.html')


def register(request):
    form = CustomUserForm
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration success. Login now!!!")
            return redirect('/login')
    return render(request,"register.html",{"form":form})

def loginpage(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(request, username=name, password=pwd)

        if user is not None:
            auth_login(request, user)
            
            if user.is_superuser:
                messages.success(request, "Superuser logged in successfully")
                return redirect('home')
            else:
                messages.success(request, "Logged in successfully")
                return redirect("home")
        else:
            messages.error(request, "Invalid Username or password")
            return redirect('login')

    return render(request, "login.html")

def logout_view(request):
    # Use the built-in logout function to log the user out
    logout(request)
    return redirect('login')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Booking, Trip, Vehicle, Driver, Location


from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Location, Vehicle, Driver, Trip, Booking  # Make sure to import your models

@login_required
def book_ride(request):
    if request.method == 'POST':
        # If the first form is submitted (search for vehicles & drivers)
        if 'confirm_booking' not in request.POST:
            start_location_id = request.POST.get('start_location')
            end_location_id = request.POST.get('end_location')

            # Validate that both start and end locations are selected
            if not start_location_id or not end_location_id:
                messages.error(request, "Please select both start and end locations.")
                return redirect('book_ride')  # Redirect back to the form
            
            # Additional booking information
            number_of_passengers = request.POST.get('number_of_passengers')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Fetch available vehicles based on the locations and capacity
            available_vehicles = Vehicle.objects.filter(
                available=True,
                seating_capacity__gte=number_of_passengers
            ).select_related('driver')

            # Fetch available drivers (you might want to filter based on other criteria)
            available_drivers = Driver.objects.filter(vehicles__available=True).distinct()

            return render(request, 'book_ride.html', {
                'available_vehicles': available_vehicles,
                'available_drivers': available_drivers,
                'start_location': Location.objects.get(id=start_location_id),
                'end_location': Location.objects.get(id=end_location_id),
                'number_of_passengers': number_of_passengers,
                'start_date': start_date,
                'end_date': end_date,
                'locations': Location.objects.all(),  # Include locations to render the form again if needed
            })

        # If the second form is submitted (confirm booking)
        else:
            # Retrieve data from the POST request
            vehicle_id = request.POST.get('vehicle')
            driver_id = request.POST.get('driver')
            start_location_id = request.POST.get('start_location')
            end_location_id = request.POST.get('end_location')
            number_of_passengers = request.POST.get('number_of_passengers')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Create a Trip object
            trip = Trip.objects.create(
                user=request.user,
                driver_id=driver_id,
                vehicle_id=vehicle_id,
                start_location_id=start_location_id,
                end_location_id=end_location_id,
                start_date=start_date,
                end_date=end_date,
                status='PENDING'
            )

            # Create a Booking object
            Booking.objects.create(
                user=request.user,
                trip=trip,
                number_of_passengers=number_of_passengers
            )
             # Update the vehicle's availability status
            vehicle = Vehicle.objects.get(id=vehicle_id)
            vehicle.available = False
            vehicle.save()

            messages.success(request, "Your booking has been confirmed!")
            return redirect('success')  # Redirect to a success page after booking

    # Render the form initially
    return render(request, 'book_ride.html', {
        'locations': Location.objects.all(),
    })


def success(request):
    return render(request,"success.html")

@login_required
def recent_bookings(request):
    # Fetch the recent bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')[:10]  # Get the latest 10 bookings
    context = {
        'bookings': bookings,
    }
    return render(request, 'recent_bookings.html', context)

from django.shortcuts import render
from django.http import JsonResponse
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
import os

api_key = "AIzaSyCT998P1u_n10ck9i_7Kqt1tWDmlJmLYoc"
genai.configure(api_key=api_key)


# Initialize model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the chatbot model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=(
        "Act as a chatbot for a Taxi booking website. For SUVs, the fare rate is Rs 20/km, "
        "for Sedans, it's Rs 17/km, and for Hatchbacks, it's Rs 12/km. "
        "Give additional details like distance and fare estimates. "
        "Predefined locations include Kattappana, Kumily, Kuttikkanam, Kottayam, "
        "Trivandrum, Thrissur, Kozhikode, Chennai, Bangalore, etc. "
        "Tell users the distances and any other relevant details."
    ),
)

# Start the chat session
chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": ["hi"],
        },
        {
            "role": "model",
            "parts": [
                "Hi there! 👋 Welcome to our taxi booking service. "
                "What kind of ride are you looking for today? We offer SUVs, Sedans, and Hatchbacks. "
                "Where are you headed? We have service to many locations including Kattappana, Kumily, "
                "Kuttikkanam, Kottayam, Trivandrum, Thrissur, Kozhikode, Chennai, Bangalore, and more. "
                "Just tell me your pickup and destination, and I'll give you a fare estimate and distance information. 😊",
            ],
        },
    ]
)

@csrf_exempt
def chat_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        response = chat_session.send_message(user_message)
        return JsonResponse({'response': response.text})

    return render(request, 'chatbot.html')
