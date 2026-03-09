from django.core.management.base import BaseCommand
from insurance.models import InsurancePlan


class Command(BaseCommand):
    help = 'Add insurance plans to the database'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Basic Plan',
                'plan_type': 'basic',
                'coverage_amount': 500000,
                'monthly_premium': 299,
                'description': 'Essential health coverage for individuals and families',
                'features': 'Basic hospitalization, Emergency care, General practitioner visits, Routine check-ups',
            },
            {
                'name': 'Silver Plan',
                'plan_type': 'silver',
                'coverage_amount': 1000000,
                'monthly_premium': 599,
                'description': 'Comprehensive coverage with additional benefits',
                'features': 'Full hospitalization, Emergency care, Specialist consultations, Dental care, Eye care, 20+ diagnostic tests',
            },
            {
                'name': 'Diamond Plan',
                'plan_type': 'diamond',
                'coverage_amount': 2000000,
                'monthly_premium': 999,
                'description': 'Premium coverage with maximum benefits and care',
                'features': 'Full hospitalization, Emergency 24/7, All specialists, Full dental care, Complete eye care, Unlimited diagnostic tests, Mental health support, Maternity benefits',
            },
            {
                'name': 'Premium Plan',
                'plan_type': 'premium',
                'coverage_amount': 5000000,
                'monthly_premium': 1499,
                'description': 'Elite coverage with comprehensive benefits',
                'features': 'Unlimited hospitalization, 24/7 emergency hotline, All specialists, Premium dental, Premium eye care, All diagnostic tests, Mental health support, Maternity benefits, Health coaching',
            },
        ]

        for plan_data in plans:
            plan, created = InsurancePlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults={
                    'name': plan_data['name'],
                    'coverage_amount': plan_data['coverage_amount'],
                    'monthly_premium': plan_data['monthly_premium'],
                    'billing_frequency': 'monthly',
                    'description': plan_data['description'],
                    'features': plan_data['features'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )

        self.stdout.write(self.style.SUCCESS('All plans processed successfully!'))
