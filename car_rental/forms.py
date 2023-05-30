from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, RentalRequest, Vehicle, Complaint, Rating,  Reassignment, RentalReturn
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserCreationFormWithProfile(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = forms.CharField(max_length=20, required=True)
    address = forms.CharField(max_length=255, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'address', 'bio')


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class LogoutForm(forms.Form):
    pass


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'bio', 'phone_number', 'address', ]
        

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('value', 'review')

        
class RentalRequestDecisionForm(forms.ModelForm):
    DECISION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        
    ]

    decision = forms.ChoiceField(choices=DECISION_CHOICES, widget=forms.RadioSelect())
    reason = forms.CharField(required=False, widget=forms.Textarea())

    class Meta:
        model = RentalRequest
        fields = ['decision', 'reason']
        
        
class RentalRequestForm(forms.ModelForm):
    
    class Meta:
        model = RentalRequest
        fields = ['vehicle', 'start_date', 'end_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if end_date and start_date:
            if end_date < start_date:
                raise ValidationError('End date cannot be earlier than start date')     

   
class RentalReturnForm(forms.ModelForm):
    class Meta:
        model = RentalReturn
        fields = ['rental_request', 'vehicle', 'vehicle_state',  'return_date']  

    
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [ 'vehicle', 'description']
        
        
class ReassignmentForm(forms.ModelForm):
    class Meta:
        model = Reassignment
        fields = ['rental_request', 'vehicle', 'reassigned_by']


        