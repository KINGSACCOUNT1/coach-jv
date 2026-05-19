from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal
import requests
import json
from .models import (
    Profile, Wallet, Transaction, Trade, MiningContract, MiningPlan,
    P2PTrade, P2POrder, Deposit, Withdrawal, SupportTicket, Newsletter, KYC
)


# ============ Crypto Price API ============
def get_crypto_prices():
    """Fetch real-time crypto prices from CoinGecko API"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum,tether,binancecoin,solana,ripple,dogecoin,cardano',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'BTC': {'price': Decimal(str(data['bitcoin']['usd'])), 'change': data['bitcoin'].get('usd_24h_change', 0)},
                'ETH': {'price': Decimal(str(data['ethereum']['usd'])), 'change': data['ethereum'].get('usd_24h_change', 0)},
                'USDT': {'price': Decimal(str(data['tether']['usd'])), 'change': data['tether'].get('usd_24h_change', 0)},
                'BNB': {'price': Decimal(str(data['binancecoin']['usd'])), 'change': data['binancecoin'].get('usd_24h_change', 0)},
                'SOL': {'price': Decimal(str(data['solana']['usd'])), 'change': data['solana'].get('usd_24h_change', 0)},
                'XRP': {'price': Decimal(str(data['ripple']['usd'])), 'change': data['ripple'].get('usd_24h_change', 0)},
                'DOGE': {'price': Decimal(str(data['dogecoin']['usd'])), 'change': data['dogecoin'].get('usd_24h_change', 0)},
                'ADA': {'price': Decimal(str(data['cardano']['usd'])), 'change': data['cardano'].get('usd_24h_change', 0)},
            }
    except Exception as e:
        print(f"Error fetching prices: {e}")
    
    # Fallback prices if API fails
    return {
        'BTC': {'price': Decimal('67245.00'), 'change': 2.34},
        'ETH': {'price': Decimal('3456.78'), 'change': 1.89},
        'USDT': {'price': Decimal('1.00'), 'change': 0.01},
        'BNB': {'price': Decimal('598.45'), 'change': -0.56},
        'SOL': {'price': Decimal('142.30'), 'change': 5.67},
        'XRP': {'price': Decimal('0.52'), 'change': -1.23},
        'DOGE': {'price': Decimal('0.082'), 'change': 3.45},
        'ADA': {'price': Decimal('0.45'), 'change': -0.89},
    }


def api_prices(request):
    """API endpoint for fetching crypto prices"""
    prices = get_crypto_prices()
    return JsonResponse({
        'success': True,
        'data': {k: {'price': float(v['price']), 'change': v['change']} for k, v in prices.items()}
    })


# ============ Authentication Views ============
def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate with username or email
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Try email login
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html', {'next': request.GET.get('next', '')})


def register_view(request):
    """Custom registration view"""
    from .email_utils import send_welcome_email
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        referral_code = request.POST.get('referral_code', '')
        
        errors = []
        
        # Validation
        if User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if len(password1) < 8:
            errors.append('Password must be at least 8 characters.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            profile = Profile.objects.create(user=user)
            
            # Handle referral
            if referral_code:
                try:
                    referrer = Profile.objects.get(referral_code=referral_code)
                    profile.referred_by = referrer
                    profile.save()
                except Profile.DoesNotExist:
                    pass
            
            # Create default wallets
            for currency in ['BTC', 'ETH', 'USDT', 'BNB']:
                Wallet.objects.create(user=user, currency=currency)
            
            # Send welcome email
            send_welcome_email(user)
            
            # Auto login
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to CoachJVTech.')
            return redirect('dashboard')
    
    return render(request, 'auth/register.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def password_reset_view(request):
    """Password reset with OTP email"""
    from .email_utils import send_otp_email, verify_otp
    
    if request.method == 'POST':
        action = request.POST.get('action', 'request')
        
        if action == 'request':
            # Send OTP
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email)
                otp = send_otp_email(user, 'password_reset', validity_minutes=15)
                if otp:
                    request.session['reset_user_id'] = user.id
                    messages.success(request, f'A verification code has been sent to {email}. It expires in 15 minutes.')
                    return render(request, 'auth/password_reset.html', {'step': 'verify'})
                else:
                    messages.error(request, 'Failed to send verification code. Please try again.')
            except User.DoesNotExist:
                # Don't reveal if email exists for security
                messages.success(request, 'If an account with that email exists, you will receive reset instructions.')
                return render(request, 'auth/password_reset.html', {'step': 'verify'})
        
        elif action == 'verify':
            # Verify OTP and reset password
            user_id = request.session.get('reset_user_id')
            if not user_id:
                messages.error(request, 'Session expired. Please start again.')
                return redirect('password_reset')
            
            try:
                user = User.objects.get(id=user_id)
                token = request.POST.get('otp_token')
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                # Verify OTP
                success, otp, error_msg = verify_otp(user, token, 'password_reset')
                
                if not success:
                    messages.error(request, error_msg or 'Invalid verification code.')
                    return render(request, 'auth/password_reset.html', {'step': 'verify'})
                
                # Validate passwords
                if new_password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return render(request, 'auth/password_reset.html', {'step': 'verify'})
                
                if len(new_password) < 8:
                    messages.error(request, 'Password must be at least 8 characters.')
                    return render(request, 'auth/password_reset.html', {'step': 'verify'})
                
                # Reset password
                user.set_password(new_password)
                user.save()
                
                # Clear session
                del request.session['reset_user_id']
                
                messages.success(request, 'Password reset successful! You can now login with your new password.')
                return redirect('login')
                
            except User.DoesNotExist:
                messages.error(request, 'Invalid session. Please start again.')
                return redirect('password_reset')
    
    return render(request, 'auth/password_reset.html', {'step': 'request'})


def home(request):
    """Landing page - CoachJVTech Trading Platform"""
    return render(request, 'index.html')


@login_required
def dashboard(request):
    """User dashboard with portfolio overview"""
    user = request.user
    from .models import PoolShare, PoolTransaction
    from django.db.models import Sum
    from decimal import Decimal
    
    # Get user's pool shares
    user_pool_shares = PoolShare.objects.filter(user=user, is_active=True).select_related('pool')
    
    # Calculate portfolio metrics
    total_portfolio_value = sum([share.current_value for share in user_pool_shares]) or Decimal('0')
    total_invested = sum([share.total_invested for share in user_pool_shares]) or Decimal('0')
    total_profits = total_portfolio_value - total_invested
    
    # Calculate average ROI
    if total_invested > 0:
        avg_roi = (total_profits / total_invested) * 100
    else:
        avg_roi = Decimal('0')
    
    # Get recent transactions
    recent_transactions = PoolTransaction.objects.filter(
        user=user, 
        status='completed'
    ).select_related('pool').order_by('-created_at')[:10]
    
    # Update current values for all shares
    for share in user_pool_shares:
        share.update_current_value()
        share.save()
    
    context = {
        'user_pool_shares': user_pool_shares,
        'active_pools_count': user_pool_shares.count(),
        'total_portfolio_value': total_portfolio_value,
        'total_profits': total_profits,
        'avg_roi': avg_roi,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def wallet_view(request):
    """Wallet management page"""
    wallets = Wallet.objects.filter(user=request.user)
    
    # Get real prices
    crypto_prices = get_crypto_prices()
    
    wallet_data = []
    total_value = Decimal('0')
    for wallet in wallets:
        price_data = crypto_prices.get(wallet.currency, {'price': Decimal('0'), 'change': 0})
        value = wallet.balance * price_data['price']
        total_value += value
        wallet_data.append({
            'wallet': wallet,
            'price': price_data['price'],
            'change': price_data['change'],
            'value': value,
        })
    
    # Recent transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    # Handle deposit/withdrawal requests
    if request.method == 'POST':
        action = request.POST.get('action')
        currency = request.POST.get('currency')
        amount = Decimal(request.POST.get('amount', '0'))
        
        if action == 'deposit':
            address = request.POST.get('address', '')
            deposit = Deposit.objects.create(
                user=request.user,
                currency=currency,
                amount=amount,
                wallet_address=address,
                status='pending'
            )
            messages.success(request, f'Deposit request for {amount} {currency} submitted. Awaiting confirmation.')
        elif action == 'withdraw':
            address = request.POST.get('address', '')
            try:
                wallet = Wallet.objects.get(user=request.user, currency=currency)
                if wallet.balance >= amount:
                    withdrawal = Withdrawal.objects.create(
                        user=request.user,
                        currency=currency,
                        amount=amount,
                        wallet_address=address,
                        status='pending'
                    )
                    messages.success(request, f'Withdrawal request for {amount} {currency} submitted.')
                else:
                    messages.error(request, 'Insufficient balance.')
            except Wallet.DoesNotExist:
                messages.error(request, 'Wallet not found.')
        
        return redirect('wallet')
    
    context = {
        'wallets': wallet_data,
        'total_value': total_value,
        'transactions': transactions,
    }
    
    return render(request, 'dashboard/wallet.html', context)


@login_required
def trading_view(request):
    """Spot trading page"""
    crypto_prices = get_crypto_prices()
    trades = Trade.objects.filter(user=request.user).order_by('-created_at')[:20]
    open_trades = Trade.objects.filter(user=request.user, status='open')
    
    # Handle trade submission
    if request.method == 'POST':
        trade_type = request.POST.get('trade_type')  # buy or sell
        pair = request.POST.get('pair', 'BTC/USDT')
        amount = Decimal(request.POST.get('amount', '0'))
        price = Decimal(request.POST.get('price', '0'))
        
        base_currency, quote_currency = pair.split('/')
        
        trade = Trade.objects.create(
            user=request.user,
            trade_type=trade_type,
            pair=pair,
            amount=amount,
            price=price,
            total=amount * price,
            status='open'
        )
        messages.success(request, f'{trade_type.upper()} order placed for {amount} {base_currency}.')
        return redirect('trading')
    
    context = {
        'trades': trades,
        'open_trades': open_trades,
        'crypto_prices': crypto_prices,
    }
    
    return render(request, 'dashboard/trading.html', context)


@login_required
def mining_view(request):
    """Mining contracts page"""
    plans = MiningPlan.objects.filter(is_active=True)
    contracts = MiningContract.objects.filter(user=request.user).order_by('-started_at')
    active_contracts = contracts.filter(status='active')
    total_earnings = contracts.aggregate(total=Sum('total_earned'))['total'] or Decimal('0')
    
    # Handle mining plan purchase
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        try:
            plan = MiningPlan.objects.get(id=plan_id, is_active=True)
            usdt_wallet = Wallet.objects.get(user=request.user, currency='USDT')
            
            if usdt_wallet.balance >= plan.price:
                usdt_wallet.balance -= plan.price
                usdt_wallet.save()
                
                contract = MiningContract.objects.create(
                    user=request.user,
                    plan=plan,
                    status='active',
                    started_at=timezone.now()
                )
                messages.success(request, f'Successfully purchased {plan.name} mining plan!')
            else:
                messages.error(request, 'Insufficient USDT balance.')
        except (MiningPlan.DoesNotExist, Wallet.DoesNotExist):
            messages.error(request, 'Invalid plan or wallet not found.')
        
        return redirect('mining')
    
    context = {
        'plans': plans,
        'contracts': contracts,
        'active_contracts': active_contracts,
        'total_earnings': total_earnings,
    }
    
    return render(request, 'dashboard/mining.html', context)


@login_required
def p2p_view(request):
    """P2P trading page"""
    my_ads = P2PTrade.objects.filter(user=request.user).order_by('-created_at')
    all_ads = P2PTrade.objects.filter(status='active').exclude(user=request.user)[:20]
    my_orders = P2POrder.objects.filter(buyer=request.user) | P2POrder.objects.filter(seller=request.user)
    my_orders = my_orders.order_by('-created_at')[:20]
    
    # Handle P2P ad creation
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_ad':
            ad_type = request.POST.get('ad_type')  # buy or sell
            currency = request.POST.get('currency')
            amount = Decimal(request.POST.get('amount', '0'))
            price = Decimal(request.POST.get('price', '0'))
            payment_method = request.POST.get('payment_method', 'bank_transfer')
            
            P2PTrade.objects.create(
                user=request.user,
                trade_type=ad_type,
                currency=currency,
                amount=amount,
                price=price,
                payment_method=payment_method,
                status='active'
            )
            messages.success(request, f'P2P {ad_type} ad created successfully!')
        
        return redirect('p2p')
    
    context = {
        'my_ads': my_ads,
        'all_ads': all_ads,
        'my_orders': my_orders,
    }
    
    return render(request, 'dashboard/p2p.html', context)


@login_required  
def profile_view(request):
    """User profile page"""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    try:
        kyc = KYC.objects.get(user=request.user)
    except KYC.DoesNotExist:
        kyc = None
    
    context = {
        'profile': profile,
        'kyc': kyc,
    }
    
    return render(request, 'dashboard/profile.html', context)


def newsletter_subscribe(request):
    """Newsletter subscription endpoint"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            Newsletter.objects.get_or_create(email=email)
            messages.success(request, 'Successfully subscribed to newsletter!')
        return redirect('home')
    return redirect('home')


