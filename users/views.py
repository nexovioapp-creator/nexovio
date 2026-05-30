from .models import RecentlyViewed, CompareHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from mobiles.models import PriceAlert
from django.contrib.auth import (
    authenticate,
    login,
    logout
)
from django.contrib import messages

# =========================
# SIGNUP
# =========================

def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")

        email = request.POST.get("email")

        password = request.POST.get("password")


        # USER EXISTS
        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect("signup")


        # CREATE USER
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect("mobile_list")


    return render(
        request,
        "users/signup.html"
    )


# =========================
# LOGIN
# =========================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")


        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("mobile_list")

        else:

            messages.error(
                request,
                "Invalid credentials"
            )

            return redirect("login")


    return render(
        request,
        "users/login.html"
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    return redirect("mobile_list")

@login_required
def account_dashboard(request):

    recent_items = (
        RecentlyViewed.objects
        .filter(user=request.user)
        .select_related(
            "mobile_variant",
            "mobile_variant__mobile"
        )[:6]
    )

    compare_history = (
        CompareHistory.objects
        .filter(user=request.user)
        .select_related(
            "mobile_1__mobile",
            "mobile_2__mobile",
            "mobile_3__mobile"
        )[:5]
    )

    return render(
        request,
        "users/account.html",
        {
            "recent_items": recent_items,
            "compare_history": compare_history
        }
    )

@login_required
def alerts_dashboard(request):

    active_alerts = (
        PriceAlert.objects
        .filter(
            user=request.user,
            is_active=True
        )
        .select_related(
            "variant",
            "variant__mobile"
        )
        .order_by("-created_at")
    )

    triggered_alerts = (
        PriceAlert.objects
        .filter(
            user=request.user,
            is_active=False
        )
        .select_related(
            "variant",
            "variant__mobile"
        )
        .order_by("-triggered_at")
    )

    return render(
        request,
        "users/alerts.html",
        {
            "active_alerts": active_alerts,
            "triggered_alerts": triggered_alerts,
        }
    )

