"""Gerenciamento de alertas por email."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class AlertManager:
    """Gerencia alertas por email."""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.email_to = os.getenv("ALERT_EMAIL_TO", "")
        self.enabled = os.getenv("ALERT_ENABLED", "false").lower() == "true"

        if self.enabled and (not self.smtp_user or not self.smtp_password or not self.email_to):
            print("⚠️ Email configurado mas credenciais incompletas")
            self.enabled = False

    def send(self, message: str, subject: str = "🚨 Camera Guardian Alert") -> bool:
        """Envia alerta por email."""
        if not self.enabled:
            print(f"📧 [Email desativado] {message}")
            return True

        try:
            # Monta email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = self.email_to

            # Conteúdo HTML
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; padding: 20px; border-radius: 8px; border-left: 4px solid #ff6b6b;">
                  <h2 style="color: #ff6b6b; margin-top: 0;">🚨 Camera Guardian Alert</h2>
                  <p><strong>{message}</strong></p>
                  <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                  <p style="font-size: 12px; color: #999;">
                    <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    <strong>Location:</strong> Your Webcam
                  </p>
                </div>
              </body>
            </html>
            """

            part = MIMEText(html, "html")
            msg.attach(part)

            # Envia
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, self.email_to, msg.as_string())

            print(f"📧 Email enviado para {self.email_to}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            return False