from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('',views.home, name='home'),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('all_apps/', views.dashboard_view, name='all_apps'),
    path('account_settings/', views.dashboard_view, name='account_settings'),
    path('settings/password/', auth_views.PasswordChangeView.as_view(
        template_name='dashboard_partials/password_change_form_page.html', # A page dedicated to password change, or handle in dashboard
        success_url = reverse_lazy('password_change_done') # Or reverse_lazy('dashboard') with a message
    ), name='password_change'),
    path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='dashboard_partials/password_change_done_page.html' # A confirmation page
    ), name='password_change_done'),
    path('profile/update/', views.update_profile_view, name='update_profile'),
]