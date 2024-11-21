import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from .hidden import CurrentReviewDefault, CurrentTitleDefault

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.HiddenField(default=CurrentTitleDefault())
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        """Проверяем, оставлял ли пользователь отзыв к произведению ранее."""
        view = self.context['view']
        request = self.context['request']
        title_id = view.kwargs.get('title_id')
        author = request.user
        if (Review.objects.filter(author=author,
                                  title__id=title_id).exists()
                and request.method != 'PATCH'):
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв к этому произведению.'
            )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.HiddenField(
        default=CurrentReviewDefault())
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        model = Comment


class BaseCustomUserSerializer(serializers.Serializer):
    """Базовый сериализатор для работы с пользователями"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    def validate_username(self, username):
        if (username.lower() == 'me'
                or re.match(r'^[\w.@+-]', username) is None):
            raise serializers.ValidationError('Нельзя создать пользователя с'
                                              'таким username!')
        return username


class AuthSignupSerializer(BaseCustomUserSerializer):
    """Сериализатор для регистрации пользователей"""
    def validate(self, data):
        if (not User.objects.filter(username=data['username']).exists()
                and User.objects.filter(email=data['email']).exists()):
            raise serializers.ValidationError('Пользователь с таким email уже'
                                              'существует!')
        return data


class AuthTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""
    username = serializers.SlugField(max_length=150)
    confirmation_code = serializers.CharField()


class UsersSerializer(BaseCustomUserSerializer, serializers.ModelSerializer):
    """Сериализатор для работы с пользователями"""
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Пользователь с таким email уже'
                                            'существует')]
    )
    username = serializers.SlugField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Пользователь с таким username уже'
                                            'существует')],
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')


class MeSerializer(UsersSerializer):
    """Сериализатор для эндпоинта users/me - данные о себе, на основе
    UsersSerializer.
    email и username необязательны при редактировании профиля
    """
    email = serializers.EmailField(
        required=False,
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Пользователь с таким email уже'
                                            'существует')]
    )
    username = serializers.SlugField(
        required=False,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='Пользователь с таким username уже'
                                            'существует')]
    )

    class Meta(UsersSerializer.Meta):
        read_only_fields = ('role',)
