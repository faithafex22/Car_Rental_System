from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import  Avg


class UserProfile(models.Model):
    full_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    

    def __str__(self):
        return self.user.username


class Vehicle(models.Model):

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('in_maintenance', 'In_Maintenance'),
    ]

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='vehicle_photos')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField( max_length=20, choices=STATUS_CHOICES, default='available',)

    def __str__(self):
        return self.name
    
    def average_rating(self):
        avg_rating = Rating.objects.filter(vehicle=self).aggregate(Avg('value'))['value__avg']
        if avg_rating is not None:
            return round(avg_rating)
        else:
            return 0
    
    class Meta:
        ordering = ['-id']


class RentalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_returned = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def undelete(self):
        self.is_deleted = False
        self.save()

    def is_active(self):
        return not self.is_deleted

    def __str__(self):
        return f'Request for {self.vehicle.name} by {self.user.username}'
    
    def total_cost(self):
        days = (self.end_date - self.start_date).days + 1
        return self.vehicle.price * days
    
    class Meta:
        ordering = ['-id']
        
        

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('solved', 'Solved'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'Complaint by {self.user.username}'


class RentalReturn(models.Model):
    VEHICLE_STATE_CHOICES = [
        ('clean', 'Clean'),
        ('damaged', 'Damaged'),
    ]
    rental_request = models.OneToOneField(RentalRequest, on_delete=models.CASCADE, null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    return_date = models.DateField()
    vehicle_state = models.CharField(max_length=20, choices=VEHICLE_STATE_CHOICES, default='clean')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'Return of {self.vehicle.name} for {self.rental_request}'


class Reassignment(models.Model):
    rental_request = models.ForeignKey(RentalRequest, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    reassigned_at = models.DateTimeField(auto_now_add=True)
    reassigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reassignments')

    def __str__(self):
        return f'{self.vehicle.name} assigned to {self.rental_request.user}'

class Rating(models.Model):
    VALUE_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='rating')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices=VALUE_CHOICES, default=0)
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vehicle.name} - {self.user.username} ({self.value})"
