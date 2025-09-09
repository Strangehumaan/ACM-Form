import qrcode
from PIL import Image
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import io
import base64

class ACMBadgeGenerator:
    def __init__(self):
        # Professional color scheme matching your logo (used for email)
        self.colors = {
            'primary_dark': '#1a2332',
            'secondary_dark': '#0f1419',
            'accent_blue': '#4da6ff',
            'text_primary': '#ffffff',
            'text_secondary': '#a8b2c1',
        }
        
        # Email configuration
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'email': 'acm.mpstme.shirpur@gmail.com',
            'password': 'ppyi qwen mghc nxgf'  # Use App Password
        }

    def create_html_badge(self, name, member_id):
        """
        Generates the HTML content for a membership badge.
        This function reads from 'membership_badge.html', populates it with member data,
        and returns the final HTML as a string.
        """
        try:
            # --- 1. Get current and valid till dates ---
            current_date = datetime.now()
            valid_from = current_date.strftime("%b %Y")
            
            # Calculate validity for 11 months from the current month
            valid_till_month = (current_date.month + 10) % 12 + 1
            valid_till_year = current_date.year + (current_date.month + 10) // 12
            valid_till = datetime(valid_till_year, valid_till_month, 1).strftime("%b %Y")

            # --- 2. Generate the QR code as a Base64 image for embedding ---
            qr = qrcode.QRCode(
                version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10, border=4,
            )
            qr.add_data(member_id)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save the QR code to a bytes buffer and encode it
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_base64_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            qr_img_html = f'<img src="data:image/png;base64,{qr_base64_data}" alt="QR Code" style="width: 100%; height: 100%; object-fit: contain;">'

            # --- 3. Read the HTML template and fill placeholders ---
            with open("templates/membership_badge.html", "r") as file:
                html_template = file.read()
            
            final_html = html_template.replace("{{name}}", name)
            final_html = final_html.replace("{{member_id}}", member_id)
            final_html = final_html.replace("{{valid_from}}", valid_from)
            final_html = final_html.replace("{{valid_till}}", valid_till)
            final_html = final_html.replace("{{qr}}", qr_img_html)
            
            return final_html

        except FileNotFoundError:
            print("❌ Error: The 'membership_badge.html' template file was not found.")
            return None
        except Exception as e:
            print(f"❌ An error occurred while creating the HTML badge: {e}")
            return None

    def create_professional_email_template(self, name, member_id, join_date=None):
        """Create a sleek HTML email template"""
        if join_date is None:
            join_date = datetime.now().strftime("%B %Y")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ACM Membership Confirmation</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%); color: #ffffff;">
            <div style="max-width: 600px; margin: 0 auto; background: #1a2332; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <div style="background: linear-gradient(135deg, #4da6ff 0%, #1a2332 100%); padding: 40px 30px; text-align: center; position: relative;">
                    <div style="background: rgba(255,255,255,0.1); display: inline-block; padding: 15px; border-radius: 50%; margin-bottom: 20px;">
                        <img src="cid:acm_logo" alt="ACM MPSTME Shirpur" style="width: 80px; height: 80px; border-radius: 50%;">
                    </div>
                    <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                        Welcome to ACM MPSTME
                    </h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; color: #e6f3ff; opacity: 0.9;">
                        Student Chapter - Shirpur
                    </p>
                </div>
                <div style="padding: 40px 30px;">
                    <div style="text-align: center; margin-bottom: 40px;">
                        <h2 style="color: #4da6ff; font-size: 24px; margin: 0 0 20px 0; font-weight: 600;">
                            🎉 Membership Confirmed!
                        </h2>
                        <p style="font-size: 16px; line-height: 1.6; color: #a8b2c1; margin: 0;">
                            Dear <strong style="color: #ffffff;">{name}</strong>, we're thrilled to welcome you as an official member of our vibrant computing community.
                        </p>
                    </div>
                    <div style="background: linear-gradient(135deg, #0f1419 0%, #1a2332 100%); border: 2px solid #4da6ff; border-radius: 15px; padding: 30px; margin: 30px 0; position: relative; overflow: hidden;">
                        <h3 style="color: #4da6ff; margin: 0 0 20px 0; font-size: 20px; font-weight: 600;">
                            📋 Membership Details
                        </h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 12px 0; border-bottom: 1px solid #2a3441; color: #a8b2c1; font-weight: 500;">Member Name:</td>
                                <td style="padding: 12px 0; border-bottom: 1px solid #2a3441; color: #ffffff; font-weight: 600; text-align: right;">{name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 0; border-bottom: 1px solid #2a3441; color: #a8b2c1; font-weight: 500;">Member ID:</td>
                                <td style="padding: 12px 0; border-bottom: 1px solid #2a3441; color: #4da6ff; font-weight: 600; text-align: right; font-family: 'Courier New', monospace;">{member_id}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 0; color: #a8b2c1; font-weight: 500;">Join Date:</td>
                                <td style="padding: 12px 0; color: #ffffff; font-weight: 600; text-align: right;">{join_date}</td>
                            </tr>
                        </table>
                    </div>
                    <div style="background: linear-gradient(135deg, #4da6ff 0%, #1a2332 100%); border-radius: 15px; padding: 25px; text-align: center; margin: 30px 0;">
                        <h3 style="margin: 0 0 15px 0; font-size: 20px; color: #ffffff; font-weight: 600;">
                            🎫 Your Digital Badge
                        </h3>
                        <p style="margin: 0; color: #e6f3ff; line-height: 1.6;">
                            Your personalized HTML membership badge is attached. Download and open it in a browser to view and save it.
                        </p>
                    </div>
                </div>
                <div style="background: #0f1419; padding: 30px; text-align: center; border-top: 3px solid #4da6ff;">
                    <p style="margin: 20px 0 0 0; color: #666; font-size: 12px;">
                        © {datetime.now().year} ACM MPSTME Shirpur Student Chapter. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    def send_professional_email(self, recipient_email, name, member_id, badge_html_content):
        """
        Sends the professional email with the generated HTML badge as an attachment.
        """
        try:
            msg = MIMEMultipart('related')
            msg['From'] = self.smtp_config['email']
            msg['To'] = recipient_email
            msg['Subject'] = f"🎉 Welcome to ACM MPSTME Shirpur - Your Membership Badge | ID: {member_id}"
            
            # Attach the beautiful HTML email body
            html_body = self.create_professional_email_template(name, member_id)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Attach the ACM logo for embedding in the email template
            try:
                with open("acm.png", 'rb') as img_file:
                    img = MIMEImage(img_file.read())
                    img.add_header('Content-ID', '<acm_logo>')
                    msg.attach(img)
            except FileNotFoundError:
                print("⚠️  ACM logo (acm.png) not found for email template. It will be missing from the email.")
            
            # Attach the generated HTML badge as a file
            badge_attachment = MIMEBase('application', 'octet-stream')
            badge_attachment.set_payload(badge_html_content.encode('utf-8'))
            encoders.encode_base64(badge_attachment)
            badge_attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="ACM_Membership_Badge_{member_id}.html"'
            )
            msg.attach(badge_attachment)
            
            # Send the email
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['email'], self.smtp_config['password'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

# -----------------------------------------------------------------------------
# REUSABLE FUNCTION TO BE CALLED FROM OTHER FILES
# -----------------------------------------------------------------------------
def generate_and_send_badge(name: str, member_id: str, recipient_email: str) -> bool:
    """
    Generates a member badge and sends it via email.

    This function orchestrates the entire process:
    1. Instantiates the badge generator.
    2. Creates the HTML badge content.
    3. Sends the badge as an attachment in a professional email.

    Args:
        name (str): The full name of the member.
        member_id (str): The unique ID for the member.
        recipient_email (str): The email address to send the badge to.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    print(f"\n▶️  Starting process for {name} ({member_id})...")
    generator = ACMBadgeGenerator()

    # Step 1: Generate HTML badge content
    print("🔄 Generating HTML badge...")
    badge_html = generator.create_html_badge(name, member_id)
    
    if badge_html is None:
        print("❌ Failed to create HTML badge. Aborting.")
        return False
    
    print("✅ HTML badge content generated successfully.")
    
    # Step 2: Send email with the HTML badge attached
    print(f"📤 Sending professional email to {recipient_email}...")
    success = generator.send_professional_email(recipient_email, name, member_id, badge_html)
    
    if success:
        print(f"✅ Email sent successfully to {recipient_email}")
        print(f"📎 Badge attached as: ACM_Membership_Badge_{member_id}.html")
    else:
        print("❌ Failed to send email. Please check the console for errors.")
        
    return success