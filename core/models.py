from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class Profile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class KYC(models.Model):
    """Know Your Customer verification"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('id_card', 'National ID Card'),
        ('drivers_license', 'Drivers License'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_front = models.ImageField(upload_to='kyc/documents/')
    document_back = models.ImageField(upload_to='kyc/documents/', blank=True, null=True)
    selfie = models.ImageField(upload_to='kyc/selfies/')
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_reviews')

    class Meta:
        verbose_name = 'KYC Verification'
        verbose_name_plural = 'KYC Verifications'

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class Wallet(models.Model):
    """User cryptocurrency wallet"""
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether USDT'),
        ('BNB', 'Binance Coin'),
        ('SOL', 'Solana'),
        ('XRP', 'Ripple'),
        ('DOGE', 'Dogecoin'),
        ('ADA', 'Cardano'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallets')
    currency = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    address = models.CharField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'currency']

    def save(self, *args, **kwargs):
        if not self.address:
            self.address = f"{self.currency.lower()}_{uuid.uuid4().hex[:32]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.currency}: {self.balance}"


class Transaction(models.Model):
    """All financial transactions"""
    TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('trade', 'Trade'),
        ('mining', 'Mining Reward'),
        ('p2p_buy', 'P2P Buy'),
        ('p2p_sell', 'P2P Sell'),
        ('referral', 'Referral Bonus'),
        ('transfer', 'Transfer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tx_hash = models.CharField(max_length=100, blank=True, help_text='Blockchain transaction hash')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type} {self.amount} {self.currency}"


class Trade(models.Model):
    """Spot trading orders"""
    SIDE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    ORDER_TYPES = [
        ('market', 'Market Order'),
        ('limit', 'Limit Order'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('filled', 'Filled'),
        ('partial', 'Partially Filled'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trades')
    pair = models.CharField(max_length=20, help_text='e.g., BTC/USDT')
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    filled_amount = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    total = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    filled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total = self.amount * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.side.upper()} {self.amount} {self.pair}"


class MiningPlan(models.Model):
    """Available mining plans"""
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=10, default='BTC')
    hashrate = models.CharField(max_length=50, help_text='e.g., 100 TH/s')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    daily_return = models.DecimalField(max_digits=10, decimal_places=6, help_text='Daily return rate')
    duration_days = models.IntegerField(help_text='Contract duration in days')
    min_investment = models.DecimalField(max_digits=10, decimal_places=2)
    max_investment = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.hashrate}"


class MiningContract(models.Model):
    """User's active mining contracts"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mining_contracts')
    plan = models.ForeignKey(MiningPlan, on_delete=models.PROTECT)
    investment = models.DecimalField(max_digits=20, decimal_places=8)
    total_earned = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    last_payout = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField()

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"


class P2PTrade(models.Model):
    """Peer-to-peer trading ads"""
    TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('crypto', 'Crypto'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='p2p_ads')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    currency = models.CharField(max_length=10)
    fiat_currency = models.CharField(max_length=10, default='USD')
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    min_amount = models.DecimalField(max_digits=20, decimal_places=8)
    max_amount = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=2, help_text='Price per unit in fiat')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_details = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'P2P Trade Ad'
        verbose_name_plural = 'P2P Trade Ads'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type.upper()} {self.currency}"


