# your_app_name/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse

class AjaxAccountAdapter(DefaultAccountAdapter):

    def is_ajax(self, request):
        """
        Helper to check if the request is an AJAX request.
        Allauth uses request.is_ajax() which checks for X-Requested-With header.
        """
        return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def get_login_redirect_url(self, request):
        """
        Determines the URL to redirect to after successful login.
        """
        # Allauth's default logic usually handles LOGIN_REDIRECT_URL well.
        # You can customize this if needed.
        url = super().get_login_redirect_url(request)
        return url or getattr(settings, 'LOGIN_REDIRECT_URL', None) or reverse('dashboard') # Fallback

    def get_logout_redirect_url(self, request):
        """
        Determines the URL to redirect to after successful logout.
        """
        return super().get_logout_redirect_url(request) or getattr(settings, 'ACCOUNT_LOGOUT_REDIRECT_URL', None) or reverse('home')


    def ajax_json_response(self, data, success=True, status_code=200):
        """
        Helper to create a consistent JSON response.
        """
        response_data = {'success': success}
        response_data.update(data)
        return JsonResponse(response_data, status=status_code)

    # --- Handle Successful Actions (Login, Signup, Password Reset Email Sent, etc.) ---

    def login(self, request, user):
        # This method is called by allauth after the user is successfully authenticated
        # but before the standard login signal is sent and session is fully set up.
        # The actual login (session setup) is done by super().login()
        
        # For AJAX requests, we don't want the default redirect.
        # Instead, we'll let super().login() do its work (which includes setting the session)
        # and then return a JSON response indicating success and the redirect URL.
        if self.is_ajax(request):
            # Perform the login to set up the session
            super().login(request, user) 
            redirect_url = self.get_login_redirect_url(request)
            print(f"Redirect URL after login: {redirect_url}")  # Debugging line
            return self.ajax_json_response({
                'message': 'Login successful! Redirecting...',
                'redirect_url': redirect_url
            })
        # For non-AJAX, let allauth's default behavior (which includes redirect) happen
        # by calling super and returning its result (or None if super handles the response)
        return super().login(request, user)


    def respond_to_login(self, request, user):
        # This method is called by allauth's LoginView *after* successful login.
        # We've handled AJAX in the `login` method above by returning JsonResponse.
        # If the `login` method returned None (for non-AJAX), then this method
        # would handle the normal HTTP redirect.
        # So, if it's AJAX, our `login` method already sent a JsonResponse.
        if self.is_ajax(request):
            # This part might not even be reached if login() already returned JsonResponse.
            # But as a safeguard:
            redirect_url = self.get_login_redirect_url(request)
            return self.ajax_json_response({
                'message': 'Login successful (from respond_to_login)!',
                'redirect_url': redirect_url
            })
        return super().respond_to_login(request, user)
        

    def respond_to_signup(self, request, user, redirect_url=None):
        # Called after successful signup.
        if self.is_ajax(request):
            # By default, allauth might log the user in after signup
            # and then redirect. We want to control this with JSON.
            # The `redirect_url` passed here is often to 'account_email_verification_sent'
            # or LOGIN_REDIRECT_URL if auto-login and no verification.

            message = "Signup successful."
            if redirect_url == reverse('account_email_verification_sent'):
                message = "Signup successful! Please check your email for verification."
            
            # Determine final redirect (could be LOGIN_REDIRECT_URL if auto-login and verified, or email sent page)
            final_redirect_url = redirect_url or self.get_login_redirect_url(request)

            return self.ajax_json_response({
                'message': message,
                'redirect_url': final_redirect_url
            })
        return super().respond_to_signup(request, user, redirect_url)
        

    def respond_to_reset_password_sent(self, request, user, email):
        # Called after the password reset email has been successfully sent.
        # Allauth's PasswordResetView redirects to 'account_reset_password_done'.
        if self.is_ajax(request):
            return self.ajax_json_response({
                'message': 'Password reset e-mail has been sent. Please check your inbox.'
                # No redirect_url needed here, JS will just show the message in the modal.
            })
        return super().respond_to_reset_password_sent(request, user, email)


    # --- Handle Form Errors ---

    def get_form_class(self, request, form_class_name, default_form_class):
        # This is just to show how you might intercept form instantiation if needed,
        # but usually not required for AJAX error handling.
        return super().get_form_class(request, form_class_name, default_form_class)

    # Allauth views typically handle form invalidation by re-rendering the template
    # with the form containing errors. For AJAX, we need to intercept this.
    # One way is to override methods in allauth's views themselves if they check for AJAX,
    # or ensure our AJAX call correctly gets the form error data.
    # The more direct way with allauth is that its views, when encountering an invalid form,
    # will eventually re-render the template. The AJAX client will receive this HTML.
    # This means the client-side JS has to be prepared to handle an HTML response in case of form errors
    # OR we ensure the view itself returns JSON on form error if AJAX.
    #
    # Allauth's `FormView` (which many account views inherit from) has a `form_invalid` method.
    # If we can get allauth to call our adapter's `form_invalid`, we can return JSON.
    #
    # Let's try a more direct approach if the above `login`/`signup` methods aren't
    # sufficient for error handling. This involves how allauth's views process forms.
    # Many allauth views (like LoginView, SignupView, PasswordResetView) are subclasses
    # of `allauth.account.views.FormView`. This `FormView` has a `form_invalid` method.
    #
    # If you use ACCOUNT_FORMS to point to your custom forms, you can handle AJAX in the form's clean method or view.
    # However, since you want to use allauth's default forms for now, we rely on the view behavior.
    #
    # The crucial part is that allauth views often look something like this (simplified):
    # if form.is_valid():
    #     response = self.form_valid(form) # This calls adapter methods like respond_to_login
    # else:
    #     response = self.form_invalid(form) # This re-renders the template
    #
    # For AJAX, when `form_invalid` is called, we want it to return JSON.
    # This is the trickiest part to make generic in the adapter without subclassing each view.
    #
    # Let's assume for now that if an AJAX request leads to form errors,
    # the default allauth view might still try to render an HTML template.
    # Our JS `fetch().then(response => response.json())` would fail.
    #
    # A common pattern to get JSON errors from default allauth views with AJAX:
    # The views might not automatically return JSON errors.
    # The `AjaxAccountAdapter` methods like `login` handle the *success* path for AJAX.
    # For the *error* path (form invalid), if allauth's view re-renders HTML,
    # your JS needs to catch the JSON parse error and then potentially parse the HTML
    # for error messages, or you need custom views that explicitly return JSON errors.
    #
    # The `form.errors.get_json_data()` is what we want.
    # Let's assume your `setupAjaxForm` gets a JSON response for errors, implying the view
    # (or a wrapper/signal) is constructing it. The adapter can help for *success* cases.
    # For error cases, if you are NOT subclassing allauth views, it's tougher.
    #
    # The most straightforward way to get JSON errors with default allauth views
    # is to check `request.is_ajax()` WITHIN a custom form's `clean()` method
    # and if it's AJAX and there are errors, raise a special exception or
    # store errors in a way that a signal can pick them up and return JsonResponse.
    # This is getting complex if you don't want custom forms.
    #
    # Let's stick to what the adapter *can* easily do: handle success paths.
    # For errors, your JavaScript currently expects JSON. If allauth sends HTML,
    # your `response.json()` will fail.
    #
    # To ensure JSON errors:
    # You might need to override allauth's base `FormView.form_invalid`
    # via a custom view that inherits from allauth's view and uses your adapter logic.
    # Example:
    # class CustomLoginView(allauth.account.views.LoginView):
    #     def form_invalid(self, form):
    #         adapter = get_adapter(self.request)
    #         if adapter.is_ajax(self.request):
    #             return adapter.ajax_json_response({'errors': form.errors.get_json_data()}, success=False, status_code=400)
    #         return super().form_invalid(form)
    # Then use this CustomLoginView in your urls.py instead of allauth.urls for login.
    # This is the most robust way for JSON errors with AJAX.

    # For this example, we'll assume that if the adapter's success methods (login, signup) are not hit,
    # it means form validation failed, and the calling view (if it's AJAX aware) should have
    # handled sending a JSON error response. If not, the JS `catch` block for `response.json()`
    # will trigger.

    # If your JS is robust enough to handle a non-JSON response (e.g. by checking content-type
    # before calling .json()), it could parse HTML errors, but that's less clean.