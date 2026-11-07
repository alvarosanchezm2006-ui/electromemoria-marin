# -*- coding: utf-8 -*-
import streamlit as st
import traceback
import pandas as pd
import base64
import os

st.set_page_config(page_title="ELECTROMARÍN - Cálculos Eléctricos REBT", page_icon="⚡", layout="wide")

# Prevenir que el traductor automático del navegador corrompa el DOM de React (NotFoundError: removeChild)
st.markdown("""
<script>
    try {
        document.documentElement.lang = "es";
        document.documentElement.classList.add("notranslate");
        document.documentElement.setAttribute("translate", "no");
        if (!document.querySelector('meta[name="google"][content="notranslate"]')) {
            var m = document.createElement('meta');
            m.name = "google";
            m.content = "notranslate";
            document.head.appendChild(m);
        }
    } catch(e) {}
</script>
<meta name="google" content="notranslate" />
""", unsafe_allow_html=True)

# =========================================================================
# IMPORTACIÓN SEGURA DE MÓDULOS
# =========================================================================
errores_import = {}

auth_manager = None
db_manager = None
perfil_instalador = None
gestion_clientes = None

try:
    from modulos import auth_manager
except Exception as e:
    auth_manager = None
    errores_import["auth_manager"] = traceback.format_exc()

try:
    from modulos import db_manager
except Exception as e:
    db_manager = None
    errores_import["db_manager"] = traceback.format_exc()

try:
    from modulos import perfil_instalador
except Exception as e:
    perfil_instalador = None
    errores_import["perfil_instalador"] = traceback.format_exc()

try:
    from modulos import gestion_clientes
except Exception as e:
    gestion_clientes = None
    errores_import["gestion_clientes"] = traceback.format_exc()

try:
    from modulos import calculo_rapido
except Exception as e:
    calculo_rapido = None
    errores_import["calculo_rapido"] = traceback.format_exc()

try:
    from modulos import prevision_cargas
except Exception as e:
    prevision_cargas = None
    errores_import["prevision_cargas"] = traceback.format_exc()

try:
    from modulos import lga
except Exception as e:
    lga = None
    errores_import["lga"] = traceback.format_exc()

try:
    from modulos import di
except Exception as e:
    di = None
    errores_import["di"] = traceback.format_exc()

try:
    from modulos import irve
except Exception as e:
    irve = None
    errores_import["irve"] = traceback.format_exc()

try:
    from modulos import presupuesto_vivienda
except Exception as e:
    presupuesto_vivienda = None
    errores_import["presupuesto_vivienda"] = traceback.format_exc()

try:
    from modulos import presupuesto_rapido_ia
except Exception as e:
    presupuesto_rapido_ia = None
    errores_import["presupuesto_rapido_ia"] = traceback.format_exc()

try:
    from modulos import rebt_tablas as rebt
except Exception as e:
    rebt = None
    errores_import["rebt_tablas"] = traceback.format_exc()

try:
    from modulos import memoria_tecnica_industria
except Exception as e:
    memoria_tecnica_industria = None
    errores_import["memoria_tecnica_industria"] = traceback.format_exc()

try:
    from modulos import tablas_normativas
except Exception as e:
    tablas_normativas = None
    errores_import["tablas_normativas"] = traceback.format_exc()

try:
    from modulos import asistente_ia_rebt
except Exception as e:
    asistente_ia_rebt = None
    errores_import["asistente_ia_rebt"] = traceback.format_exc()

try:
    from modulos import fotovoltaica
except Exception as e:
    fotovoltaica = None
    errores_import["fotovoltaica"] = traceback.format_exc()

try:
    from modulos import radar_normativo
except Exception as e:
    radar_normativo = None
    errores_import["radar_normativo"] = traceback.format_exc()

try:
    from modulos import control_salida
except Exception as e:
    control_salida = None
    errores_import["control_salida"] = traceback.format_exc()

try:
    from modulos import unifilar_foto
except Exception as e:
    unifilar_foto = None
    errores_import["unifilar_foto"] = traceback.format_exc()

try:
    from modulos import control_obras
except Exception as e:
    control_obras = None
    errores_import["control_obras"] = traceback.format_exc()

# =========================================================================
# CONTROL DE SALIDA Y PROTECCIÓN CONTRA CIERRES (TECLA ESCAPE / NAVEGADOR)
# =========================================================================
if control_salida:
    control_salida.inyectar_control_escape()
    control_salida.procesar_salida_url(auth_manager)

# =========================================================================
# CONFIGURACIÓN DE TEMA: MODO SOLAR (CLARO) / MODO OSCURO (REBT)
# =========================================================================
st.session_state["tema_modo"] = "oscuro"
tema_es_oscuro = True

tema_es_oscuro = st.session_state.get("tema_modo", "oscuro") == "oscuro"

