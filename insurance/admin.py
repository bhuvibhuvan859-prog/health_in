from django.contrib import admin
from .models import InsurancePlan, UserProfile, Claim, PremiumCalculation


@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'coverage_amount', 'monthly_premium', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name', 'description')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'age', 'selected_plan', 'created_at')
    list_filter = ('selected_plan',)
    search_fields = ('name', 'email')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'claim_type', 'amount', 'status', 'date_filed')
    list_filter = ('status', 'claim_type')
    search_fields = ('user__name', 'description')
    list_editable = ('status',)


@admin.register(PremiumCalculation)
class PremiumCalculationAdmin(admin.ModelAdmin):
    list_display = ('plan', 'age', 'has_preexisting', 'smoker', 'calculated_premium', 'calculation_date')
    list_filter = ('has_preexisting', 'smoker')
