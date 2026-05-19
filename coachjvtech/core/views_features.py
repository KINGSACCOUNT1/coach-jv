# Additional views for new features
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal
from datetime import timedelta

from .models import (
    KYC, SupportTicket, TicketReply, UserMembership, MembershipTier,
    Profile, Wallet, InvestmentPool, PoolShare, MiningContract, Transaction as TxModel
)


# ============ KYC SUBMISSION VIEWS ============

@login_required
def kyc_submit_view(request):
    """KYC document submission"""
    # Check if user already has KYC submitted
    try:
        kyc_status = KYC.objects.get(user=request.user)
        return render(request, 'dashboard/kyc_submit.html', {'kyc_status': kyc_status})
    except KYC.DoesNotExist:
        kyc_status = None
    
    if request.method == 'POST':
        # Create KYC submission
        kyc = KYC.objects.create(
            user=request.user,
            document_type=request.POST.get('document_type'),
            full_name=request.POST.get('full_name'),
            date_of_birth=request.POST.get('date_of_birth'),
            address=request.POST.get('address'),
            document_front=request.FILES.get('document_front'),
            document_back=request.FILES.get('document_back'),
            selfie=request.FILES.get('selfie'),
            status='pending'
        )
        
        messages.success(request, '✓ KYC documents submitted successfully! We\'ll review within 24-48 hours.')
        return redirect('dashboard')
    
    return render(request, 'dashboard/kyc_submit.html', {'kyc_status': kyc_status})


# ============ SUPPORT TICKET SYSTEM ============

@login_required
def support_tickets_view(request):
    """List user's support tickets"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/support_tickets.html', {'tickets': tickets})


@login_required
def create_ticket_view(request):
    """Create new support ticket"""
    if request.method == 'POST':
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
            priority=request.POST.get('priority', 'medium')
        )
        
        messages.success(request, f'✓ Ticket #{ticket.id} created successfully!')
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    return render(request, 'dashboard/create_ticket.html')


@login_required
def ticket_detail_view(request, ticket_id):
    """View ticket details and replies"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    replies = ticket.replies.all().order_by('created_at')
    
    if request.method == 'POST':
        # Add reply
        TicketReply.objects.create(
            ticket=ticket,
            user=request.user,
            message=request.POST.get('message'),
            is_staff=request.user.is_staff
        )
        
        # Reopen ticket if it was closed
        if ticket.status == 'closed':
            ticket.status = 'open'
            ticket.save()
        
        messages.success(request, '✓ Reply added')
        return redirect('ticket_detail', ticket_id=ticket.id)
    
    return render(request, 'dashboard/ticket_detail.html', {
        'ticket': ticket,
        'replies': replies
    })


# ============ COACHING BOOKING SYSTEM ============

@login_required
def coaching_sessions_view(request):
    """View and book coaching sessions"""
    # Check membership tier access
    try:
        membership = UserMembership.objects.get(user=request.user)
        has_access = membership.tier.access_private_coaching
    except UserMembership.DoesNotExist:
        has_access = False
        membership = None
    
    # This is a placeholder - full implementation would include calendar integration
    return render(request, 'dashboard/coaching_sessions.html', {
        'has_access': has_access,
        'membership': membership
    })


# ============ ENHANCED PORTFOLIO TRACKER ============

@login_required
def portfolio_tracker_view(request):
    """Enhanced portfolio tracker with charts and analytics"""
    # Get user's wallets
    wallets = Wallet.objects.filter(user=request.user)
    
    # Get investment pool shares
    pool_shares = PoolShare.objects.filter(user=request.user, is_active=True)
    
    # Get mining contracts
    mining_contracts = MiningContract.objects.filter(user=request.user, status='active')
    
    # Calculate total portfolio value
    total_crypto = sum([w.balance for w in wallets if w.currency == 'USDT'], Decimal('0'))
    total_pools = sum([s.current_value for s in pool_shares], Decimal('0'))
    total_mining = sum([m.investment for m in mining_contracts], Decimal('0'))
    
    total_value = total_crypto + total_pools + total_mining
    
    # Fetch crypto prices for live tracking
    import requests
    try:
        prices_response = requests.get('https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'bitcoin,ethereum,tether', 'vs_currencies': 'usd'},
            timeout=5
        )
        crypto_prices = prices_response.json() if prices_response.ok else {}
    except:
        crypto_prices = {}
    
    return render(request, 'dashboard/portfolio_tracker.html', {
        'wallets': wallets,
        'pool_shares': pool_shares,
        'mining_contracts': mining_contracts,
        'total_value': total_value,
        'total_crypto': total_crypto,
        'total_pools': total_pools,
        'total_mining': total_mining,
        'crypto_prices': crypto_prices
    })


# ============ COMMUNITY FORUM ============

@login_required
def community_forum_view(request):
    """Community forum main page"""
    # Check membership access
    try:
        membership = UserMembership.objects.get(user=request.user)
        has_access = membership.tier.access_community_forum
    except UserMembership.DoesNotExist:
        has_access = False
        membership = None
    
    # Placeholder for forum - full implementation would include posts, categories, etc.
    return render(request, 'dashboard/community_forum.html', {
        'has_access': has_access,
        'membership': membership
    })


# ============ MEMBERSHIP & TIERS ============

@login_required
def membership_tiers_view(request):
    """View and upgrade membership tiers"""
    tiers = MembershipTier.objects.filter(is_active=True).order_by('order')
    
    try:
        current_membership = UserMembership.objects.get(user=request.user)
    except UserMembership.DoesNotExist:
        current_membership = None
    
    return render(request, 'dashboard/membership_tiers.html', {
        'tiers': tiers,
        'current_membership': current_membership
    })


@login_required
def upgrade_membership_view(request, tier_id):
    """Upgrade to a specific tier"""
    tier = get_object_or_404(MembershipTier, id=tier_id, is_active=True)
    
    if request.method == 'POST':
        billing_cycle = request.POST.get('billing_cycle', 'monthly')
        
        # Get or create membership
        membership, created = UserMembership.objects.get_or_create(
            user=request.user,
            defaults={
                'tier': tier,
                'billing_cycle': billing_cycle,
                'status': 'active'
            }
        )
        
        if not created:
            # Update existing membership
            membership.tier = tier
            membership.billing_cycle = billing_cycle
            membership.status = 'active'
            membership.save()
        
        # Set expiry dates
        membership.renew_membership()
        
        messages.success(request, f'✓ Successfully upgraded to {tier.name}!')
        return redirect('dashboard')
    
    return render(request, 'dashboard/upgrade_membership.html', {'tier': tier})