class P2POrder(models.Model):
    """P2P trade orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid - Awaiting Release'),
        ('completed', 'Completed'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    ]

    ad = models.ForeignKey(P2PTrade, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='p2p_buys')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='p2p_sells')
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    total_fiat = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_proof = models.ImageField(upload_to='p2p/payments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"P2P Order #{self.id} - {self.amount} {self.ad.currency}"


class Deposit(models.Model):
    """Fiat/Crypto deposits"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    METHOD_CHOICES = [
        ('crypto', 'Cryptocurrency'),
        ('bank', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    tx_hash = models.CharField(max_length=100, blank=True)
    proof = models.ImageField(upload_to='deposits/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"


class Withdrawal(models.Model):
    """Withdrawal requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    currency = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    address = models.CharField(max_length=100)
    network = models.CharField(max_length=20, blank=True)
    tx_hash = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"


class Newsletter(models.Model):
    """Newsletter subscribers"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class SupportTicket(models.Model):
    """Customer support tickets"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.subject}"


class TicketReply(models.Model):
    """Replies to support tickets"""
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Ticket Replies'
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to #{self.ticket.id}"


# ============ INVESTMENT POOL MODELS ============

class InvestmentPool(models.Model):
    """Investment pools managed by CoachJVTech"""
    RISK_LEVELS = [
        ('conservative', 'Conservative - Low Risk'),
        ('balanced', 'Balanced - Medium Risk'),
        ('aggressive', 'Aggressive - High Risk'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active - Accepting Investments'),
        ('closed', 'Closed - Not Accepting New Investors'),
        ('paused', 'Paused'),
    ]
    
    name = models.CharField(max_length=100, help_text='e.g., Bitcoin Conservative Pool')
    description = models.TextField()
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    currency = models.CharField(max_length=10, default='USDT', help_text='Base currency for pool')
    
    # Pool Financials
    total_value = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'), 
                                      help_text='Current total pool value')
    total_invested = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    available_capital = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'),
                                           help_text='Capital available for trading')
    
    # Share Management
    share_price = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('100.00'),
                                      help_text='Current price per share')
    total_shares = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    # Investment Limits
    min_investment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    max_investment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100000.00'))
    lock_period_days = models.IntegerField(default=30, help_text='Minimum days before withdrawal')
    
    # Performance Metrics
    total_profit = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    total_loss = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    roi_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'),
                                         help_text='Return on Investment %')
    
    # Fees
    management_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('2.00'),
                                                  help_text='Annual management fee %')
    performance_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('20.00'),
                                                   help_text='Performance fee on profits %')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    featured = models.BooleanField(default=False, help_text='Show on homepage')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-total_value']
        verbose_name = 'Investment Pool'
        verbose_name_plural = 'Investment Pools'
    
    def __str__(self):
        return f"{self.name} ({self.get_risk_level_display()})"
    
    def calculate_share_price(self):
        """Calculate current share price based on pool value"""
        if self.total_shares > 0:
            self.share_price = self.total_value / self.total_shares
        return self.share_price
    
    def update_roi(self):
        """Update ROI percentage"""
        if self.total_invested > 0:
            net_profit = self.total_profit - self.total_loss
            self.roi_percentage = (net_profit / self.total_invested) * 100
        return self.roi_percentage


class PoolShare(models.Model):
    """User's shares in investment pools"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pool_shares')
    pool = models.ForeignKey(InvestmentPool, on_delete=models.CASCADE, related_name='shareholders')
    
    shares_owned = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    purchase_price = models.DecimalField(max_digits=20, decimal_places=8, help_text='Average purchase price per share')
    total_invested = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    current_value = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    total_profit_received = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    last_profit_date = models.DateTimeField(null=True, blank=True)
    
    locked_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'pool']
        ordering = ['-total_invested']
        verbose_name = 'Pool Share'
        verbose_name_plural = 'Pool Shares'
    
    def __str__(self):
        return f"{self.user.username} - {self.pool.name}: {self.shares_owned} shares"
    
    def update_current_value(self):
        """Update current value based on pool's share price"""
        self.current_value = self.shares_owned * self.pool.share_price
        return self.current_value
    
    def calculate_profit_loss(self):
        """Calculate unrealized profit/loss"""
        return self.current_value - self.total_invested


class PoolTransaction(models.Model):
    """All pool-related transactions"""
    TYPE_CHOICES = [
        ('investment', 'Investment - Buy Shares'),
        ('withdrawal', 'Withdrawal - Sell Shares'),
        ('profit_distribution', 'Profit Distribution'),
        ('management_fee', 'Management Fee'),
        ('performance_fee', 'Performance Fee'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pool_transactions')
    pool = models.ForeignKey(InvestmentPool, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    
    shares = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    share_price = models.DecimalField(max_digits=20, decimal_places=8)
    amount = models.DecimalField(max_digits=20, decimal_places=8, help_text='Amount in pool currency')
    fee = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pool Transaction'
        verbose_name_plural = 'Pool Transactions'
    
    def __str__(self):
        return f"{self.user.username} - {self.type} {self.amount} in {self.pool.name}"


class PoolTrade(models.Model):
    """Trades executed by admin for investment pools"""
    SIDE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('filled', 'Filled'),
        ('partial', 'Partially Filled'),
        ('cancelled', 'Cancelled'),
    ]
    
    pool = models.ForeignKey(InvestmentPool, on_delete=models.CASCADE, related_name='trades')
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='executed_pool_trades')
    
    pair = models.CharField(max_length=20, help_text='e.g., BTC/USDT')
    side = models.CharField(max_length=10, choices=SIDE_CHOICES)
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    exit_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=8, help_text='Amount traded')
    
    profit_loss = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))
    profit_loss_percent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    notes = models.TextField(blank=True)
    
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-opened_at']
        verbose_name = 'Pool Trade'
        verbose_name_plural = 'Pool Trades'
    
    def __str__(self):
        return f"{self.pool.name} - {self.side.upper()} {self.pair} @ {self.entry_price}"
    
    def calculate_profit_loss(self):
        """Calculate profit/loss when trade is closed"""
        if self.exit_price and self.status == 'filled':
            if self.side == 'buy':
                self.profit_loss = (self.exit_price - self.entry_price) * self.amount
            else:  # sell
                self.profit_loss = (self.entry_price - self.exit_price) * self.amount
            
            if self.entry_price > 0:
                self.profit_loss_percent = (self.profit_loss / (self.entry_price * self.amount)) * 100
        
        return self.profit_loss


