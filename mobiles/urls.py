from django.urls import path
from .views import mobile_list, mobile_compare, mobile_search, autocomplete

from django.urls import path

from .views import (
    mobile_list,
    mobile_compare,
    mobile_search,
    autocomplete,
    wishlist_page,
    toggle_wishlist,
    compare_page,
    price_history_api,
    create_price_alert,
    delete_price_alert,
    about_page,
    contact_page,
    privacy_page,
    terms_page,
    help_page,
    report_price_page,
)

urlpatterns = [

    # HOME
    path(
        "",
        mobile_list,
        name="mobile_list"
    ),

    # SEARCH
    path(
        "search/",
        mobile_search,
        name="mobile_search"
    ),

    # MOBILE DETAILS / COMPARE
    path(
        "mobile/<str:model_number>/",
        mobile_compare,
        name="mobile_compare"
    ),

    # AUTOCOMPLETE
    path(
        "autocomplete/",
        autocomplete,
        name="autocomplete"
    ),

    # COMPARE PAGE
    path(
        "compare/",
        compare_page,
        name="compare_page"
    ),

    # WISHLIST PAGE
    path(
        "wishlist/",
        wishlist_page,
        name="wishlist"
    ),

    # TOGGLE WISHLIST
    path(
        "wishlist/<slug:slug>/",
        toggle_wishlist,
        name="toggle_wishlist"
    ),

    path(
        "api/price-history/<slug:slug>/",
        price_history_api,
        name="price_history_api"
    ),

    path(
        "price-alert/create/",
        create_price_alert,
        name="create_price_alert"
    ),
    
    path(
        "price-alert/delete/<int:alert_id>/",
        delete_price_alert,
        name="delete_price_alert"
    ),

    # STATIC PAGES
    path("about/", about_page, name="about"),
    path("contact/", contact_page, name="contact"),
    path("privacy/", privacy_page, name="privacy"),
    path("terms/", terms_page, name="terms"),
    path("help/", help_page, name="help"),
    path("report-price/", report_price_page, name="report_price"),

]
