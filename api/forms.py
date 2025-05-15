from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    # You might want to use a clearable file input for the avatar
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'your-tailwind-classes-for-file-input'}))
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'website_url'] # Add User model fields if not on UserProfile
        # Or, if first_name and last_name are on the User model:
        # fields = ['bio', 'avatar', 'website_url']
        # You'd handle User.first_name and User.last_name separately in the view.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom initializations or widget attributes here if needed
        # Example:
        # self.fields['bio'].widget.attrs.update({'rows': 3})