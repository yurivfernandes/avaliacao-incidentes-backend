from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="api_login"),
    path("logout/", views.LogoutView.as_view(), name="api_logout"),
    path("create/", views.UserCreateView.as_view(), name="create"),
    path(
        "check-username/<str:username>/",
        views.CheckUsernameView.as_view(),
        name="check-username",
    ),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/<int:user_id>/",
        views.ProfileView.as_view(),
        name="update-user",
    ),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path(
        "users/", views.UserListView.as_view(), name="user-list"
    ),  # Nova URL    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path(
        "empresa/list/", views.EmpresaListView.as_view(), name="empresa-list"
    ),
    path(
        "empresa/create/",
        views.EmpresaCreateView.as_view(),
        name="empresa-create",
    ),
    path(
        "empresa/<int:empresa_id>/",
        views.EmpresaEditView.as_view(),
        name="empresa-edit",
    ),
]
