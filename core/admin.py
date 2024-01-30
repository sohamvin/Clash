from django.contrib import admin
from .models import Custom_user,Mcq,Submission, CustomUser, CustomToken

# Register your models here.
# admin.site.register(Custom_user)
admin.site.register(Mcq)
# admin.site.register(Submission)
admin.site.register(CustomToken)
admin.site.register(CustomUser)
# admin.site.register(User)