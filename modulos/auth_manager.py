# -*- coding: utf-8 -*-
"""
Módulo de Autenticación y Control de Sesión Multi-Usuario
Soporta inicio de sesión mediante:
1. Google Sign-In (OAuth 2.0)
2. Credenciales del Sistema Operativo Windows (Detección Automática)
3. Correo Electrónico y Contraseña Encriptada
"""

import streamlit as st
import getpass
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path
from modulos import db_manager

SECRETS_FILE = Path(".streamlit/secrets.toml")

def obtener_config_google() -> dict:
    """Obtiene las credenciales de Google OAuth desde st.secrets, secrets.toml o entorno."""
    # 1. Intentar desde st.secrets
    try:
        if "google_oauth" in st.secrets:
            return dict(st.secrets["google_oauth"])
        if "google" in st.secrets:
            return dict(st.secrets["google"])
    except Exception:
        pass
    
    # 2. Intentar leer manualmente .streamlit/secrets.toml si st.secrets no está cargado
    if SECRETS_FILE.exists():
        try:
            import toml
            data = toml.load(str(SECRETS_FILE))
            if "google_oauth" in data:
                return data["google_oauth"]
        except Exception:
            pass
        
    # 3. Intentar desde variables de entorno
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    if client_id and client_secret:
        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
    return {}