# =========================================================================
# ESTILOS CSS GLOBALES (RESPONSIVOS & DINÁMICOS POR TEMA)
# =========================================================================
css_tema_oscuro = """
    /* --- TEMA OSCURO REBT DE ALTO CONTRASTE --- */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container {
        background-color: #0b1120 !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #1e293b !important;
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] button {
        background-color: #0f172a !important;
        border: 1.5px solid #334155 !important;
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] button:hover {
        border-color: #38bdf8 !important;
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }

    /* TODOS LOS BOTONES ESTÁNDAR Y SECUNDARIOS EN MODO OSCURO (ELIMINA CASILLAS BLANCAS CON TEXTO INVISIBLE) */
    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[kind="secondary"],
    div.stDownloadButton > button {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1.5px solid #475569 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button p,
    div.stButton > button span,
    div.stButton > button div,
    div[data-testid="stFormSubmitButton"] > button p,
    div[data-testid="stFormSubmitButton"] > button span,
    button[kind="secondary"] p,
    button[kind="secondary"] span {
        color: #f8fafc !important;
    }
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[kind="secondary"]:hover,
    div.stDownloadButton > button:hover {
        background-color: #334155 !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }
    div.stButton > button:hover p,
    div.stButton > button:hover span,
    div[data-testid="stFormSubmitButton"] > button:hover p,
    div[data-testid="stFormSubmitButton"] > button:hover span {
        color: #38bdf8 !important;
    }

    /* BOTONES PRIMARIOS EN MODO OSCURO */
    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"],
    button[kind="primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 1.5px solid #38bdf8 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4) !important;
    }
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span,
    button[kind="primary"] p,
    button[kind="primary"] span {
        color: #ffffff !important;
    }
    div.stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.6) !important;
    }

    /* CONTENEDORES CON BORDE, PESTAÑAS Y TARJETAS EN MODO OSCURO (ENCERRADOS CON LÍNEA GRUESA) */
    div[data-testid="stTabPanel"],
    div[role="tabpanel"],
    div[data-testid="stTabContent"] {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 14px !important;
        padding: 24px 20px !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 12px rgba(2, 132, 199, 0.2) !important;
    }
    div[data-testid="stTabPanel"] div[data-testid="stTabPanel"],
    div[role="tabpanel"] div[role="tabpanel"] {
        border: 1px solid #2d3b55 !important;
        background-color: #1e293b !important;
        border-radius: 10px !important;
        padding: 16px !important;
        margin-top: 8px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div.ep3ma5o3,
    div[class*="ep3ma5o3"],
    div.e1wbhg7m1,
    div[class*="e1wbhg7m1"],
    div[data-testid="stVerticalBlock"] > div[style*="border"],
    div:has(> [data-testid="stVerticalBlock"]):has([style*="border"]) {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 16px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover,
    div[class*="ep3ma5o3"]:hover,
    div[class*="e1wbhg7m1"]:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.25) !important;
    }
    div[data-testid="stTabPanel"] div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stTabPanel"] div.ep3ma5o3,
    div[data-testid="stTabPanel"] div[class*="ep3ma5o3"],
    div[role="tabpanel"] div[data-testid="stVerticalBlockBorderWrapper"],
    div[role="tabpanel"] div.ep3ma5o3,
    div[role="tabpanel"] div[class*="ep3ma5o3"] {
        border: 1px solid #2d3b55 !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stExpander"] {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 14px !important;
    }
    div[data-testid="stExpander"] > details {
        background-color: #0f172a !important;
    }
    div[data-testid="stExpander"]:hover {
        border-color: #38bdf8 !important;
    }
    .electromemoria-card {{
        background-color: #111827 !important;
        border: 1px solid #1f293d !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s ease !important;
    }}
    .electromemoria-card:hover {{
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.15) !important;
    }}

    /* INPUTS, SELECTORES, NUMBER INPUTS Y ÁREAS DE TEXTO - MODO OSCURO */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [role="combobox"],
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div {
        background-color: #1e293b !important;
        background: #1e293b !important;
        border: 1px solid #2d3b55 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        -webkit-text-fill-color: #ffffff !important;
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.25) !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] input {
        color: #ffffff !important;
        background-color: transparent !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="select"]:focus-within,
    div[data-baseweb="textarea"]:focus-within,
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        background-color: #0f172a !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.55) !important;
    }

    /* FLECHA DESPLEGABLE (CHEVRON SELECTBOX) EN MODO OSCURO - MUY VISUAL Y CIAN BRILLANTE */
    div[data-baseweb="select"] svg,
    div[data-testid="stSelectbox"] svg {
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        min-height: 26px !important;
        stroke-width: 3px !important;
        fill: #38bdf8 !important;
        color: #38bdf8 !important;
        stroke: #38bdf8 !important;
        filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.8)) !important;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-baseweb="select"]:hover svg,
    div[data-testid="stSelectbox"]:hover svg {
        fill: #7dd3fc !important;
        stroke: #7dd3fc !important;
        transform: scale(1.18) !important;
    }

    /* BOTONES DE INCREMENTO / DECREMENTO (-) (+) EN NUMBER INPUTS */
    div[data-testid="stNumberInput"] button {
        background-color: #0f172a !important;
        background: #0f172a !important;
        color: #38bdf8 !important;
        border: 1.5px solid #38bdf8 !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4) !important;
    }
    div[data-testid="stNumberInput"] button svg {
        fill: #38bdf8 !important;
        stroke: #38bdf8 !important;
    }
    div[data-testid="stNumberInput"] button:hover svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* TEXTO SELECCIONADO EN SELECTBOX */
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #ffffff !important;
    }

    /* CHECKBOXES Y RADIOS - MODO OSCURO */
    div[data-testid="stCheckbox"] label,
    div[data-testid="stRadio"] label,
    div[data-testid="stCheckbox"] label *,
    div[data-testid="stRadio"] label * {
        color: #f8fafc !important;
    }
    div[data-testid="stCheckbox"] label > span + div,
    div[data-testid="stCheckbox"] label > div:first-of-type,
    div[data-testid="stCheckbox"] label > div:not([data-testid="stWidgetLabel"]),
    div[data-testid="stCheckbox"] [class*="e15oan335"],
    div[data-testid="stCheckbox"] div.e15oan335,
    .st-emotion-cache-e15oan335,
    div[data-testid="stCheckbox"] [role="checkbox"],
    div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] > div:first-child {
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        min-height: 22px !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        background-color: #1e293b !important;
        background: #1e293b !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.35) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        flex-shrink: 0 !important;
    }
    div[data-testid="stCheckbox"] label:hover > span + div,
    div[data-testid="stCheckbox"] label:hover > div:first-of-type,
    div[data-testid="stCheckbox"] label:hover [class*="e15oan335"] {
        border-color: #7dd3fc !important;
        background-color: #0f172a !important;
        background: #0f172a !important;
        transform: scale(1.08) !important;
    }
    div[data-testid="stCheckbox"] label[data-selected="true"] > span + div,
    div[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type,
    div[data-testid="stCheckbox"] label[data-selected="true"] [class*="e15oan335"],
    div[data-testid="stCheckbox"] label:has(input:checked) > span + div,
    div[data-testid="stCheckbox"] label:has(input:checked) > div:first-of-type,
    div[data-testid="stCheckbox"] label:has(input:checked) [class*="e15oan335"],
    div[data-testid="stCheckbox"] label > span + div:has(svg),
    div[data-testid="stCheckbox"] label > div:first-of-type:has(svg),
    div[data-testid="stCheckbox"] [class*="e15oan335"]:has(svg) {
        background-color: #0284c7 !important;
        background: #0284c7 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.6) !important;
    }
    div[data-testid="stCheckbox"] svg,
    div[data-testid="stCheckbox"] [class*="e15oan335"] svg {
        width: 14px !important;
        height: 14px !important;
        stroke-width: 3.5px !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
        fill: none !important;
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.35)) !important;
    }
    div[data-testid="stCheckbox"] svg polyline,
    div[data-testid="stCheckbox"] svg path {
        stroke: #ffffff !important;
        stroke-width: 3.5px !important;
        fill: none !important;
    }

    /* =========================================================================
       CÍRCULOS DE RADIO BUTTON (MODO OSCURO - MÁXIMA NITIDEZ Y CONTRASTE)
       ========================================================================= */
    div[data-testid="stRadio"] [role="radiogroup"] label,
    div[data-testid="stRadioOption"] {
        display: inline-flex !important;
        align-items: center !important;
        cursor: pointer !important;
        gap: 10px !important;
        margin-bottom: 6px !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] label:hover,
    div[data-testid="stRadioOption"]:hover {
        background-color: rgba(56, 189, 248, 0.12) !important;
    }

    /* Círculo Exterior del Radio Button en Modo Oscuro - Borde Celeste Eléctrico y Fondo Oscuro */
    div[data-testid="stRadio"] [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"] [class*="e1mpz0hj4"],
    div[data-testid="stRadio"] div.e1mpz0hj4,
    div[data-testid="stRadio"] .st-emotion-cache-e1mpz0hj4 {
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        min-height: 22px !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 50% !important;
        background-color: #0f172a !important;
        background: #0f172a !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.35) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        flex-shrink: 0 !important;
        box-sizing: border-box !important;
    }

    /* Interior del círculo no seleccionado en Modo Oscuro */
    div[data-testid="stRadio"] [class*="e1mpz0hj5"],
    div[data-testid="stRadioOption"] [class*="e1mpz0hj5"],
    div[data-testid="stRadio"] div.e1mpz0hj5,
    div[data-testid="stRadio"] .st-emotion-cache-e1mpz0hj5 {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
    }

    /* Hover en el círculo del Radio Button */
    div[data-testid="stRadio"] label:hover [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"]:hover [class*="e1mpz0hj4"] {
        border-color: #7dd3fc !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.6) !important;
        transform: scale(1.08) !important;
    }

    /* Círculo Seleccionado en Modo Oscuro */
    div[data-testid="stRadio"] label:has(input:checked) [class*="e1mpz0hj4"],
    div[data-testid="stRadio"] label[data-selected="true"] [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"][data-selected="true"] [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"]:has(input:checked) [class*="e1mpz0hj4"] {
        background-color: #0284c7 !important;
        background: #0284c7 !important;
        border-color: #38bdf8 !important;
        border-width: 2.5px !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.75) !important;
    }

    /* Punto central blanco cuando está seleccionado */
    div[data-testid="stRadio"] label:has(input:checked) [class*="e1mpz0hj5"],
    div[data-testid="stRadio"] label[data-selected="true"] [class*="e1mpz0hj5"],
    div[data-testid="stRadioOption"][data-selected="true"] [class*="e1mpz0hj5"],
    div[data-testid="stRadioOption"]:has(input:checked) [class*="e1mpz0hj5"] {
        width: 9px !important;
        height: 9px !important;
        min-width: 9px !important;
        min-height: 9px !important;
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-radius: 50% !important;
        box-shadow: 0 0 8px #ffffff !important;
        display: block !important;
    }

    /* Texto de Radio Button en Modo Oscuro */
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadioOption"] p,
    div[data-testid="stRadioOption"] span {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        letter-spacing: 0.2px !important;
    }

    /* MENÚS DESPLEGABLES Y POPOVERS - MODO OSCURO */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 12px !important;
        box-shadow: 0 16px 45px rgba(0, 0, 0, 0.85), 0 0 20px rgba(56, 189, 248, 0.35) !important;
    }
    li[role="option"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        padding: 12px 18px !important;
        border-bottom: 1.5px solid #1e293b !important;
        border-radius: 8px !important;
        margin-bottom: 3px !important;
        transition: all 0.15s ease !important;
    }
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
    }
    li[role="option"] span,
    li[role="option"] div {
        color: inherit !important;
    }

    /* =========================================================================
       MENÚ DE SECCIONES (BOTONES EN 2 FILAS / RETÍCULA TÁCTIL) - MODO OSCURO
       ========================================================================= */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px 12px !important;
        background-color: #0b1329 !important;
        padding: 12px !important;
        border-radius: 14px !important;
        border: 2px solid #1e293b !important;
        margin-bottom: 18px !important;
        overflow: visible !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-baseweb="tab-border"] {
        display: none !important;
    }
    div[data-baseweb="tab-highlight"] {
        display: none !important;
    }
    button[data-baseweb="tab"] {
        flex: 1 1 calc(33.333% - 12px) !important;
        min-width: 175px !important;
        height: auto !important;
        min-height: 50px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 12px 18px !important;
        border-radius: 10px !important;
        border: 2px solid #334155 !important;
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        font-size: 15.5px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        white-space: normal !important;
        word-break: normal !important;
        cursor: pointer !important;
    }
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] div {
        color: #f1f5f9 !important;
        font-size: 15.5px !important;
        font-weight: 700 !important;
        text-align: center !important;
        line-height: 1.3 !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #0f172a !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 14px rgba(56, 189, 248, 0.3) !important;
    }
    button[data-baseweb="tab"]:hover p,
    button[data-baseweb="tab"]:hover span,
    button[data-baseweb="tab"]:hover div {
        color: #38bdf8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        border: 1px solid #2d3b55 !important;
        color: #ffffff !important;
        font-size: 15.5px !important;
        font-weight: 800 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.6) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span,
    button[data-baseweb="tab"][aria-selected="true"] div {
        color: #ffffff !important;
        font-size: 15.5px !important;
        font-weight: 800 !important;
    }
    /* Pestañas anidadas dentro de secciones */
    div[data-testid="stTabPanel"] div[data-baseweb="tab-list"],
    div[role="tabpanel"] div[data-baseweb="tab-list"] {
        gap: 8px !important;
        padding: 8px !important;
        margin-bottom: 14px !important;
        border: 1.5px solid #0284c7 !important;
    }
    div[data-testid="stTabPanel"] button[data-baseweb="tab"],
    div[role="tabpanel"] button[data-baseweb="tab"] {
        flex: 1 1 calc(25% - 8px) !important;
        min-width: 145px !important;
        min-height: 44px !important;
        font-size: 14.5px !important;
        padding: 8px 14px !important;
    }
    div[data-testid="stTabPanel"] button[data-baseweb="tab"] p,
    div[data-testid="stTabPanel"] button[data-baseweb="tab"] span,
    div[data-testid="stTabPanel"] button[data-baseweb="tab"] div,
    div[role="tabpanel"] button[data-baseweb="tab"] p,
    div[role="tabpanel"] button[data-baseweb="tab"] span,
    div[role="tabpanel"] button[data-baseweb="tab"] div {
        font-size: 14.5px !important;
    }
    /* Neutralizar botones y flechas de scroll de pestañas BaseWeb */
    button[aria-label="Previous tab"],
    button[aria-label="Next tab"],
    div[data-baseweb="tab-list"] ~ button,
    div[data-baseweb="tab-list"] button[aria-label*="tab"] {
        display: none !important;
    }

    /* CONVERSIÓN DE FONDOS CLAROS INLINE EN MODO OSCURO (NUNCA CASILLAS BLANCAS CON TEXTO INVISIBLE) */
    div[style*="background: #f0f9ff"],
    div[style*="background-color: #f0f9ff"],
    div[style*="background: #f1f5f9"],
    div[style*="background-color: #f1f5f9"],
    div[style*="background: #f8fafc"],
    div[style*="background-color: #f8fafc"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border-color: #0284c7 !important;
        color: #f1f5f9 !important;
    }
    div[style*="background: #f0f9ff"] *,
    div[style*="background-color: #f0f9ff"] *,
    div[style*="background: #f1f5f9"] *,
    div[style*="background-color: #f1f5f9"] *,
    div[style*="background: #f8fafc"] *,
    div[style*="background-color: #f8fafc"] * {
        color: #f1f5f9 !important;
    }
    div[style*="background: #f0f9ff"] h1,
    div[style*="background: #f0f9ff"] h2,
    div[style*="background: #f0f9ff"] h3,
    div[style*="background: #f0f9ff"] h4,
    div[style*="background-color: #f0f9ff"] h1,
    div[style*="background-color: #f0f9ff"] h2,
    div[style*="background-color: #f0f9ff"] h3,
    div[style*="background-color: #f0f9ff"] h4 {
        color: #38bdf8 !important;
    }

    /* TOOLTIPS */
    div[data-baseweb="tooltip"],
    div[role="tooltip"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1.5px solid #38bdf8 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.6) !important;
    }
    div[data-baseweb="tooltip"] *,
    div[role="tooltip"] * {
        color: #f8fafc !important;
    }

    /* ALERTAS */
    div[data-testid="stAlert"] {
        background-color: #0f172a !important;
        border: 1.5px solid #0284c7 !important;
        color: #f1f5f9 !important;
    }
    div[data-testid="stAlert"] * {
        color: #f1f5f9 !important;
    }

    /* TABLAS Y DATAFRAMES */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        background-color: #0f172a !important;
    }
    table {
        color: #f1f5f9 !important;
        background-color: #0f172a !important;
    }
    th {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border-bottom: 2px solid #0284c7 !important;
    }
    td {
        border-bottom: 1px solid #334155 !important;
        color: #f1f5f9 !important;
    }

    p, span, label, h1, h2, h3, h4, h5, h6, li {
        color: #f1f5f9 !important;
    }
    .section-header-blue {
        background: linear-gradient(90deg, #0c4a6e 0%, #0f172a 100%) !important;
        border: 1px solid #1e293b !important;
        border-left: 10px solid #38bdf8 !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        margin: 14px 0 14px 0 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4) !important;
    }
    .section-header-blue h1,
    .section-header-blue h2,
    .section-header-blue h3,
    .section-header-blue h4,
    .section-header-blue p,
    .section-header-blue span {
        color: #38bdf8 !important;
        font-weight: 800 !important;
    }
    .section-header-green {
        background: linear-gradient(90deg, #064e3b 0%, #0f172a 100%) !important;
        border: 2.5px solid #16a34a !important;
        border-left: 10px solid #22c55e !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        margin: 14px 0 14px 0 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4) !important;
    }
    .section-header-green h1,
    .section-header-green h2,
    .section-header-green h3,
    .section-header-green h4,
    .section-header-green p,
    .section-header-green span {
        color: #4ade80 !important;
        font-weight: 800 !important;
    }
    .section-header-amber {
        background: linear-gradient(90deg, #451a03 0%, #0f172a 100%) !important;
        border: 2.5px solid #d97706 !important;
        border-left: 10px solid #f59e0b !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        margin: 14px 0 14px 0 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4) !important;
    }
    .section-header-amber h1,
    .section-header-amber h2,
    .section-header-amber h3,
    .section-header-amber h4,
    .section-header-amber p,
    .section-header-amber span {
        color: #fbbf24 !important;
        font-weight: 800 !important;
    }
    .section-header-slate {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%) !important;
        border: 2.5px solid #475569 !important;
        border-left: 10px solid #94a3b8 !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        margin: 14px 0 14px 0 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.4) !important;
    }
    .section-header-slate h1,
    .section-header-slate h2,
    .section-header-slate h3,
    .section-header-slate h4,
    .section-header-slate p,
    .section-header-slate span {
        color: #e2e8f0 !important;
        font-weight: 800 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
""" if tema_es_oscuro else ""

