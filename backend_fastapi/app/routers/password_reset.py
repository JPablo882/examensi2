from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
from app.schemas import RecuperarPasswordRequest, ResetPasswordRequest
from app.security import get_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/api/password", tags=["Recuperar Contraseña"])

# ==================== CONFIGURACIÓN DE CORREO ====================
# ¡CAMBIA ESTOS DATOS CON LOS TUYOS!
SMTP_SERVER = "smtp.gmail.com"  # Para Gmail
SMTP_PORT = 587
SMTP_USER = "dbanegas205@gmail.com"  # ← TU CORREO
SMTP_PASSWORD = "guhj uaah vdti whdy"  # ← CONTRASEÑA DE APLICACIÓN
FRONTEND_URL = "http://localhost:4200"  # URL de tu frontend

# Almacenamiento temporal de tokens
tokens_temp = {}

# ==================== FUNCIÓN PARA ENVIAR CORREO ====================
def enviar_correo_recuperacion(destinatario: str, token: str):
    """Envía correo con enlace de recuperación"""
    enlace = f"{FRONTEND_URL}/reset-password?token={token}"
    
    asunto = "🔐 Recuperación de contraseña - EmergAuto"
    
    cuerpo_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Recuperar contraseña</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 550px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: #ff6200;
                color: white;
                text-align: center;
                padding: 30px;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 10px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 10px 0 0;
                opacity: 0.9;
            }}
            .content {{
                padding: 35px;
                text-align: center;
            }}
            .content p {{
                color: #333;
                line-height: 1.6;
                margin: 15px 0;
            }}
            .btn {{
                display: inline-block;
                background: #ff6200;
                color: white;
                text-decoration: none;
                padding: 14px 35px;
                border-radius: 50px;
                font-weight: bold;
                font-size: 16px;
                margin: 20px 0;
                transition: background 0.3s;
            }}
            .btn:hover {{
                background: #e05500;
            }}
            .warning {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px;
                margin: 20px 0;
                font-size: 13px;
                color: #856404;
            }}
            .footer {{
                background: #f8f9fa;
                text-align: center;
                padding: 20px;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #eee;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">📞</div>
                <h1>EmergAuto</h1>
                <p>Asistencia vehicular 24/7</p>
            </div>
            <div class="content">
                <h2>¿Olvidaste tu contraseña?</h2>
                <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
                <p>Haz clic en el botón para crear una nueva contraseña:</p>
                
                <a href="{enlace}" class="btn">🔑 Restablecer contraseña</a>
                
                <div class="warning">
                    ⚠️ Este enlace expirará en <strong>1 hora</strong>.
                </div>
                
                <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
                <p>Tu contraseña seguirá siendo la misma.</p>
            </div>
            <div class="footer">
                <p>EmergAuto - Asistencia vehicular 24 horas</p>
                <p>© 2025 Todos los derechos reservados</p>
                <p>📞 Emergencias: 900 000 000</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg["Subject"] = asunto
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg.attach(MIMEText(cuerpo_html, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Correo enviado a: {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False

# ==================== ENDPOINTS ====================

@router.post("/recuperar")
def solicitar_recuperacion(request: RecuperarPasswordRequest, db: Session = Depends(get_db)):
    """Solicitar recuperación de contraseña - envía correo con enlace"""
    
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()
    
    if not usuario:
        # Por seguridad, no revelamos si el email existe
        return {"message": "Si el correo existe, recibirás un enlace de recuperación"}
    
    # Generar token único
    token = secrets.token_urlsafe(32)
    expiracion = datetime.now() + timedelta(hours=1)
    
    # Guardar token en memoria temporal
    tokens_temp[token] = {
        "email": request.email,
        "expiracion": expiracion,
        "usuario_id": usuario.id
    }
    
    print(f"\n📧 Solicitando recuperación para: {request.email}")
    print(f"🔑 Token generado: {token[:20]}...")
    
    # Enviar correo
    if enviar_correo_recuperacion(request.email, token):
        return {"message": "✅ Correo de recuperación enviado. Revisa tu bandeja de entrada."}
    else:
        return {"message": "❌ Error al enviar el correo. Intenta más tarde."}

@router.post("/reset")
def resetear_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Restablecer la contraseña con el token recibido por correo"""
    
    # Verificar token
    token_data = tokens_temp.get(request.token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o ya fue utilizado"
        )
    
    if datetime.now() > token_data["expiracion"]:
        # Limpiar token expirado
        del tokens_temp[request.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado. Solicita un nuevo enlace"
        )
    
    # Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.id == token_data["usuario_id"]).first()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Validar nueva contraseña
    if len(request.nueva_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 6 caracteres"
        )
    
    # 🔥 ACTUALIZAR CONTRASEÑA EN POSTGRESQL
    usuario.password_hash = get_password_hash(request.nueva_password)
    
    # Limpiar token usado
    del tokens_temp[request.token]
    
    db.commit()
    
    print(f"✅ Contraseña actualizada para: {usuario.email}")
    
    return {"message": "✅ Contraseña actualizada correctamente. Ahora puedes iniciar sesión."}

@router.get("/verificar-token")
def verificar_token(token: str):
    """Verificar si un token es válido"""
    
    token_data = tokens_temp.get(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido"
        )
    
    if datetime.now() > token_data["expiracion"]:
        del tokens_temp[token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado"
        )
    
    return {"valid": True, "email": token_data["email"]}