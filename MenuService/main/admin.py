from django.contrib import admin
from .models import Restaurant, Menu, Employee, Vote

admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(Employee)
admin.site.register(Vote)
