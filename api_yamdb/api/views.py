from random import randint

from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User
from reviews.utils import is_read_method
from api_yamdb.settings import EMAIL_FROM
from . import filters, permissions, serializers

EMAIL_SUBJECT = 'Письмо с кодом подтверждения'
EMAIL_MESSAGE = 'Ваш код подтверждения {}.'
USERNAME_EXISTS_ERROR = {
    'error': 'Пользователь с данным именем пользователя существует!'
}
EMAIL_EXISTS_ERROR = {
    'error': ('Пользователь с данным email существует!')
}
CODE_ERROR = {'error': 'Неправильный confirmation_code!'}


class BaseNameSlugViewSet(
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsReadOnly | permissions.IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(BaseNameSlugViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenresSerializer


class CategoryViewSet(BaseNameSlugViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all().order_by('id')
        .annotate(rating=Avg('reviews__score'))
    )
    permission_classes = (permissions.IsReadOnly | permissions.IsAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.TitleFilter

    def get_serializer_class(self):
        if is_read_method(self.request.method):
            return serializers.TitleSerializerRead
        return serializers.TitleSerializerWrite


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserModelSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAdmin | IsAdminUser,)
    lookup_field = 'username'


class UserMeViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = serializers.UserModelSerializer(self.request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = serializers.UserModelSerializer(
            self.request.user,
            data=self.request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
        return Response(
            {**serializer.validated_data, 'role': request.user.role},
            status=status.HTTP_200_OK
        )


class RegisterUserView(APIView):
    permission_classes = (AllowAny,)

    def code_generator(self):
        return '-'.join(map(str, (randint(1000, 9999) for i in range(5))))

    def post(self, request):
        serializer = serializers.RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, created = User.objects.get_or_create(
                **serializer.validated_data
            )
        except IntegrityError as err:
            created = False
            if 'username' in err.args[0]:
                error_message = USERNAME_EXISTS_ERROR
            else:
                error_message = EMAIL_EXISTS_ERROR
            return Response(
                error_message,
                status=status.HTTP_400_BAD_REQUEST
            )
        if created:
            user.confirmation_code = self.code_generator()
            user.save()
        send_mail(
            subject=EMAIL_SUBJECT,
            message=EMAIL_MESSAGE.format(user.confirmation_code),
            from_email=EMAIL_FROM,
            recipient_list=(serializer.validated_data['email'],),
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RequestTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = serializers.RequestTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )
        if (user.confirmation_code
           != serializer.validated_data['confirmation_code']):
            return Response(CODE_ERROR, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })


class RelatedBaseSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthorOrAdminOrModeratorOrReadonly,)
    parent_model = None
    url_lookup = None
    child_relation = None
    field_name = None

    def get_parent_object(self):
        return get_object_or_404(
            self.parent_model, id=self.kwargs.get(self.url_lookup)
        )

    def get_queryset(self):
        return getattr(self.get_parent_object(), self.child_relation).all()

    def perform_create(self, serializer):
        save_kwargs = {
            self.field_name: self.get_parent_object()
        }
        serializer.save(author=self.request.user, **save_kwargs)


class ReviewViewSet(RelatedBaseSet):
    serializer_class = serializers.ReviewSerializer
    parent_model = Title
    url_lookup = 'title_id'
    child_relation = 'reviews'
    field_name = 'title'


class CommentViewSet(RelatedBaseSet):
    serializer_class = serializers.CommentSerializer
    parent_model = Review
    url_lookup = 'review_id'
    child_relation = 'comments'
    field_name = 'review'
