"""
Stripe Payment Integration
Ödeme ve abonelik yönetimi
"""

from flask import Blueprint, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
import stripe
import os
from datetime import datetime, timedelta
from models import db, User, SubscriptionPlan

payment_bp = Blueprint('payment', __name__)

# Stripe API keys
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')


def init_payment(app):
    """Payment blueprint'ini Flask app'e bağla"""
    app.register_blueprint(payment_bp)


@payment_bp.route('/pricing')
def pricing():
    """Fiyatlandırma sayfası"""
    from flask import render_template
    plans = [
        {
            'name': 'Free',
            'price': 0,
            'price_display': 'Ücretsiz',
            'features': [
                '5 analiz/gün',
                'Temel portföy analizi',
                'Risk skoru hesaplama',
                'Basit kaldıraç analizi'
            ],
            'popular': False,
            'plan_id': 'free'
        },
        {
            'name': 'Starter',
            'price': 9.99,
            'price_display': '$9.99/ay',
            'features': [
                '50 analiz/gün',
                'Gelişmiş portföy analizi',
                'Kaldıraç analizi (tüm özellikler)',
                'Pozisyon boyutu hesaplama',
                'Risk/Reward analizi',
                'Email desteği',
                'Reklam yok'
            ],
            'popular': True,
            'plan_id': 'starter'
        },
        {
            'name': 'Pro',
            'price': 29.99,
            'price_display': '$29.99/ay',
            'features': [
                'Sınırsız analiz',
                'Tüm özellikler',
                'API erişimi',
                'Öncelikli destek',
                'PDF/CSV export',
                'Gelişmiş raporlama',
                'Reklam yok'
            ],
            'popular': False,
            'plan_id': 'pro'
        }
    ]
    return render_template('pricing.html', plans=plans)


@payment_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Stripe Checkout session oluştur"""
    try:
        plan = request.json.get('plan', 'starter')
        
        # Plan fiyatlarını belirle (Stripe Price ID'leri)
        price_map = {
            'starter': {
                'price_id': os.getenv('STRIPE_PRICE_STARTER', 'price_starter'),  # Stripe'da oluşturulacak
                'amount': 999  # $9.99 in cents
            },
            'pro': {
                'price_id': os.getenv('STRIPE_PRICE_PRO', 'price_pro'),
                'amount': 2999  # $29.99 in cents
            }
        }
        
        if plan not in price_map:
            return jsonify({'error': 'Geçersiz plan'}), 400
        
        # Stripe Customer oluştur veya mevcut olanı kullan
        customer_id = current_user.stripe_customer_id
        
        if not customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name or current_user.email,
                metadata={'user_id': str(current_user.id)}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
            customer_id = customer.id
        
        # Checkout session oluştur
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{plan.capitalize()} Plan',
                        'description': f'Kripto Portföy Risk Analiz - {plan.capitalize()} Plan'
                    },
                    'unit_amount': price_map[plan]['amount'],
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'payment/cancel',
            metadata={
                'user_id': str(current_user.id),
                'plan': plan
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        })
        
    except Exception as e:
        print(f"Checkout session error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/success')
@login_required
def payment_success():
    """Ödeme başarılı sayfası"""
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.customer == current_user.stripe_customer_id:
                # Webhook henüz gelmemiş olabilir, manuel kontrol
                flash('Ödeme başarılı! Aboneliğiniz aktif ediliyor...', 'success')
        except Exception as e:
            print(f"Session retrieve error: {str(e)}")
    
    return redirect(url_for('auth.profile'))


@payment_bp.route('/cancel')
@login_required
def payment_cancel():
    """Ödeme iptal sayfası"""
    flash('Ödeme iptal edildi. İstediğiniz zaman tekrar deneyebilirsiniz.', 'info')
    return redirect(url_for('auth.profile'))


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Stripe webhook handler"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        print("Invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        print("Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Event handling
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify({'status': 'success'}), 200


def handle_checkout_completed(session):
    """Checkout tamamlandığında aboneliği aktif et"""
    try:
        user_id = session['metadata'].get('user_id')
        plan = session['metadata'].get('plan', 'starter')
        
        user = User.query.get(int(user_id))
        if not user:
            print(f"User not found: {user_id}")
            return
        
        # Subscription bilgilerini al
        subscription_id = session.get('subscription')
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Plan güncelle
            if plan == 'starter':
                user.subscription_plan = SubscriptionPlan.STARTER
            elif plan == 'pro':
                user.subscription_plan = SubscriptionPlan.PRO
            
            user.stripe_subscription_id = subscription_id
            user.subscription_started = datetime.utcnow()
            user.subscription_ends = datetime.fromtimestamp(subscription.current_period_end)
            
            db.session.commit()
            print(f"Subscription activated for user {user.email}: {plan}")
    except Exception as e:
        print(f"Error handling checkout completed: {str(e)}")


def handle_subscription_updated(subscription):
    """Abonelik güncellendiğinde"""
    try:
        user = User.query.filter_by(stripe_subscription_id=subscription.id).first()
        if not user:
            return
        
        # Subscription durumunu kontrol et
        if subscription.status == 'active':
            user.subscription_ends = datetime.fromtimestamp(subscription.current_period_end)
        elif subscription.status == 'past_due' or subscription.status == 'unpaid':
            # Abonelik sorunlu, kullanıcıyı bilgilendir
            pass
        
        db.session.commit()
    except Exception as e:
        print(f"Error handling subscription updated: {str(e)}")


def handle_subscription_deleted(subscription):
    """Abonelik iptal edildiğinde"""
    try:
        user = User.query.filter_by(stripe_subscription_id=subscription.id).first()
        if not user:
            return
        
        # Free plan'a düşür
        user.subscription_plan = SubscriptionPlan.FREE
        user.stripe_subscription_id = None
        user.subscription_ends = None
        
        db.session.commit()
        print(f"Subscription cancelled for user {user.email}")
    except Exception as e:
        print(f"Error handling subscription deleted: {str(e)}")


def handle_payment_succeeded(invoice):
    """Ödeme başarılı olduğunda"""
    try:
        subscription_id = invoice.get('subscription')
        if subscription_id:
            user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
            if user:
                # Abonelik süresini uzat
                subscription = stripe.Subscription.retrieve(subscription_id)
                user.subscription_ends = datetime.fromtimestamp(subscription.current_period_end)
                db.session.commit()
    except Exception as e:
        print(f"Error handling payment succeeded: {str(e)}")


def handle_payment_failed(invoice):
    """Ödeme başarısız olduğunda"""
    try:
        subscription_id = invoice.get('subscription')
        if subscription_id:
            user = User.query.filter_by(stripe_subscription_id=subscription_id).first()
            if user:
                # Kullanıcıyı bilgilendir (email gönderilebilir)
                print(f"Payment failed for user {user.email}")
    except Exception as e:
        print(f"Error handling payment failed: {str(e)}")