class PoolPerformance(models.Model):
    """Historical performance snapshots of pools"""
    pool = models.ForeignKey(InvestmentPool, on_delete=models.CASCADE, related_name='performance_history')
    
    date = models.DateField(auto_now_add=True)
    total_value = models.DecimalField(max_digits=20, decimal_places=8)
    share_price = models.DecimalField(max_digits=20, decimal_places=8)
    roi_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    daily_change = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    
    total_investors = models.IntegerField(default=0)
    trades_count = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['pool', 'date']
        verbose_name = 'Pool Performance Snapshot'
        verbose_name_plural = 'Pool Performance Snapshots'
    
    def __str__(self):
        return f"{self.pool.name} - {self.date}"


# ============ OTP EMAIL VERIFICATION ============

class OTPToken(models.Model):
    """One-Time Password tokens for email verification and security"""
    PURPOSE_CHOICES = [
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
        ('login_2fa', 'Two-Factor Authentication Login'),
        ('withdrawal_confirm', 'Withdrawal Confirmation'),
        ('account_change', 'Account Settings Change'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_tokens')
    email = models.EmailField(help_text='Email where OTP was sent')
    token = models.CharField(max_length=6, help_text='6-digit OTP code')
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    
    is_used = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)
    
    # Security
    attempts = models.IntegerField(default=0, help_text='Number of verification attempts')
    max_attempts = models.IntegerField(default=5)
    
    # Metadata for specific purposes
    metadata = models.JSONField(default=dict, blank=True, help_text='Additional context (e.g., withdrawal ID)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP Token'
        verbose_name_plural = 'OTP Tokens'
        indexes = [
            models.Index(fields=['user', 'purpose', 'is_valid']),
            models.Index(fields=['token', 'is_valid']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.purpose} - {'Used' if self.is_used else 'Active'}"
    
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    def can_verify(self):
        """Check if token can still be verified"""
        return (
            self.is_valid and 
            not self.is_used and 
            not self.is_expired() and 
            self.attempts < self.max_attempts
        )
    
    def verify(self, input_token):
        """Verify the OTP token"""
        self.attempts += 1
        
        if not self.can_verify():
            self.save()
            return False
        
        if self.token == input_token:
            self.is_used = True
            self.used_at = timezone.now()
            self.save()
            return True
        
        # Max attempts reached, invalidate
        if self.attempts >= self.max_attempts:
            self.is_valid = False
        
        self.save()
        return False
    
    @classmethod
    def generate_token(cls):
        """Generate a random 6-digit OTP"""
        import random
        return str(random.randint(100000, 999999))
    
    @classmethod
    def create_otp(cls, user, purpose, validity_minutes=10, **metadata):
        """Create a new OTP token"""
        # Invalidate any existing unused tokens for this purpose
        cls.objects.filter(
            user=user, 
            purpose=purpose, 
            is_used=False, 
            is_valid=True
        ).update(is_valid=False)
        
        # Create new token
        token = cls.generate_token()
        expires_at = timezone.now() + timezone.timedelta(minutes=validity_minutes)
        
        otp = cls.objects.create(
            user=user,
            email=user.email,
            token=token,
            purpose=purpose,
            expires_at=expires_at,
            metadata=metadata
        )
        
        return otp


# ============ MEMBERSHIP TIERS & SUBSCRIPTIONS ============

class MembershipTier(models.Model):
    """Membership tier levels (Free, Warrior, Ascension Plus, VIP)"""
    TIER_LEVELS = [
        ('free', 'Free'),
        ('warrior', 'Warrior'),
        ('ascension', 'Ascension Plus'),
        ('vip', 'VIP'),
    ]
    
    tier_level = models.CharField(max_length=20, choices=TIER_LEVELS, unique=True)
    name = models.CharField(max_length=100, help_text='Display name')
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Feature Access
    max_investment_pools = models.IntegerField(default=1, help_text='Max pools can invest in')
    max_withdrawal_per_day = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('1000.00'))
    priority_support = models.BooleanField(default=False)
    access_courses = models.BooleanField(default=False)
    access_live_events = models.BooleanField(default=False)
    access_private_coaching = models.BooleanField(default=False)
    access_community_forum = models.BooleanField(default=False)
    access_resource_library = models.BooleanField(default=False)
    access_portfolio_tracker = models.BooleanField(default=True)
    access_wealth_tools = models.BooleanField(default=False)
    access_insurance_services = models.BooleanField(default=False)
    access_crypto_ira = models.BooleanField(default=False)
    
    # Fees and Bonuses
    trading_fee_discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'),
                                              help_text='Trading fee discount %')
    withdrawal_fee_discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'),
                                                   help_text='Withdrawal fee discount %')
    referral_bonus_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'),
                                                    help_text='Referral bonus multiplier')
    
    # Display
    order = models.IntegerField(default=0, help_text='Display order')
    badge_color = models.CharField(max_length=20, default='#6c757d', help_text='Badge color hex code')
    icon = models.CharField(max_length=50, default='fa-user', help_text='Font Awesome icon class')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Membership Tier'
        verbose_name_plural = 'Membership Tiers'
    
    def __str__(self):
        return f"{self.name} (${self.price_monthly}/month)"
    
    def get_yearly_savings(self):
        """Calculate savings when paying yearly"""
        if self.price_yearly > 0 and self.price_monthly > 0:
            yearly_from_monthly = self.price_monthly * 12
            savings = yearly_from_monthly - self.price_yearly
            return savings
        return Decimal('0.00')


