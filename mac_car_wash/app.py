from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import re
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mac-mobile-car-wash-2025-secure-key')

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Mail configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_USERNAME'),
    MAIL_USE_SSL=False,
    MAIL_DEBUG=False
)

mail = Mail(app)

# Business Configuration
BUSINESS_CONFIG = {
    'name': 'MAC Mobile Car Wash',
    'phone': '+971 5011 34356',
    'email': os.getenv('BUSINESS_EMAIL', 'info@macmobilecarwash.com'),
    'location': 'Dubai, UAE',
    'experience': '10+ Years',
    'customers': '15,000+',
    'rating': '4.9/5',
    'coverage': 'All UAE Emirates'
}

# SIMPLE Service Configuration - Flat structure for easy access
SERVICES_CONFIG = {
    'premium_wash': {
        'silver': {
            'name': 'Silver Shine',
            'price': 65,
            'duration': '45 mins',
            'type': 'Premium Wash',
            'features': [
                'Professional exterior wash',
                'Premium foam treatment',
                'Tire cleaning & shine',
                'Window cleaning',
                'Basic interior vacuum'
            ]
        },
        'gold': {
            'name': 'Gold Wash',
            'price': 75,
            'duration': '60 mins',
            'type': 'Premium Wash',
            'features': [
                'Complete exterior and interior cleaning',
                'Dashboard conditioning',
                'Tire cleaning & shine',
                'Window cleaning inside & out',
                'Vacuum cleaning'
            ]
        },
        'platinum': {
            'name': 'Platinum Elite',
            'price': 135,
            'duration': '90 mins',
            'type': 'Elite Wash',
            'features': [
                'Complete premium service',
                'Ceramic coating application',
                'Paint protection',
                'Headlight restoration',
                'Undercarriage wash',
                'Premium wax finish'
            ]
        }
    },
    'monthly_packages': {
        'green-monthly': {
            'name': 'Green Package',
            'price': 180,
            'duration': '4 washes',
            'type': 'Monthly Package',
            'savings': 40,
            'features': [
                'Regular monthly car wash service',
                '4 washes per month',
                'Basic exterior cleaning',
                'Interior vacuum'
            ]
        },
        'blue-monthly': {
            'name': 'Blue Package',
            'price': 240,
            'duration': '4 washes',
            'type': 'Monthly Package',
            'savings': 60,
            'features': [
                'Premium monthly car wash with detailing',
                '4 washes per month',
                'Complete exterior & interior',
                'Dashboard conditioning',
                'Tire shine'
            ]
        },
        'premium-monthly': {
            'name': 'Premium Monthly',
            'price': 320,
            'duration': '4 washes',
            'type': 'Monthly Package',
            'savings': 60,
            'features': [
                'Premium monthly service',
                '4 washes per month',
                'Complete detailing',
                'Leather treatment',
                'Engine bay cleaning'
            ]
        }
    },
    'yearly_packages': {
        'eco-annual': {
            'name': 'Eco Annual Plan',
            'price': 2200,
            'savings': 920,
            'duration': '48 washes',
            'type': 'Annual Package',
            'features': [
                '48 washes per year',
                '30% discount',
                'Silver Shine service',
                'Priority booking'
            ]
        },
        'premium-annual': {
            'name': 'Premium Annual Plan',
            'price': 3200,
            'savings': 1360,
            'duration': '48 washes',
            'type': 'Annual Package',
            'features': [
                '48 washes per year',
                '30% discount',
                'Gold Luxury service',
                'Priority booking',
                'Free upgrades'
            ]
        }
    }
}

def init_files():
    """Initialize text files"""
    if not os.path.exists('bookings.txt'):
        with open('bookings.txt', 'w', encoding='utf-8') as f:
            f.write("=== MAC MOBILE CAR WASH BOOKINGS ===\n\n")