# ============ INVESTMENT POOL VIEWS ============

@login_required
def investment_pools_view(request):
    """View all available investment pools"""
    from .models import InvestmentPool, PoolShare
    
    # Get all active pools
    pools = InvestmentPool.objects.filter(status='active').order_by('-featured', '-roi_percentage')
    
    # Get user's pool shares
    user_shares = PoolShare.objects.filter(user=request.user, is_active=True).select_related('pool')
    
    # Get user's USDT balance for investment
    try:
        usdt_wallet = Wallet.objects.get(user=request.user, currency='USDT')
        usdt_balance = usdt_wallet.balance
    except Wallet.DoesNotExist:
        usdt_balance = Decimal('0')
    
    context = {
        'pools': pools,
        'user_shares': user_shares,
        'usdt_balance': usdt_balance,
    }
    
    return render(request, 'dashboard/investment_pools.html', context)


@login_required
def pool_detail_view(request, pool_id):
    """View detailed information about a specific pool"""
    from .models import InvestmentPool, PoolShare, PoolTrade, PoolPerformance
    
    pool = get_object_or_404(InvestmentPool, id=pool_id)
    
    # Get user's share in this pool
    try:
        user_share = PoolShare.objects.get(user=request.user, pool=pool, is_active=True)
        user_share.update_current_value()
    except PoolShare.DoesNotExist:
        user_share = None
    
    # Recent trades
    recent_trades = PoolTrade.objects.filter(pool=pool).order_by('-opened_at')[:10]
    
    # Performance history (last 30 days)
    performance_history = PoolPerformance.objects.filter(pool=pool).order_by('-date')[:30]
    
    # Get user's USDT balance
    try:
        usdt_wallet = Wallet.objects.get(user=request.user, currency='USDT')
        usdt_balance = usdt_wallet.balance
    except Wallet.DoesNotExist:
        usdt_balance = Decimal('0')
    
    # Calculate pool statistics
    total_investors = PoolShare.objects.filter(pool=pool, is_active=True).count()
    winning_trades = recent_trades.filter(status='filled', profit_loss__gt=0).count()
    losing_trades = recent_trades.filter(status='filled', profit_loss__lt=0).count()
    
    context = {
        'pool': pool,
        'user_share': user_share,
        'recent_trades': recent_trades,
        'performance_history': performance_history,
        'usdt_balance': usdt_balance,
        'total_investors': total_investors,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
    }
    
    return render(request, 'dashboard/pool_detail.html', context)


