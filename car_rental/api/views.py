from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, render
from rest_framework.generics import CreateAPIView
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import  LoginSerializer, UserSerializer, UserProfileSerializer, RatingSerializer, VehicleSerializer, VehicleRatingSerializer
from .serializers import RentalRequestSerializer, VehicleSerializer, RentalReturnSerializer, ComplaintSerializer, ReassignmentSerializer
from .serializers import RentalRequestDecisionSerializer, RentalRequestCreateSerializer, RentalRequestCompletedSerializer
from rest_framework import generics
from django.db.models import Avg
from car_rental.models import UserProfile, Vehicle, Rating, RentalRequest, RentalReturn, Complaint, Reassignment


class SignUpAPIView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        data = {'message': 'User created successfully'}
        response.data = data
        return response
    

class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                    login(request, user)
                    return Response({'message': 'Login successful.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserProfileListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)


class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        

class VehicleCreateAPIView(generics.CreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class VehicleListAPIView(generics.ListAPIView):
    queryset = Vehicle.objects.filter(status='available')
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Vehicle.objects.annotate(avg_rating=Avg('rating__value'))
        return queryset

class VehicleDetailAPIView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.annotate(avg_rating=Avg('rating__value'))
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    


class RatingCreateAPIView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    queryset = Rating.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RentalRequestCreateAPIView(generics.CreateAPIView):
    serializer_class = RentalRequestCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        vehicle_id = self.kwargs.get('vehicle_id')
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        
        if vehicle.status == 'available':
            serializer.save(user=self.request.user, vehicle=vehicle, status='pending')

            if serializer.instance.status == 'approved':
                vehicle.status = 'rented'
                vehicle.save()
        else:
            message = 'Vehicle is currently rented. Please choose another vehicle.'
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)


class RentalRequestListAPIView(generics.ListAPIView):
    serializer_class = RentalRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return RentalRequest.objects.all()
        return RentalRequest.objects.filter(user=user)

        
class RentalRequestDetailAPIView(generics.RetrieveAPIView):
    serializer_class = RentalRequestSerializer
    queryset = RentalRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if not self.request.user.is_staff and obj.user != self.request.user:
            raise PermissionDenied()
        return obj

class RentalRequestDecisionAPIView(generics.UpdateAPIView):
    queryset = RentalRequest.objects.all()
    serializer_class = RentalRequestDecisionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, *args, **kwargs):
        rental_request = get_object_or_404(RentalRequest, pk=kwargs['pk'])
        if not request.user.is_superuser and not request.user.is_staff:
            raise PermissionDenied()
        serializer = self.get_serializer(rental_request, data=request.data)
        serializer.is_valid(raise_exception=True)
        rental_request = serializer.save()
        if rental_request.status == 'approved':
            rental_request.vehicle.status = 'rented'
            rental_request.vehicle.save()
        elif rental_request.status == 'rejected':
            rental_request.is_completed = False
        rental_request.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class MarkRentalRequestCompleted(APIView):
    def post(self, request, rental_request_id, format=None):
        rental_request = RentalRequest.objects.get(pk=rental_request_id)
        if rental_request.status != 'approved' :
            return Response({'error': 'This rental request cannot be marked as completed'}, status=status.HTTP_400_BAD_REQUEST)
        rental_request.is_completed = True
        rental_request.save()
        serializer = RentalRequestCompletedSerializer(rental_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
   

class RentalReturnCreateAPIView(generics.CreateAPIView):
    queryset = RentalReturn.objects.all()
    serializer_class = RentalReturnSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        rental_request = get_object_or_404(RentalRequest, id=self.kwargs['request_id'])
        serializer.save(
            user=self.request.user,
            vehicle=rental_request.vehicle,
        )
        rental_request.is_completed = True
        rental_request.vehicle.status = 'available'
        rental_request.vehicle.save()
        rental_request.delete()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class ComplaintCreateAPIView(generics.CreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ComplaintListAPIView(generics.ListAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Complaint.objects.all()
        return Complaint.objects.filter(user=user)


class ComplaintDetailAPIView(generics.RetrieveAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]


class ComplaintStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class ReassignmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ReassignmentSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            rental_request_id = serializer.validated_data['rental_request_id']
            vehicle_id = serializer.validated_data['vehicle_id']
            rental_request = RentalRequest.objects.get(id=rental_request_id)
            vehicle = Vehicle.objects.get(id=vehicle_id)
            reassigned_by = request.user
            reassignment = Reassignment.objects.create(
                rental_request=rental_request,
                vehicle=vehicle,
                reassigned_by=reassigned_by,
            )
            rental_request.vehicle = vehicle
            rental_request.save()
            vehicle.status = 'unavailable'
            vehicle.save()
            return Response({'reassignment_id': reassignment.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleRatingListView(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleRatingSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_ratings = []
        for vehicle in queryset:
            average_rating = Rating.objects.filter(vehicle=vehicle).aggregate(avg_rating=Avg('value'))
            reviews = Rating.objects.filter(vehicle=vehicle).exclude(review__exact='').select_related('user')
            vehicle_ratings.append({
                'vehicle': vehicle,
                'average_rating': round(average_rating['avg_rating'], 1) if average_rating['avg_rating'] else None,
                'reviews': reviews,
            })
        return vehicle_ratings