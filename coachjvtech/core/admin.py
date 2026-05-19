from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
from .models import (
    Profile, KYC, Wallet, Transaction, Trade, 
    MiningPlan, MiningContract, P2PTrade, P2POrder,
    Deposit, Withdrawal, Newsletter, SupportTicket, TicketReply,
    InvestmentPool, PoolShare, PoolTransaction, PoolTrade, PoolPerformance,
    OTPToken,
    MembershipTier, UserMembership, MembershipPayment
)


# ========== Custom Admin Site ==========
class CryptoAdminSite(admin.AdminSite):
    site_header = 'CryptoTrade Admin'
    site_title = 'CryptoTrade'
    index_title = 'Dashboard'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Dashboard stats
        extra_context['user_count'] = User.objects.count()
        extra_context['pending_kyc'] = KYC.objects.filter(status='pending').count()
        extra_context['pending_deposits'] = Deposit.objects.filter(status='pending').count()
        extra_context['pending_withdrawals'] = Withdrawal.objects.filter(status='pending').count()
        extra_context['open_tickets'] = SupportTicket.objects.filter(status='open').count()
        extra_context['active_mining'] = MiningContract.objects.filter(status='active').count()
        extra_context['active_p2p'] = P2PTrade.objects.filter(status='active').count()
        
        # Total balances
        total_btc = Wallet.objects.filter(currency='BTC').aggregate(total=Sum('balance'))['total'] or 0
        total_eth = Wallet.objects.filter(currency='ETH').aggregate(total=Sum('balance'))['total'] or 0
        total_usdt = Wallet.objects.filter(currency='USDT').aggregate(total=Sum('balance'))['total'] or 0
        extra_context['total_btc'] = total_btc
        extra_context['total_eth'] = total_eth
        extra_context['total_usdt'] = total_usdt
        
        return super().index(request, extra_context)


# ========== Inline for Profile in User admin ==========
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class WalletInline(admin.TabularInline):
    model = Wallet
    extra = 0
    readonly_fields = ('address', 'created_at')
    can_delete = False


# ========== Extended User Admin ==========
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, WalletInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    actions = ['activate_users', 'deactivate_users', 'create_wallets']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} user(s) activated.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'

    def create_wallets(self, request, queryset):
        currencies = ['BTC', 'ETH', 'USDT', 'BNB']
        created = 0
        for user in queryset:
            for currency in currencies:
                _, was_created = Wallet.objects.get_or_create(user=user, currency=currency)
                if was_created:
                    created += 1
        self.message_user(request, f'{created} wallet(s) created.')
    create_wallets.short_description = 'Create default wallets for users'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ========== Profile Admin ==========
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'country', 'is_verified', 'referral_code', 'created_at')
    list_filter = ('is_verified', 'country', 'two_factor_enabled')
    search_fields = ('user__username', 'user__email', 'phone', 'referral_code')
    readonly_fields = ('referral_code', 'created_at', 'updated_at')
    actions = ['verify_profiles', 'unverify_profiles']

    def verify_profiles(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} profile(s) verified.')
    verify_profiles.short_description = 'Mark as Verified'

    def unverify_profiles(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f'{queryset.count()} profile(s) unverified.')
    unverify_profiles.short_description = 'Mark as Unverified'


