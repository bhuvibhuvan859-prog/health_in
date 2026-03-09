from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import InsurancePlan, UserProfile, Claim, PremiumCalculation
from .forms import UserProfileForm, ClaimForm, PremiumCalculatorForm, SignUpForm


class CustomLoginView(LoginView):
    template_name = 'insurance/login.html'
    redirect_authenticated_user = True
    next_page = 'insurance:dashboard'


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'insurance/register.html'
    success_url = reverse_lazy('insurance:login')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('insurance:dashboard')
        return super().get(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect('insurance:login')


def dashboard(request):
    """Main dashboard with stats overview."""
    total_plans = InsurancePlan.objects.filter(is_active=True).count()
    total_users = UserProfile.objects.count()
    total_claims = Claim.objects.count()
    pending_claims = Claim.objects.filter(status='pending').count()
    approved_claims = Claim.objects.filter(status='approved').count()
    rejected_claims = Claim.objects.filter(status='rejected').count()

    total_claim_amount = Claim.objects.aggregate(
        total=Sum('amount'))['total'] or 0
    approved_amount = Claim.objects.filter(status='approved').aggregate(
        total=Sum('amount'))['total'] or 0

    recent_claims = Claim.objects.select_related('user')[:5]
    plans = InsurancePlan.objects.filter(is_active=True)[:3]

    context = {
        'total_plans': total_plans,
        'total_users': total_users,
        'total_claims': total_claims,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'rejected_claims': rejected_claims,
        'total_claim_amount': total_claim_amount,
        'approved_amount': approved_amount,
        'recent_claims': recent_claims,
        'plans': plans,
    }
    return render(request, 'insurance/dashboard.html', context)


def plan_list(request):
    """List all active insurance plans with optional search."""
    query = request.GET.get('q', '')
    plans = InsurancePlan.objects.filter(is_active=True)
    if query:
        plans = plans.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(plan_type__icontains=query)
        )
    return render(request, 'insurance/plan_list.html', {
        'plans': plans, 'query': query
    })


def plan_detail(request, pk):
    """Detailed view of a single insurance plan."""
    plan = get_object_or_404(InsurancePlan, pk=pk)
    return render(request, 'insurance/plan_detail.html', {'plan': plan})


def premium_calculator(request):
    """Calculate estimated premium based on user inputs."""
    result = None
    if request.method == 'POST':
        form = PremiumCalculatorForm(request.POST)
        if form.is_valid():
            plan = form.cleaned_data['plan']
            age = form.cleaned_data['age']
            has_preexisting = form.cleaned_data['has_preexisting']
            smoker = form.cleaned_data['smoker']

            # Premium calculation logic
            base = plan.monthly_premium
            # Age factor
            if age < 25:
                factor = Decimal('0.85')
            elif age < 35:
                factor = Decimal('1.00')
            elif age < 45:
                factor = Decimal('1.20')
            elif age < 55:
                factor = Decimal('1.50')
            elif age < 65:
                factor = Decimal('1.80')
            else:
                factor = Decimal('2.20')

            calculated = base * factor
            if has_preexisting:
                calculated *= Decimal('1.30')
            if smoker:
                calculated *= Decimal('1.25')

            calculated = calculated.quantize(Decimal('0.01'))

            # Save calculation
            PremiumCalculation.objects.create(
                plan=plan,
                age=age,
                has_preexisting=has_preexisting,
                smoker=smoker,
                calculated_premium=calculated,
            )

            result = {
                'plan': plan,
                'age': age,
                'base_premium': base,
                'calculated_monthly': calculated,
                'calculated_annual': (calculated * 12).quantize(Decimal('0.01')),
                'has_preexisting': has_preexisting,
                'smoker': smoker,
            }
    else:
        form = PremiumCalculatorForm()

    return render(request, 'insurance/premium_calculator.html', {
        'form': form, 'result': result
    })


def claim_list(request):
    """List all claims with optional status filter."""
    status_filter = request.GET.get('status', '')
    claims = Claim.objects.select_related('user')
    if status_filter:
        claims = claims.filter(status=status_filter)

    status_choices = Claim.STATUS_CHOICES
    return render(request, 'insurance/claim_list.html', {
        'claims': claims,
        'status_filter': status_filter,
        'status_choices': status_choices,
    })


def claim_create(request):
    """Submit a new insurance claim."""
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('insurance:claim_list')
    else:
        form = ClaimForm()
    return render(request, 'insurance/claim_form.html', {'form': form})


def claim_detail(request, pk):
    """View details of a single claim."""
    claim = get_object_or_404(Claim.objects.select_related('user'), pk=pk)
    return render(request, 'insurance/claim_detail.html', {'claim': claim})


def claim_approve(request, pk):
    """Approve a pending claim."""
    claim = get_object_or_404(Claim, pk=pk)
    if request.method == 'POST':
        if claim.status == 'pending':
            claim.status = 'approved'
            claim.admin_notes = request.POST.get('admin_notes', '')
            claim.rejection_reason = ''
            claim.save()
            messages.success(request, 'Claim approved successfully!')
    return redirect('insurance:claim_detail', pk=pk)


def claim_reject(request, pk):
    """Reject a pending claim."""
    claim = get_object_or_404(Claim, pk=pk)
    if request.method == 'POST':
        if claim.status == 'pending':
            claim.status = 'rejected'
            claim.rejection_reason = request.POST.get('rejection_reason', 'No reason provided')
            claim.admin_notes = request.POST.get('admin_notes', '')
            claim.save()
            messages.success(request, 'Claim rejected successfully!')
    return redirect('insurance:claim_detail', pk=pk)


def claim_update_status(request, pk):
    """Update claim status."""
    claim = get_object_or_404(Claim, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        if new_status in dict(Claim.STATUS_CHOICES):
            claim.status = new_status
            if new_status == 'approved' and claim.status != 'approved':
                claim.admin_notes = request.POST.get('admin_notes', '')
            elif new_status == 'rejected' and claim.status != 'rejected':
                claim.rejection_reason = request.POST.get('rejection_reason', '')
                claim.admin_notes = request.POST.get('admin_notes', '')
            elif new_status == 'pending':
                claim.rejection_reason = ''
            claim.save()
            messages.success(request, f'Claim status updated to {claim.get_status_display()}!')
    return redirect('insurance:claim_detail', pk=pk)


def user_profile_list(request):
    """List all user profiles."""
    profiles = UserProfile.objects.select_related('selected_plan').all()
    return render(request, 'insurance/user_profile_list.html', {
        'profiles': profiles
    })


def user_profile_create(request):
    """Create a new user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('insurance:user_profile_list')
    else:
        form = UserProfileForm()
    return render(request, 'insurance/user_profile_form.html', {
        'form': form, 'editing': False
    })


def user_profile_edit(request, pk):
    """Edit an existing user profile."""
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('insurance:user_profile_list')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'insurance/user_profile_form.html', {
        'form': form, 'editing': True, 'profile': profile
    })
