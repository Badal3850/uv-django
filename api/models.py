from django.db import models
from django.contrib.auth.models import User # Or your custom User model
from django.utils.text import slugify
from django.urls import reverse, NoReverseMatch
from django.apps import apps # To inspect installed Django apps
from django.conf import settings
from django.core.exceptions import ValidationError

# --- Helper Functions for Upload Paths ---
def tool_icon_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/tool_icons/<tool_slug>/<filename>
    return f'tool_icons/{instance.slug}/{filename}'

def tool_banner_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/tool_banners/<tool_slug>/<filename>
    return f'tool_banners/{instance.slug}/{filename}'

def tool_screenshot_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/tool_screenshots/<tool_slug>/<filename>
    return f'tool_screenshots/{instance.tool.slug}/{filename}'

def user_avatar_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_avatars/<user_id>/<filename>
    return f'user_avatars/{instance.user.id}/{filename}'


# --- Category Model ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome class, e.g., 'fas fa-code'")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # return reverse('category_detail_view_name', kwargs={'slug': self.slug}) # Define this URL name
        return "#" # Placeholder until you define the URL

# --- Tag Model ---
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# --- Tool Model ---
class Tool(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('coming_soon', 'Coming Soon'),
    ]
    ACCESS_TYPE_CHOICES = [
        ('free', 'Free'),
        ('freemium', 'Freemium'),
        ('paid', 'Paid'),
        ('open_source', 'Open Source'),
    ]
    IMPLEMENTATION_TYPE_CHOICES = [
        ('django_app', 'Internal Django App'),
        ('external_link', 'External Link'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True, help_text="Leave blank to auto-generate from name")
    tagline = models.CharField(max_length=255, help_text="A short, catchy phrase for the tool.")
    short_description = models.TextField(help_text="Brief summary shown in listings.")
    long_description = models.TextField(blank=True, null=True, help_text="Detailed description for the tool's page.")
    
    icon_image = models.ImageField(upload_to=tool_icon_path, blank=True, null=True, help_text="Recommended size: 128x128px")
    banner_image = models.ImageField(upload_to=tool_banner_path, blank=True, null=True, help_text="Recommended size: 1200x400px")
    
    category = models.ForeignKey(Category, related_name='tools', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='tools', blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='free')
    
    implementation_type = models.CharField(
        max_length=20,
        choices=IMPLEMENTATION_TYPE_CHOICES,
        default='external_link'
    )
    
    external_tool_url = models.URLField(
        max_length=2000, blank=True, null=True,
        help_text="Required if Implementation Type is 'External Link'."
    )
    internal_app_config_name = models.CharField(
        max_length=100, blank=True, null=True, unique=True,
        help_text="AppConfig name (e.g., 'app_label.apps.AppLabelConfig'). Required if Implementation Type is 'Internal Django App'."
    )
    internal_app_url_namespace = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="URL namespace for the internal app. Required if Implementation Type is 'Internal Django App'."
    )
    internal_app_entry_view_name = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Entry view name (e.g., 'index') within the namespace. Required if Implementation Type is 'Internal Django App'."
    )

    website_url = models.URLField(max_length=2000, blank=True, null=True, help_text="Optional: Official website or documentation URL.")
    repository_url = models.URLField(max_length=2000, blank=True, null=True, help_text="Optional: Link to source code repository.")

    version = models.CharField(max_length=20, blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    last_updated_on_platform = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    developer_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the individual developer or company.")
    developer_link = models.URLField(blank=True, null=True, help_text="Link to developer's website or profile.")
    
    is_featured = models.BooleanField(default=False, help_text="Highlight this tool on the homepage or special sections.")
    views_count = models.PositiveIntegerField(default=0, editable=False)
    launch_count = models.PositiveIntegerField(default=0, editable=False)

    accent_color_class = models.CharField(max_length=50, blank=True, null=True, help_text="Tailwind color class (e.g., 'teal', 'purple') for UI consistency.")
    font_awesome_icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="E.g., 'fas fa-cogs'. Use if no icon_image.")

    created_by = models.ForeignKey(User, related_name='tools_created', on_delete=models.SET_NULL, null=True, blank=True, help_text="Admin/staff who added this tool to the platform.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-published_at', 'name']

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.implementation_type == 'django_app':
            if not self.internal_app_config_name:
                raise ValidationError({'internal_app_config_name': "This field is required for 'Internal Django App' implementation."})
            if not self.internal_app_url_namespace:
                raise ValidationError({'internal_app_url_namespace': "This field is required for 'Internal Django App' implementation."})
            if not self.internal_app_entry_view_name:
                raise ValidationError({'internal_app_entry_view_name': "This field is required for 'Internal Django App' implementation."})
            
            # Basic check if app config seems valid (more robust checks can be added)
            try:
                app_label = self.internal_app_config_name.split('.')[0] # Simplistic extraction
                apps.get_app_config(app_label)
                # Further check if self.internal_app_config_name is in settings.INSTALLED_APPS (can be complex due to different ways of listing)
            except (LookupError, IndexError):
                raise ValidationError({'internal_app_config_name': f"Could not find an app with config '{self.internal_app_config_name}'. Ensure it's installed and correctly named."})

        elif self.implementation_type == 'external_link':
            if not self.external_tool_url:
                 raise ValidationError({'external_tool_url': "This field is required for 'External Link' implementation."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            # Ensure slug uniqueness if auto-generated
            while Tool.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        self.full_clean() # Call clean() method before saving
        super().save(*args, **kwargs)

    def get_launch_url(self):
        if self.implementation_type == 'django_app':
            if self.internal_app_url_namespace and self.internal_app_entry_view_name:
                try:
                    return reverse(f"{self.internal_app_url_namespace}:{self.internal_app_entry_view_name}")
                except NoReverseMatch:
                    # Log this error for admin attention
                    print(f"ERROR: NoReverseMatch for tool '{self.name}' with namespace '{self.internal_app_url_namespace}' and view '{self.internal_app_entry_view_name}'")
                    return "#error-generating-url" 
            return "#misconfigured-internal-app"
        elif self.implementation_type == 'external_link':
            return self.external_tool_url
        return "#unknown-implementation"

    def get_absolute_url(self):
        # return reverse('tool_detail_view_name', kwargs={'slug': self.slug}) # Define this URL name
        return "#" # Placeholder until you define the URL

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def increment_launches(self):
        self.launch_count += 1
        self.save(update_fields=['launch_count'])

# --- ToolScreenshot Model ---
class ToolScreenshot(models.Model):
    tool = models.ForeignKey(Tool, related_name='screenshots', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=tool_screenshot_path)
    caption = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display, lower numbers first.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"Screenshot {self.order} for {self.tool.name}"

# --- Review Model ---
class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Terrible'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    tool = models.ForeignKey(Tool, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True, help_text="Admin can unapprove problematic reviews.")

    class Meta:
        ordering = ['-created_at']
        unique_together = ('tool', 'user') # User can only review a tool once

    def __str__(self):
        return f"Review for {self.tool.name} by {self.user.username}"

# --- UserProfile Model ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, default='user_avatars/default_avatar.png')
    website_url = models.URLField(blank=True, null=True, max_length=2000)
    # Consider adding fields like: date_of_birth, location, etc.

    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- UserToolInteraction Model ---
class UserToolInteraction(models.Model):
    INTERACTION_TYPES = [
        ('favorite', 'Favorite'),
        ('last_used', 'Last Used'),
        # ('subscribed', 'Subscribed'), # Add if you implement subscriptions
        # ('bookmarked', 'Bookmarked'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tool_interactions')
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='user_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    interacted_at = models.DateTimeField(auto_now=True) # auto_now=True will update on every save

    class Meta:
        unique_together = ('user', 'tool', 'interaction_type')
        ordering = ['-interacted_at']

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.tool.name}"