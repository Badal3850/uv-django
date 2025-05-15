from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from api.forms import UserProfileForm # Assuming you create this
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from api.models import UserProfile # Assuming you create this


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

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

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST) # Or your custom form
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login') # Redirect to login page after successful registration
        else:
            messages.error(request, 'Error creating account. Please try again.')
    else:
        form = UserCreationForm() # Or your custom form
    return render(request, 'register.html', {'form': form})

@login_required
def update_profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        # Handle User model fields if separate
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.save()

        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard') # Or back to settings with data-target=#settings-content
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Populate form with User model data if UserProfileForm doesn't include them
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)
    
    # This view should probably only handle profile updates.
    # Password change is better handled by Django's built-in views.
    # For the dashboard SPA, you might pass these forms in the main dashboard_view context.
    
    # If this view is *only* for POST, then redirect after processing.
    # For SPA, the dashboard_view provides the forms for GET.
    return redirect('dashboard') # This needs to be smarter for SPA



