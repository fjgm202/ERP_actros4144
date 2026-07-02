import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN PARA CELULARES ---
st.set_page_config(page_title="ERP Flota Maquehue", page_icon="🚛", layout="centered")

# --- BASE DE DATOS EN LA NUBE: FLOTA DE 10 CAMIONES ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario = ""

if 'flota' not in st.session_state:
    flota_inicial = []
    # Coordenadas base en Temuco/Maquehue
    lat_base = -38.7396
    lon_base = -72.6019
    
    for i in range(1, 11):
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "kms": random.randint(500000, 580000),
            "horas": random.randint(18000, 22000),
            "lat": lat_base + random.uniform(-0.06, 0.06), # Posiciones esparcidas
            "lon": lon_base + random.uniform(-0.06, 0.06),
            "estado": "OPERATIVO",
            "db_comb": []
        })
    st.session_state.flota = flota_inicial

# --- PANTALLA DE LOGIN ---
if not st.session_state.conectado:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=80)
    st.title("🏭 ERP Cloud - Flota Maquehue")
    st.write("Autenticación segura requerida (AWS)")
    
    usuario = st.text_input("Usuario Corporativo", value="admin1")
    clave = st.text_input("Contraseña", type="password", value="inacap2026")
    
    if st.button("Conectar al Servidor Remoto", type="primary", use_container_width=True):
        if usuario in ["admin1", "jefe_taller"] and clave == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

# --- INTERFAZ PRINCIPAL DEL ERP ---
else:
    st.success(f"🌐 Conectado | Operador: {st.session_state.usuario} | Flota Total: 10 Equipos")
    
    # Selector de Camión
    nombres_camiones = [f"{c['id']} (Patente: {c['patente']})" for c in st.session_state.flota]
    camion_idx = st.selectbox("Seleccione Vehículo para Auditoría:", range(10), format_func=lambda x: nombres_camiones[x])
    
    # Obtener los datos del camión seleccionado
    camion_actual = st.session_state.flota[camion_idx]
    
    st.header(f"🚛 {camion_actual['id']}")
    
    # Pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dash", "📍 GPS Flota", "⛽ Comb", "📋 Check", "📊 Matriz"])
    
    # MÓDULO 1: DASHBOARD
    with tab1:
        st.subheader("Resumen de Operación")
        col1, col2 = st.columns(2)
        col1.metric("Odómetro CAN-Bus", f"{camion_actual['kms']:,} Km")
        col2.metric("Horómetro Motor", f"{camion_actual['horas']:,} Hrs")
