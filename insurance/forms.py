from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Claim, InsurancePlan


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'phone', 'age', 'address', 'selected_plan']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': '+91 XXXXX XXXXX'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Your Age', 'min': 1, 'max': 120
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input form-textarea', 'placeholder': 'Your Address',
                'rows': 3
            }),
            'selected_plan': forms.Select(attrs={'class': 'form-input'}),
        }


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['user', 'claim_type', 'amount', 'description',
                  'hospital_name', 'date_of_service']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-input'}),
            'claim_type': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Claim Amount (₹)',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Describe the reason for your claim...',
                'rows': 4
            }),
            'hospital_name': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Hospital / Clinic Name'
            }),
            'date_of_service': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date'
            }),
        }


class PremiumCalculatorForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=InsurancePlan.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-input'}),
        label='Select Plan'
    )
    age = forms.IntegerField(
        min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-input', 'placeholder': 'Your Age'
        })
    )
    has_preexisting = forms.BooleanField(
        required=False,
        label='Pre-existing Conditions',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    smoker = forms.BooleanField(
        required=False,
        label='Smoker',
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