css_tema_solar = """
    /* --- MODO SOLAR (DÍA) - CELDAS DE INTRODUCCIÓN DE DATOS MÁS OSCURAS Y DEFINIDAS --- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [role="combobox"],
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"],
    div[data-baseweb="textarea"] > div {
        background-color: #e2e8f0 !important;
        background: #e2e8f0 !important;
        border: 2px solid #0284c7 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        -webkit-text-fill-color: #0f172a !important;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] input {
        color: #0f172a !important;
        background-color: transparent !important;
        -webkit-text-fill-color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Foco activo en Modo Solar: Se ilumina en blanco con halo azul */
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="select"]:focus-within,
    div[data-baseweb="textarea"]:focus-within,
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-color: #0369a1 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.28) !important;
    }

    /* FLECHA DESPLEGABLE (CHEVRON SELECTBOX) EN MODO SOLAR - VISIBLE, AZUL Y MÁS GRANDE */
    div[data-baseweb="select"] svg,
    div[data-testid="stSelectbox"] svg {
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        min-height: 26px !important;
        stroke-width: 3px !important;
        fill: #0284c7 !important;
        color: #0284c7 !important;
        stroke: #0284c7 !important;
        filter: drop-shadow(0 2px 4px rgba(2, 132, 199, 0.45)) !important;
        transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div[data-baseweb="select"]:hover svg,
    div[data-testid="stSelectbox"]:hover svg {
        fill: #0369a1 !important;
        stroke: #0369a1 !important;
        transform: scale(1.18) !important;
    }

    /* BOTONES DE INCREMENTO / DECREMENTO (-) (+) EN NUMBER INPUTS - MODO SOLAR */
    div[data-testid="stNumberInput"] button {
        background-color: #cbd5e1 !important;
        background: #cbd5e1 !important;
        color: #0f172a !important;
        border: 1.5px solid #0284c7 !important;
        border-radius: 6px !important;
        font-weight: 800 !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background-color: #0284c7 !important;
        background: #0284c7 !important;
        color: #ffffff !important;
        border-color: #0369a1 !important;
    }
    div[data-testid="stNumberInput"] button svg {
        fill: #0f172a !important;
        stroke: #0f172a !important;
    }
    div[data-testid="stNumberInput"] button:hover svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* MENÚS DESPLEGABLES Y POPOVERS - MODO SOLAR */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[role="listbox"] {
        background-color: #ffffff !important;
        background: #ffffff !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px !important;
        box-shadow: 0 14px 40px rgba(2, 132, 199, 0.28), 0 4px 16px rgba(0, 0, 0, 0.12) !important;
    }
    div[data-baseweb="popover"] li[role="option"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        line-height: 1.45 !important;
        padding: 12px 18px !important;
        border-bottom: 1.5px solid #f1f5f9 !important;
        border-radius: 8px !important;
        margin-bottom: 3px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    div[data-baseweb="popover"] li[role="option"]:hover {
        background-color: #e0f2fe !important;
        color: #0284c7 !important;
        font-weight: 700 !important;
        transform: translateX(3px) !important;
    }
    div[data-baseweb="popover"] li[role="option"][aria-selected="true"] {
        background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.4) !important;
    }
    div[data-baseweb="popover"] li[role="option"] * {
        color: inherit !important;
    }

    /* CASILLAS DE CHECKBOX EN MODO SOLAR (DÍA) - CUADRO MUY VISIBLE CON FONDO Y BORDE AZUL */
    div[data-testid="stCheckbox"] label > span + div,
    div[data-testid="stCheckbox"] label > div:first-of-type,
    div[data-testid="stCheckbox"] label > div:not([data-testid="stWidgetLabel"]),
    div[data-testid="stCheckbox"] [class*="e15oan335"],
    div[data-testid="stCheckbox"] div.e15oan335,
    .st-emotion-cache-e15oan335,
    div[data-testid="stCheckbox"] [role="checkbox"],
    div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] > div:first-child {
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        min-height: 22px !important;
        border: 1px solid #1e293b !important;
        border-radius: 6px !important;
        background-color: #e2e8f0 !important;
        background: #e2e8f0 !important;
        box-shadow: 0 1px 4px rgba(2, 132, 199, 0.25), inset 0 1px 2px rgba(0, 0, 0, 0.08) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        flex-shrink: 0 !important;
    }
    div[data-testid="stCheckbox"] label:hover > span + div,
    div[data-testid="stCheckbox"] label:hover > div:first-of-type,
    div[data-testid="stCheckbox"] label:hover [class*="e15oan335"] {
        border-color: #0369a1 !important;
        background-color: #bae6fd !important;
        background: #bae6fd !important;
        transform: scale(1.08) !important;
    }
    div[data-testid="stCheckbox"] label[data-selected="true"] > span + div,
    div[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type,
    div[data-testid="stCheckbox"] label[data-selected="true"] [class*="e15oan335"],
    div[data-testid="stCheckbox"] label:has(input:checked) > span + div,
    div[data-testid="stCheckbox"] label:has(input:checked) > div:first-of-type,
    div[data-testid="stCheckbox"] label:has(input:checked) [class*="e15oan335"],
    div[data-testid="stCheckbox"] label > span + div:has(svg),
    div[data-testid="stCheckbox"] label > div:first-of-type:has(svg),
    div[data-testid="stCheckbox"] [class*="e15oan335"]:has(svg) {
        background-color: #0284c7 !important;
        background: #0284c7 !important;
        border-color: #0284c7 !important;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.45) !important;
    }
    div[data-testid="stCheckbox"] svg,
    div[data-testid="stCheckbox"] [class*="e15oan335"] svg {
        width: 14px !important;
        height: 14px !important;
        stroke-width: 3.5px !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
        fill: none !important;
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.35)) !important;
    }
    div[data-testid="stCheckbox"] svg polyline,
    div[data-testid="stCheckbox"] svg path {
        stroke: #ffffff !important;
        stroke-width: 3.5px !important;
        fill: none !important;
    }
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label span {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* =========================================================================
       CÍRCULOS DE RADIO BUTTON (MODO SOLAR / DÍA - MÁXIMA NITIDEZ Y CONTRASTE)
       ========================================================================= */
    div[data-testid="stRadio"] [role="radiogroup"] label,
    div[data-testid="stRadioOption"] {
        display: inline-flex !important;
        align-items: center !important;
        cursor: pointer !important;
        gap: 10px !important;
        margin-bottom: 6px !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stRadio"] [role="radiogroup"] label:hover,
    div[data-testid="stRadioOption"]:hover {
        background-color: rgba(2, 132, 199, 0.08) !important;
    }

    /* Círculo Exterior del Radio Button en Modo Solar - Reposo con Borde Azul 2.5px y Fondo Slate-200 */
    div[data-testid="stRadio"] [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"] [class*="e1mpz0hj4"],
    div[data-testid="stRadio"] div.e1mpz0hj4,
    div[data-testid="stRadio"] .st-emotion-cache-e1mpz0hj4 {
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        min-height: 22px !important;
        border: 1px solid #1e293b !important;
        border-radius: 50% !important;
        background-color: #e2e8f0 !important;
        background: #e2e8f0 !important;
        box-shadow: 0 1px 4px rgba(2, 132, 199, 0.25), inset 0 1px 2px rgba(0, 0, 0, 0.08) !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease !important;
        flex-shrink: 0 !important;
        box-sizing: border-box !important;
    }

    /* Interior del círculo no seleccionado en Modo Solar */
    div[data-testid="stRadio"] [class*="e1mpz0hj5"],
    div[data-testid="stRadioOption"] [class*="e1mpz0hj5"],
    div[data-testid="stRadio"] div.e1mpz0hj5,
    div[data-testid="stRadio"] .st-emotion-cache-e1mpz0hj5 {
        background-color: #e2e8f0 !important;
        background: #e2e8f0 !important;
        border-radius: 50% !important;
        transition: all 0.2s ease !important;
    }

    /* Hover en el círculo del Radio Button en Modo Solar */
    div[data-testid="stRadio"] label:hover [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"]:hover [class*="e1mpz0hj4"] {
        border-color: #0369a1 !important;
        background-color: #bae6fd !important;
        background: #bae6fd !important;
        transform: scale(1.08) !important;
    }

    /* Círculo Seleccionado en Modo Solar - Azul Océano Sólido */
    div[data-testid="stRadio"] label:has(input:checked) [class*="e1mpz0hj4"],
    div[data-testid="stRadio"] label[data-selected="true"] [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"][data-selected="true"] [class*="e1mpz0hj4"],
    div[data-testid="stRadioOption"]:has(input:checked) [class*="e1mpz0hj4"] {
        background-color: #0284c7 !important;
        background: #0284c7 !important;
        border-color: #0284c7 !important;
        border-width: 2.5px !important;
        box-shadow: 0 2px 8px rgba(2, 132, 199, 0.5) !important;
    }

    /* Punto central blanco cuando está seleccionado en Modo Solar */
    div[data-testid="stRadio"] label:has(input:checked) [class*="e1mpz0hj5"],
    div[data-testid="stRadio"] label[data-selected="true"] [class*="e1mpz0hj5"],
    div[data-testid="stRadioOption"][data-selected="true"] [class*="e1mpz0hj5"],
    div[data-testid="stRadioOption"]:has(input:checked) [class*="e1mpz0hj5"] {
        width: 9px !important;
        height: 9px !important;
        min-width: 9px !important;
        min-height: 9px !important;
        background-color: #ffffff !important;
        background: #ffffff !important;
        border-radius: 50% !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.35) !important;
        display: block !important;
    }

    /* Texto de Radio Button en Modo Solar */
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span,
    div[data-testid="stRadioOption"] p,
    div[data-testid="stRadioOption"] span {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        letter-spacing: 0.2px !important;
    }
""" if not tema_es_oscuro else ""

container_bg_global = "#0f172a" if tema_es_oscuro else "#ffffff"
container_text_global = "#f1f5f9" if tema_es_oscuro else "#0f172a"
container_sub_bg_global = "#1e293b" if tema_es_oscuro else "#f8fafc"
radio_border_global = "#38bdf8" if tema_es_oscuro else "#0284c7"
radio_bg_global = "#0f172a" if tema_es_oscuro else "#e2e8f0"
radio_dot_global = "#38bdf8" if tema_es_oscuro else "#0284c7"

