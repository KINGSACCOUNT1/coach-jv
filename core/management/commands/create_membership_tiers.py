from django.core.management.base import BaseCommand
from core.models import MembershipTier
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates default membership tiers (Free, Warrior, Ascension Plus, VIP)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating membership tiers...')
        
        tiers_data = [
            {
                'tier_level': 'free',
                'name': 'Free',
                'description': 'Basic access to the platform. Perfect for getting started with crypto trading.',
                'price_monthly': Decimal('0.00'),
                'price_yearly': Decimal('0.00'),
                'max_investment_pools': 1,
                'max_withdrawal_per_day': Decimal('1000.00'),
                'priority_support': False,
                'access_courses': False,
                'access_live_events': False,
                'access_private_coaching': False,
                'access_community_forum': True,  # Basic forum access
                'access_resource_library': False,
                'access_portfolio_tracker': True,  # Basic tracker
                'access_wealth_tools': False,
                'access_insurance_services': False,
                'access_crypto_ira': False,
                'trading_fee_discount': Decimal('0.00'),
                'withdrawal_fee_discount': Decimal('0.00'),
                'referral_bonus_multiplier': Decimal('1.00'),
                'order': 1,
                'badge_color': '#6B7280',
                'icon': 'fa-user',
                'is_active': True,
                'is_featured': False,
            },
            {
                'tier_level': 'warrior',
                'name': 'Warrior',
                'description': 'Full access to 3T Warrior Academy courses, community forum, and weekly coaching calls. Build your wealth with proven strategies.',
                'price_monthly': Decimal('97.00'),
                'price_yearly': Decimal('970.00'),  # Save $194 per year
                'max_investment_pools': 5,
                'max_withdrawal_per_day': Decimal('10000.00'),
                'priority_support': False,
                'access_courses': True,  # Full course access
                'access_live_events': True,  # Weekly coaching calls
                'access_private_coaching': False,
                'access_community_forum': True,  # Full forum access
                'access_resource_library': True,  # E-books, guides
                'access_portfolio_tracker': True,  # Full tracker with alerts
                'access_wealth_tools': True,  # Basic wealth tools
                'access_insurance_services': False,
                'access_crypto_ira': False,
                'trading_fee_discount': Decimal('10.00'),  # 10% discount
                'withdrawal_fee_discount': Decimal('25.00'),  # 25% discount
                'referral_bonus_multiplier': Decimal('1.25'),  # 25% bonus
                'order': 2,
                'badge_color': '#3B82F6',  # Blue
                'icon': 'fa-shield',
                'is_active': True,
                'is_featured': True,
            },
            {
                'tier_level': 'ascension',
                'name': 'Ascension Plus',
                'description': 'All Warrior features PLUS lifetime access, 3 private coaching calls, advanced wealth tools, and insurance services. Transform your financial future.',
                'price_monthly': Decimal('297.00'),
                'price_yearly': Decimal('2970.00'),  # Save $594 per year
                'max_investment_pools': 15,
                'max_withdrawal_per_day': Decimal('50000.00'),
                'priority_support': True,
                'access_courses': True,
                'access_live_events': True,
                'access_private_coaching': True,  # 3 private coaching calls
                'access_community_forum': True,
                'access_resource_library': True,
                'access_portfolio_tracker': True,
                'access_wealth_tools': True,  # Advanced wealth tools
                'access_insurance_services': True,  # Insurance needs assessment
                'access_crypto_ira': True,  # Crypto IRA setup
                'trading_fee_discount': Decimal('25.00'),  # 25% discount
                'withdrawal_fee_discount': Decimal('50.00'),  # 50% discount
                'referral_bonus_multiplier': Decimal('1.50'),  # 50% bonus
                'order': 3,
                'badge_color': '#8B5CF6',  # Purple
                'icon': 'fa-crown',
                'is_active': True,
                'is_featured': True,
            },
            {
                'tier_level': 'vip',
                'name': 'VIP Elite',
                'description': 'Ultimate experience with unlimited private coaching, concierge services, exclusive investment opportunities, and direct access to Coach JV. For serious wealth builders only.',
                'price_monthly': Decimal('997.00'),
                'price_yearly': Decimal('9970.00'),  # Save $1,994 per year
                'max_investment_pools': 999,  # Unlimited
                'max_withdrawal_per_day': Decimal('1000000.00'),  # $1M per day
                'priority_support': True,  # Highest priority
                'access_courses': True,
                'access_live_events': True,
                'access_private_coaching': True,  # Unlimited coaching
                'access_community_forum': True,
                'access_resource_library': True,
                'access_portfolio_tracker': True,
                'access_wealth_tools': True,
                'access_insurance_services': True,
                'access_crypto_ira': True,
                'trading_fee_discount': Decimal('50.00'),  # 50% discount
                'withdrawal_fee_discount': Decimal('100.00'),  # FREE withdrawals
                'referral_bonus_multiplier': Decimal('2.00'),  # 2x bonus
                'order': 4,
                'badge_color': '#F59E0B',  # Gold
                'icon': 'fa-star',
                'is_active': True,
                'is_featured': False,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for tier_data in tiers_data:
            tier, created = MembershipTier.objects.update_or_create(
                tier_level=tier_data['tier_level'],
                defaults=tier_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {tier.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'→ Updated: {tier.name}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_count} new tier(s)'))
        self.stdout.write(self.style.WARNING(f'→ Updated {updated_count} existing tier(s)'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ Membership tiers setup complete!'))
