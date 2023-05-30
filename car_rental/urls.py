from django.urls import path
from django.contrib.auth.views import LoginView
from .import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('', views.HomePageView.as_view(), name='home'),
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    path('vehicles/<int:vehicle_id>/rate/', views.RatingCreateView.as_view(), name='vehicle_rating_create'),
    path('vehicle-ratings/', views.VehicleRatingListView.as_view(), name='vehicle_rating_list'),
    path('rental_request/<int:vehicle_id>/create/', views.RentalRequestCreateView.as_view(), name='rental_request_create'),
    path('rental_requests/', views.RentalRequestListView.as_view(), name='rental_request_list'),
    path('rental_returns/', views.RentalReturnListView.as_view(), name='rental_return_list'),
    path('rental_request/<int:pk>/', views.RentalRequestDetailView.as_view(), name='rental_request_detail'),
    path('rental_request/<int:pk>/decision/', views.RentalRequestDecisionView.as_view(), name='rental_request_decision'),
    path('rental_request/<int:rental_request_id>/rental_return/create/', views.RentalReturnCreateView.as_view(), name='rental_return_create'),
    path('complaint/create/', views.ComplaintCreateView.as_view(), name='complaint_create'),
    path('complaints/', views.ComplaintListView.as_view(), name='complaint_list'),
    path('complaints/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaints/<int:pk>/update/', views.ComplaintStatusUpdateView.as_view(), name='complaint_update'),
    path('rental_request/<int:rental_request_id>/reassign/', views.ReassignVehicleView.as_view(), name='reassign_vehicle'),
]


    



    


