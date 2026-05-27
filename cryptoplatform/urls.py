from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from core.views_features import (
    kyc_submit_view, support_tickets_view, create_ticket_view, ticket_detail_view,
    coaching_sessions_view, portfolio_tracker_view, community_forum_view,
    membership_tiers_view, upgrade_membership_view
)
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/wallet/', views.wallet_view, name='wallet'),
    path('dashboard/trading/', views.trading_view, name='trading'),
    path('dashboard/mining/', views.mining_view, name='mining'),
    path('dashboard/p2p/', views.p2p_view, name='p2p'),
    path('dashboard/profile/', views.profile_view, name='profile'),
    path('dashboard/transactions/', views.transaction_history_view, name='transaction_history'),
    
    # Investment Pools
    path('dashboard/pools/', views.investment_pools_view, name='investment_pools'),
    path('dashboard/pools/<int:pool_id>/', views.pool_detail_view, name='pool_detail'),
    path('dashboard/pools/<int:pool_id>/invest/', views.pool_invest_view, name='pool_invest'),
    path('dashboard/pools/<int:pool_id>/withdraw/', views.pool_withdraw_view, name='pool_withdraw'),
    path('dashboard/my-investments/', views.my_investments_view, name='my_investments'),
    
    # NEW FEATURES
    # KYC
    path('dashboard/kyc/submit/', kyc_submit_view, name='kyc_submit'),
    path('dashboard/kyc/resubmit/', kyc_submit_view, name='kyc_resubmit'),
    
    # Support Tickets
    path('dashboard/support/', support_tickets_view, name='support_tickets'),
    path('dashboard/support/create/', create_ticket_view, name='create_ticket'),
    path('dashboard/support/<int:ticket_id>/', ticket_detail_view, name='ticket_detail'),
    
    # Coaching
    path('dashboard/coaching/', coaching_sessions_view, name='coaching_sessions'),
    
    # Portfolio Tracker
    path('dashboard/portfolio/', portfolio_tracker_view, name='portfolio_tracker'),
    
    # Community Forum
    path('dashboard/community/', community_forum_view, name='community_forum'),
    
    # Membership
    path('dashboard/membership/', membership_tiers_view, name='membership_tiers'),
    path('dashboard/membership/upgrade/<int:tier_id>/', upgrade_membership_view, name='upgrade_membership'),
    
    # Asset Test Page
    path('dashboard/asset-test/', TemplateView.as_view(template_name='dashboard/asset_test.html'), name='asset_test'),
    
    # API
    path('api/prices/', views.api_prices, name='api_prices'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