# ========== KYC Admin ==========
@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'full_name', 'status', 'status_badge', 'submitted_at')
    list_filter = ('status', 'document_type', 'submitted_at')
    search_fields = ('user__username', 'full_name')
    readonly_fields = ('submitted_at', 'document_preview')
    actions = ['approve_kyc', 'reject_kyc']
    fieldsets = (
        ('User Info', {'fields': ('user', 'full_name', 'date_of_birth', 'address')}),
        ('Documents', {'fields': ('document_type', 'document_front', 'document_back', 'selfie', 'document_preview')}),
        ('Status', {'fields': ('status', 'rejection_reason', 'submitted_at', 'reviewed_at', 'reviewed_by')}),
    )

    def status_badge(self, obj):
        colors = {'pending': 'orange', 'approved': 'green', 'rejected': 'red'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def document_preview(self, obj):
        html = ''
        if obj.document_front:
            html += f'<img src="{obj.document_front.url}" style="max-width: 200px; margin: 5px;"/>'
        if obj.document_back:
            html += f'<img src="{obj.document_back.url}" style="max-width: 200px; margin: 5px;"/>'
        if obj.selfie:
            html += f'<img src="{obj.selfie.url}" style="max-width: 200px; margin: 5px;"/>'
        return format_html(html) if html else 'No images'
    document_preview.short_description = 'Document Preview'

    def approve_kyc(self, request, queryset):
        from core.email_utils import send_kyc_status_email
        
        approved_count = 0
        for kyc in queryset.filter(status='pending'):
            kyc.status = 'approved'
            kyc.reviewed_at = timezone.now()
            kyc.reviewed_by = request.user
            kyc.save()
            
            # Also verify user profiles
            Profile.objects.filter(user=kyc.user).update(is_verified=True)
            
            # Send approval email
            try:
                send_kyc_status_email(kyc.user, kyc)
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            approved_count += 1
        
        self.message_user(request, f'✅ {approved_count} KYC application(s) approved and users verified.', level='SUCCESS')
    approve_kyc.short_description = '✅ Approve selected KYC'

    def reject_kyc(self, request, queryset):
        from core.email_utils import send_kyc_status_email
        
        rejected_count = 0
        for kyc in queryset.filter(status='pending'):
            kyc.status = 'rejected'
            kyc.reviewed_at = timezone.now()
            kyc.reviewed_by = request.user
            if not kyc.rejection_reason:
                kyc.rejection_reason = 'Documents do not meet verification requirements. Please resubmit with clearer images.'
            kyc.save()
            
            # Send rejection email
            try:
                send_kyc_status_email(kyc.user, kyc)
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            rejected_count += 1
        
        self.message_user(request, f'❌ {rejected_count} KYC application(s) rejected.', level='WARNING')
    reject_kyc.short_description = '❌ Reject selected KYC'


# ========== Wallet Admin ==========
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'balance_display', 'address_short', 'is_active', 'created_at')
    list_filter = ('currency', 'is_active')
    search_fields = ('user__username', 'address')
    readonly_fields = ('address', 'created_at')
    actions = ['add_bonus', 'deduct_balance', 'activate_wallets', 'deactivate_wallets']

    def balance_display(self, obj):
        color = 'green' if obj.balance > 0 else 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">{} {}</span>', 
                          color, obj.balance, obj.currency)
    balance_display.short_description = 'Balance'

    def address_short(self, obj):
        return f'{obj.address[:15]}...' if len(obj.address) > 15 else obj.address
    address_short.short_description = 'Address'

    def add_bonus(self, request, queryset):
        # Add 0.001 bonus to each selected wallet
        bonus = Decimal('0.001')
        for wallet in queryset:
            wallet.balance += bonus
            wallet.save()
            Transaction.objects.create(
                user=wallet.user,
                type='referral',
                currency=wallet.currency,
                amount=bonus,
                status='completed',
                description='Admin bonus'
            )
        self.message_user(request, f'Added {bonus} bonus to {queryset.count()} wallet(s).')
    add_bonus.short_description = 'Add 0.001 bonus'

    def deduct_balance(self, request, queryset):
        self.message_user(request, 'Use individual wallet edit to deduct balance.')
    deduct_balance.short_description = 'Deduct balance (edit individually)'

    def activate_wallets(self, request, queryset):
        queryset.update(is_active=True)
    activate_wallets.short_description = 'Activate wallets'

    def deactivate_wallets(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_wallets.short_description = 'Deactivate wallets'


# ========== Transaction Admin ==========
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'currency', 'amount_display', 'fee', 'status_badge', 'created_at')
    list_filter = ('type', 'status', 'currency', 'created_at')
    search_fields = ('user__username', 'tx_hash', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    actions = ['mark_completed', 'mark_failed']

    def amount_display(self, obj):
        color = 'green' if obj.amount > 0 else 'red'
        return format_html('<span style="color: {};">{}</span>', color, obj.amount)
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {'pending': 'orange', 'completed': 'green', 'failed': 'red', 'cancelled': 'gray'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def mark_completed(self, request, queryset):
        queryset.update(status='completed', completed_at=timezone.now())
    mark_completed.short_description = 'Mark as Completed'

    def mark_failed(self, request, queryset):
        queryset.update(status='failed')
    mark_failed.short_description = 'Mark as Failed'


# ========== Trade Admin ==========
@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('user', 'pair', 'side_badge', 'order_type', 'amount', 'price', 'total', 'status_badge', 'created_at')
    list_filter = ('side', 'order_type', 'status', 'pair')
    search_fields = ('user__username', 'pair')
    readonly_fields = ('total', 'created_at')
    actions = ['execute_trades', 'cancel_trades']

    def side_badge(self, obj):
        color = 'green' if obj.side == 'buy' else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.side.upper())
    side_badge.short_description = 'Side'

    def status_badge(self, obj):
        colors = {'open': 'blue', 'filled': 'green', 'partial': 'orange', 'cancelled': 'gray'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def execute_trades(self, request, queryset):
        for trade in queryset.filter(status='open'):
            trade.status = 'filled'
            trade.filled_amount = trade.amount
            trade.filled_at = timezone.now()
            trade.save()
            # Create transaction record
            Transaction.objects.create(
                user=trade.user,
                type='trade',
                currency=trade.pair.split('/')[0],
                amount=trade.amount if trade.side == 'buy' else -trade.amount,
                fee=trade.fee,
                status='completed',
                description=f'{trade.side.upper()} {trade.pair}'
            )
        self.message_user(request, f'{queryset.count()} trade(s) executed.')
    execute_trades.short_description = 'Execute/Fill trades'

    def cancel_trades(self, request, queryset):
        queryset.filter(status='open').update(status='cancelled')
    cancel_trades.short_description = 'Cancel trades'


# ========== Mining Plan Admin ==========
@admin.register(MiningPlan)
class MiningPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'currency', 'hashrate', 'price', 'daily_return', 'duration_days', 'is_active')
    list_filter = ('currency', 'is_active')
    search_fields = ('name',)
    actions = ['activate_plans', 'deactivate_plans']

    def activate_plans(self, request, queryset):
        queryset.update(is_active=True)
    activate_plans.short_description = 'Activate plans'

    def deactivate_plans(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_plans.short_description = 'Deactivate plans'


# ========== Mining Contract Admin ==========
@admin.register(MiningContract)
class MiningContractAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'investment', 'total_earned', 'status_badge', 'started_at', 'ends_at')
    list_filter = ('status', 'plan', 'started_at')
    search_fields = ('user__username',)
    readonly_fields = ('started_at',)
    actions = ['process_payouts', 'complete_contracts', 'cancel_contracts']

    def status_badge(self, obj):
        colors = {'active': 'green', 'completed': 'blue', 'cancelled': 'red'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def process_payouts(self, request, queryset):
        for contract in queryset.filter(status='active'):
            # Calculate daily payout
            daily_payout = contract.investment * contract.plan.daily_return
            contract.total_earned += daily_payout
            contract.last_payout = timezone.now()
            contract.save()
            
            # Credit wallet
            wallet, _ = Wallet.objects.get_or_create(user=contract.user, currency=contract.plan.currency)
            wallet.balance += daily_payout
            wallet.save()
            
            # Create transaction
            Transaction.objects.create(
                user=contract.user,
                type='mining',
                currency=contract.plan.currency,
                amount=daily_payout,
                status='completed',
                description=f'Mining payout - {contract.plan.name}'
            )
        self.message_user(request, f'Processed payouts for {queryset.count()} contract(s).')
    process_payouts.short_description = 'Process daily payouts'

    def complete_contracts(self, request, queryset):
        queryset.filter(status='active').update(status='completed')
    complete_contracts.short_description = 'Mark as Completed'

    def cancel_contracts(self, request, queryset):
        # Refund investment
        for contract in queryset.filter(status='active'):
            wallet, _ = Wallet.objects.get_or_create(user=contract.user, currency=contract.plan.currency)
            wallet.balance += contract.investment
            wallet.save()
            contract.status = 'cancelled'
            contract.save()
        self.message_user(request, f'{queryset.count()} contract(s) cancelled and refunded.')
    cancel_contracts.short_description = 'Cancel and refund'


# ========== P2P Trade Admin ==========
@admin.register(P2PTrade)
class P2PTradeAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_badge', 'currency', 'amount', 'price', 'fiat_currency', 'payment_method', 'status')
    list_filter = ('type', 'status', 'currency', 'payment_method')
    search_fields = ('user__username',)
    actions = ['activate_ads', 'deactivate_ads']

    def type_badge(self, obj):
        color = 'green' if obj.type == 'buy' else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.type.upper())
    type_badge.short_description = 'Type'

    def activate_ads(self, request, queryset):
        queryset.update(status='active')
    activate_ads.short_description = 'Activate ads'

    def deactivate_ads(self, request, queryset):
        queryset.update(status='cancelled')
    deactivate_ads.short_description = 'Deactivate ads'


# ========== P2P Order Admin ==========
@admin.register(P2POrder)
class P2POrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'amount', 'total_fiat', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'seller__username')
    actions = ['release_crypto', 'cancel_orders', 'resolve_dispute_buyer', 'resolve_dispute_seller']

    def status_badge(self, obj):
        colors = {'pending': 'orange', 'paid': 'blue', 'completed': 'green', 'disputed': 'red', 'cancelled': 'gray'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'

    def release_crypto(self, request, queryset):
        for order in queryset.filter(status='paid'):
            # Transfer crypto to buyer
            wallet, _ = Wallet.objects.get_or_create(user=order.buyer, currency=order.ad.currency)
            wallet.balance += order.amount
            wallet.save()
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
        self.message_user(request, f'{queryset.count()} order(s) completed - crypto released.')
    release_crypto.short_description = 'Release crypto to buyer'

    def cancel_orders(self, request, queryset):
        for order in queryset.filter(status__in=['pending', 'paid']):
            # Return crypto to seller
            wallet, _ = Wallet.objects.get_or_create(user=order.seller, currency=order.ad.currency)
            wallet.balance += order.amount
            wallet.save()
            order.status = 'cancelled'
            order.save()
        self.message_user(request, f'{queryset.count()} order(s) cancelled - crypto returned to seller.')
    cancel_orders.short_description = 'Cancel and refund seller'

    def resolve_dispute_buyer(self, request, queryset):
        """Resolve dispute in favor of buyer"""
        for order in queryset.filter(status='disputed'):
            wallet, _ = Wallet.objects.get_or_create(user=order.buyer, currency=order.ad.currency)
            wallet.balance += order.amount
            wallet.save()
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
        self.message_user(request, f'Dispute resolved for {queryset.count()} order(s) - buyer wins.')
    resolve_dispute_buyer.short_description = 'Resolve: Buyer wins'

    def resolve_dispute_seller(self, request, queryset):
        """Resolve dispute in favor of seller"""
        for order in queryset.filter(status='disputed'):
            wallet, _ = Wallet.objects.get_or_create(user=order.seller, currency=order.ad.currency)
            wallet.balance += order.amount
            wallet.save()
            order.status = 'cancelled'
            order.save()
        self.message_user(request, f'Dispute resolved for {queryset.count()} order(s) - seller wins.')
    resolve_dispute_seller.short_description = 'Resolve: Seller wins'


# ========== Deposit Admin ==========
@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'method', 'currency', 'amount_display', 'status_badge', 'proof_preview', 'created_at', 'processed_at')
    list_filter = ('status', 'method', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email', 'tx_hash')
    readonly_fields = ('created_at', 'proof_image')
    date_hierarchy = 'created_at'
    actions = ['approve_deposits', 'reject_deposits']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'method', 'currency', 'amount')
        }),
        ('Transaction Details', {
            'fields': ('tx_hash', 'proof', 'proof_image', 'status')
        }),
        ('Admin Notes', {
            'fields': ('admin_note', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        return format_html('<strong>{} {}</strong>', obj.amount, obj.currency)
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {'pending': '#F59E0B', 'approved': '#10B981', 'rejected': '#EF4444'}
        icons = {'pending': '⏳', 'approved': '✅', 'rejected': '❌'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px;">{} {}</span>', 
            colors.get(obj.status, '#6B7280'),
            icons.get(obj.status, ''),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def proof_preview(self, obj):
        if obj.proof:
            return format_html('<a href="{}" target="_blank">📄 View Proof</a>', obj.proof.url)
        return '—'
    proof_preview.short_description = 'Proof'
    
    def proof_image(self, obj):
        if obj.proof:
            return format_html('<img src="{}" style="max-width: 400px; border-radius: 8px;" />', obj.proof.url)
        return 'No proof uploaded'
    proof_image.short_description = 'Proof Image'

    def approve_deposits(self, request, queryset):
        from core.email_utils import send_deposit_approved_email
        from django.db import transaction as db_transaction
        
        approved_count = 0
        failed_count = 0
        
        for deposit in queryset.filter(status='pending'):
            try:
                with db_transaction.atomic():
                    # Credit wallet
                    wallet, _ = Wallet.objects.get_or_create(user=deposit.user, currency=deposit.currency)
                    wallet.balance += deposit.amount
                    wallet.save()
                    
                    # Update deposit status
                    deposit.status = 'approved'
                    deposit.processed_at = timezone.now()
                    deposit.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        user=deposit.user,
                        type='deposit',
                        currency=deposit.currency,
                        amount=deposit.amount,
                        status='completed',
                        tx_hash=deposit.tx_hash or '',
                        description=f'Deposit via {deposit.get_method_display()}',
                        completed_at=timezone.now()
                    )
                    
                    # Send email notification
                    try:
                        send_deposit_approved_email(deposit.user, deposit)
                    except Exception as e:
                        print(f"Failed to send email: {e}")
                    
                    approved_count += 1
                    
            except Exception as e:
                failed_count += 1
                self.message_user(request, f'Failed to approve deposit #{deposit.id}: {str(e)}', level='ERROR')
        
        if approved_count > 0:
            self.message_user(request, f'✅ {approved_count} deposit(s) approved and credited to wallets.', level='SUCCESS')
        if failed_count > 0:
            self.message_user(request, f'❌ {failed_count} deposit(s) failed to process.', level='ERROR')
            
    approve_deposits.short_description = '✅ Approve and credit deposits'

    def reject_deposits(self, request, queryset):
        from core.email_utils import send_notification_email
        
        rejected_count = 0
        for deposit in queryset.filter(status='pending'):
            deposit.status = 'rejected'
            deposit.processed_at = timezone.now()
            if not deposit.admin_note:
                deposit.admin_note = 'Deposit rejected by admin'
            deposit.save()
            
            # Send rejection email
            try:
                send_notification_email(
                    user=deposit.user,
                    subject='Deposit Rejected - CoachJVTech',
                    template_name='deposit_rejected.html',
                    context={
                        'deposit': deposit,
                        'message': f'Your deposit of {deposit.amount} {deposit.currency} has been rejected. Reason: {deposit.admin_note}'
                    }
                )
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            rejected_count += 1
        
        self.message_user(request, f'❌ {rejected_count} deposit(s) rejected.', level='WARNING')
    reject_deposits.short_description = '❌ Reject deposits'


# ========== Withdrawal Admin ==========
@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'amount_display', 'fee', 'address_short', 'status_badge', 'created_at', 'processed_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__username', 'user__email', 'address', 'tx_hash')
    readonly_fields = ('created_at', 'net_amount_display')
    date_hierarchy = 'created_at'
    actions = ['mark_processing', 'complete_withdrawals', 'reject_withdrawals']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'currency', 'amount', 'fee', 'net_amount_display')
        }),
        ('Withdrawal Details', {
            'fields': ('address', 'network', 'tx_hash', 'status')
        }),
        ('Admin Notes', {
            'fields': ('admin_note', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        return format_html('<strong>{} {}</strong>', obj.amount, obj.currency)
    amount_display.short_description = 'Amount'
    
    def net_amount_display(self, obj):
        net = obj.amount - obj.fee
        return format_html('<strong style="color: #10B981;">{} {}</strong> <small>(after fee)</small>', net, obj.currency)
    net_amount_display.short_description = 'Net Amount'

    def address_short(self, obj):
        addr = obj.address
        if len(addr) > 25:
            return format_html('<code style="font-size: 10px;">{}</code>', addr[:12] + '...' + addr[-8:])
        return format_html('<code style="font-size: 10px;">{}</code>', addr)
    address_short.short_description = 'Wallet Address'

    def status_badge(self, obj):
        colors = {'pending': '#F59E0B', 'processing': '#3B82F6', 'completed': '#10B981', 'rejected': '#EF4444'}
        icons = {'pending': '⏳', 'processing': '⚙️', 'completed': '✅', 'rejected': '❌'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-size: 11px;">{} {}</span>', 
            colors.get(obj.status, '#6B7280'),
            icons.get(obj.status, ''),
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def mark_processing(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='processing')
        self.message_user(request, f'⚙️ {updated} withdrawal(s) marked as processing.', level='INFO')
    mark_processing.short_description = '⚙️ Mark as processing'
    
    def complete_withdrawals(self, request, queryset):
        from core.email_utils import send_withdrawal_completed_email
        
        completed_count = 0
        for withdrawal in queryset.filter(status__in=['pending', 'processing']):
            # Note: In production, verify blockchain transaction first
            withdrawal.status = 'completed'
            withdrawal.processed_at = timezone.now()
            
            # Add tx_hash if not present (admin should add manually)
            if not withdrawal.tx_hash:
                withdrawal.tx_hash = f'pending_blockchain_confirmation_{withdrawal.id}'
            
            withdrawal.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=withdrawal.user,
                type='withdrawal',
                currency=withdrawal.currency,
                amount=-withdrawal.amount,
                fee=withdrawal.fee,
                status='completed',
                tx_hash=withdrawal.tx_hash,
                description=f'Withdrawal to {withdrawal.address[:20]}...',
                completed_at=timezone.now()
            )
            
            # Send email notification
            try:
                send_withdrawal_completed_email(withdrawal.user, withdrawal)
            except Exception as e:
                print(f"Failed to send email: {e}")
            
            completed_count += 1
        
        self.message_user(request, f'✅ {completed_count} withdrawal(s) completed. Funds should be sent to user wallets.', level='SUCCESS')
    complete_withdrawals.short_description = '✅ Complete withdrawals'
    
    def reject_withdrawals(self, request, queryset):
        from core.email_utils import send_notification_email
        from django.db import transaction as db_transaction
        
        rejected_count = 0
        refunded_count = 0
        
        for withdrawal in queryset.filter(status='pending'):
            try:
                with db_transaction.atomic():
                    # Refund to user wallet
                    wallet, _ = Wallet.objects.get_or_create(user=withdrawal.user, currency=withdrawal.currency)
                    wallet.balance += withdrawal.amount  # Refund full amount (including fee)
                    wallet.save()
                    
                    # Update withdrawal status
                    withdrawal.status = 'rejected'
                    withdrawal.processed_at = timezone.now()
                    if not withdrawal.admin_note:
                        withdrawal.admin_note = 'Withdrawal rejected and refunded'
                    withdrawal.save()
                    
                    # Send rejection email
                    try:
                        send_notification_email(
                            user=withdrawal.user,
                            subject='Withdrawal Rejected - CoachJVTech',
                            template_name='withdrawal_rejected.html',
                            context={
                                'withdrawal': withdrawal,
                                'message': f'Your withdrawal request of {withdrawal.amount} {withdrawal.currency} has been rejected and refunded. Reason: {withdrawal.admin_note}'
                            }
                        )
                    except Exception as e:
                        print(f"Failed to send email: {e}")
                    
                    rejected_count += 1
                    refunded_count += 1
                    
            except Exception as e:
                self.message_user(request, f'Failed to reject withdrawal #{withdrawal.id}: {str(e)}', level='ERROR')
        
        if rejected_count > 0:
            self.message_user(request, f'❌ {rejected_count} withdrawal(s) rejected and {refunded_count} refunded.', level='WARNING')
            
    reject_withdrawals.short_description = '❌ Reject and refund withdrawals'



@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'is_staff', 'message_preview', 'created_at')
    list_filter = ('is_staff', 'created_at')
    search_fields = ('ticket__subject', 'user__username', 'message')
    readonly_fields = ('created_at',)

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


# ============ INVESTMENT POOL ADMIN ============

@admin.register(InvestmentPool)
class InvestmentPoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'risk_badge', 'total_value_display', 'roi_badge', 'investor_count', 'status_badge', 'featured')
    list_filter = ('risk_level', 'status', 'featured', 'currency')
    search_fields = ('name', 'description')
    readonly_fields = ('total_shares', 'created_at', 'updated_at', 'performance_summary')
    actions = ['update_pool_values', 'feature_pools', 'activate_pools', 'close_pools']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'risk_level', 'currency', 'status', 'featured')
        }),
        ('Financial Data', {
            'fields': ('total_value', 'total_invested', 'available_capital', 'share_price', 'total_shares')
        }),
        ('Investment Limits', {
            'fields': ('min_investment', 'max_investment', 'lock_period_days')
        }),
        ('Performance', {
            'fields': ('total_profit', 'total_loss', 'roi_percentage', 'performance_summary')
        }),
        ('Fees', {
            'fields': ('management_fee_percent', 'performance_fee_percent')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def risk_badge(self, obj):
        colors = {'conservative': 'green', 'balanced': 'blue', 'aggressive': 'red'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          colors.get(obj.risk_level, 'gray'), obj.get_risk_level_display())
    risk_badge.short_description = 'Risk Level'
    
    def total_value_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">${:,.2f}</span>', obj.total_value)
    total_value_display.short_description = 'Total Value'
    
    def roi_badge(self, obj):
        color = 'green' if obj.roi_percentage > 0 else 'red'
        icon = '▲' if obj.roi_percentage > 0 else '▼'
        return format_html('<span style="color: {}; font-weight: bold;">{} {:.2f}%</span>', 
                          color, icon, obj.roi_percentage)
    roi_badge.short_description = 'ROI'
    
    def status_badge(self, obj):
        colors = {'active': 'green', 'closed': 'red', 'paused': 'orange'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def investor_count(self, obj):
        count = obj.shareholders.filter(is_active=True).count()
        return format_html('<strong>{}</strong> investors', count)
    investor_count.short_description = 'Investors'
    
    def performance_summary(self, obj):
        trades = obj.trades.filter(status='filled')
        winning = trades.filter(profit_loss__gt=0).count()
        losing = trades.filter(profit_loss__lt=0).count()
        win_rate = (winning / (winning + losing) * 100) if (winning + losing) > 0 else 0
        
        html = f"""
        <div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">
            <strong>Trading Performance</strong><br>
            Total Trades: {trades.count()}<br>
            Winning Trades: <span style="color: green;">{winning}</span><br>
            Losing Trades: <span style="color: red;">{losing}</span><br>
            Win Rate: <span style="color: {'green' if win_rate > 50 else 'red'};">{win_rate:.1f}%</span>
        </div>
        """
        return format_html(html)
    performance_summary.short_description = 'Performance Summary'
    
    def update_pool_values(self, request, queryset):
        """Recalculate pool values and share prices"""
        for pool in queryset:
            pool.calculate_share_price()
            pool.update_roi()
            pool.save()
        self.message_user(request, f'Updated values for {queryset.count()} pool(s).')
    update_pool_values.short_description = 'Update Pool Values'
    
    def feature_pools(self, request, queryset):
        queryset.update(featured=True)
    feature_pools.short_description = 'Mark as Featured'
    
    def activate_pools(self, request, queryset):
        queryset.update(status='active')
    activate_pools.short_description = 'Activate Pools'
    
    def close_pools(self, request, queryset):
        queryset.update(status='closed')
    close_pools.short_description = 'Close Pools'


@admin.register(PoolShare)
class PoolShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'pool', 'shares_owned', 'current_value_display', 'profit_loss_badge', 'is_locked', 'created_at')
    list_filter = ('pool', 'is_active', 'created_at')
    search_fields = ('user__username', 'pool__name')
    readonly_fields = ('current_value', 'created_at', 'updated_at')
    actions = ['update_share_values', 'unlock_shares']
    
    def current_value_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">${:,.2f}</span>', obj.current_value)
    current_value_display.short_description = 'Current Value'
    
    def profit_loss_badge(self, obj):
        pl = obj.calculate_profit_loss()
        color = 'green' if pl > 0 else 'red'
        icon = '▲' if pl > 0 else '▼'
        return format_html('<span style="color: {}; font-weight: bold;">{} ${:,.2f}</span>', 
                          color, icon, abs(pl))
    profit_loss_badge.short_description = 'Profit/Loss'
    
    def is_locked(self, obj):
        if obj.locked_until and obj.locked_until > timezone.now():
            return format_html('<span style="color: red;">🔒 Locked until {}</span>', 
                             obj.locked_until.strftime('%Y-%m-%d'))
        return format_html('<span style="color: green;">✓ Unlocked</span>')
    is_locked.short_description = 'Lock Status'
    
    def update_share_values(self, request, queryset):
        for share in queryset:
            share.update_current_value()
            share.save()
        self.message_user(request, f'Updated values for {queryset.count()} share(s).')
    update_share_values.short_description = 'Update Share Values'
    
    def unlock_shares(self, request, queryset):
        queryset.update(locked_until=None)
    unlock_shares.short_description = 'Unlock Shares'


@admin.register(PoolTransaction)
class PoolTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'pool', 'type_badge', 'shares', 'amount_display', 'status_badge', 'created_at')
    list_filter = ('type', 'status', 'pool', 'created_at')
    search_fields = ('user__username', 'pool__name', 'description')
    readonly_fields = ('created_at', 'completed_at')
    date_hierarchy = 'created_at'
    actions = ['complete_transactions', 'cancel_transactions']
    
    def type_badge(self, obj):
        colors = {
            'investment': 'green',
            'withdrawal': 'red',
            'profit_distribution': 'blue',
            'management_fee': 'orange',
            'performance_fee': 'purple'
        }
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          colors.get(obj.type, 'gray'), obj.get_type_display())
    type_badge.short_description = 'Type'
    
    def amount_display(self, obj):
        color = 'green' if obj.type in ['investment', 'profit_distribution'] else 'red'
        return format_html('<span style="color: {};">${:,.2f}</span>', color, obj.amount)
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {'pending': 'orange', 'completed': 'green', 'failed': 'red', 'cancelled': 'gray'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def complete_transactions(self, request, queryset):
        queryset.filter(status='pending').update(status='completed', completed_at=timezone.now())
    complete_transactions.short_description = 'Mark as Completed'
    
    def cancel_transactions(self, request, queryset):
        queryset.filter(status='pending').update(status='cancelled')
    cancel_transactions.short_description = 'Cancel Transactions'


@admin.register(PoolTrade)
class PoolTradeAdmin(admin.ModelAdmin):
    list_display = ('pool', 'pair', 'side_badge', 'entry_price', 'exit_price', 'profit_loss_display', 'status_badge', 'opened_at')
    list_filter = ('side', 'status', 'pool', 'opened_at')
    search_fields = ('pool__name', 'pair', 'notes')
    readonly_fields = ('opened_at', 'closed_at', 'profit_loss')
    date_hierarchy = 'opened_at'
    actions = ['close_trades_profit', 'close_trades_loss', 'cancel_trades']
    
    fieldsets = (
        ('Trade Info', {
            'fields': ('pool', 'executed_by', 'pair', 'side', 'amount')
        }),
        ('Pricing', {
            'fields': ('entry_price', 'exit_price')
        }),
        ('Performance', {
            'fields': ('profit_loss', 'profit_loss_percent')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes', 'opened_at', 'closed_at')
        }),
    )
    
    def side_badge(self, obj):
        color = 'green' if obj.side == 'buy' else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.side.upper())
    side_badge.short_description = 'Side'
    
    def profit_loss_display(self, obj):
        if obj.status == 'filled' and obj.profit_loss:
            color = 'green' if obj.profit_loss > 0 else 'red'
            icon = '▲' if obj.profit_loss > 0 else '▼'
            return format_html('<span style="color: {}; font-weight: bold;">{} ${:,.2f} ({:+.2f}%)</span>', 
                              color, icon, abs(obj.profit_loss), obj.profit_loss_percent)
        return format_html('<span style="color: gray;">Pending</span>')
    profit_loss_display.short_description = 'Profit/Loss'
    
    def status_badge(self, obj):
        colors = {'open': 'blue', 'filled': 'green', 'partial': 'orange', 'cancelled': 'gray'}
        return format_html('<span style="color: {};">{}</span>', 
                          colors.get(obj.status, 'gray'), obj.get_status_display())
    status_badge.short_description = 'Status'
    
    def close_trades_profit(self, request, queryset):
        """Close trades with profit"""
        for trade in queryset.filter(status='open'):
            # Simulate 5% profit
            trade.exit_price = trade.entry_price * Decimal('1.05')
            trade.status = 'filled'
            trade.closed_at = timezone.now()
            trade.calculate_profit_loss()
            trade.save()
            
            # Update pool
            trade.pool.total_profit += trade.profit_loss
            trade.pool.total_value += trade.profit_loss
            trade.pool.calculate_share_price()
            trade.pool.update_roi()
            trade.pool.save()
        
        self.message_user(request, f'Closed {queryset.count()} trade(s) with profit.')
    close_trades_profit.short_description = 'Close with +5% Profit'
    
    def close_trades_loss(self, request, queryset):
        """Close trades with loss"""
        for trade in queryset.filter(status='open'):
            # Simulate 3% loss
            trade.exit_price = trade.entry_price * Decimal('0.97')
            trade.status = 'filled'
            trade.closed_at = timezone.now()
            trade.calculate_profit_loss()
            trade.save()
            
            # Update pool
            trade.pool.total_loss += abs(trade.profit_loss)
            trade.pool.total_value += trade.profit_loss  # Adds negative value
            trade.pool.calculate_share_price()
            trade.pool.update_roi()
            trade.pool.save()
        
        self.message_user(request, f'Closed {queryset.count()} trade(s) with loss.')
    close_trades_loss.short_description = 'Close with -3% Loss'
    
    def cancel_trades(self, request, queryset):
        queryset.filter(status='open').update(status='cancelled')
    cancel_trades.short_description = 'Cancel Trades'


