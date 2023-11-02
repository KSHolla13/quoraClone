from django.contrib import admin
from .models import Question , Profile , Comment 
# Register your models here.
admin.site.register(Question)
admin.site.register(Profile)
admin.site.register(Comment)
