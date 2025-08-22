import logging
import os
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from domain.interfaces.email_service import EmailServiceInterface


class EmailService(EmailServiceInterface):
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp-relay.brevo.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL')
        self.from_name = os.getenv('FROM_NAME', 'Your App')
        self.frontend_url = os.getenv('FRONTEND_URL')
        self.logger = logging.getLogger(__name__)
        
        if not all([self.smtp_username, self.smtp_password, self.from_email]):
            raise ValueError("Missing required SMTP configuration")

    async def send_email(self, to: str, subject: str, html_body: str) -> bool:
        """Send email asynchronously using Brevo SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))

            context = ssl.create_default_context()

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_username,
                password=self.smtp_password,
                tls_context=context
            )

            self.logger.info(f"✅ Email sent to: {to}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to send email: {e}")
            return False

    async def send_verification_email(self, username: str, email: str, token: str) -> bool:
        link = f"{self.frontend_url}/auth/verify-email?token={token}"
        subject = "Verify your email"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; 
                    padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2>👋 Welcome, {username}!</h2>
            <p>Thanks for signing up. Please verify your email:</p>
            <a href="{link}" style="padding: 12px 24px; background: #4CAF50; 
               color: white; text-decoration: none; border-radius: 5px;">Verify Email</a>
            <p>{link}</p>
        </div>"""
        return await self.send_email(email, subject, html_body)

    async def send_password_reset_email(self, username: str, email: str, token: str) -> bool:
        link = f"{self.frontend_url}/auth/reset-password?token={token}"
        subject = "Reset your password"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; 
                    padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2>🔒 Password Reset</h2>
            <p>Hello {username}, we received a request to reset your password.</p>
            <a href="{link}" style="padding: 12px 24px; background: #f44336; 
               color: white; text-decoration: none; border-radius: 5px;">Reset Password</a>
            <p>{link}</p>
        </div>"""
        return await self.send_email(email, subject, html_body)