@admin.register(PoolPerformance)
class PoolPerformanceAdmin(admin.ModelAdmin):
    list_display = ('pool', 'date', 'total_value', 'share_price', 'roi_badge', 'total_investors', 'win_rate')
    list_filter = ('pool', 'date')
    search_fields = ('pool__name',)
    readonly_fields = ('date', 'created_at')
    date_hierarchy = 'date'
    
    def roi_badge(self, obj):
        color = 'green' if obj.roi_percentage > 0 else 'red'
        icon = '▲' if obj.roi_percentage > 0 else '▼'
        return format_html('<span style="color: {}; font-weight: bold;">{} {:.2f}%</span>', 
                          color, icon, obj.roi_percentage)
    roi_badge.short_description = 'ROI'
    
    def win_rate(self, obj):
        total_trades = obj.winning_trades + obj.losing_trades
        if total_trades > 0:
            rate = (obj.winning_trades / total_trades) * 100
            color = 'green' if rate > 50 else 'red'
            return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
        return '—'
    win_rate.short_description = 'Win Rate'


# ========== OTP Token Admin ==========
@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'purpose_badge', 'token_masked', 'status_badge', 'attempts', 'created_at', 'expires_at')
    list_filter = ('purpose', 'is_valid', 'is_used', 'created_at')
    search_fields = ('user__username', 'email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at', 'used_at', 'attempts')
    date_hierarchy = 'created_at'
    actions = ['invalidate_tokens']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'email', 'purpose')
        }),
        ('Token Details', {
            'fields': ('token', 'is_valid', 'is_used', 'attempts', 'max_attempts')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'used_at')
        }),
    )
    
    def purpose_badge(self, obj):
        colors = {
            'email_verification': '#3B82F6',
            'password_reset': '#F59E0B',
            'login_2fa': '#10B981',
            'withdrawal_confirm': '#EF4444',
            'account_change': '#8B5CF6',
        }
        return format_html('<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px;">{}</span>', 
                          colors.get(obj.purpose, '#6B7280'), obj.get_purpose_display())
    purpose_badge.short_description = 'Purpose'
    
    def token_masked(self, obj):
        """Show token as XXX*** for security"""
        if obj.is_used:
            return format_html('<span style="color: #9CA3AF; text-decoration: line-through;">{}</span>', obj.token[:3] + '***')
        elif obj.is_expired():
            return format_html('<span style="color: #EF4444;">{} (Expired)</span>', obj.token[:3] + '***')
        else:
            return format_html('<span style="font-weight: bold;">{}</span>', obj.token)
    token_masked.short_description = 'Token'
    
    def status_badge(self, obj):
        if obj.is_used:
            return format_html('<span style="color: #9CA3AF;">✓ Used</span>')
        elif not obj.is_valid:
            return format_html('<span style="color: #EF4444;">✗ Invalid</span>')
        elif obj.is_expired():
            return format_html('<span style="color: #F59E0B;">⌛ Expired</span>')
        elif obj.attempts >= obj.max_attempts:
            return format_html('<span style="color: #EF4444;">🔒 Locked</span>')
        else:
            return format_html('<span style="color: #10B981;">✓ Active</span>')
    status_badge.short_description = 'Status'
    
    def invalidate_tokens(self, request, queryset):
        updated = queryset.filter(is_valid=True, is_used=False).update(is_valid=False)
        self.message_user(request, f'{updated} token(s) invalidated.')
    invalidate_tokens.short_description = 'Invalidate selected tokens'
    
    def has_add_permission(self, request):
        # Prevent manual creation via admin - should use email_utils
        return False