class UserMembership(models.Model):
    """User's membership subscription"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]
    BILLING_CYCLES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    tier = models.ForeignKey(MembershipTier, on_delete=models.PROTECT, related_name='members')
    
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES, default='monthly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Subscription dates
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Payment tracking
    auto_renew = models.BooleanField(default=True)
    payment_method = models.CharField(max_length=50, blank=True, help_text='e.g., Stripe, PayPal, Crypto')
    payment_id = models.CharField(max_length=100, blank=True, help_text='External payment system ID')
    
    # Usage tracking
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    billing_count = models.IntegerField(default=0, help_text='Number of successful billings')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Membership'
        verbose_name_plural = 'User Memberships'
    
    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"
    
    def is_active_membership(self):
        """Check if membership is currently active"""
        if self.status != 'active':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True
    
    def renew_membership(self):
        """Renew membership for next billing cycle"""
        from datetime import timedelta
        
        if self.billing_cycle == 'monthly':
            self.next_billing_date = timezone.now() + timedelta(days=30)
            self.expires_at = self.next_billing_date
            amount = self.tier.price_monthly
        elif self.billing_cycle == 'yearly':
            self.next_billing_date = timezone.now() + timedelta(days=365)
            self.expires_at = self.next_billing_date
            amount = self.tier.price_yearly
        else:  # lifetime
            self.next_billing_date = None
            self.expires_at = None
            amount = Decimal('0.00')
        
        self.total_paid += amount
        self.billing_count += 1
        self.status = 'active'
        self.save()
        
        return amount
    
    def cancel_membership(self):
        """Cancel membership (won't renew)"""
        self.auto_renew = False
        self.cancelled_at = timezone.now()
        self.save()
    
    def downgrade_to_free(self):
        """Downgrade to free tier"""
        free_tier = MembershipTier.objects.get(tier_level='free')
        self.tier = free_tier
        self.billing_cycle = 'lifetime'
        self.auto_renew = False
        self.status = 'active'
        self.expires_at = None
        self.next_billing_date = None
        self.save()


class MembershipPayment(models.Model):
    """Track membership payments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_payments')
    membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    billing_cycle = models.CharField(max_length=20)
    
    payment_method = models.CharField(max_length=50)
    payment_id = models.CharField(max_length=100, blank=True, help_text='External payment system ID')
    transaction_id = models.CharField(max_length=100, blank=True, help_text='Internal transaction reference')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    failure_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Membership Payment'
        verbose_name_plural = 'Membership Payments'
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"


# ============ COMMUNITY FORUM MODELS ============

class ForumCategory(models.Model):
    """Forum discussion categories"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='💬', help_text='Emoji or icon class')
    slug = models.SlugField(unique=True)
    
    # Access Control
    is_public = models.BooleanField(default=True)
    min_membership_tier = models.ForeignKey(MembershipTier, on_delete=models.SET_NULL, null=True, blank=True,
                                            help_text='Minimum tier required to access')
    
    # Stats
    post_count = models.IntegerField(default=0)
    order = models.IntegerField(default=0, help_text='Display order')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Forum Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ForumPost(models.Model):
    """Forum discussion posts/threads"""
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Engagement
    views = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    # Moderation
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_pinned', '-last_activity']
        verbose_name = 'Forum Post'
        verbose_name_plural = 'Forum Posts'
    
    def __str__(self):
        return self.title
    
    def get_like_count(self):
        return self.likes.count()


class ForumReply(models.Model):
    """Replies to forum posts"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies')
    
    content = models.TextField()
    
    # Engagement
    likes = models.ManyToManyField(User, related_name='liked_replies', blank=True)
    
    # Moderation
    is_solution = models.BooleanField(default=False, help_text='Marked as solution by post author')
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Forum Replies'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to: {self.post.title}"
    
    def get_like_count(self):
        return self.likes.count()


# ============ COACHING MODELS ============

class CoachingSession(models.Model):
    """Coaching booking sessions"""
    SESSION_TYPES = [
        ('one_on_one', 'One-on-One'),
        ('group', 'Group Session'),
        ('workshop', 'Workshop'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coaching_sessions')
    membership = models.ForeignKey(UserMembership, on_delete=models.SET_NULL, null=True)
    
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='one_on_one')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Scheduling
    scheduled_date = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    meeting_link = models.URLField(blank=True, help_text='Zoom/Google Meet link')
    
    # Coaching Details
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='coached_sessions')
    topics = models.TextField(blank=True, help_text='Session topics/agenda')
    notes = models.TextField(blank=True, help_text='Coach notes after session')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    attended = models.BooleanField(default=False)
    
    # Pricing (if not included in membership)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = 'Coaching Session'
        verbose_name_plural = 'Coaching Sessions'
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.scheduled_date.strftime('%Y-%m-%d')})"


# ============ EDUCATIONAL COURSES MODELS ============

class CourseCategory(models.Model):
    """Course categories for organization"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📚')
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Course Categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Educational courses"""
    DIFFICULTY_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    
    # Content
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    intro_video_url = models.URLField(blank=True, help_text='YouTube/Vimeo intro video')
    
    # Course Details
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, help_text='Total course duration in hours')
    
    # Access Control
    is_free = models.BooleanField(default=False)
    min_membership_tier = models.ForeignKey(MembershipTier, on_delete=models.SET_NULL, null=True, blank=True,
                                            help_text='Minimum tier required')
    
    # Stats
    student_count = models.IntegerField(default=0)
    lesson_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Learning Outcomes
    what_you_learn = models.TextField(blank=True, help_text='Comma-separated list of outcomes')
    requirements = models.TextField(blank=True, help_text='Prerequisites')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title


class CourseModule(models.Model):
    """Course modules/sections"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    """Individual lessons within modules"""
    LESSON_TYPES = [
        ('video', 'Video'),
        ('article', 'Article'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]
    
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES, default='video')
    order = models.IntegerField(default=0)
    
    # Content
    video_url = models.URLField(blank=True, help_text='YouTube/Vimeo URL')
    video_duration_minutes = models.IntegerField(default=0)
    content = models.TextField(blank=True, help_text='Article content or lesson description')
    
    # Attachments
    pdf_file = models.FileField(upload_to='courses/pdfs/', blank=True, null=True)
    resources = models.TextField(blank=True, help_text='Additional resources/links')
    
    # Settings
    is_preview = models.BooleanField(default=False, help_text='Can be viewed without enrollment')
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.course.title} - {self.title}"


class CourseEnrollment(models.Model):
    """Student enrollments in courses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    # Progress
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    completed_lessons = models.ManyToManyField(Lesson, related_name='completed_by', blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title} ({self.progress_percent}%)"
    
    def update_progress(self):
        """Calculate and update progress percentage"""
        total_lessons = Lesson.objects.filter(module__course=self.course).count()
        if total_lessons > 0:
            completed_count = self.completed_lessons.count()
            self.progress_percent = (completed_count / total_lessons) * 100
            
            # Mark as completed if 100%
            if self.progress_percent >= 100 and not self.completed_at:
                self.completed_at = timezone.now()
                self.certificate_issued = True
        
        self.save()
        return self.progress_percent


class CourseReview(models.Model):
    """Student reviews and ratings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text='1-5 stars')
    review = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}: {self.rating}/5"

