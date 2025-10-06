from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Restaurant, Menu, Employee, Vote

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'created_at']

class MenuSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(
        source='restaurant', queryset=Restaurant.objects.all(), write_only=True
    )
    class Meta:
        model = Menu
        fields = ['id', 'restaurant', 'restaurant_id', 'date', 'items']

class LegacyMenuSerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(read_only=True)
    dishes = serializers.JSONField(source='items')
    class Meta:
        model = Menu
        fields = ['id', 'restaurant', 'date', 'dishes']

class CreateEmployeeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Employee.objects.create(user=user)
        return user

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'menu', 'created_at']

    def _get_employee(self):
        user = self.context['request'].user
        employee, _ = Employee.objects.get_or_create(user=user)
        return employee

    def validate(self, attrs):
        employee = self._get_employee()
        menu = attrs['menu']
        if Vote.objects.filter(employee=employee, menu=menu).exists():
            raise serializers.ValidationError("You have already voted for this menu.")
        return attrs

    def create(self, validated_data):
        employee = self._get_employee()
        return Vote.objects.create(employee=employee, **validated_data)
