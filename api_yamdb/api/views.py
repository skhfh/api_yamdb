from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from .mixins import CreateListDestroyViewSet
from .permissions import (AllActionsOnlyAdminPermission,
                          ReadOnlyOrAdminPermission,
                          ReviewCommentPermission)
from .serializers import (ReviewSerializer, CategorySerializer,
                          AuthSignupSerializer, AuthTokenSerializer,
                          CommentSerializer, GenreSerializer,
                          TitleGetSerializer, TitleWriteSerializer,
                          MeSerializer, UsersSerializer)

User = get_user_model()


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (ReadOnlyOrAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (ReadOnlyOrAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    serializer_class = TitleGetSerializer
    permission_classes = (ReadOnlyOrAdminPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermission,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        new_queryset = title.reviews.all()
        return new_queryset


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentPermission,)
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        new_queryset = review.comments.all()
        return new_queryset


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (AllActionsOnlyAdminPermission,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == 'PATCH':
            serializer = MeSerializer(request.user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_signup(request):
    serializer = AuthSignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        email = serializer.data.get('email')
        username = serializer.data.get('username')
        user, _ = User.objects.get_or_create(
            username=username,
            email=email
        )
    except IntegrityError:
        return Response('Пользователь с таким username уже существует',
                        status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        f'{username}, your Confirmation code',
        confirmation_code,
        'ymdb@ymdb.com',
        [email],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_token(request):
    serializer = AuthTokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data.get('confirmation_code')
        if default_token_generator.check_token(user, confirmation_code):
            refresh = RefreshToken.for_user(user)
            return Response({'token': str(refresh.access_token)},
                            status=status.HTTP_200_OK)
        return Response({'confirmation_code': 'Неверный код подтверждения'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
