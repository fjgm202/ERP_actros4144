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
    lat_base = -38.7396
    lon_base = -72.6019
    
    for i in range(1, 11):
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "kms": random.randint(500000, 580000),
            "horas": random.randint(18000, 22000),
            "lat": lat_base + random.uniform(-0.06, 0.06),
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
    
    nombres_camiones = [f"{c['id']} (Patente: {c['patente']})" for c in st.session_state.flota]
    camion_idx = st.selectbox("Seleccione Vehículo para Auditoría:", range(10), format_func=lambda x: nombres_camiones[x])
    camion_actual = st.session_state.flota[camion_idx]
    
    st.header(f"🚛 {camion_actual['id']}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dash", "📍 GPS Flota", "⛽ Comb", "📋 Check", "📊 Matriz"])
    
    # MÓDULO 1: DASHBOARD
    with tab1:
        st.subheader("Resumen de Operación")
        col1, col2 = st.columns(2)
        col1.metric("Odómetro CAN-Bus", f"{camion_actual['kms']:,} Km")
        col2.metric("Horómetro Motor", f"{camion_actual['horas']:,} Hrs")
        
        if camion_actual['estado'] == "OPERATIVO":
            st.info("🟢 ESTADO: OPERATIVO Y AUTORIZADO")
        else:
            st.error("🔴 ESTADO: BLOQUEADO POR FALLA CRÍTICA")

    # MÓDULO 2: GPS GLOBAL
    with tab2:
        st.subheader("Radar Satelital de Flota Completa")
        st.write("El mapa muestra la ubicación en tiempo real de los 10 camiones Actros.")
        coords = [{"lat": c["lat"], "lon": c["lon"]} for c in st.session_state.flota]
        df_mapa = pd.DataFrame(coords)
        st.map(df_mapa, zoom=11)
        if st.button("Simular Movimiento de Toda la Flota 🔄", use_container_width=True):
            for c in st.session_state.flota:
                c["kms"] += random.randint(2, 10)
                c["lat"] += random.uniform(-0.002, 0.002)
                c["lon"] += random.uniform(-0.002, 0.002)
            st.rerun()

    # MÓDULO 3: COMBUSTIBLE
    with tab3:
        st.subheader(f"Carga de Diésel - {camion_actual['patente']}")
        litros = st.number_input("Litros Cargados", min_value=0, step=10, key="litros")
        costo = st.number_input("Costo Total ($)", min_value=0, step=5000, key="costo")
        if st.button("Guardar Registro", type="primary", use_container_width=True):
            if litros > 0 and costo > 0:
                nuevo_reg = {
                    "Fecha": str(datetime.date.today()),
                    "Litros": f"{litros} L",
                    "Costo": f"${costo:,}",
                    "Rendimiento": f"{round(random.uniform(1.1, 1.4), 1)} Km/L",
                    "Operador": st.session_state.usuario
                }
                camion_actual["db_comb"].append(nuevo_reg)
                st.success(f"Guardado exitosamente para el {camion_actual['id']}.")
        
        st.write("**Historial de Cargas de este equipo:**")
        if len(camion_actual["db_comb"]) > 0:
            st.dataframe(pd.DataFrame(camion_actual["db_comb"]), use_container_width=True)
        else:
            st.write("No hay registros de carga para este camión aún.")

    # MÓDULO 4: CHECKLIST
    with tab4:
        st.subheader("Inspección Pre-Uso")
        st.write(f"Evaluando: **{camion_actual['patente']}**")
        f1 = st.checkbox("Frenos y Sistema Neumático (Campanas, balatas)", key="f1")
        f2 = st.checkbox("Chasis, Grapas y Suspensión Parabólica", key="f2")
        f3 = st.checkbox("Niveles de Motor (Aceite, O-Rings)", key="f3")
        f4 = st.checkbox("Sistema Hidráulico (Pistón de tolva)", key="f4")
        f5 = st.checkbox("Neumáticos y Tuercas", key="f5")
        if st.button("Enviar Evaluación", type="primary", use_container_width=True):
            if any([f1, f2, f3, f4, f5]):
                camion_actual['estado'] = "BLOQUEADO"
                st.error("🚨 FALLA CRÍTICA DETECTADA: Vehículo bloqueado.")
            else:
                camion_actual['estado'] = "OPERATIVO"
                st.success("✅ Aprobado: Vehículo autorizado para operar.")

    # MÓDULO 5: CRITICIDAD
    with tab5:
        st.subheader("Matriz Kaufmann (FxF)")
        datos_crit = [
            {"Sistema": "Frenos", "F": 4, "I": 5, "Total": 20, "Riesgo": "🔴 CRÍTICO"},
            {"Sistema": "Chasis", "F": 4, "I": 4, "Total": 16, "Riesgo": "🔴 CRÍTICO"},
            {"Sistema": "Hidráulico", "F": 3, "I": 5, "Total": 15, "Riesgo": "🔴 CRÍTICO"},
            {"Sistema": "Motor", "F": 3, "I": 4, "Total": 12, "Riesgo": "🟡 MEDIO"},
            {"Sistema": "Eléctrico", "F": 2, "I": 3, "Total": 6, "Riesgo": "🟢 BAJO"}
        ]
        st.dataframe(pd.DataFrame(datos_crit), use_container_width=True)
        
    st.divider()
    if st.button("Cerrar Sesión Segura", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()
