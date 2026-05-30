from django.urls import path

from .views import (
    signup_view,
    login_view,
    logout_view,
    account_dashboard,
    alerts_dashboard,
)

urlpatterns = [

    path(
        "signup/",
        signup_view,
        name="signup"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "signout/",
        logout_view,
        name="logout"
    ),

    path(
        "account/",
        account_dashboard,
        name="account_dashboard"
    ),

    path(
        "alerts/",
        alerts_dashboard,
        name="alerts_dashboard"
    ),

]
