from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/',views.register,name="register"),
    path('login/',views.loginpage,name="login"),
    path('logout/',views.logout_view, name='logout'),
    path('book-ride/', views.book_ride, name='book_ride'),  # Booking URL
    path('suc/', views.success, name='success'),
    path('recent-bookings/', views.recent_bookings, name='recent_bookings'),
    path('chatbot/', views.chat_view, name='chatbot_view'),
    
]
