from datetime import date
from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Restaurant, Menu, Employee
from .serializers import (
    RestaurantSerializer, MenuSerializer, LegacyMenuSerializer,
    CreateEmployeeSerializer, VoteSerializer
)
from .permissions import IsStaffOrReadOnly

class  VersionedSerializerMixin:
    legacy_serializer_class = None
    serializer_class = None

    def get_serializer_class(self):
        if self.request.version == 'legacy' and self.legacy_serializer_class:
            return self.legacy_serializer_class
        return self.serializer_class

class RestaurantViewSet(VersionedSerializerMixin, viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated & IsStaffOrReadOnly]

class MenuViewSet(VersionedSerializerMixin, viewsets.ModelViewSet):
    queryset = Menu.objects.select_related('restaurant').all()
    serializer_class = MenuSerializer
    legacy_serializer_class = LegacyMenuSerializer
    permission_classes = [IsAuthenticated & IsStaffOrReadOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        restaurant = serializer.validated_data['restaurant']
        menu_date = serializer.validated_data['date']
        if Menu.objects.filter(restaurant=restaurant, date=menu_date).exists():
            return Response({'detail': 'Menu already exist for this restaurant and date'}, status=400)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], url_path='today', permission_classes=[IsAuthenticated])
    def today(self, request):
        today = date.today()
        qs = self.get_queryset().filter(date=today)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='today/results', permission_classes=[IsAuthenticated])
    def today_results(self, request):
        today = date.today()
        qs = self.get_queryset().filter(date=today)
        results = []
        for i in qs:
            results.append({
                'menu_id': i.id,
                'restaurant': getattr(i.restaurant, 'name', None),
                'date': str(i.date),
                'votes': i.votes.count(),
            })
        return Response(results)

    @action(detail=True, methods=['post'], url_path='vote', permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        menu = self.get_object()
        serializer = VoteSerializer(data={'menu': menu.id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        vote = serializer.save()
        return Response({'id': vote.id, 'menu': menu.id, 'created_at': vote.created_at}, status=201)

class EmployeeViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin):
    queryset = User.objects.all()
    serializer_class = CreateEmployeeSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]