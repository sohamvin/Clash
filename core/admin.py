from django.contrib import admin
from .models import Custom_user,Mcq,Submission

# Register your models here.
admin.site.register(Custom_user)
admin.site.register(Mcq)
admin.site.register(Submission)
# admin.site.register(User)