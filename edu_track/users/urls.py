from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserLogoutView,
    CustomTokenRefreshView,
    SendTokenView,
    ValidateTokenView,
)
from django.urls import path

urlpatterns = [
    path("/register", RegisterView.as_view(), name="create-user"),
    path("/login", CustomTokenObtainPairView.as_view(), name="login-user"),
    path("/logout", UserLogoutView.as_view(), name="logout_view"),
    path("/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("/tokens/resend", SendTokenView.as_view()),
    path("/tokens/validate", ValidateTokenView.as_view()),
]
