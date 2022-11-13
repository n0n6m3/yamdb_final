from re import search

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.utils import get_current_year

USER_ME_ERROR = 'Имя пользователя "me" зарезервировано!'
USER_REGEXP_ERROR = 'Имя пользователя содержит запрещенные символы'
YEAR_VALIDATION_ERROR = 'Год выпуска не может быть больше текущего!'
REVIEW_VALIDATION_ERROR = 'Нельзя оставить повторный отзыв'


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )]

    def validate_username(self, value):
        if 'me' == value.lower():
            raise serializers.ValidationError(USER_ME_ERROR)
        if not search(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(USER_REGEXP_ERROR)
        return value


class BaseUserSerializer(serializers.Serializer):
    username = serializers.RegexField(
        r'^[\w.@+-]+\Z', required=True, max_length=150
    )

    def validate_username(self, value):
        if 'me' == value.lower():
            raise serializers.ValidationError(USER_ME_ERROR)
        return value


class RegisterUserSerializer(BaseUserSerializer):
    email = serializers.EmailField(required=True, max_length=254)


class RequestTokenSerializer(BaseUserSerializer):
    confirmation_code = serializers.CharField(required=False, max_length=50)


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializerRead(serializers.ModelSerializer):
    category = CategorySerializer(required=True)
    genre = GenresSerializer(many=True, required=True,)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'category', 'genre', 'description', 'rating'
        )
        read_only_fields = ('__all__',)


class TitleSerializerWrite(serializers.ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug', required=True, queryset=Category.objects.all()
    )
    genre = SlugRelatedField(
        many=True, required=True, slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category', 'genre', 'description')

    def validate_year(self, value):
        if value > get_current_year():
            raise serializers.ValidationError(YEAR_VALIDATION_ERROR)
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data
        title = get_object_or_404(
            Title,
            id=self.context['view'].kwargs.get('title_id')
        )
        if request.user.reviews.filter(title=title).exists():
            raise serializers.ValidationError(REVIEW_VALIDATION_ERROR)
        return data

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review',)
