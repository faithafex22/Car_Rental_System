from django.urls import path
from . import views 

urlpatterns = [
    path('signup/', views.SignUpAPIView.as_view(), name='api_signup'),
    path('login/', views.LoginAPIView.as_view(), name='api_login'),
    path('profiles/', views.UserProfileListAPIView.as_view(), name='api_profile_list'),
    path('profiles/<int:pk>/', views.UserProfileRetrieveUpdateAPIView.as_view(), name='api_profile_detail'),
    path('vehicles/', views.VehicleListAPIView.as_view(), name='api-vehicle-list'),
    path('vehicles/<int:pk>/', views.VehicleDetailAPIView.as_view(), name='api-vehicle-detail'),
    path('vehicles/create/', views.VehicleCreateAPIView.as_view(), name='api-vehicle-create'),
    path('ratings/create/', views.RatingCreateAPIView.as_view(), name='api-rating-create'),
    path('ratings/', views.VehicleRatingListView.as_view(), name='api_vehicle-ratings'),
    path('vehicles/<int:vehicle_id>/rental_request/', views.RentalRequestCreateAPIView.as_view(), name='rental_request_create_api'),
    path('rental-requests/', views.RentalRequestListAPIView.as_view(), name='rental_request_list_api'),
    path('rental-requests/<int:pk>/', views.RentalRequestDetailAPIView.as_view(), name='rental_request_detail_api'),
    path('rental-requests/<int:pk>/decision/', views.RentalRequestDecisionAPIView.as_view(), name='rental_request_decision_api'),
    path('rental-requests/<int:rental_request_id>/mark-completed/', views.MarkRentalRequestCompleted.as_view(), name='mark-rental-request-completed_api'),
    path('rental-requests/<int:request_id>/return/', views.RentalReturnCreateAPIView.as_view(), name='rental_return_create_api'),
    path('complaints/create/', views.ComplaintCreateAPIView.as_view(), name='complaint_create_api'),
    path('complaints/', views.ComplaintListAPIView.as_view(), name='complaint-list-api'),
    path('complaints/<int:pk>/', views.ComplaintDetailAPIView.as_view(), name='complaint-detail-api'),   
    path('complaints/<int:pk>/status-update/', views.ComplaintStatusUpdateAPIView.as_view(), name='complaint_status_update_api'),
    path('reassign/', views.ReassignmentAPIView.as_view(), name='reassign_vehicle_api'),
    ]   