st.markdown(f"""
    <style>
        {css_tema_oscuro}
        {css_tema_solar}

        /* Botón Permanente de Modo Solar / Oscuro (Clonado con precisión de imagen) */
        .st-key-btn_toggle_tema_top button {{
            background-color: #111827 !important;
            border: 1.5px solid #d1d5db !important;
            border-radius: 6px !important;
            color: {'#fef08a' if tema_es_oscuro else '#38bdf8'} !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            letter-spacing: 0.5px !important;
            height: 42px !important;
            margin-bottom: 12px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
        }}
        .st-key-btn_toggle_tema_top button:hover {{
            border-color: {'#facc15' if tema_es_oscuro else '#38bdf8'} !important;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(250, 204, 21, 0.4) !important;
            transform: translateY(-1px) !important;
        }}

        /* Desplegables de Streamlit / BaseWeb Popovers: Dimensiones Responsivas y Legibilidad */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div {{
            min-width: 650px !important;
            max-width: 96vw !important;
            width: max-content !important;
            z-index: 999999 !important;
        }}

        div[data-baseweb="popover"] ul[role="listbox"] {{
            min-width: 100% !important;
            max-width: 96vw !important;
            max-height: 480px !important;
            padding: 8px !important;
        }}

        div[data-baseweb="popover"] li[role="option"] > div,
        div[data-baseweb="popover"] li[role="option"] span {{
            white-space: normal !important;
            word-break: normal !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
            text-overflow: unset !important;
            display: block !important;
        }}

        div[data-baseweb="select"] {{
            width: 100% !important;
        }}

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {{
            white-space: normal !important;
            word-break: break-word !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }}
        
        /* Barra Lateral */
        [data-testid="stSidebar"] {{
            transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), width 0.28s ease !important;
        }}
        [data-testid="stSidebar"] button {{
            width: 100%;
            text-align: left;
            border-radius: 8px;
            font-weight: 500;
            margin-bottom: 6px;
            transition: all 0.2s ease-in-out;
        }}
        [data-testid="stSidebar"] button:hover {{
            border-color: #0284c7;
            color: #0284c7;
            box-shadow: 0 2px 6px rgba(2, 132, 199, 0.15);
            transform: translateX(2px);
        }}

        /* =========================================================================
           PESTAÑA FLOTANTE PERMANENTE PARA DESPLEGAR MENÚ LATERAL (TABLETS & MÓVILES)
           Garantiza que el botón ☰ MENÚ permanezca SIEMPRE visible al hacer scroll vertical hacia abajo.
           ========================================================================= */
        /* =========================================================================
           PESTAÑA FLOTANTE PERMANENTE PARA DESPLEGAR MENÚ LATERAL (TABLETS & MÓVILES)
           Garantiza que el botón ☰ MENÚ permanezca SIEMPRE visible al hacer scroll vertical hacia abajo.
           ========================================================================= */
        header[data-testid="stHeader"] {{
            transform: none !important;
            filter: none !important;
            perspective: none !important;
            background: transparent !important;
            z-index: 9999999 !important;
        }}

        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"],
        header [data-testid="stSidebarCollapsedControl"] {{
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            z-index: 99999999 !important;
            display: flex !important;
            align-items: center !important;
            visibility: visible !important;
            opacity: 1 !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button,
        button[data-testid="stExpandSidebarButton"],
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"] button,
        header [data-testid="stSidebarCollapsedControl"] button,
        header button[data-testid="stExpandSidebarButton"] {{
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            z-index: 99999999 !important;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
            color: #ffffff !important;
            border: 1px solid #2d3b55 !important;
            border-radius: 10px !important;
            padding: 8px 16px !important;
            min-height: 44px !important;
            min-width: 120px !important;
            box-shadow: 0 4px 18px rgba(2, 132, 199, 0.65), 0 2px 8px rgba(0, 0, 0, 0.4) !important;
            cursor: pointer !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 6px !important;
            font-size: 14px !important;
            font-weight: 800 !important;
            letter-spacing: 0.6px !important;
            visibility: visible !important;
            opacity: 1 !important;
            transition: all 0.2s ease !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button::after,
        button[data-testid="stExpandSidebarButton"]::after,
        [data-testid="stExpandSidebarButton"]::after,
        [data-testid="collapsedControl"] button::after,
        header [data-testid="stSidebarCollapsedControl"] button::after {{
            content: " ☰ MENÚ" !important;
            color: #ffffff !important;
            font-size: 13.5px !important;
            font-weight: 800 !important;
            letter-spacing: 0.8px !important;
            margin-left: 4px !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button:hover,
        button[data-testid="stExpandSidebarButton"]:hover,
        [data-testid="stExpandSidebarButton"]:hover,
        [data-testid="collapsedControl"] button:hover {{
            background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
            border-color: #7dd3fc !important;
            box-shadow: 0 6px 22px rgba(2, 132, 199, 0.85) !important;
            transform: scale(1.04) !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button svg,
        button[data-testid="stExpandSidebarButton"] svg,
        [data-testid="stExpandSidebarButton"] svg,
        [data-testid="collapsedControl"] button svg,
        [data-testid="stSidebarCollapsedControl"] button span,
        button[data-testid="stExpandSidebarButton"] span,
        [data-testid="stExpandSidebarButton"] span,
        [data-testid="collapsedControl"] button span {{
            fill: #ffffff !important;
            color: #ffffff !important;
            stroke: #ffffff !important;
            font-size: 20px !important;
            width: 20px !important;
            height: 20px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* Botón para colapsar menú (dentro del sidebar) */
        [data-testid="stSidebarCollapseButton"] button {{
            background-color: #0f172a !important;
            color: #38bdf8 !important;
            border: 1.5px solid #0284c7 !important;
            border-radius: 8px !important;
            padding: 6px 12px !important;
            min-height: 38px !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.2s ease !important;
        }}
        [data-testid="stSidebarCollapseButton"] button::after {{
            content: " ✕ CERRAR MENÚ" !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            color: #38bdf8 !important;
            margin-left: 3px !important;
        }}
        [data-testid="stSidebarCollapseButton"] button:hover {{
            background-color: #0284c7 !important;
            color: #ffffff !important;
        }}
        [data-testid="stSidebarCollapseButton"] button:hover::after {{
            color: #ffffff !important;
        }}
        [data-testid="stSidebarCollapseButton"] button svg {{
            fill: #38bdf8 !important;
        }}
        [data-testid="stSidebarCollapseButton"] button:hover svg {{
            fill: #ffffff !important;
        }}

        /* Contenedores con Borde, Pestañas y Tarjetas (Línea Gruesa de Sección) */
        div[data-testid="stTabPanel"],
        div[role="tabpanel"],
        div[data-testid="stTabContent"] {{
            border: 1px solid #1e293b !important;
            border-radius: 14px !important;
            padding: 24px 20px !important;
            margin-top: 14px !important;
            margin-bottom: 24px !important;
            background-color: {container_bg_global} !important;
            color: {container_text_global} !important;
            box-shadow: {'0 4px 20px rgba(0, 0, 0, 0.5), 0 0 12px rgba(2, 132, 199, 0.2)' if tema_es_oscuro else '0 4px 18px rgba(2, 132, 199, 0.12), 0 2px 6px rgba(0, 0, 0, 0.04)'} !important;
        }}
        div[data-testid="stTabPanel"] div[data-testid="stTabPanel"],
        div[role="tabpanel"] div[role="tabpanel"] {{
            border: 1px solid #2d3b55 !important;
            background-color: {container_sub_bg_global} !important;
            border-radius: 10px !important;
            padding: 16px !important;
            margin-top: 8px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 2px 10px rgba(56, 189, 248, 0.08) !important;
        }}

        /* Contenedores con Borde y Sombra Nítidos y Marcados */
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stVerticalBlockBorderWrapper"] > div,
        div.ep3ma5o3,
        div[class*="ep3ma5o3"],
        div.e1wbhg7m1,
        div[class*="e1wbhg7m1"],
        div[data-testid="stVerticalBlock"] > div[style*="border"],
        div:has(> [data-testid="stVerticalBlock"]):has([style*="border"]) {{
            border-radius: 12px !important;
            border: 1px solid #1e293b !important;
            background-color: {container_bg_global} !important;
            color: {container_text_global} !important;
            box-shadow: {'0 4px 16px rgba(0, 0, 0, 0.4)' if tema_es_oscuro else '0 4px 16px rgba(2, 132, 199, 0.12), 0 1px 4px rgba(0, 0, 0, 0.05)'} !important;
            margin-bottom: 16px !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:hover,
        div[class*="ep3ma5o3"]:hover,
        div[class*="e1wbhg7m1"]:hover {{
            border-color: #0369a1 !important;
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.2) !important;
        }}

        /* Si el contenedor está dentro de una pestaña que ya tiene marco exterior */
        div[data-testid="stTabPanel"] div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stTabPanel"] div.ep3ma5o3,
        div[data-testid="stTabPanel"] div[class*="ep3ma5o3"],
        div[role="tabpanel"] div[data-testid="stVerticalBlockBorderWrapper"],
        div[role="tabpanel"] div.ep3ma5o3,
        div[role="tabpanel"] div[class*="ep3ma5o3"] {{
            border: 1px solid #2d3b55 !important;
            box-shadow: 0 2px 10px rgba(2, 132, 199, 0.08) !important;
        }}

        /* Expanders con Borde Nítido y Sombra */
        div[data-testid="stExpander"] {{
            border-radius: 10px !important;
            border: 1px solid #1e293b !important;
            background-color: {container_bg_global} !important;
            color: {container_text_global} !important;
            box-shadow: 0 2px 10px rgba(2, 132, 199, 0.08) !important;
            margin-bottom: 14px !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stExpander"] > details {{
            background-color: {container_bg_global} !important;
            color: {container_text_global} !important;
        }}
        div[data-testid="stExpander"]:hover {{
            border-color: #0369a1 !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.16) !important;
        }}

        /* Etiquetas y Textos Informativos de Alto Contraste */
        div[data-testid="stWidgetLabel"] label,
        div[data-testid="stWidgetLabel"] p,
        label[data-testid="stWidgetLabel"] {{
            color: {container_text_global} !important;
            font-weight: 700 !important;
            font-size: 14px !important;
        }}
        div[data-testid="stCaption"],
        .stCaption,
        p[data-testid="stCaption"] {{
            color: {'#94a3b8' if tema_es_oscuro else '#475569'} !important;
            font-weight: 600 !important;
        }}

        /* =========================================================================
           FIGURAS Y CÍRCULOS DE TILDE (RADIO BUTTONS Y CHECKBOXES DE ALTA NITIDEZ)
           ========================================================================= */
        /* Círculos de Radio Button */
        div[data-testid="stRadio"] [role="radiogroup"] label,
        div[data-testid="stRadioOption"] {{
            display: inline-flex !important;
            align-items: center !important;
            cursor: pointer !important;
            gap: 10px !important;
            margin-bottom: 6px !important;
            padding: 4px 8px !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
        }}
        div[data-testid="stRadio"] [role="radiogroup"] label:hover,
        div[data-testid="stRadioOption"]:hover {{
            background-color: {'rgba(56, 189, 248, 0.12)' if tema_es_oscuro else 'rgba(2, 132, 199, 0.08)'} !important;
        }}

        /* Círculo Exterior del Radio Button */
        div[data-testid="stRadio"] [class*="e1mpz0hj4"],
        div[data-testid="stRadioOption"] [class*="e1mpz0hj4"],
        div[data-testid="stRadio"] div.e1mpz0hj4,
        div[data-testid="stRadio"] .st-emotion-cache-e1mpz0hj4 {{
            width: 22px !important;
            height: 22px !important;
            min-width: 22px !important;
            min-height: 22px !important;
            border: 2.5px solid {radio_border_global} !important;
            border-radius: 50% !important;
            background-color: {radio_bg_global} !important;
            box-shadow: {'0 0 10px rgba(56, 189, 248, 0.35)' if tema_es_oscuro else '0 1px 4px rgba(2, 132, 199, 0.25)'} !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
            flex-shrink: 0 !important;
            box-sizing: border-box !important;
        }}

        /* Interior del Círculo no seleccionado */
        div[data-testid="stRadio"] [class*="e1mpz0hj5"],
        div[data-testid="stRadioOption"] [class*="e1mpz0hj5"],
        div[data-testid="stRadio"] div.e1mpz0hj5,
        div[data-testid="stRadio"] .st-emotion-cache-e1mpz0hj5 {{
            background-color: {radio_bg_global} !important;
            border-radius: 50% !important;
            transition: all 0.2s ease !important;
        }}

        /* Hover en el Círculo */
        div[data-testid="stRadio"] label:hover [class*="e1mpz0hj4"],
        div[data-testid="stRadioOption"]:hover [class*="e1mpz0hj4"] {{
            border-color: {'#7dd3fc' if tema_es_oscuro else '#0369a1'} !important;
            transform: scale(1.08) !important;
            box-shadow: {'0 0 14px rgba(56, 189, 248, 0.6)' if tema_es_oscuro else '0 2px 6px rgba(2, 132, 199, 0.35)'} !important;
        }}

        /* Círculo Exterior Seleccionado */
        div[data-testid="stRadio"] label:has(input:checked) [class*="e1mpz0hj4"],
        div[data-testid="stRadio"] label[data-selected="true"] [class*="e1mpz0hj4"],
        div[data-testid="stRadioOption"][data-selected="true"] [class*="e1mpz0hj4"],
        div[data-testid="stRadioOption"]:has(input:checked) [class*="e1mpz0hj4"] {{
            background-color: {'#0284c7' if tema_es_oscuro else '#0284c7'} !important;
            border-color: {'#38bdf8' if tema_es_oscuro else '#0284c7'} !important;
            border-width: 2.5px !important;
            box-shadow: {'0 0 14px rgba(56, 189, 248, 0.75)' if tema_es_oscuro else '0 2px 8px rgba(2, 132, 199, 0.5)'} !important;
        }}

        /* Punto Interior del Radio Button Seleccionado (Blanco Nítido de 9px) */
        div[data-testid="stRadio"] label:has(input:checked) [class*="e1mpz0hj5"],
        div[data-testid="stRadio"] label[data-selected="true"] [class*="e1mpz0hj5"],
        div[data-testid="stRadioOption"][data-selected="true"] [class*="e1mpz0hj5"],
        div[data-testid="stRadioOption"]:has(input:checked) [class*="e1mpz0hj5"] {{
            width: 9px !important;
            height: 9px !important;
            min-width: 9px !important;
            min-height: 9px !important;
            border-radius: 50% !important;
            background-color: #ffffff !important;
            background: #ffffff !important;
            box-shadow: {'0 0 8px #ffffff' if tema_es_oscuro else '0 1px 3px rgba(0, 0, 0, 0.35)'} !important;
            display: block !important;
        }}

        /* Texto de Opción de Radio Button */
        div[data-testid="stRadio"] [role="radiogroup"] label p,
        div[data-testid="stRadio"] [role="radiogroup"] label span,
        div[data-testid="stRadioOption"] p,
        div[data-testid="stRadioOption"] span {{
            font-size: 15px !important;
            font-weight: 700 !important;
            color: {container_text_global} !important;
            letter-spacing: 0.2px !important;
        }}

        /* Casillas de Checkbox (Tilde Cuadrada / Selección) */
        div[data-testid="stCheckbox"] label {{
            display: inline-flex !important;
            align-items: center !important;
            cursor: pointer !important;
            gap: 10px !important;
            padding: 4px 8px !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
        }}
        div[data-testid="stCheckbox"] label:hover {{
            background-color: {'rgba(56, 189, 248, 0.12)' if tema_es_oscuro else 'rgba(2, 132, 199, 0.08)'} !important;
        }}
        /* Cuadro Exterior del Checkbox (Desmarcado) */
        div[data-testid="stCheckbox"] label > span + div,
        div[data-testid="stCheckbox"] label > div:first-of-type,
        div[data-testid="stCheckbox"] label > div:not([data-testid="stWidgetLabel"]),
        div[data-testid="stCheckbox"] [class*="e15oan335"],
        div[data-testid="stCheckbox"] div.e15oan335,
        .st-emotion-cache-e15oan335,
        div[data-testid="stCheckbox"] [role="checkbox"],
        div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] > div:first-child {{
            width: 22px !important;
            height: 22px !important;
            min-width: 22px !important;
            min-height: 22px !important;
            border: 2.5px solid {radio_border_global} !important;
            border-radius: 6px !important;
            background-color: {'#1e293b' if tema_es_oscuro else '#e2e8f0'} !important;
            background: {'#1e293b' if tema_es_oscuro else '#e2e8f0'} !important;
            box-shadow: {'0 0 10px rgba(56, 189, 248, 0.35)' if tema_es_oscuro else '0 1px 4px rgba(2, 132, 199, 0.25), inset 0 1px 2px rgba(0, 0, 0, 0.08)'} !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.2s ease !important;
            flex-shrink: 0 !important;
        }}
        div[data-testid="stCheckbox"] label:hover > span + div,
        div[data-testid="stCheckbox"] label:hover > div:first-of-type,
        div[data-testid="stCheckbox"] label:hover [class*="e15oan335"] {{
            border-color: {'#7dd3fc' if tema_es_oscuro else '#0369a1'} !important;
            background-color: {'#0f172a' if tema_es_oscuro else '#bae6fd'} !important;
            background: {'#0f172a' if tema_es_oscuro else '#bae6fd'} !important;
            transform: scale(1.08) !important;
        }}
        /* Cuadro Exterior del Checkbox (Marcado con Tilde) */
        div[data-testid="stCheckbox"] label[data-selected="true"] > span + div,
        div[data-testid="stCheckbox"] label[data-selected="true"] > div:first-of-type,
        div[data-testid="stCheckbox"] label[data-selected="true"] [class*="e15oan335"],
        div[data-testid="stCheckbox"] label:has(input:checked) > span + div,
        div[data-testid="stCheckbox"] label:has(input:checked) > div:first-of-type,
        div[data-testid="stCheckbox"] label:has(input:checked) [class*="e15oan335"],
        div[data-testid="stCheckbox"] label > span + div:has(svg),
        div[data-testid="stCheckbox"] label > div:first-of-type:has(svg),
        div[data-testid="stCheckbox"] [class*="e15oan335"]:has(svg) {{
            background-color: #0284c7 !important;
            background: #0284c7 !important;
            border-color: {'#38bdf8' if tema_es_oscuro else '#0284c7'} !important;
            box-shadow: {'0 0 12px rgba(56, 189, 248, 0.6)' if tema_es_oscuro else '0 2px 8px rgba(2, 132, 199, 0.45)'} !important;
        }}
        /* Icono de Tilde (Checkmark SVG) */
        div[data-testid="stCheckbox"] svg,
        div[data-testid="stCheckbox"] [class*="e15oan335"] svg {{
            width: 14px !important;
            height: 14px !important;
            stroke-width: 3.5px !important;
            stroke: #ffffff !important;
            color: #ffffff !important;
            fill: none !important;
            filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.35)) !important;
        }}
        div[data-testid="stCheckbox"] svg polyline,
        div[data-testid="stCheckbox"] svg path {{
            stroke: #ffffff !important;
            stroke-width: 3.5px !important;
            fill: none !important;
        }}
        /* Texto del Checkbox */
        div[data-testid="stCheckbox"] label p,
        div[data-testid="stCheckbox"] label span,
        div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stCheckbox"] [data-testid="stWidgetLabel"] span {{
            font-size: 15px !important;
            font-weight: 700 !important;
            color: {container_text_global} !important;
            letter-spacing: 0.2px !important;
        }}

        /* Cabeceras de Secciones con Insignia y Borde Integral */
        .section-header-blue {{
            background: linear-gradient(90deg, #f0f9ff 0%, #ffffff 100%);
            border: 1px solid #1e293b !important;
            border-left: 10px solid #0284c7 !important;
            padding: 14px 20px !important;
            border-radius: 10px !important;
            margin: 14px 0 14px 0 !important;
            box-shadow: 0 3px 10px rgba(2, 132, 199, 0.15) !important;
        }}
        .section-header-blue h1, .section-header-blue h2, .section-header-blue h3, .section-header-blue h4 {{
            color: #0369a1 !important;
            font-weight: 800 !important;
        }}
        .section-header-green {{
            background: linear-gradient(90deg, #f0fdf4 0%, #ffffff 100%);
            border: 2.5px solid #16a34a !important;
            border-left: 10px solid #16a34a !important;
            padding: 14px 20px !important;
            border-radius: 10px !important;
            margin: 14px 0 14px 0 !important;
            box-shadow: 0 3px 10px rgba(22, 163, 74, 0.15) !important;
        }}
        .section-header-green h1, .section-header-green h2, .section-header-green h3, .section-header-green h4 {{
            color: #15803d !important;
            font-weight: 800 !important;
        }}
        .section-header-amber {{
            background: linear-gradient(90deg, #fffbeb 0%, #ffffff 100%);
            border: 2.5px solid #d97706 !important;
            border-left: 10px solid #d97706 !important;
            padding: 14px 20px !important;
            border-radius: 10px !important;
            margin: 14px 0 14px 0 !important;
            box-shadow: 0 3px 10px rgba(217, 119, 6, 0.15) !important;
        }}
        .section-header-amber h1, .section-header-amber h2, .section-header-amber h3, .section-header-amber h4 {{
            color: #b45309 !important;
            font-weight: 800 !important;
        }}
        .section-header-slate {{
            background: linear-gradient(90deg, #f8fafc 0%, #ffffff 100%);
            border: 2.5px solid #475569 !important;
            border-left: 10px solid #475569 !important;
            padding: 14px 20px !important;
            border-radius: 10px !important;
            margin: 14px 0 14px 0 !important;
            box-shadow: 0 3px 10px rgba(71, 85, 105, 0.15) !important;
        }}
        .section-header-slate h1, .section-header-slate h2, .section-header-slate h3, .section-header-slate h4 {{
            color: #1e293b !important;
            font-weight: 800 !important;
        }}

        /* Tarjeta Genérica ElectroMemoria MARÍN */
        .electromemoria-card {{
        background-color: #111827 !important;
        border: 1px solid #1f293d !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s ease !important;
    }}
    .electromemoria-card:hover {{
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.15) !important;
    }}

        /* =========================================================================
           MENÚ DE SECCIONES (BOTONES EN 2 FILAS / RETÍCULA TÁCTIL) - MODO SOLAR
           ========================================================================= */
        div[data-baseweb="tab-list"] {{
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 10px 12px !important;
            background: #f1f5f9 !important;
            padding: 12px !important;
            border-radius: 14px !important;
            border: 2px solid #cbd5e1 !important;
            margin-bottom: 18px !important;
            overflow: visible !important;
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }}
        div[data-baseweb="tab-border"] {{
            display: none !important;
        }}
        div[data-baseweb="tab-highlight"] {{
            display: none !important;
        }}
        button[data-baseweb="tab"] {{
            flex: 1 1 calc(33.333% - 12px) !important;
            min-width: 175px !important;
            height: auto !important;
            min-height: 50px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            padding: 12px 18px !important;
            border-radius: 10px !important;
            border: 2px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            color: #1e293b !important;
            font-size: 15.5px !important;
            font-weight: 700 !important;
            letter-spacing: 0.3px !important;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08) !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            white-space: normal !important;
            word-break: normal !important;
            cursor: pointer !important;
        }}
        button[data-baseweb="tab"] p,
        button[data-baseweb="tab"] span,
        button[data-baseweb="tab"] div {{
            color: #1e293b !important;
            font-size: 15.5px !important;
            font-weight: 700 !important;
            text-align: center !important;
            line-height: 1.3 !important;
        }}
        button[data-baseweb="tab"]:hover {{
            background-color: #e0f2fe !important;
            border-color: #0284c7 !important;
            color: #0284c7 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25) !important;
        }}
        button[data-baseweb="tab"]:hover p,
        button[data-baseweb="tab"]:hover span,
        button[data-baseweb="tab"]:hover div {{
            color: #0284c7 !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: #ffffff !important;
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
            border: 2px solid #0284c7 !important;
            font-size: 15.5px !important;
            font-weight: 800 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.45) !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] p,
        button[data-baseweb="tab"][aria-selected="true"] span,
        button[data-baseweb="tab"][aria-selected="true"] div {{
            color: #ffffff !important;
            font-size: 15.5px !important;
            font-weight: 800 !important;
        }}
        /* Pestañas anidadas dentro de secciones */
        div[data-testid="stTabPanel"] div[data-baseweb="tab-list"],
        div[role="tabpanel"] div[data-baseweb="tab-list"] {{
            gap: 8px !important;
            padding: 8px !important;
            margin-bottom: 14px !important;
            border: 1.5px solid #38bdf8 !important;
        }}
        div[data-testid="stTabPanel"] button[data-baseweb="tab"],
        div[role="tabpanel"] button[data-baseweb="tab"] {{
            flex: 1 1 calc(25% - 8px) !important;
            min-width: 145px !important;
            min-height: 44px !important;
            font-size: 14.5px !important;
            padding: 8px 14px !important;
        }}
        div[data-testid="stTabPanel"] button[data-baseweb="tab"] p,
        div[data-testid="stTabPanel"] button[data-baseweb="tab"] span,
        div[data-testid="stTabPanel"] button[data-baseweb="tab"] div,
        div[role="tabpanel"] button[data-baseweb="tab"] p,
        div[role="tabpanel"] button[data-baseweb="tab"] span,
        div[role="tabpanel"] button[data-baseweb="tab"] div {{
            font-size: 14.5px !important;
        }}
        /* Neutralizar botones y flechas de scroll de BaseWeb */
        div[data-baseweb="tab-list"] ~ button,
        button[aria-label="Previous tab"],
        button[aria-label="Next tab"] {{
            display: none !important;
        }}
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# CONTROL DE ACCESO Y AUTENTICACIÓN OBLIGATORIA
if auth_manager:
    auth_manager.inicializar_sesion_auth()
    usuario_actual = st.session_state.get("usuario_autenticado")
    
    # Si no hay usuario autenticado o la sesión fue cerrada, mostrar login y DETENER
    if not usuario_actual or st.session_state.get("sesion_cerrada_manual"):
        auth_manager.renderizar_pantalla_login()
        st.stop()
else:
    st.error("Error crítico: Sistema de autenticación no disponible.")
    st.stop()

# Sincronizar clave Gemini global para todos los módulos
try:
    from modulos import auditor_ia_rebt
    auditor_ia_rebt.obtener_gemini_api_key()
except Exception:
    pass

# MENÚ LATERAL - ESTILO INDUSTRIAL DARK EXECUTIVE (ALTO CONTRASTE)
# =========================================================================
with st.sidebar:
    logo_mostrado = False
    logo_b64 = usuario_actual.get("logo_base64")
    if logo_b64:
        try:
            st.image(base64.b64decode(logo_b64), use_container_width=True)
            logo_mostrado = True
        except Exception:
            pass
    if not logo_mostrado and os.path.exists("logo_electromemoria.PNG"):
        st.image("logo_electromemoria.PNG", use_container_width=True)

    st.markdown("""
        <div style="background: linear-gradient(135deg, #090d16 0%, #111d33 100%); 
                    padding: 14px; border-radius: 12px; margin-bottom: 14px; 
                    border: 1.5px solid #0284c7; box-shadow: 0 4px 16px rgba(2, 132, 199, 0.25); text-align: center;">
            <div style="font-size: 18px; font-weight: 900; color: #38bdf8; letter-spacing: 0.8px; display: flex; align-items: center; justify-content: center; gap: 8px;">
                <span>⚡</span> ELECTROMARÍN
            </div>
            <div style="color: #ffffff; font-size: 13.5px; font-weight: 800; letter-spacing: 0.5px; margin-top: 3px;">REBT PRO</div>
            <div style="color: #94a3b8; font-size: 11px; margin-top: 6px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; padding: 0 4px;">
                <span>Murcia • DGEAIM 30</span>
                <span style="background: #0284c7; color: #ffffff; padding: 2px 7px; border-radius: 5px; font-weight: 800; font-size: 10px;">v2.5 PRO</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    usuario_actual["email"] = "alvarosanchezm2006@gmail.com"
    user_email = "alvarosanchezm2006@gmail.com"

    # Panel de Instalador en Sidebar con contraste perfecto
    st.markdown(f"""
        <div style="background: #090e17; border: 1.5px solid #1e293b; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
            <div style="background: #041830; border: 1px solid #0284c7; border-radius: 7px; padding: 8px 10px; margin-bottom: 10px;">
                <div style="font-size: 10px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;">🌐 Cuenta Google Oficial</div>
                <div style="font-size: 12px; color: #ffffff; font-weight: 700; word-break: break-all; margin-top: 2px;">alvarosanchezm2006@gmail.com</div>
            </div>
            <div style="font-size: 12.5px; color: #ffffff; margin-bottom: 5px;">
                <strong style="color: #94a3b8;">Instalador:</strong> <span style="color: #38bdf8; font-weight: 700;">{usuario_actual.get('nombre_instalador', 'Álvaro Marín')}</span>
            </div>
            <div style="font-size: 12.5px; color: #ffffff; margin-bottom: 8px;">
                <strong style="color: #94a3b8;">Licencia:</strong> <span style="background: #1e293b; color: #10b981; font-weight: 700; padding: 2px 6px; border-radius: 4px; font-size: 11.5px;">{usuario_actual.get('num_licencia_rebt', 'REBT-30/15892')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_sbtn1, col_sbtn2 = st.columns(2)
    with col_sbtn1:
        if st.button("🔄 Cambiar", key="btn_switch_acc", use_container_width=True, help="Cambiar cuenta"):
            if control_salida:
                control_salida.mostrar_dialogo_cambiar_cuenta(auth_manager)
            elif auth_manager:
                auth_manager.cerrar_sesion()
    with col_sbtn2:
        if st.button("🚪 Salir", key="btn_logout_side", use_container_width=True, help="Cerrar sesión"):
            if control_salida:
                control_salida.mostrar_dialogo_confirmacion_salida(auth_manager)
            elif auth_manager:
                auth_manager.cerrar_sesion()

    # Indicador Clave Gemini
    clave_gemini_act = ""
    try:
        from modulos import auditor_ia_rebt
        clave_gemini_act = auditor_ia_rebt.obtener_gemini_api_key()
    except Exception:
        pass

    if clave_gemini_act and len(clave_gemini_act) > 8:
        enmascarada = f"{clave_gemini_act[:4]}...{clave_gemini_act[-4:]}"
        st.markdown(
            f"<div style='background-color:#052e16; border:1px solid #16a34a; border-radius:8px; padding:7px 10px; margin-bottom:8px; display:flex; align-items:center; justify-content:space-between;'>"
            f"<span style='font-size:11.5px; font-weight:800; color:#4ade80;'>🟢 Clave IA Conectada</span>"
            f"<code style='font-size:11px; color:#86efac; background:transparent;'>{enmascarada}</code></div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background-color:#1c0f13; border:1px solid #991b1b; border-radius:8px; padding:7px 10px; margin-bottom:8px;'>"
            "<span style='font-size:11.5px; font-weight:800; color:#f87171;'>⚡ IA: Sin Clave (Opcional)</span></div>",
            unsafe_allow_html=True
        )

    with st.expander("🤖 Configurar Clave IA (Gemini)", expanded=(not bool(clave_gemini_act))):
        in_key_side = st.text_input(
            "API Key Gemini:",
            value=clave_gemini_act,
            type="password",
            key="input_sidebar_gemini_key",
            help="Clave gratuita de Google AI Studio para dictado por voz y visión de cuadros"
        )
        if st.button("💾 Guardar Clave IA", key="btn_side_save_gemini", use_container_width=True, type="primary"):
            if in_key_side.strip():
                try:
                    from modulos import auditor_ia_rebt
                    auditor_ia_rebt.guardar_gemini_api_key(in_key_side.strip())
                    st.success("¡Clave guardada!")
                    st.rerun()
                except Exception as ex_k:
                    st.error(f"Error: {ex_k}")

    # Sincronización y navegación
    mod_url = st.query_params.get("modulo")
    if mod_url and ("menu_activo" not in st.session_state or st.session_state.menu_activo in ("Panel de Control", "Menú Principal", "🏠 Menú Principal", "")):
        st.session_state.menu_activo = mod_url

    if 'menu_activo' not in st.session_state:
        st.session_state.menu_activo = "Panel de Control"

    def navegar_a_modulo(modulo_destino: str):
        st.session_state.menu_activo = modulo_destino
        if modulo_destino and modulo_destino not in ("Panel de Control", "Menú Principal", "🏠 Menú Principal"):
            st.query_params["modulo"] = modulo_destino
        elif "modulo" in st.query_params:
            try:
                del st.query_params["modulo"]
            except Exception:
                pass
        st.rerun()

    grupos_menu = [
        {
            "categoria": "📊 PANEL PRINCIPAL",
            "items": [
                ("📊 Panel de Control", "Panel de Control"),
            ]
        },
        {
            "categoria": "📑 MEMORIAS & PLANOS",
            "items": [
                ("📑 Memoria Técnica (MTD 30)", "Memoria Técnica (MTD 30)"),
                ("📸 Unifilar por Foto (IA)", "Unifilar por Foto (IA)"),
            ]
        },
        {
            "categoria": "⚡ CÁLCULOS TÉCNICOS REBT",
            "items": [
                ("⚡ Cálculo Rápido (CDT & Icc)", "Cálculo Rápido (CDT & Icc)"),
                ("🏢 Previsión de Cargas (Pt)", "Previsión de Cargas (Pt)"),
                ("🔌 Línea General (LGA)", "Línea General (LGA)"),
                ("🏠 Derivación Individual (DI)", "Derivación Individual (DI)"),
                ("🚗 Línea Recarga (IRVE)", "Línea Recarga (IRVE)"),
                ("☀️ Solar Fotovoltaica", "Solar Fotovoltaica"),
                ("📖 Tablas Oficiales REBT", "Tablas REBT"),
            ]
        },
        {
            "categoria": "💼 GESTIÓN & OBRAS",
            "items": [
                ("🎙️ Presupuesto Rápido IA & Voz", "Presupuesto Rápido IA & Voz"),
                ("🏡 Presupuesto Vivienda", "Presupuesto Vivienda"),
                ("📅 Control de Obras & Cuadrilla", "Control de Obras & Cuadrilla"),
                ("👥 Gestión de Clientes (CRM)", "Gestión de Clientes (CRM)"),
            ]
        },
        {
            "categoria": "🤖 INTELIGENCIA & NORMATIVA",
            "items": [
                ("💬 Consultor IA REBT & Telecom", "Consultor IA REBT & Telecom"),
                ("📡 Radar Normativo BOE", "Radar Normativo BOE"),
                ("⚙️ Perfil del Instalador", "Perfil del Instalador"),
            ]
        }
    ]

    for grp in grupos_menu:
        st.markdown(
            f"<div style='font-size: 11px; font-weight: 800; color: #38bdf8; letter-spacing: 0.08em; "
            f"margin: 14px 0 6px 2px; text-transform: uppercase; border-bottom: 1.5px solid #1e293b; padding-bottom: 3px;'>"
            f"{grp['categoria']}</div>",
            unsafe_allow_html=True
        )
        for label, target in grp["items"]:
            es_activo = (st.session_state.menu_activo == target or 
                         (st.session_state.menu_activo in ("Panel de Control", "Menú Principal", "🏠 Menú Principal") and target == "Panel de Control"))
            btn_type = "primary" if es_activo else "secondary"
            btn_label = f"▶ {label}" if es_activo else label
            if st.button(btn_label, key=f"nav_btn_{target}", use_container_width=True, type=btn_type):
                navegar_a_modulo(target)

    seleccion_modulo = st.session_state.menu_activo

    if seleccion_modulo and seleccion_modulo not in ("Panel de Control", "Menú Principal", "🏠 Menú Principal"):
        if st.query_params.get("modulo") != seleccion_modulo:
            st.query_params["modulo"] = seleccion_modulo
    elif seleccion_modulo in ("Panel de Control", "Menú Principal", "🏠 Menú Principal") and "modulo" in st.query_params:
        try:
            del st.query_params["modulo"]
        except Exception:
            pass

# =========================================================================
# BARRA SUPERIOR UNIFICADA (RESPONSIVE FLEXBOX - NUNCA SE SOLAPA)
# =========================================================================
modulo_mostrar = seleccion_modulo if seleccion_modulo not in ("Menú Principal", "🏠 Menú Principal", "", None) else "Panel de Control"

st.markdown(f"""
<div style="background: #090e17; border: 1.5px solid #1e293b; border-radius: 10px; padding: 10px 18px; 
            margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
        <span style="font-size: 16px; font-weight: 900; color: #38bdf8; letter-spacing: 0.5px;">⚡ ELECTROMEMORIA MARÍN</span>
        <span style="background: rgba(16, 185, 129, 0.2); color: #10b981; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 5px; border: 1px solid rgba(16, 185, 129, 0.4);">
            ● REBT RD 842/2002 • DGEAIM Murcia 30
        </span>
        <span style="color: #64748b;">›</span>
        <span style="color: #ffffff; font-size: 13.5px; font-weight: 700;">{modulo_mostrar}</span>
    </div>
    <div style="color: #94a3b8; font-size: 12px; font-weight: 600;">
        👤 {usuario_actual.get('nombre_instalador', 'Álvaro Marín')} | 📍 {usuario_actual.get('localidad', 'Murcia')}
    </div>
</div>
""", unsafe_allow_html=True)

if modulo_mostrar != "Panel de Control":
    if st.button("⬅️ Volver al Panel de Control", key="btn_back_home_top"):
        navegar_a_modulo("Panel de Control")

# =========================================================================
# ENRUTADOR PRINCIPAL & PANEL DE CONTROL
# =========================================================================
es_panel_control = seleccion_modulo in ("Panel de Control", "Menú Principal", "🏠 Menú Principal", "", None)

if es_panel_control:
    # HERO EXECUTIVE BANNER - CENTRADO Y ULTRA NÍTIDO
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #090e17 0%, #0f1c30 50%, #081426 100%); 
                border: 1.5px solid #0284c7; border-radius: 14px; padding: 22px 28px; margin-bottom: 22px; 
                box-shadow: 0 6px 24px rgba(2, 132, 199, 0.2); text-align: center;">
        <div style="display: inline-block; background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; 
                    border-radius: 6px; padding: 4px 12px; font-size: 11.5px; font-weight: 800; color: #38bdf8; margin-bottom: 10px; letter-spacing: 0.5px;">
            SISTEMA INTEGRAL DE INGENIERÍA Y LEGALIZACIÓN REBT
        </div>
        <h1 style="color: #ffffff; font-size: 28px; font-weight: 900; margin: 0 0 10px 0; letter-spacing: 0.8px;">
            ⚡ ElectroMemoria MARÍN REBT
        </h1>
        <p style="color: #cbd5e1; font-size: 14.5px; margin: 0 auto; max-width: 850px; font-weight: 500; line-height: 1.6;">
            Instalador Autorizado: <strong style="color: #ffffff;">{usuario_actual.get('nombre_instalador', 'Álvaro Marín')}</strong> &nbsp;|&nbsp; 
            Empresa: <strong style="color: #38bdf8;">{usuario_actual.get('nombre_empresa', 'ELECTROMEMORIA MARÍN S.L.')}</strong> &nbsp;|&nbsp; 
            Licencia Oficial: <strong style="color: #10b981; background: #061528; padding: 2px 8px; border-radius: 4px; border: 1px solid #1e293b;">{usuario_actual.get('num_licencia_rebt', 'REBT-30/15892')}</strong>
        </p>
        <div style="margin-top: 14px; display: inline-flex; align-items: center; gap: 8px; background: #061528; border: 1px solid #0284c7; border-radius: 8px; padding: 6px 14px;">
            <span style="font-size: 14px;">🏛️</span>
            <span style="font-size: 12px; font-weight: 800; color: #ffffff;">Homologación Oficial: <strong style="color: #10b981;">DGEAIM Región de Murcia (Código 30)</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 MÉTRICAS EJECUTIVAS RESPONSIVAS (NUNCA SE CORTAN NI SE APLASTAN)
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 22px;">
        <div style="background: #090e17; border: 1.5px solid #1e293b; border-radius: 12px; padding: 18px 14px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
            <div style="font-size: 26px; margin-bottom: 4px;">🏛️</div>
            <div style="font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">MEMORIA OFICIAL</div>
            <div style="font-size: 17px; font-weight: 900; color: #38bdf8; margin: 4px 0 2px 0;">MTD 30 Murcia</div>
            <div style="font-size: 11px; color: #10b981; font-weight: 700;">100% Homologado</div>
        </div>
        <div style="background: #090e17; border: 1.5px solid #1e293b; border-radius: 12px; padding: 18px 14px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
            <div style="font-size: 26px; margin-bottom: 4px;">⚡</div>
            <div style="font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">CÁLCULO TÉCNICO</div>
            <div style="font-size: 17px; font-weight: 900; color: #38bdf8; margin: 4px 0 2px 0;">CDT, Icc & Iz</div>
            <div style="font-size: 11px; color: #10b981; font-weight: 700;">Precisión Exacta</div>
        </div>
        <div style="background: #090e17; border: 1.5px solid #1e293b; border-radius: 12px; padding: 18px 14px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
            <div style="font-size: 26px; margin-bottom: 4px;">☀️</div>
            <div style="font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">SOLAR & RECARGA</div>
            <div style="font-size: 17px; font-weight: 900; color: #38bdf8; margin: 4px 0 2px 0;">RD 244 & BT-52</div>
            <div style="font-size: 11px; color: #10b981; font-weight: 700;">Actualizado 2026</div>
        </div>
        <div style="background: #090e17; border: 1.5px solid #1e293b; border-radius: 12px; padding: 18px 14px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
            <div style="font-size: 26px; margin-bottom: 4px;">🤖</div>
            <div style="font-size: 11px; font-weight: 800; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">INTELIGENCIA REBT</div>
            <div style="font-size: 17px; font-weight: 900; color: #38bdf8; margin: 4px 0 2px 0;">Gemini & BOE</div>
            <div style="font-size: 11px; color: #10b981; font-weight: 700;">Auditoría en Línea</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ACCIONES RÁPIDAS DIRECTAS (4 BOTONES PRIMARIOS CENTRADOS)
    st.markdown("""
        <div style="font-size: 13.5px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 10px;">
            ⚡ Acciones Rápidas
        </div>
    """, unsafe_allow_html=True)
    
    act_col1, act_col2, act_col3, act_col4 = st.columns(4)
    with act_col1:
        if st.button("📑 Nueva Memoria MTD", key="quick_mtd", use_container_width=True, type="primary"):
            navegar_a_modulo("Memoria Técnica (MTD 30)")
    with act_col2:
        if st.button("📸 Unifilar por Foto", key="quick_unifilar", use_container_width=True):
            navegar_a_modulo("Unifilar por Foto (IA)")
    with act_col3:
        if st.button("🎙️ Presupuesto con Voz", key="quick_presupuesto", use_container_width=True):
            navegar_a_modulo("Presupuesto Rápido IA & Voz")
    with act_col4:
        if st.button("💬 Consultor IA REBT", key="quick_consultor", use_container_width=True):
            navegar_a_modulo("Consultor IA REBT & Telecom")

    st.write("")

    # PESTAÑAS ORGANIZADAS POR ÁREAS DE TRABAJO (LETRAS ULTRA LEGIBLES)
    tab_memorias, tab_calculos, tab_gestion, tab_ia = st.tabs([
        "📑 Memorias & Industria", 
        "⚡ Cálculos Técnicos REBT", 
        "💼 Presupuestos & Obras", 
        "🤖 Asistencia & Normativa"
    ])

    with tab_memorias:
        st.write("")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🏛️ Memoria Técnica Oficial (MTD 30)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Tramitación oficial ante la <strong>DGEAIM de la Región de Murcia (Código 30)</strong>. Auto-rellenado desde cálculos técnicos, protocolo ITC-BT-05, Esquema Unifilar oficial y exportación completa en PDF de MTD, CIE y Manual.</p>", unsafe_allow_html=True)
                if st.button("Abrir Memoria Técnica Oficial", key="card_mtd", type="primary", use_container_width=True):
                    navegar_a_modulo("Memoria Técnica (MTD 30)")

        with col_m2:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>📸 Unifilar por Foto (Visión IA REBT)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Genera el esquema unifilar completo a partir de una foto del cuadro eléctrico. La IA reconoce <strong>IGA, protector de sobretensiones, diferenciales y PIAs</strong>, audita la regla de 5 circuitos por diferencial (ITC-BT-25) y exporta en PDF y PNG.</p>", unsafe_allow_html=True)
                if st.button("Abrir Unifilar por Foto", key="card_unifilar", use_container_width=True):
                    navegar_a_modulo("Unifilar por Foto (IA)")

    with tab_calculos:
        st.write("")
        tc1, tc2 = st.columns(2)
        with tc1:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🧮 Cálculo Rápido de Secciones (CDT & Icc)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Dimensionamiento reglamentario por caída de tensión y comprobación térmica (Iz). Comprobación de cortocircuito máximo y mínimo y curva de disparo del automático.</p>", unsafe_allow_html=True)
                if st.button("Abrir Cálculo Rápido", key="card_cr", use_container_width=True):
                    navegar_a_modulo("Cálculo Rápido (CDT & Icc)")

            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🏢 Previsión de Cargas (Pt) - ITC-BT-10</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Cálculo analítico de potencia total del edificio. Viviendas de grado básico y elevado, locales comerciales, oficinas, garajes y servicios generales con factores de simultaneidad.</p>", unsafe_allow_html=True)
                if st.button("Abrir Previsión de Cargas", key="card_pc", use_container_width=True):
                    navegar_a_modulo("Previsión de Cargas (Pt)")

            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🔌 Línea General de Alimentación (LGA)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Dimensionamiento según ITC-BT-14. Conductores de Cobre y Aluminio, centralización de contadores, cálculo de caídas al 0.5% o 1% y tubos normalizados.</p>", unsafe_allow_html=True)
                if st.button("Abrir Módulo LGA", key="card_lga", use_container_width=True):
                    navegar_a_modulo("Línea General (LGA)")

        with tc2:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🏠 Derivación Individual (DI) - ITC-BT-15</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Cálculo de enlaces a vivienda. Comprobación de límite de caída de tensión (1.5%), fusible de protección, IGA correspondiente y sección mínima reglamentaria.</p>", unsafe_allow_html=True)
                if st.button("Abrir Derivación Individual", key="card_di", use_container_width=True):
                    navegar_a_modulo("Derivación Individual (DI)")

            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>☀️ Solar Fotovoltaica (RD 244/2019 / BT-40)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Dimensionamiento de ingeniería y campo: cálculo térmico de strings (-5ºC a 70ºC), compatibilidad MPPT, cable H1Z2Z2-K, cuadro AC/DC y estimación solar de Murcia.</p>", unsafe_allow_html=True)
                if st.button("Abrir Solar Fotovoltaica", key="card_pv", use_container_width=True):
                    navegar_a_modulo("Solar Fotovoltaica")

            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🚗 Recarga de Vehículo Eléctrico (IRVE)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Circuitos terminales según ITC-BT-52. Esquemas normalizados 1, 2, 3a, 3b y 4, cálculo de caída al 1% y protecciones diferenciales Clase A superinmunizadas o Tipo B.</p>", unsafe_allow_html=True)
                if st.button("Abrir Módulo IRVE", key="card_irve", use_container_width=True):
                    navegar_a_modulo("Línea Recarga (IRVE)")

        with st.container(border=True):
            st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>📖 Tablas Oficiales del REBT</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Consulta rápida de tablas reglamentarias de intensidades admisibles (ITC-BT-19), factores de corrección por agrupamiento, temperatura ambiente y tipos de aislamiento.</p>", unsafe_allow_html=True)
            if st.button("Consultar Tablas REBT", key="card_tablas", use_container_width=True):
                navegar_a_modulo("Tablas REBT")

    with tab_gestion:
        st.write("")
        tg1, tg2 = st.columns(2)
        with tg1:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🎙️ Presupuesto Rápido (IA & Dictado por Voz)</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Presupuesta trabajos y reformas dictando por micrófono o escribiendo. La IA desglosa automáticamente materiales, mano de obra, tiempos estimados y margen con/sin IVA.</p>", unsafe_allow_html=True)
                if st.button("Abrir Presupuesto Rápido IA", key="card_pr", type="primary", use_container_width=True):
                    navegar_a_modulo("Presupuesto Rápido IA & Voz")

            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>🏡 Presupuesto Completo de Vivienda</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Inspector REBT ITC-BT-25, metraje de rozas, tubo corrugado, líneas de cableado libre de halógenos y mecanismos. Exportación a presupuestos de cliente y acopio.</p>", unsafe_allow_html=True)
                if st.button("Abrir Presupuesto Vivienda", key="card_pv_viv", use_container_width=True):
                    navegar_a_modulo("Presupuesto Vivienda")

        with tg2:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>📅 Control de Obras, Calendario & Cuadrilla</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Control integral de obras: asigna trabajos para ti o con tu compañero de cuadrilla, anota compras de material y tickets deducibles, y visualiza el reparto de beneficios.</p>", unsafe_allow_html=True)
                if st.button("Abrir Control de Obras", key="card_obras", use_container_width=True):
                    navegar_a_modulo("Control de Obras & Cuadrilla")

            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>👥 Gestión de Clientes (CRM) & Expedientes</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Administración de fichas de clientes, NIF, teléfonos, dirección de suministro, CUPS y expedientes técnicos vinculados para recuperar cálculos en 1 clic.</p>", unsafe_allow_html=True)
                if st.button("Abrir Gestión de Clientes", key="card_crm", use_container_width=True):
                    navegar_a_modulo("Gestión de Clientes (CRM)")

    with tab_ia:
        st.write("")
        tia1, tia2 = st.columns(2)
        with tia1:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>💬 Consultor IA Experto REBT & Telecom</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Asesor reglamentario permanente con visión de Ingeniero y Maestro Instalador. Resuelve dudas del REBT, ICT-2 (RD 346/2011), fibra FTTH, cableado Cat6 y normativas DGEAIM.</p>", unsafe_allow_html=True)
                if st.button("Consultar Asesor IA", key="card_asistente_ia", type="primary", use_container_width=True):
                    navegar_a_modulo("Consultor IA REBT & Telecom")

        with tia2:
            with st.container(border=True):
                st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>📡 Radar Normativo BOE en Directo</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Vigilancia legislativa conectada a la API de Datos Abiertos del BOE. Monitoriza reformas en el REBT, autoconsumo, vehículo eléctrico y CTE con análisis de impacto con IA.</p>", unsafe_allow_html=True)
                if st.button("Abrir Radar BOE", key="card_radar", use_container_width=True):
                    navegar_a_modulo("Radar Normativo BOE")

        with st.container(border=True):
            st.markdown("<h3 style='color: #38bdf8; margin-top: 0;'>⚙️ Perfil del Instalador y Logotipo</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #e2e8f0; font-size: 14px; line-height: 1.6;'>Configura tus datos fiscales oficiales: Razón Social, CIF, número de instalador autorizado, tarifas de mano de obra por hora, logotipo corporativo y copias de seguridad.</p>", unsafe_allow_html=True)
            if st.button("Abrir Perfil del Instalador", key="card_perfil", use_container_width=True):
                navegar_a_modulo("Perfil del Instalador")

# =========================================================================
# ENRUTADOR DE MÓDULOS (COMPATIBLE CON NOMBRES LIMPIOS Y PREVIOS)
# =========================================================================
elif "Memoria" in seleccion_modulo or "MTD" in seleccion_modulo or "🏛️" in seleccion_modulo or "Industria" in seleccion_modulo:
    if memoria_tecnica_industria:
        memoria_tecnica_industria.renderizar()
    else:
        st.error("Módulo de Memoria Técnica Oficial (Industria DGEAIM) no disponible.")
        if "memoria_tecnica_industria" in errores_import:
            st.code(errores_import["memoria_tecnica_industria"])

elif "Unifilar" in seleccion_modulo or "📸" in seleccion_modulo or "Foto" in seleccion_modulo:
    if unifilar_foto:
        unifilar_foto.render_modulo_unifilar_foto()
    else:
        st.error("Módulo Unifilar por Foto no disponible.")
        if "unifilar_foto" in errores_import:
            st.code(errores_import["unifilar_foto"])

elif "Cálculo Rápido" in seleccion_modulo or "Calculo Rapido" in seleccion_modulo or "🧮" in seleccion_modulo or "CDT" in seleccion_modulo or (seleccion_modulo.startswith("⚡") and "Cálculo" in seleccion_modulo):
    if calculo_rapido:
        calculo_rapido.renderizar()
    else:
        st.error("Módulo Cálculo Rápido no disponible.")
        if "calculo_rapido" in errores_import:
            st.code(errores_import["calculo_rapido"])

elif "Previsión" in seleccion_modulo or "Prevision" in seleccion_modulo or "🏢" in seleccion_modulo or "(Pt)" in seleccion_modulo:
    if prevision_cargas:
        prevision_cargas.renderizar()
    else:
        st.error("Módulo Previsión de Cargas no disponible.")
        if "prevision_cargas" in errores_import:
            st.code(errores_import["prevision_cargas"])

elif "LGA" in seleccion_modulo or "Línea General" in seleccion_modulo or "Linea General" in seleccion_modulo:
    if lga:
        lga.renderizar()
    else:
        st.error("Módulo LGA no disponible.")
        if "lga" in errores_import:
            st.code(errores_import["lga"])

elif "DI" in seleccion_modulo or "Derivación" in seleccion_modulo or "Derivacion" in seleccion_modulo or "🔌" in seleccion_modulo or "Individual" in seleccion_modulo:
    if di:
        di.renderizar()
    else:
        st.error("Módulo DI no disponible.")
        if "di" in errores_import:
            st.code(errores_import["di"])

elif "IRVE" in seleccion_modulo or "Recarga" in seleccion_modulo or "🚗" in seleccion_modulo:
    if irve:
        irve.renderizar()
    else:
        st.error("Módulo IRVE no disponible.")
        if "irve" in errores_import:
            st.code(errores_import["irve"])

elif "Solar" in seleccion_modulo or "☀️" in seleccion_modulo or "Fotovoltaica" in seleccion_modulo:
    if fotovoltaica:
        fotovoltaica.renderizar()
    else:
        st.error("Módulo de Solar Fotovoltaica no disponible.")
        if "fotovoltaica" in errores_import:
            st.code(errores_import["fotovoltaica"])

elif "Tablas" in seleccion_modulo or "📚" in seleccion_modulo or "📖" in seleccion_modulo:
    if tablas_normativas:
        tablas_normativas.renderizar()
    else:
        st.error("Módulo de Tablas Normativas no disponible.")
        if "tablas_normativas" in errores_import:
            st.code(errores_import["tablas_normativas"])

elif "Presupuesto Rápido" in seleccion_modulo or "Presupuesto Rapido" in seleccion_modulo or "🎙️" in seleccion_modulo or "IA & Voz" in seleccion_modulo or "Voz" in seleccion_modulo:
    if presupuesto_rapido_ia:
        try:
            presupuesto_rapido_ia.renderizar()
        except Exception as e:
            st.error(f"⚠️ Ocurrió una incidencia en el módulo de Presupuesto Rápido: {e}")
            import traceback
            st.code(traceback.format_exc())
            if st.button("🔄 Reiniciar módulo de presupuesto rápido", key="btn_reset_pr_error"):
                for k in list(st.session_state.keys()):
                    if k.startswith("pr_") or k.startswith("prm_"):
                        del st.session_state[k]
                st.rerun()
    else:
        st.error("Error: El módulo presupuesto_rapido_ia no se pudo importar correctamente.")
        if "presupuesto_rapido_ia" in errores_import:
            st.code(errores_import["presupuesto_rapido_ia"])

elif "Autónomo" in seleccion_modulo or "Autonomo" in seleccion_modulo or "🧑‍🔧" in seleccion_modulo:
    st.session_state['perfil_tarifa_autonomo'] = True
    if presupuesto_vivienda:
        presupuesto_vivienda.renderizar()
    else:
        st.error("Error: El módulo presupuesto_vivienda no se pudo importar correctamente.")
        if "presupuesto_vivienda" in errores_import:
            st.code(errores_import["presupuesto_vivienda"])

elif "Presupuesto" in seleccion_modulo or "🏡" in seleccion_modulo or "Vivienda" in seleccion_modulo:
    st.session_state['perfil_tarifa_autonomo'] = False
    if presupuesto_vivienda:
        presupuesto_vivienda.renderizar()
    else:
        st.error("Error: El módulo presupuesto_vivienda no se pudo importar correctamente.")
        if "presupuesto_vivienda" in errores_import:
            st.code(errores_import["presupuesto_vivienda"])

elif "Control de Obras" in seleccion_modulo or "Planificación" in seleccion_modulo or "Planificacion" in seleccion_modulo or "📅" in seleccion_modulo or "Cuadrilla" in seleccion_modulo or "Obras" in seleccion_modulo:
    if control_obras:
        control_obras.renderizar()
    else:
        st.error("Módulo Control de Obras no disponible.")
        if "control_obras" in errores_import:
            st.code(errores_import["control_obras"])

elif "Clientes" in seleccion_modulo or "CRM" in seleccion_modulo or "👥" in seleccion_modulo:
    if gestion_clientes:
        gestion_clientes.renderizar()
    else:
        st.error("Módulo de Gestión de Clientes no disponible.")

elif "Consultor IA" in seleccion_modulo or "💬" in seleccion_modulo or "🤖" in seleccion_modulo or "Telecom" in seleccion_modulo:
    if asistente_ia_rebt:
        asistente_ia_rebt.render_interfaz_asistente_rebt()
    else:
        st.error("Módulo Consultor IA REBT no disponible.")
        if "asistente_ia_rebt" in errores_import:
            st.code(errores_import["asistente_ia_rebt"])

elif "Radar" in seleccion_modulo or "🛰️" in seleccion_modulo or "📡" in seleccion_modulo or "Normativo" in seleccion_modulo or "BOE" in seleccion_modulo:
    if radar_normativo:
        radar_normativo.renderizar()
    else:
        st.error("Módulo de Radar Normativo BOE no disponible.")
        if "radar_normativo" in errores_import:
            st.code(errores_import["radar_normativo"])

elif "Perfil" in seleccion_modulo or "👤" in seleccion_modulo or "⚙️" in seleccion_modulo or "Instalador" in seleccion_modulo:
    if perfil_instalador:
        perfil_instalador.renderizar()
    else:
        st.error("Módulo de Perfil del Instalador no disponible.")
