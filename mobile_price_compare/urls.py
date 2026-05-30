from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

admin.site.site_header = "Nexovio Admin"
admin.site.site_title = "Nexovio Admin"
admin.site.index_title = "Welcome to Nexovio"

urlpatterns = [
    path('admin/', admin.site.urls),
    # AUTH
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path("accounts/", include("django.contrib.auth.urls")),
    # APP
    path('', include('mobiles.urls')),
    path("", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
