from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import  View,  TemplateView, CreateView, UpdateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Avg
from datetime import date
from django.contrib import messages
from django.core.paginator import Paginator
from .models import UserProfile, Vehicle, Rating, RentalRequest, RentalReturn, Complaint, Reassignment
from django.shortcuts import get_object_or_404
from .forms import UserCreationFormWithProfile, LoginForm, LogoutForm, UserProfileForm, RatingForm, RentalReturnForm
from .forms import RentalRequestForm, ComplaintForm, ReassignmentForm
from django.contrib.auth.models import User


class SignUpView(CreateView):
    form_class = UserCreationFormWithProfile
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user_profile = UserProfile.objects.create(
            user=self.object,
            phone_number=form.cleaned_data['phone_number'],
            address=form.cleaned_data['address'],
            bio=form.cleaned_data['bio']
        )
        return response


class LoginView(View):
    form_class = LoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid username or password')
        return render(request, self.template_name, {'form': form})
    
class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'
    form_class = LogoutForm
    
    
class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.userprofile


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user.userprofile


class HomePageView(TemplateView):
    template_name = 'home.html'


class VehicleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Vehicle
    fields = ['name', 'brand', 'year', 'photo', 'description', 'price', 'status']
    template_name = 'car_rental/vehicle_create.html'
    success_url = reverse_lazy('vehicle_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff 


class VehicleListView(ListView ):
    model = Vehicle
    context_object_name = 'vehicles'
    template_name = 'car_rental/vehicle_list.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(price__icontains=query) |
                Q(year__icontains=query)
            )

        queryset = queryset.filter(status="available")
        queryset = queryset.annotate(avg_rating=Avg('rating__value'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')

        paginator = Paginator(self.object_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['paginator'] = paginator

        return context


class VehicleDetailView(LoginRequiredMixin, DetailView):
    model = Vehicle
    template_name = 'car_rental/vehicle_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = context['object']
        ratings = Rating.objects.filter(vehicle=vehicle)
        context['average_rating'] = ratings.aggregate(Avg('value'))['value__avg']
        context['ratings'] = ratings
        return context
    
    

class RatingCreateView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RatingForm
    template_name = 'car_rental/rating_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.vehicle_id = self.kwargs['vehicle_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vehicle_detail', kwargs={'pk': self.kwargs['vehicle_id']})

    def get_initial(self):
        initial = super().get_initial()
        initial['vehicle'] = Vehicle.objects.get(id=self.kwargs.get('vehicle_id'))
        return initial


class RentalRequestCreateView(LoginRequiredMixin, CreateView):
    model = RentalRequest
    form_class = RentalRequestForm
    template_name = 'car_rental/rental_request_form.html'
    success_url = reverse_lazy('rental_request_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        vehicle_id = self.kwargs.get('vehicle_id')
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(id=vehicle.id)
        #form.initial['vehicle'] = vehicle
        return form

    def form_valid(self, form):
        vehicle_id = self.kwargs.get('vehicle_id')
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        if vehicle.status == 'available':
            form.instance.user = self.request.user
            form.instance.vehicle = vehicle
            form.instance.status = 'pending'
            form.save()

            if form.instance.status == 'approved':
                vehicle.status = 'rented'
                vehicle.save()

            return super().form_valid(form)
        else:
            messages.warning(self.request, 'Vehicle is currently rented. Please choose another vehicle.')
            return redirect('vehicle_list')



class RentalRequestListView(LoginRequiredMixin, ListView):
    model = RentalRequest
    template_name = 'car_rental/rental_request_list.html'
    context_object_name = 'rental_requests'

    def get_queryset(self):
        if self.request.user.is_staff:
            return RentalRequest.objects.filter(is_deleted=False)
        return RentalRequest.objects.filter(user=self.request.user)
    

class RentalRequestDetailView(LoginRequiredMixin, DetailView):
    model = RentalRequest
    template_name = 'car_rental/rental_request_detail.html'
    context_object_name = 'rental_request'


class RentalRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RentalRequest
    fields = ['start_date', 'end_date']
    template_name = 'car_rental/rental_request_decision.html'
    success_url = reverse_lazy('rental_request_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class RentalRequestDecisionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RentalRequest
    fields = ['status', 'reason']
    template_name = 'car_rental/rental_request_decision.html'
    success_url = reverse_lazy('rental_request_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        rental_request = form.save(commit=False)
        if rental_request.status == 'approved':
            rental_request.vehicle.status = 'rented'
            rental_request.vehicle.save()
        elif rental_request.status == 'rejected':
            rental_request.is_completed = False
        rental_request.save()
        return super().form_valid(form)
    

class RentalReturnCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = RentalReturn
    form_class = RentalReturnForm
    template_name = 'car_rental/rental_return_form.html'
    success_url = reverse_lazy('rental_request_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        rental_request = get_object_or_404(RentalRequest, id=self.kwargs['rental_request_id'])
        form.fields['rental_request'].queryset = RentalRequest.objects.filter(id=rental_request.id)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(id=rental_request.vehicle.id)
        return form

    def form_valid(self, form):
        rental_request = get_object_or_404(RentalRequest, id=self.kwargs['rental_request_id'])
        if not rental_request.status == 'approved':
            raise Http404("The rental request must be approved before creating a rental return")

        rental_return = form.save(commit=False)
        rental_return.vehicle = rental_request.vehicle
        rental_return.return_date = date.today()

        vehicle = rental_request.vehicle
        vehicle.status = 'available'
        vehicle.save()

        rental_request.is_returned = True
        rental_request.is_completed = True
        rental_request.save()

        rental_return.rental_request = rental_request
        rental_return.save()

        return super().form_valid(form)



class RentalReturnListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = RentalReturn
    template_name = 'car_rental/rental_return_list.html'
    context_object_name = 'rental_returns'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'car_rental/complaint_form.html'
    success_url = reverse_lazy('complaint_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class ComplaintListView(LoginRequiredMixin, ListView):
    model = Complaint
    template_name = 'car_rental/complaint_list.html'
    context_object_name = 'complaints'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Complaint.objects.all()
        return Complaint.objects.filter(user=self.request.user)
    

class ComplaintDetailView(LoginRequiredMixin, DetailView):
    model = Complaint
    template_name = 'car_rental/complaint_detail.html'
    context_object_name = 'complaint'


class ComplaintStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Complaint
    fields = ['reply', 'status']
    template_name = 'car_rental/complaint_status_update.html'
    success_url = reverse_lazy('complaint_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff


class ReassignVehicleView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'car_rental/reassign_vehicle.html'
    form_class = ReassignmentForm
    success_url = reverse_lazy('rental_request_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        rental_request = get_object_or_404(RentalRequest, id=self.kwargs['rental_request_id'])
        form.fields['rental_request'].queryset = RentalRequest.objects.filter(id=rental_request.id)
        form.fields['vehicle'].queryset = Vehicle.objects.filter(status='available')
        form.fields['reassigned_by'].queryset = User.objects.filter(id=self.request.user.id)
        
        return form

    def form_valid(self, form):
        rental_request = form.cleaned_data['rental_request']
        vehicle = form.cleaned_data['vehicle']
        reassigned_by = form.cleaned_data['reassigned_by']
        Reassignment.objects.create(
            rental_request=rental_request,
            vehicle=vehicle,
            reassigned_by=reassigned_by,
        )
        rental_request.vehicle = vehicle  
        rental_request.save()
        return super().form_valid(form)


class VehicleRatingListView(ListView, LoginRequiredMixin):
    model = Vehicle
    template_name = 'car_rental/ratings_reviews.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle_ratings = []
        for vehicle in context['object_list']:
            average_rating = Rating.objects.filter(vehicle=vehicle).aggregate(avg_rating=Avg('value'))
            reviews = Rating.objects.filter(vehicle=vehicle).exclude(review__exact='').select_related('user')
            vehicle_ratings.append({
                'vehicle': vehicle,
                'average_rating': round(average_rating['avg_rating'], 1) if average_rating['avg_rating'] else None,
                'reviews': reviews,
            })
        context['vehicle_ratings'] = vehicle_ratings
        return context