@login_required
@require_POST
def pool_invest_view(request, pool_id):
    """Invest in a pool"""
    from .models import InvestmentPool, PoolShare, PoolTransaction
    from django.db import transaction as db_transaction
    
    pool = get_object_or_404(InvestmentPool, id=pool_id, status='active')
    amount = Decimal(request.POST.get('amount', '0'))
    
    # Validation
    if amount < pool.min_investment:
        messages.error(request, f'Minimum investment is {pool.min_investment} {pool.currency}.')
        return redirect('pool_detail', pool_id=pool_id)
    
    if amount > pool.max_investment:
        messages.error(request, f'Maximum investment is {pool.max_investment} {pool.currency}.')
        return redirect('pool_detail', pool_id=pool_id)
    
    # Check user's USDT balance
    try:
        wallet = Wallet.objects.get(user=request.user, currency=pool.currency)
        if wallet.balance < amount:
            messages.error(request, f'Insufficient {pool.currency} balance.')
            return redirect('pool_detail', pool_id=pool_id)
    except Wallet.DoesNotExist:
        messages.error(request, f'{pool.currency} wallet not found.')
        return redirect('pool_detail', pool_id=pool_id)
    
    try:
        with db_transaction.atomic():
            # Deduct from wallet
            wallet.balance -= amount
            wallet.save()
            
            # Calculate shares to purchase
            shares_purchased = amount / pool.share_price
            
            # Get or create user's pool share
            pool_share, created = PoolShare.objects.get_or_create(
                user=request.user,
                pool=pool,
                defaults={
                    'shares_owned': Decimal('0'),
                    'purchase_price': pool.share_price,
                    'total_invested': Decimal('0'),
                    'current_value': Decimal('0'),
                    'locked_until': timezone.now() + timezone.timedelta(days=pool.lock_period_days),
                }
            )
            
            # Update share ownership
            if created:
                pool_share.shares_owned = shares_purchased
                pool_share.purchase_price = pool.share_price
                pool_share.total_invested = amount
            else:
                # Calculate weighted average purchase price
                total_shares_after = pool_share.shares_owned + shares_purchased
                total_cost = (pool_share.shares_owned * pool_share.purchase_price) + (shares_purchased * pool.share_price)
                pool_share.purchase_price = total_cost / total_shares_after
                pool_share.shares_owned = total_shares_after
                pool_share.total_invested += amount
                # Update lock period
                pool_share.locked_until = timezone.now() + timezone.timedelta(days=pool.lock_period_days)
            
            pool_share.update_current_value()
            pool_share.is_active = True
            pool_share.save()
            
            # Update pool totals
            pool.total_invested += amount
            pool.total_value += amount
            pool.available_capital += amount
            pool.total_shares += shares_purchased
            pool.save()
            
            # Create transaction record
            PoolTransaction.objects.create(
                user=request.user,
                pool=pool,
                type='investment',
                shares=shares_purchased,
                share_price=pool.share_price,
                amount=amount,
                status='completed',
                description=f'Investment in {pool.name}',
                completed_at=timezone.now()
            )
            
            # Create general transaction
            Transaction.objects.create(
                user=request.user,
                type='transfer',
                currency=pool.currency,
                amount=-amount,
                status='completed',
                description=f'Investment in {pool.name}',
                completed_at=timezone.now()
            )
            
            messages.success(request, f'Successfully invested {amount} {pool.currency} in {pool.name}! You received {shares_purchased:.4f} shares.')
    
    except Exception as e:
        messages.error(request, f'Investment failed: {str(e)}')
    
    return redirect('pool_detail', pool_id=pool_id)


