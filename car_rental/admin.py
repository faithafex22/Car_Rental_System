from django.contrib import admin
from .models import Vehicle, RentalRequest, Complaint, RentalReturn, Rating, UserProfile, Reassignment


admin.site.register(Vehicle)
admin.site.register(RentalRequest)
admin.site.register(Complaint)
admin.site.register(RentalReturn)
admin.site.register(Rating)
admin.site.register(UserProfile)
admin.site.register(Reassignment)