# ========== MEMBERSHIP TIERS & SUBSCRIPTIONS ADMIN ==========

@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier_level', 'price_badge', 'member_count', 'features_summary', 'order', 'active_badge', 'featured_badge')
    list_filter = ('is_active', 'is_featured', 'tier_level')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tier_level', 'name', 'description', 'order', 'is_active', 'is_featured')
        }),
        ('Pricing', {
            'fields': ('price_monthly', 'price_yearly')
        }),
        ('Investment & Trading Access', {
            'fields': ('max_investment_pools', 'max_withdrawal_per_day')
        }),
        ('Feature Access', {
            'fields': (
                'access_courses', 'access_live_events', 'access_private_coaching',
                'access_community_forum', 'access_resource_library', 'access_portfolio_tracker',
                'access_wealth_tools', 'access_insurance_services', 'access_crypto_ira'
            ),
            'classes': ('collapse',)
        }),
        ('Fees & Bonuses', {
            'fields': ('trading_fee_discount', 'withdrawal_fee_discount', 'referral_bonus_multiplier', 'priority_support'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('badge_color', 'icon'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_badge(self, obj):
        monthly = obj.price_monthly
        yearly = obj.price_yearly
        savings = obj.get_yearly_savings()
        
        if monthly == 0:
            return format_html('<span style="color: #10B981; font-weight: bold;">FREE</span>')
        
        html = f'<div style="font-size: 12px;">'
        html += f'<div style="font-weight: bold;">${monthly}/month</div>'
        if yearly > 0:
            html += f'<div style="color: #6B7280;">${yearly}/year'
            if savings > 0:
                html += f' <span style="color: #10B981;">(Save ${savings})</span>'
            html += '</div>'
        html += '</div>'
        return format_html(html)
    price_badge.short_description = 'Pricing'
    
    def member_count(self, obj):
        count = obj.members.filter(status='active').count()
        return format_html('<span style="font-weight: bold; color: #3B82F6;">{}</span>', count)
    member_count.short_description = 'Active Members'
    
    def features_summary(self, obj):
        features = []
        if obj.access_courses:
            features.append('📚 Courses')
        if obj.access_live_events:
            features.append('🎥 Live Events')
        if obj.access_private_coaching:
            features.append('👨‍🏫 Coaching')
        if obj.access_community_forum:
            features.append('💬 Forum')
        if obj.priority_support:
            features.append('⚡ Priority Support')
        
        return format_html('<span style="font-size: 11px;">{}</span>', ' | '.join(features) if features else '—')
    features_summary.short_description = 'Key Features'
    
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10B981;">✓ Active</span>')
        return format_html('<span style="color: #EF4444;">✗ Inactive</span>')
    active_badge.short_description = 'Status'
    
    def featured_badge(self, obj):
        if obj.is_featured:
            return format_html('<span style="color: #F59E0B;">⭐ Featured</span>')
        return '—'
    featured_badge.short_description = 'Featured'


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'tier_badge', 'status_badge', 'billing_cycle', 'next_billing_date', 'auto_renew_badge', 'total_paid')
    list_filter = ('tier', 'status', 'billing_cycle', 'auto_renew', 'started_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('started_at', 'created_at', 'updated_at', 'billing_count')
    date_hierarchy = 'started_at'
    actions = ['renew_memberships', 'cancel_memberships', 'activate_memberships']
    
    fieldsets = (
        ('User & Tier', {
            'fields': ('user', 'tier', 'status')
        }),
        ('Billing', {
            'fields': ('billing_cycle', 'auto_renew', 'payment_method', 'payment_id')
        }),
        ('Dates', {
            'fields': ('started_at', 'expires_at', 'next_billing_date', 'cancelled_at')
        }),
        ('Payment Tracking', {
            'fields': ('total_paid', 'billing_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tier_badge(self, obj):
        colors = {
            'free': '#6B7280',
            'warrior': '#3B82F6',
            'ascension': '#8B5CF6',
            'vip': '#F59E0B',
        }
        color = colors.get(obj.tier.tier_level, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">{}</span>',
            color, obj.tier.name
        )
    tier_badge.short_description = 'Tier'
    
    def status_badge(self, obj):
        colors = {
            'active': '#10B981',
            'expired': '#6B7280',
            'cancelled': '#EF4444',
            'pending': '#F59E0B',
        }
        icons = {
            'active': '✓',
            'expired': '⌛',
            'cancelled': '✗',
            'pending': '⏳',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            colors.get(obj.status, '#6B7280'),
            icons.get(obj.status, '•'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def auto_renew_badge(self, obj):
        if obj.auto_renew:
            return format_html('<span style="color: #10B981;">✓ Yes</span>')
        return format_html('<span style="color: #EF4444;">✗ No</span>')
    auto_renew_badge.short_description = 'Auto Renew'
    
    def renew_memberships(self, request, queryset):
        count = 0
        for membership in queryset:
            if membership.auto_renew and membership.status == 'active':
                try:
                    membership.renew_membership()
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Error renewing {membership.user.username}: {str(e)}', 'error')
        
        self.message_user(request, f'{count} membership(s) renewed successfully.')
    renew_memberships.short_description = 'Renew selected memberships'
    
    def cancel_memberships(self, request, queryset):
        for membership in queryset:
            membership.cancel_membership()
        self.message_user(request, f'{queryset.count()} membership(s) cancelled.')
    cancel_memberships.short_description = 'Cancel selected memberships'
    
    def activate_memberships(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()} membership(s) activated.')
    activate_memberships.short_description = 'Activate selected memberships'


@admin.register(MembershipPayment)
class MembershipPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_badge', 'tier_display', 'status_badge', 'payment_method', 'created_at', 'completed_at')
    list_filter = ('status', 'payment_method', 'billing_cycle', 'created_at')
    search_fields = ('user__username', 'user__email', 'payment_id', 'transaction_id')
    readonly_fields = ('created_at', 'completed_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed', 'mark_as_failed', 'refund_payments']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'membership', 'amount', 'currency', 'billing_cycle')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'payment_id', 'transaction_id', 'status')
        }),
        ('Failure Info', {
            'fields': ('failure_reason',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def amount_badge(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #10B981;">${} {}</span>',
            obj.amount, obj.currency
        )
    amount_badge.short_description = 'Amount'
    
    def tier_display(self, obj):
        return obj.membership.tier.name
    tier_display.short_description = 'Tier'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#F59E0B',
            'completed': '#10B981',
            'failed': '#EF4444',
            'refunded': '#6B7280',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6B7280'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_completed(self, request, queryset):
        queryset.filter(status='pending').update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} payment(s) marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_failed(self, request, queryset):
        queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f'{queryset.count()} payment(s) marked as failed.')
    mark_as_failed.short_description = 'Mark as failed'
    
    def refund_payments(self, request, queryset):
        queryset.filter(status='completed').update(status='refunded')
        self.message_user(request, f'{queryset.count()} payment(s) refunded.')
    refund_payments.short_description = 'Refund payments'
