from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from api.forms import UserProfileForm # Assuming you create this
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from api.models import UserProfile # Assuming you create this
from django.contrib.auth import logout
from django.conf import settings
from allauth.account.forms import LoginForm, SignupForm, ResetPasswordForm  # Import allauth forms


def home_page(request):
    context = {
        'page_title': 'ToolVerse - Home',
    }
    if not request.user.is_authenticated:
        context['request'] = request 
        from allauth.account.utils import get_request_param
        context['redirect_field_name'] = get_request_param(request, "next") or "next" # from allauth login view
        context['redirect_field_value'] = get_request_param(request, context['redirect_field_name'])

        from allauth.socialaccount.templatetags.socialaccount import get_providers
        providers = get_providers(context=context)
        if providers:
            context['socialaccount_providers'] = providers
        
        # For ACCOUNT_AUTHENTICATION_METHOD in placeholder
        from allauth.account import app_settings as allauth_settings
        context['LOGIN_METHODS'] = allauth_settings.LOGIN_METHODS
        return render(request, 'home.html', context)
    return render(request, 'dashboard.html', context)


@login_required
def dashboard_view(request):
    user = request.user
    
    # Dummy data for now - replace with actual queries
    recently_used_tools_qs = [] # Example: UserActivity.objects.filter(user=user, action_type='launch').order_by('-timestamp')[:3].select_related('app')
    # recently_used_tools = [activity.app for activity in recently_used_tools_qs]
    
    # Dummy list of recently used tools for the template
    recently_used_tools = [
        {'name': 'DataScrape Pro', 'icon_class': 'fas fa-spider', 'accent_color': 'teal', 'short_description': 'Scraped product data for Q4 report.', 'last_used': '1 day ago', 'launch_url': '#'},
        {'name': 'InsightAI Summarizer', 'icon_class': 'fas fa-brain', 'accent_color': 'purple', 'short_description': 'Summarized tech news articles.', 'last_used': '3 days ago', 'launch_url': '#'},
    ] if not recently_used_tools_qs else [] # Use dummy if real query is empty for now

    # Dummy data for discoverable tools
    discoverable_tools_qs = [] # Example: App.objects.exclude(id__in=[app.id for app in recently_used_tools]).order_by('-created_at')[:4]
    # discoverable_tools = list(discoverable_tools_qs)

    discoverable_tools = [
        {'name': 'AutoReport Gen', 'icon_class': 'fas fa-chart-pie', 'accent_color': 'pink', 'short_description': 'Automate your weekly sales reports.', 'learn_more_url': '#'},
        {'name': 'TaskFlow Scheduler', 'icon_class': 'fas fa-calendar-alt', 'accent_color': 'yellow', 'short_description': 'Manage all your background tasks.', 'learn_more_url': '#'},
        {'name': 'QuickMedia Optimizer', 'icon_class': 'fas fa-images', 'accent_color': 'green', 'short_description': 'Compress images for your website.', 'learn_more_url': '#'},
        {'name': 'CSV Pro Toolkit', 'icon_class': 'fas fa-file-csv', 'accent_color': 'blue', 'short_description': 'Advanced CSV manipulation.', 'learn_more_url': '#'},
    ] if not discoverable_tools_qs else []


    # Dummy quick stats
    quick_stats = {
        'tools_launched': 0, # user.launched_activities.count()
        'favorites_added': 0, # user.favorited_apps.count()
        'time_saved_est': 'N/A',
        'tasks_completed': 0,
    }

    context = {
        'user': user, # Already available by default if using auth context processor, but explicit is fine
        'recently_used_tools': recently_used_tools,
        'discoverable_tools': discoverable_tools,
        'quick_stats': quick_stats,
        'page_title': 'Dashboard' # For setting browser tab title dynamically
    }
    return render(request, 'dashboard.html', context)

def custom_logout_view(request):
    logout(request)
    # Redirect to LOGOUT_REDIRECT_URL or a specific page
    redirect_url = getattr(settings, 'LOGOUT_REDIRECT_URL', 'home')
    return redirect(redirect_url)


    def form_invalid(self, form):
        adapter = get_adapter(self.request)
        if adapter.is_ajax(self.request):
            print("AjaxPasswordResetView: Form is invalid, AJAX request detected. Returning JSON errors.") # DEBUG
            return JsonResponse({
                'success': False, 
                'errors': form.errors.get_json_data(),
                'message': "Please provide a valid email address."
            }, status=400)
        print("AjaxPasswordResetView: Form is invalid, NON-AJAX request. Rendering HTML.") # DEBUG
        return super().form_invalid(form)