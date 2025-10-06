from django.db import models
from django.contrib.auth.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    date = models.DateTimeField()
    items = models.JSONField(default=list)

    class Meta:
        unique_together = ('restaurant', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.restaurant.name} - {self.date}"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')

    def __str__(self):
        return self.user.username

class Vote(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='votes')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'menu')

    def __str__(self):
        return f"{self.employee} - {self.menu}"