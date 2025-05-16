from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('',views.home_page, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')), # Allauth URLs
    path('api/', include('api.urls')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
]