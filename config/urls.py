# your_project/urls.py OR your_app_name/urls.py (adjust imports accordingly)

from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

# Your app's views where manual_ajax_login_view, etc. are defined
from . import auth_views as app_views # Assuming views are in 'your_app_name.views'
from . import views
# Django's built-in auth views are still useful for parts of password reset
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('admin/', admin.site.urls),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.dashboard_view, name='account_settings'),
    path('settings/profile/update', views.dashboard_view, name='update_profile'),
    path('apps/all/', views.dashboard_view, name='all_apps'),
    
    # Add other specific application URLs here
    path('ajax/login/', app_views.ajax_login_view, name='ajax_login'),
    path('logout/', app_views.logout_view, name='logout'),
    path('ajax/signup/', app_views.ajax_signup_view, name='ajax_signup'),
    path('ajax/password/reset/', app_views.ajax_password_reset_view, name='ajax_password_reset'),
    path('ajax/username/recover/', app_views.ajax_username_recovery_view, name='ajax_username_recover'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)