import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_reset_password_email(to_email: str, reset_link: str):
    """
    发送重置密码邮件
    """
    if not settings.SMTP_USER or settings.SMTP_USER == "your_email@qq.com":
        logger.warning("⚠️ 邮件发送失败：未配置 SMTP_USER")
        return False, "未配置发件人邮箱"
    
    msg = MIMEMultipart()
    # 格式化发件人： "RSOD Platform <xxx@qq.com>"
    msg['From'] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    msg['To'] = to_email
    msg['Subject'] = f"【{settings.SMTP_FROM_NAME}】密码重置请求"

    # 邮件正文 (HTML 格式)
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #409eff; text-align: center;">密码重置请求</h2>
                <p>您好，</p>
                <p>我们收到了您重置密码的请求。请点击下方按钮重置您的密码（链接在15分钟内有效）：</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" style="padding: 12px 24px; background-color: #409eff; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">点击重置密码</a>
                </div>
                <p style="font-size: 13px; color: #666;">如果按钮无法点击，请复制下方链接并在浏览器中打开：</p>
                <p style="font-size: 13px; color: #409eff; word-break: break-all;">{reset_link}</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p>如果您并未请求重置密码，请忽略此邮件。</p>
                <br>
                <p>此致</p>
                <p><b>{settings.SMTP_FROM_NAME} 团队</b></p>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    try:
        logger.info(f"正在尝试发送邮件到 {to_email}，服务器: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        
        if settings.SMTP_PORT == 465:
            # SSL 方式
            server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15)
        else:
            # TLS 方式 (587 等)
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"邮件成功发送到 {to_email}")
        return True, "邮件发送成功"
    except smtplib.SMTPAuthenticationError:
        error_msg = "邮件服务认证失败，请检查 SMTP_PASSWORD (授权码) 是否正确"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"邮件发送失败: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
