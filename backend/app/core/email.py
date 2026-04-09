#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""邮件发送服务"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from app.core.config import settings


class EmailService:
    """邮件服务"""
    
    def __init__(self):
        self.host = settings.MAIL_HOST
        self.port = settings.MAIL_PORT
        self.username = settings.MAIL_USERNAME
        self.password = settings.MAIL_PASSWORD
        self.from_email = settings.MAIL_FROM
        self.from_name = settings.MAIL_FROM_NAME
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        is_html: bool = True
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            is_html: 是否为HTML格式
            
        Returns:
            bool: 是否发送成功
        """
        try:
            # 创建邮件（使用简单的MIMEText）
            if is_html:
                message = MIMEText(content, 'html', 'utf-8')
            else:
                message = MIMEText(content, 'plain', 'utf-8')
            
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = subject
            
            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=True,
                sender=self.from_email,
                recipients=[to_email],
                # 解决中文主机名问题
                local_hostname="localhost"
            )
            
            return True
            
        except Exception as e:
            print(f"Email send error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_verification_code(self, to_email: str, code: str, purpose: str = "注册") -> bool:
        """
        发送验证码邮件
        
        Args:
            to_email: 收件人邮箱
            code: 验证码
            purpose: 用途（注册、重置密码等）
            
        Returns:
            bool: 是否发送成功
        """
        # 根据用途设置不同的主题和描述
        if purpose == "重置密码":
            subject = "【健康筛查】重置密码验证码"
            description = "您正在进行密码重置操作，请使用以下验证码完成验证："
        else:
            subject = "【健康筛查】注册验证码"
            description = "感谢您选择肿瘤数智化筛查系统。您正在进行账号注册，请使用以下验证码完成验证："
        
        content = f"""<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Microsoft YaHei', Arial, sans-serif; padding: 20px; background: #f0f7ff;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
        <!-- 顶部蓝色横条 -->
        <div style="background: #1890ff; height: 6px;"></div>
        
        <div style="padding: 40px 30px;">
            <!-- Logo区域 -->
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; width: 60px; height: 60px; background: #e6f7ff; border-radius: 50%; line-height: 60px; margin-bottom: 15px;">
                    <span style="font-size: 30px;">🏥</span>
                </div>
                <h2 style="color: #1890ff; margin: 10px 0 5px 0; font-size: 22px;">肿瘤数智化筛查系统</h2>
                <p style="color: #999; font-size: 13px; margin: 0;">AI赋能健康 · 早筛早诊早治</p>
            </div>
            
            <!-- 问候语 -->
            <p style="font-size: 16px; color: #333; line-height: 1.6;">您好！</p>
            <p style="font-size: 14px; color: #666; line-height: 1.8;">{description}</p>
            
            <!-- 验证码区域 -->
            <div style="background: #f0f7ff; border: 2px dashed #1890ff; padding: 25px; text-align: center; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0 0 10px 0; color: #666; font-size: 13px;">验证码</p>
                <div style="font-size: 40px; font-weight: bold; color: #1890ff; letter-spacing: 12px; font-family: 'Courier New', monospace;">
                    {code}
                </div>
            </div>
            
            <!-- 提示信息 -->
            <div style="background: #fff7e6; border-left: 4px solid #faad14; padding: 12px 15px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 0; color: #fa8c16; font-size: 13px;">
                    ⏰ <strong>有效期：5分钟</strong> | 请尽快完成注册
                </p>
            </div>
            
            <div style="background: #f6ffed; border-left: 4px solid #52c41a; padding: 12px 15px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 0; color: #52c41a; font-size: 13px;">
                    🔒 <strong>安全提示：</strong>请勿将验证码告诉他人
                </p>
            </div>
            
            <p style="font-size: 13px; color: #999; line-height: 1.6;">如果这不是您本人的操作，请忽略此邮件，您的账号安全不会受到影响。</p>
        </div>
        
        <!-- 页脚 -->
        <div style="background: #fafafa; padding: 20px 30px; border-top: 1px solid #f0f0f0;">
            <p style="color: #999; font-size: 12px; margin: 5px 0; text-align: center;">
                此邮件由系统自动发送，请勿回复
            </p>
            <p style="color: #ccc; font-size: 11px; margin: 5px 0; text-align: center;">
                © 2025 肿瘤数智化筛查系统 | 第七届全球校园人工智能算法精英大赛
            </p>
        </div>
    </div>
</body>
</html>"""
        
        return await self.send_email(to_email, subject, content, is_html=True)


# 全局邮件服务实例
email_service = EmailService()

