from django.contrib import admin
from .models import Mcq,Submission, CustomUser

# Register your models here.
# admin.site.register(Custom_user)
admin.site.register(Mcq)
# admin.site.register(Submission)
# admin.site.register(CustomToken)
admin.site.register(Submission)
admin.site.register(CustomUser)
# admin.site.register(User)