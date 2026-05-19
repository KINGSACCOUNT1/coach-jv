"""
Management command to create sample investment pools for testing
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from core.models import InvestmentPool


class Command(BaseCommand):
    help = 'Create sample investment pools for testing'

    def handle(self, *args, **kwargs):
        pools_data = [
            {
                'name': 'Bitcoin Conservative Pool',
                'description': 'Low-risk Bitcoin investment strategy focused on steady growth. Perfect for beginners and risk-averse investors. Uses dollar-cost averaging and strategic entry points.',
                'risk_level': 'conservative',
                'currency': 'USDT',
                'total_value': Decimal('50000.00'),
                'total_invested': Decimal('45000.00'),
                'available_capital': Decimal('40000.00'),
                'share_price': Decimal('105.00'),
                'total_shares': Decimal('476.19'),
                'min_investment': Decimal('100.00'),
                'max_investment': Decimal('10000.00'),
                'lock_period_days': 30,
                'total_profit': Decimal('5000.00'),
                'total_loss': Decimal('0.00'),
                'roi_percentage': Decimal('11.11'),
                'management_fee_percent': Decimal('2.00'),
                'performance_fee_percent': Decimal('20.00'),
                'status': 'active',
                'featured': True,
            },
            {
                'name': 'Ethereum Growth Pool',
                'description': 'Balanced approach to Ethereum trading with medium risk. Combines swing trading and position holds for optimal returns. Targets 15-25% annual ROI.',
                'risk_level': 'balanced',
                'currency': 'USDT',
                'total_value': Decimal('75000.00'),
                'total_invested': Decimal('65000.00'),
                'available_capital': Decimal('60000.00'),
                'share_price': Decimal('112.50'),
                'total_shares': Decimal('666.67'),
                'min_investment': Decimal('250.00'),
                'max_investment': Decimal('25000.00'),
                'lock_period_days': 45,
                'total_profit': Decimal('12000.00'),
                'total_loss': Decimal('2000.00'),
                'roi_percentage': Decimal('15.38'),
                'management_fee_percent': Decimal('2.50'),
                'performance_fee_percent': Decimal('20.00'),
                'status': 'active',
                'featured': True,
            },
            {
                'name': 'Altcoin Aggressive Pool',
                'description': 'High-risk, high-reward strategy trading promising altcoins and new tokens. Targets 30-50% returns but with higher volatility. For experienced investors only.',
                'risk_level': 'aggressive',
                'currency': 'USDT',
                'total_value': Decimal('35000.00'),
                'total_invested': Decimal('30000.00'),
                'available_capital': Decimal('28000.00'),
                'share_price': Decimal('125.00'),
                'total_shares': Decimal('280.00'),
                'min_investment': Decimal('500.00'),
                'max_investment': Decimal('50000.00'),
                'lock_period_days': 60,
                'total_profit': Decimal('8000.00'),
                'total_loss': Decimal('3000.00'),
                'roi_percentage': Decimal('16.67'),
                'management_fee_percent': Decimal('3.00'),
                'performance_fee_percent': Decimal('25.00'),
                'status': 'active',
                'featured': False,
            },
            {
                'name': 'Stablecoin Yield Pool',
                'description': 'Ultra-conservative stablecoin yield farming and lending strategy. Minimal risk with steady 5-8% APY. Capital preservation focused.',
                'risk_level': 'conservative',
                'currency': 'USDT',
                'total_value': Decimal('120000.00'),
                'total_invested': Decimal('115000.00'),
                'available_capital': Decimal('110000.00'),
                'share_price': Decimal('103.50'),
                'total_shares': Decimal('1159.42'),
                'min_investment': Decimal('100.00'),
                'max_investment': Decimal('20000.00'),
                'lock_period_days': 30,
                'total_profit': Decimal('5500.00'),
                'total_loss': Decimal('500.00'),
                'roi_percentage': Decimal('4.35'),
                'management_fee_percent': Decimal('1.50'),
                'performance_fee_percent': Decimal('15.00'),
                'status': 'active',
                'featured': False,
            },
            {
                'name': 'DeFi Diversified Pool',
                'description': 'Balanced portfolio across DeFi protocols including lending, liquidity provision, and yield farming. Medium risk with diversification benefits.',
                'risk_level': 'balanced',
                'currency': 'USDT',
                'total_value': Decimal('95000.00'),
                'total_invested': Decimal('85000.00'),
                'available_capital': Decimal('80000.00'),
                'share_price': Decimal('110.00'),
                'total_shares': Decimal('863.64'),
                'min_investment': Decimal('200.00'),
                'max_investment': Decimal('30000.00'),
                'lock_period_days': 45,
                'total_profit': Decimal('12000.00'),
                'total_loss': Decimal('2000.00'),
                'roi_percentage': Decimal('11.76'),
                'management_fee_percent': Decimal('2.00'),
                'performance_fee_percent': Decimal('20.00'),
                'status': 'active',
                'featured': True,
            },
        ]

        created_count = 0
        updated_count = 0

        for pool_data in pools_data:
            pool, created = InvestmentPool.objects.update_or_create(
                name=pool_data['name'],
                defaults=pool_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created pool: {pool.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated pool: {pool.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nSummary: {created_count} created, {updated_count} updated'))
        self.stdout.write(self.style.SUCCESS('Sample investment pools ready!'))
