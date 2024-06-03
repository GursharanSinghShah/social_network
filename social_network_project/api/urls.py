from django.urls import path
from .views import UserSignupView, UserLoginView, UserSearchView, FriendRequestViewSet
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='search'),
]


router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')

urlpatterns += router.urls