from rest_framework import serializers
from django.contrib.auth.models import User
from django.db.models import Avg
from car_rental.models import UserProfile, Vehicle, Rating, RentalRequest, RentalReturn, Complaint, Reassignment



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('full_name', 'phone_number', 'address', 'bio')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'profile')

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        profile = UserProfile.objects.create(user=user, **profile_data)
        user.profile = profile
        return user




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'address', 'bio']
        read_only_fields = ['id', 'user']
        

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['vehicle', 'value', 'review']



class VehicleRatingSerializer(serializers.Serializer):
    vehicle = serializers.StringRelatedField()
    average_rating = serializers.FloatField()
    reviews = serializers.SerializerMethodField()
    
    def get_reviews(self, obj):
        reviews_data = []
        for rating in obj['reviews']:
            reviews_data.append({
                'review': rating.review,
                'user': rating.user.username
            })
        return reviews_data

class VehicleSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = '__all__'

    def get_avg_rating(self, obj):
        return obj.average_rating()
    

class RentalRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalRequest
        fields = [ 'user', 'start_date', 'end_date', ]
        

class RentalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalRequest
        fields = ['id', 'vehicle', 'user', 'start_date', 'end_date', 'status']
        

class RentalRequestDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalRequest
        fields = [ 'user', 'status', 'reason' ]


class RentalRequestCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalRequest
        fields = ['is_completed']


class RentalReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalReturn
        fields = ['id', 'user', 'vehicle', 'return_date', 'vehicle_state' ]


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'


class ReassignmentSerializer(serializers.ModelSerializer):
    rental_request_id = serializers.IntegerField()
    vehicle_id = serializers.IntegerField()

    class Meta:
        model = Reassignment
        fields = ['rental_request_id', 'vehicle_id', 'reassigned_by']
    