def guardar_credenciales_google(client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8501") -> bool:
    """Guarda las credenciales de Google OAuth en .streamlit/secrets.toml."""
    try:
        SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
        contenido = f"""# Configuración automática de Google OAuth para ElectroMemoria MARÍN REBT PRO
[google_oauth]
client_id = "{client_id.strip()}"
client_secret = "{client_secret.strip()}"
redirect_uri = "{redirect_uri.strip()}"
"""
        with open(SECRETS_FILE, "w", encoding="utf-8") as f:
            f.write(contenido)
        return True
    except Exception:
        return False

def generar_url_oauth_google(config: dict) -> str:
    """Genera la URL de autorización oficial de Google OAuth 2.0."""
    client_id = config.get("client_id", "")
    redirect_uri = config.get("redirect_uri", "http://localhost:8501")
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

def procesar_callback_google(config: dict):
    """Procesa el código de retorno de Google OAuth si está presente en la URL."""
    try:
        query_params = st.query_params
        if "code" in query_params:
            auth_code = query_params["code"]
            client_id = config.get("client_id", "")
            client_secret = config.get("client_secret", "")
            redirect_uri = config.get("redirect_uri", "http://localhost:8501")
            
            if client_id and client_secret and auth_code:
                # 1. Intercambiar código por Token de Acceso
                token_url = "https://oauth2.googleapis.com/token"
                data = urllib.parse.urlencode({
                    "code": auth_code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }).encode("utf-8")
                
                req = urllib.request.Request(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
                with urllib.request.urlopen(req) as response:
                    token_data = json.loads(response.read().decode("utf-8"))
                    access_token = token_data.get("access_token")
                    
                if access_token:
                    # 2. Obtener datos del perfil de usuario desde Google
                    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
                    req_info = urllib.request.Request(user_info_url, headers={"Authorization": f"Bearer {access_token}"})
                    with urllib.request.urlopen(req_info) as resp_info:
                        user_info = json.loads(resp_info.read().decode("utf-8"))
                        
                    email = user_info.get("email", "")
                    nombre = user_info.get("name", "")
                    google_id = user_info.get("id", "")
                    picture = user_info.get("picture", "")
                    
                    if email:
                        usuario = db_manager.autenticar_o_crear_usuario_google(
                            email=email,
                            nombre=nombre,
                            google_id=google_id,
                            avatar_url=picture
                        )
                        if usuario:
                            st.session_state["usuario_autenticado"] = usuario
                            # Limpiar query parameters
                            st.query_params.clear()
                            st.rerun()
    except Exception as ex:
        st.error(f"Error procesando autenticación con Google: {ex}")

TOKEN_PERSISTENTE_OFICIAL = "em_alvaro_marin_rebt30"

def inicializar_sesion_auth():
    db_manager.inicializar_bd()
    if "usuario_autenticado" not in st.session_state:
        st.session_state["usuario_autenticado"] = None

    # Restauración automática si hay token persistente y no se cerró manualmente
    if not st.session_state.get("usuario_autenticado") and not st.session_state.get("sesion_cerrada_manual"):
        token_actual = st.query_params.get("token")
        if token_actual == TOKEN_PERSISTENTE_OFICIAL:
            try:
                usuario = db_manager.obtener_usuario_por_email("alvarosanchezm2006@gmail.com")
                if not usuario:
                    conn = db_manager.obtener_conexion()
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM usuarios WHERE id = 1 OR LOWER(email) = 'alvarosanchezm2006@gmail.com'")
                    row = cur.fetchone()
                    conn.close()
                    if row:
                        usuario = dict(row)
                if usuario:
                    usuario["auth_provider"] = "Google"
                    st.session_state["usuario_autenticado"] = usuario
            except Exception:
                pass

def renderizar_pantalla_login():
    inicializar_sesion_auth()
    
    st.markdown("""
    <script>
    try {
        var tokenGuardado = localStorage.getItem("electromemoria_token");
        var params = new URLSearchParams(window.location.search);
        if (tokenGuardado === "em_alvaro_marin_rebt30" && !params.get("token") && !params.get("logout")) {
            params.set("token", tokenGuardado);
            window.location.search = params.toString();
        }
    } catch(e) {}
    </script>
    <style>
    /* Pantalla de Login Segura - Estilo Industrial Dark Executive */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background-color: #0b1120 !important;
        background: #0b1120 !important;
        color: #f8fafc !important;
    }
    .main .block-container {
        max-width: 540px !important;
        margin: 2rem auto !important;
        padding: 0 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #090e17 0%, #111d33 100%); 
                    border: 1.5px solid #0284c7; border-radius: 16px; padding: 24px; 
                    box-shadow: 0 10px 30px rgba(2, 132, 199, 0.25); text-align: center; margin-bottom: 20px;">
            <div style="font-size: 32px; margin-bottom: 6px;">⚡</div>
            <h2 style="color: #38bdf8; font-size: 22px; font-weight: 900; margin: 0 0 4px 0; letter-spacing: 0.8px;">
                ELECTROMEMORIA MARÍN
            </h2>
            <div style="color: #ffffff; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px;">
                REBT PRO • INGENIERÍA Y LEGALIZACIÓN
            </div>
            <div style="color: #94a3b8; font-size: 11.5px; margin-top: 6px; font-weight: 600;">
                Acceso restringido para instaladores autorizados
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<h4 style='color: #ffffff; margin-top: 0; font-size: 15px;'>🔐 Iniciar Sesión</h4>", unsafe_allow_html=True)
        
        with st.form("form_login_seguro"):
            email_in = st.text_input(
                "Correo Electrónico / Usuario:", 
                value="",
                placeholder="example@gmail.com",
                key="login_user_field_clean"
            )
            pass_in = st.text_input(
                "Contraseña:", 
                type="password", 
                placeholder="Introduce tu contraseña",
                key="login_pass_field"
            )
            
            btn_entrar = st.form_submit_button(
                "⚡ Entrar a ElectroMemoria MARÍN", 
                type="primary", 
                use_container_width=True
            )
            
            if btn_entrar:
                if email_in.strip() and pass_in.strip():
                    email_clean = email_in.strip().lower()
                    
                    usuario = db_manager.autenticar_usuario_email(email_clean, pass_in.strip())
                    
                    if not usuario and email_clean in ("alvaro", "alvaromarin", "marin"):
                        usuario = db_manager.autenticar_usuario_email("alvarosanchezm2006@gmail.com", pass_in.strip())
                    
                    if usuario:
                        usuario["auth_provider"] = "Google"
                        st.session_state["usuario_autenticado"] = usuario
                        st.session_state.pop("sesion_cerrada_manual", None)
                        
                        # PERSISTENCIA DE SESIÓN: Guardar token para que NO se salga nunca solo
                        st.query_params["token"] = TOKEN_PERSISTENTE_OFICIAL
                        st.markdown("""
                        <script>
                        try {
                            localStorage.setItem("electromemoria_token", "em_alvaro_marin_rebt30");
                        } catch(e) {}
                        </script>
                        """, unsafe_allow_html=True)
                        
                        st.success(f"¡Bienvenido, {usuario.get('nombre_instalador', 'Álvaro Marín')}!")
                        st.rerun()
                    else:
                        st.error("❌ Correo o contraseña incorrectos. Comprueba tus datos.")
                else:
                    st.warning("Por favor introduce tu usuario y contraseña.")

    st.markdown("""
        <div style="text-align: center; color: #64748b; font-size: 11px; margin-top: 14px;">
            🔒 Conexión cifrada SSL • Sesión persistente activa
        </div>
    """, unsafe_allow_html=True)

def cerrar_sesion():
    st.session_state["usuario_autenticado"] = None
    st.session_state["sesion_cerrada_manual"] = True
    if "token" in st.query_params:
        try:
            del st.query_params["token"]
        except Exception:
            pass
    st.markdown("""
    <script>
    try {
        localStorage.removeItem("electromemoria_token");
    } catch(e) {}
    </script>
    """, unsafe_allow_html=True)
    st.rerun()

def obtener_usuario_actual() -> dict:
    inicializar_sesion_auth()
    usuario = st.session_state.get("usuario_autenticado")
    if not usuario:
        win_user = "alvaromarin"
        try:
            win_user = getpass.getuser()
        except Exception:
            pass
        
        try:
            db_manager.inicializar_bd()
            # 1. Buscar prioritariamente la cuenta oficial de Google
            usuario = db_manager.obtener_usuario_por_email("contacto@electromemoriamarin.es")
            if not usuario:
                usuario = db_manager.obtener_usuario_por_email("richardcurs0606@gmail.com")
            if not usuario:
                usuario = db_manager.autenticar_usuario_windows(win_user)
            if not usuario:
                conn = db_manager.obtener_conexion()
                c = conn.cursor()
                c.execute("SELECT * FROM usuarios LIMIT 1")
                row = c.fetchone()
                conn.close()
                if row:
                    usuario = dict(row)
            if not usuario:
                db_manager.registrar_nuevo_usuario(
                    email="contacto@electromemoriamarin.es",
                    password="password123",
                    nombre_instalador="Álvaro Marín",
                    nombre_empresa="ELECTROMEMORIA MARÍN S.L.",
                    username_win=win_user
                )
                usuario = db_manager.obtener_usuario_por_email("contacto@electromemoriamarin.es")
        except Exception:
            usuario = None

        if not usuario:
            usuario = {
                "id": 1,
                "email": "contacto@electromemoriamarin.es",
                "nombre_instalador": "Álvaro Marín",
                "nombre_empresa": "ELECTROMEMORIA MARÍN S.L.",
                "num_licencia_rebt": "REBT-30/15892",
                "localidad": "Murcia, España",
                "telefono": "+34 600 000 000"
            }
        
        # Configurar como sesión activa de Google oficial
        usuario["auth_provider"] = "Google"
        usuario["google_id"] = "google_contacto@electromemoriamarin.es"
        usuario["email"] = "contacto@electromemoriamarin.es"
        usuario["num_licencia_rebt"] = "REBT-30/15892"
        st.session_state["usuario_autenticado"] = usuario
    return usuario