def save_booking_to_file(booking_data):
    """Save booking to text file"""
    try:
        with open('bookings.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"BOOKING ID: {booking_data['booking_id']}\n")
            f.write(f"DATE: {booking_data['timestamp']}\n")
            f.write(f"CUSTOMER: {booking_data['customer']['name']}\n")
            f.write(f"PHONE: {booking_data['customer']['phone']}\n")
            f.write(f"EMAIL: {booking_data['customer']['email']}\n")
            f.write(f"SERVICE: {booking_data['service']['name']}\n")
            f.write(f"PRICE: AED {booking_data['service']['price']}\n")
            f.write(f"MESSAGE: {booking_data.get('message', 'N/A')}\n")
            f.write(f"EMAIL SENT: {booking_data.get('email_sent', 'No')}\n")
            f.write("="*60 + "\n")
        return True
    except Exception as e:
        print(f"Error saving booking: {e}")
        return False

def get_service_details(service_type):
    """Get service details with simple lookup"""
    print(f"Looking for service: {service_type}")
    
    # Search through all categories
    for category_name, category_services in SERVICES_CONFIG.items():
        if service_type in category_services:
            service = category_services[service_type]
            print(f"Found service: {service['name']}")
            return service
    
    # Fallback
    print(f"Service not found, using fallback for: {service_type}")
    return {
        'name': f'{service_type.replace("-", " ").title()}',
        'price': 75,
        'type': 'Custom Service',
        'duration': '60 mins',
        'features': ['Professional car wash service']
    }

def send_booking_emails(name, phone, email, service_info, message, booking_id):
    """Send booking confirmation emails"""
    try:
        print(f"Sending emails for booking {booking_id}")
        
        # Business email
        business_subject = f'New Booking #{booking_id} - {name}'
        business_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #dc3545;">🚗 New Booking Alert!</h2>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>Booking Details</h3>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Service:</strong> {service_info['name']}</p>
                <p><strong>Price:</strong> AED {service_info['price']}</p>
                <p><strong>Duration:</strong> {service_info.get('duration', 'N/A')}</p>
            </div>
            <div style="background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>Customer Information</h3>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Phone:</strong> <a href="tel:{phone}">{phone}</a></p>
                <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                {f'<p><strong>Message:</strong> {message}</p>' if message else ''}
            </div>
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; text-align: center;">
                <h3 style="color: #856404;">⚠️ Contact customer within 1 hour!</h3>
                <a href="tel:{phone}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px;">📞 Call Now</a>
            </div>
        </div>
        """
        
        business_msg = Message(
            subject=business_subject,
            recipients=[BUSINESS_CONFIG['email']],
            html=business_html
        )
        
        # Customer email
        customer_subject = f'Booking Confirmed #{booking_id} - {BUSINESS_CONFIG["name"]}'
        customer_html = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #28a745;">✅ Booking Confirmed!</h2>
            <p>Dear {name},</p>
            <p>Thank you for choosing {BUSINESS_CONFIG['name']}!</p>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>Your Booking Details</h3>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Service:</strong> {service_info['name']}</p>
                <p><strong>Price:</strong> AED {service_info['price']}</p>
                <p><strong>Duration:</strong> {service_info.get('duration', 'N/A')}</p>
            </div>
            
            <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3>What's Next?</h3>
                <p>✅ Our team will contact you within 1 hour</p>
                <p>✅ We'll schedule a convenient time for your service</p>
                <p>✅ Our professionals will arrive at your location</p>
                <p>✅ Payment is made after service completion</p>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; text-align: center;">
                <h3>Need Help?</h3>
                <p><strong>📞 {BUSINESS_CONFIG['phone']}</strong></p>
                <p>Available 7 days a week, 8 AM - 8 PM</p>
            </div>
        </div>
        """
        
        customer_msg = Message(
            subject=customer_subject,
            recipients=[email],
            html=customer_html
        )
        
        # Send emails
        mail.send(business_msg)
        mail.send(customer_msg)
        
        print("✅ Emails sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

# Initialize files
init_files()

@app.route('/')
def home():
    """Home page"""
    try:
        print("Loading home page...")
        return render_template('index.html', 
                             business=BUSINESS_CONFIG, 
                             services=SERVICES_CONFIG)
    except Exception as e:
        print(f"Home page error: {e}")
        return f"<h1>MAC Mobile Car Wash</h1><p>Error loading page: {e}</p><p>Please check if templates/index.html exists</p>"

@app.route('/api/contact', methods=['POST'])
@limiter.limit("10 per minute")
def handle_contact():
    """Handle contact form submission"""
    try:
        print("=== New Booking Request ===")
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400
        
        # Get form data
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        service_type = data.get('service', '').strip()
        message = data.get('message', '').strip()
        
        print(f"Booking details: {name}, {phone}, {email}, {service_type}")
        
        # Basic validation
        if not name or len(name) < 2:
            return jsonify({'success': False, 'message': 'Please provide a valid name'}), 400
        
        if not phone:
            return jsonify({'success': False, 'message': 'Please provide a phone number'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': 'Please provide a valid email'}), 400
        
        if not service_type:
            return jsonify({'success': False, 'message': 'Please select a service'}), 400
        
        # Get service details
        service_info = get_service_details(service_type)
        
        # Generate booking ID
        booking_id = f"MAC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare booking data
        booking_data = {
            "booking_id": booking_id,
            "timestamp": datetime.now().isoformat(),
            "customer": {
                "name": name,
                "phone": phone,
                "email": email
            },
            "service": {
                "type": service_type,
                "name": service_info['name'],
                "price": service_info['price'],
            },
            "message": message,
            "status": "pending",
            "email_sent": False
        }
        
        # Save to file
        file_saved = save_booking_to_file(booking_data)
        
        # Send emails
        email_sent = False
        try:
            email_sent = send_booking_emails(name, phone, email, service_info, message, booking_id)
            booking_data["email_sent"] = email_sent
        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
        
        # Also save to JSON backup
        try:
            with open('bookings.json', 'a') as f:
                f.write(json.dumps(booking_data) + '\n')
        except:
            pass
        
        print(f"✅ Booking completed: {booking_id}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you! Your booking has been confirmed. We will contact you within 1 hour.',
            'booking_id': booking_id,
            'service': service_info['name'],
            'price': f"AED {service_info['price']}",
            'email_sent': email_sent,
            'file_saved': file_saved
        })
        
    except Exception as e:
        print(f"❌ Booking error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'Something went wrong. Please call us directly.',
            'error': str(e) if app.debug else None
        }), 500

@app.route('/test-email')
def test_email():
    """Test email functionality"""
    try:
        print("Testing email...")
        msg = Message(
            subject='Test Email - MAC Car Wash',
            recipients=[BUSINESS_CONFIG['email']],
            html=f"""
            <h2>✅ Email Test Successful!</h2>
            <p>Your email configuration is working.</p>
            <p><strong>Test Time:</strong> {datetime.now()}</p>
            <p><strong>From:</strong> {BUSINESS_CONFIG['name']}</p>
            """
        )
        mail.send(msg)
        return jsonify({
            'success': True,
            'message': 'Test email sent successfully!',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Test email failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/admin/bookings')
def admin_bookings():
    """View recent bookings"""
    try:
        bookings = []
        if os.path.exists('bookings.txt'):
            with open('bookings.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                
        return jsonify({
            'success': True,
            'message': 'Bookings loaded from text file',
            'file_exists': os.path.exists('bookings.txt'),
            'file_size': os.path.getsize('bookings.txt') if os.path.exists('bookings.txt') else 0,
            'content_preview': content[-1000:] if os.path.exists('bookings.txt') else 'No bookings file found'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting MAC Mobile Car Wash Application...")
    print(f"📧 Email: {app.config.get('MAIL_USERNAME', 'Not configured')}")
    print(f"🏢 Business: {BUSINESS_CONFIG['email']}")
    print(f"📋 Services: {sum(len(cat) for cat in SERVICES_CONFIG.values())} services loaded")
    print("=" * 60)
    print("🌐 Available routes:")
    print("   • Main site: http://localhost:5000")
    print("   • Test email: http://localhost:5000/test-email")
    print("   • Admin: http://localhost:5000/admin/bookings")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
