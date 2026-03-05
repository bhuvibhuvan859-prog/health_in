from django import forms
from .models import UserProfile, Claim, InsurancePlan


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