@login_required
@require_POST
def pool_withdraw_view(request, pool_id):
    """Withdraw from a pool"""
    from .models import InvestmentPool, PoolShare, PoolTransaction
    from django.db import transaction as db_transaction
    
    pool = get_object_or_404(InvestmentPool, id=pool_id)
    
    # Get user's share
    try:
        pool_share = PoolShare.objects.get(user=request.user, pool=pool, is_active=True)
    except PoolShare.DoesNotExist:
        messages.error(request, 'You have no shares in this pool.')
        return redirect('pool_detail', pool_id=pool_id)
    
    # Check lock period
    if pool_share.locked_until and timezone.now() < pool_share.locked_until:
        days_left = (pool_share.locked_until - timezone.now()).days
        messages.error(request, f'Your investment is locked for {days_left} more days.')
        return redirect('pool_detail', pool_id=pool_id)
    
    withdrawal_type = request.POST.get('withdrawal_type', 'full')
    
    if withdrawal_type == 'full':
        shares_to_sell = pool_share.shares_owned
    else:
        # Partial withdrawal
        amount_to_withdraw = Decimal(request.POST.get('amount', '0'))
        shares_to_sell = amount_to_withdraw / pool.share_price
        
        if shares_to_sell > pool_share.shares_owned:
            messages.error(request, 'Insufficient shares.')
            return redirect('pool_detail', pool_id=pool_id)
    
    try:
        with db_transaction.atomic():
            # Calculate withdrawal amount
            withdrawal_amount = shares_to_sell * pool.share_price
            
            # Apply management fee if configured
            fee = Decimal('0')
            if pool.management_fee_percent > 0:
                fee = (withdrawal_amount * pool.management_fee_percent) / 100
            
            net_amount = withdrawal_amount - fee
            
            # Credit user's wallet
            wallet, _ = Wallet.objects.get_or_create(user=request.user, currency=pool.currency)
            wallet.balance += net_amount
            wallet.save()
            
            # Update pool share
            pool_share.shares_owned -= shares_to_sell
            pool_share.total_invested -= (shares_to_sell * pool_share.purchase_price)
            
            if pool_share.shares_owned <= Decimal('0.00000001'):
                pool_share.is_active = False
                pool_share.shares_owned = Decimal('0')
            
            pool_share.update_current_value()
            pool_share.save()
            
            # Update pool totals
            pool.total_value -= withdrawal_amount
            pool.available_capital -= withdrawal_amount
            pool.total_shares -= shares_to_sell
            pool.save()
            
            # Create transaction records
            PoolTransaction.objects.create(
                user=request.user,
                pool=pool,
                type='withdrawal',
                shares=shares_to_sell,
                share_price=pool.share_price,
                amount=withdrawal_amount,
                fee=fee,
                status='completed',
                description=f'Withdrawal from {pool.name}',
                completed_at=timezone.now()
            )
            
            Transaction.objects.create(
                user=request.user,
                type='transfer',
                currency=pool.currency,
                amount=net_amount,
                fee=fee,
                status='completed',
                description=f'Withdrawal from {pool.name}',
                completed_at=timezone.now()
            )
            
            if withdrawal_type == 'full':
                messages.success(request, f'Successfully withdrew all shares from {pool.name}! Received {net_amount:.4f} {pool.currency}.')
            else:
                messages.success(request, f'Successfully withdrew {withdrawal_amount:.4f} {pool.currency} from {pool.name}! ({shares_to_sell:.4f} shares)')
    
    except Exception as e:
        messages.error(request, f'Withdrawal failed: {str(e)}')
    
    return redirect('pool_detail', pool_id=pool_id)


@login_required
def my_investments_view(request):
    """View user's investment portfolio"""
    from .models import PoolShare, PoolTransaction
    
    # Get all user's pool shares
    user_shares = PoolShare.objects.filter(
        user=request.user, 
        is_active=True
    ).select_related('pool').order_by('-total_invested')
    
    # Update current values
    for share in user_shares:
        share.update_current_value()
        share.save()
    
    # Calculate totals
    total_invested = sum([share.total_invested for share in user_shares]) or Decimal('0')
    total_current_value = sum([share.current_value for share in user_shares]) or Decimal('0')
    total_profit_loss = total_current_value - total_invested
    
    if total_invested > 0:
        total_roi = (total_profit_loss / total_invested) * 100
    else:
        total_roi = Decimal('0')
    
    # Recent transactions
    recent_transactions = PoolTransaction.objects.filter(
        user=request.user,
        status='completed'
    ).select_related('pool').order_by('-created_at')[:20]
    
    context = {
        'user_shares': user_shares,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
        'total_roi': total_roi,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'dashboard/my_investments.html', context)

