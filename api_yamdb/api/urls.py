from django.urls import include, path
from rest_framework import routers

from . import views

api_v1 = routers.DefaultRouter()
api_v1.register(r'categories', views.CategoryViewSet, basename='categories')
api_v1.register(r'genres', views.GenreViewSet, basename='genres')
api_v1.register(r'titles', views.TitleViewSet, basename='titles')
api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet, basename='comments'
)
api_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet, basename='reviews'
)
api_v1.register('users', views.UserViewSet, basename='users')

auth_urls = [
    path('token/', views.RequestTokenView.as_view(), name='auth_token'),
    path('signup/', views.RegisterUserView.as_view(), name='auth_signup')
]

urlpatterns = [
    path('v1/auth/', include(auth_urls)),
    path('v1/users/me/', views.UserMeViewSet.as_view(), name='users_me'),
    path('v1/', include(api_v1.urls)),
]
