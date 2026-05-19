"""
Email utility functions for sending OTP and notification emails
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import OTPToken


def send_otp_email(user, purpose, validity_minutes=10, **metadata):
    """
    Generate and send OTP token to user's email
    
    Args:
        user: User object
        purpose: Purpose of OTP (from OTPToken.PURPOSE_CHOICES)
        validity_minutes: How long the OTP is valid (default: 10 minutes)
        **metadata: Additional context to store with the OTP
    
    Returns:
        OTPToken object or None if failed
    """
    try:
        # Create OTP token
        otp = OTPToken.create_otp(user, purpose, validity_minutes, **metadata)
        
        # Email subject based on purpose
        subjects = {
            'email_verification': 'Verify Your Email - CoachJVTech',
            'password_reset': 'Password Reset Code - CoachJVTech',
            'login_2fa': 'Your Login Verification Code - CoachJVTech',
            'withdrawal_confirm': 'Confirm Your Withdrawal - CoachJVTech',
            'account_change': 'Verify Account Changes - CoachJVTech',
        }
        
        subject = subjects.get(purpose, 'Verification Code - CoachJVTech')
        
        # Render email template
        context = {
            'user': user,
            'otp_token': otp.token,
            'purpose': dict(OTPToken.PURPOSE_CHOICES).get(purpose),
            'validity_minutes': validity_minutes,
            'metadata': metadata,
        }
        
        # Use HTML template if exists, otherwise plain text
        try:
            html_message = render_to_string('emails/otp_email.html', context)
            plain_message = strip_tags(html_message)
        except:
            # Fallback to plain text
            plain_message = f"""
Hello {user.first_name or user.username},

Your verification code is: {otp.token}

This code is valid for {validity_minutes} minutes.

Purpose: {dict(OTPToken.PURPOSE_CHOICES).get(purpose)}

If you did not request this code, please ignore this email or contact support.

Best regards,
CoachJVTech Team
            """
            html_message = None
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return otp
    
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return None


def verify_otp(user, token, purpose):
    """
    Verify an OTP token
    
    Args:
        user: User object
        token: The OTP code to verify
        purpose: Purpose of the OTP
    
    Returns:
        tuple: (success: bool, otp: OTPToken or None, error_message: str or None)
    """
    try:
        # Find the most recent valid OTP for this user and purpose
        otp = OTPToken.objects.filter(
            user=user,
            purpose=purpose,
            is_valid=True,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp:
            return False, None, "No valid OTP found. Please request a new code."
        
        if otp.is_expired():
            otp.is_valid = False
            otp.save()
            return False, otp, "OTP has expired. Please request a new code."
        
        if otp.attempts >= otp.max_attempts:
            otp.is_valid = False
            otp.save()
            return False, otp, "Maximum verification attempts exceeded. Please request a new code."
        
        # Verify the token
        if otp.verify(token):
            return True, otp, None
        else:
            remaining = otp.max_attempts - otp.attempts
            if remaining > 0:
                return False, otp, f"Invalid code. {remaining} attempts remaining."
            else:
                return False, otp, "Invalid code. Maximum attempts exceeded."
    
    except Exception as e:
        print(f"Error verifying OTP: {e}")
        return False, None, "An error occurred during verification."


def send_notification_email(user, subject, template_name, context):
    """
    Send a general notification email
    
    Args:
        user: User object
        subject: Email subject
        template_name: Template file name (without path)
        context: Context dictionary for template
    """
    try:
        context['user'] = user
        
        try:
            html_message = render_to_string(f'emails/{template_name}', context)
            plain_message = strip_tags(html_message)
        except:
            # Fallback
            plain_message = context.get('message', 'You have a new notification from CoachJVTech.')
            html_message = None
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending notification email: {e}")
        return False


# Specific notification helpers

def send_deposit_approved_email(user, deposit):
    """Send email when deposit is approved"""
    return send_notification_email(
        user=user,
        subject='Deposit Approved - CoachJVTech',
        template_name='deposit_approved.html',
        context={'deposit': deposit}
    )


def send_withdrawal_completed_email(user, withdrawal):
    """Send email when withdrawal is completed"""
    return send_notification_email(
        user=user,
        subject='Withdrawal Completed - CoachJVTech',
        template_name='withdrawal_completed.html',
        context={'withdrawal': withdrawal}
    )


def send_kyc_status_email(user, kyc):
    """Send email when KYC status changes"""
    status_subjects = {
        'approved': 'KYC Verification Approved - CoachJVTech',
        'rejected': 'KYC Verification Update - CoachJVTech',
    }
    return send_notification_email(
        user=user,
        subject=status_subjects.get(kyc.status, 'KYC Status Update - CoachJVTech'),
        template_name='kyc_status.html',
        context={'kyc': kyc}
    )


def send_welcome_email(user):
    """Send welcome email to new users"""
    return send_notification_email(
        user=user,
        subject='Welcome to CoachJVTech - Your Crypto Trading Platform',
        template_name='welcome.html',
        context={}
    )
