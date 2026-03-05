from django.db import models


class InsurancePlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    name = models.CharField(max_length=200)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_premium = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    features = models.TextField(help_text="Comma-separated list of features")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_features_list(self):
        return [f.strip() for f in self.features.split(',') if f.strip()]

    def annual_premium(self):
        return self.monthly_premium * 12

    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"

    class Meta:
        ordering = ['monthly_premium']


class UserProfile(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField()
    address = models.TextField(blank=True)
    selected_plan = models.ForeignKey(
        InsurancePlan, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subscribers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    CLAIM_TYPE_CHOICES = [
        ('hospitalization', 'Hospitalization'),
        ('outpatient', 'Outpatient'),
        ('medication', 'Medication'),
        ('diagnostic', 'Diagnostic Tests'),
        ('surgery', 'Surgery'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='claims'
    )
    claim_type = models.CharField(max_length=30, choices=CLAIM_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    description = models.TextField()
    hospital_name = models.CharField(max_length=200, blank=True)
    date_of_service = models.DateField()
    date_filed = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim #{self.pk} - {self.get_claim_type_display()} ({self.get_status_display()})"

    class Meta:
        ordering = ['-date_filed']


class PremiumCalculation(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, null=True, blank=True,
        related_name='calculations'
    )
    plan = models.ForeignKey(
        InsurancePlan, on_delete=models.CASCADE, related_name='calculations'
    )
    age = models.PositiveIntegerField()
    has_preexisting = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    calculated_premium = models.DecimalField(max_digits=10, decimal_places=2)
    calculation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Premium calc for {self.plan.name} (age {self.age}): ₹{self.calculated_premium}"

    class Meta:
        ordering = ['-calculation_date']
