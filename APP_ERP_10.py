import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN E INTERFAZ MÓVIL ---
st.set_page_config(page_title="SGO Flota Maquehue", page_icon="🚛", layout="centered")

# --- BASE DE DATOS CENTRALIZADA EN LA NUBE (SESSION STATE) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario = ""

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base = -38.7396
    lon_base = -72.6019
    
    for i in range(1, 11):
        kms_actuales = random.randint(500000, 580000)
        # Calcular cuándo le toca la próxima mantención de 10,000 Km
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "Mercedes-Benz Actros 4144 Tolva",
            "kms": kms_actuales,
            "horas": random.randint(18000, 22000),
            "lat": lat_base + random.uniform(-0.05, 0.05),
            "lon": lon_base + random.uniform(-0.05, 0.05),
            "estado": "OPERATIVO",
            "kms_para_mantencion": kms_restantes,
            "db_comb": [
                {"Fecha": "2026-06-28", "Litros": "320 L", "Costo": "$352,000", "Rendimiento": "1.2 Km/L"},
                {"Fecha": "2026-07-01", "Litros": "280 L", "Costo": "$308,000", "Rendimiento": "1.3 Km/L"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0941", "Tipo": "Preventiva", "Detalle": "Cambio pauta de filtros de aire y combustible", "Estado": "Cerrada", "Fecha": "2026-06-15"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Faena Áridos Maquehue", "Destino": "Obra Inacap Temuco", "Distancia": "14 Km", "Estado": "Completada"},
                {"Fecha": str(datetime.date.today()), "Origen": "Obra Inacap Temuco", "Destino": "Planta de Lavado", "Distancia": "22 Km", "Estado": "En Ruta"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- ACCESO AL SISTEMA ---
if not st.session_state.conectado:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=70)
    st.title("🚛 SGO Cloud - Áridos Maquehue")
    st.caption("Sistema de Gestión Operativa y Mantenimiento de Flota")
    
    usuario = st.text_input("Usuario (Rut/ID)", value="admin1")
    clave = st.text_input("Contraseña Operativa", type="password", value="inacap2026")
    
    if st.button("Iniciar Sesión Servidor AWS", type="primary", use_container_width=True):
        if usuario in ["admin1", "supervisor_taller"] and clave == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("❌ Credenciales inválidas.")

# --- ENTRADA AL ERP ---
else:
    st.write(f"🟢 **Servidor Activo** | Supervisor: `{st.session_state.usuario}`")
    
    # Selector de Unidades
    lista_desplegable = [f"{c['id']} [Patente: {c['patente']}]" for c in st.session_state.flota]
    camion_idx = st.selectbox("Seleccionar Camión Actros para Auditoría:", range(10), format_func=lambda x: lista_desplegable[x])
    camion_sel = st.session_state.flota[camion_idx]
    
    st.header(f"🚛 {camion_sel['id']} - Mod. {camion_sel['modelo']}")
    
    # Estructura de navegación solicitada por el Profesor
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Panel", 
        "📍 GPS y Rutas", 
        "📋 Checklist Diario", 
        "🛠️ Órdenes Taller", 
        "⛽ Combustible",
        "📊 Informes"
    ])
    
    # 1. TAB PANEL (MÓDULO DE ALERTAS DE MANTENCIÓN PERIÓDICA)
    with tab1:
        st.subheader("Telemetría del Motor y Alertas")
        col1, col2 = st.columns(2)
        col1.metric("Odómetro CAN-Bus", f"{camion_sel['kms']:,} Km")
        col2.metric("Horómetro de Trabajo", f"{camion_sel['horas']:,} Hrs")
        
        # Lógica de Alertas Periódicas Automáticas
        st.markdown("### ⏰ Alertas de Mantención Periódica")
        restantes = camion_sel['kms_para_mantencion']
        
        if restantes <= 0:
            st.error(f"🚨 ALERTAS CRÍTICA: ¡MANTENCIÓN VENCIDA HACE {abs(restantes)} KM! Se requiere detención inmediata e ingreso a taller.")
        elif restantes < 1000:
            st.warning(f"⚠️ ALERTA PREVENTIVA: Próximo Cambio de Aceite y Filtros en {restantes} Km. Agendar taller.")
        else:
            st.success(f"✅ Motor Estable: Faltan {restantes:,} Km para la pauta de mantención periódica estándar (Cada 10k Km).")
            
        if camion_sel['estado'] == "OPERATIVO":
            st.info("🟢 Estado Operativo: LIBRE DE RESTRICCIONES EN RUTA")
        else:
            st.error("🔴 Estado Operativo: RESTRINGUIDO - BLOQUEADO EN TALLER")

    # 2. TAB GPS Y RUTAS (MÓDULO DE INFORMES DE RUTAS)
    with tab2:
        st.subheader("📍 Georreferenciación e Informe de Rutas")
        
        # Mapa global de los 10 puntos
        coords_flota = [{"lat": c["lat"], "lon": c["lon"]} for c in st.session_state.flota]
        st.map(pd.DataFrame(coords_flota), zoom=10)
        
        st.markdown("### 📋 Informe de Rutas Diarias (Logística)")
        st.write("Historial de tránsitos registrados por el dispositivo GPS el día de hoy:")
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)
        
        if st.button("Simular Recorrido en Ruta 🔄", use_container_width=True):
            camion_sel['kms'] += random.randint(15, 45)
            camion_sel['kms_para_mantencion'] -= random.randint(15, 45)
            camion_sel['lat'] += random.uniform(-0.005, 0.005)
            camion_sel['lon'] += random.uniform(-0.005, 0.005)
            st.rerun()

    # 3. TAB CHECKLIST (INSPECCIÓN DIARIA DE CONTROL PRE-USO)
    with tab3:
        st.subheader("📋 Checklist Diario de Control de Seguridad")
        st.write("El conductor debe declarar el estado de los componentes antes de salir de faena.")
        st.write(f"Unidad Evaluada: **{camion_sel['patente']}**")
        
        st.markdown("**Marque los sistemas que están en BUEN ESTADO:**")
        chk_frenos = st.checkbox("Sistemas de Frenos y Presión de Aire OK", value=True, key="c1")
        chk_direccion = st.checkbox("Dirección Hidráulica y Servoasistencia OK", value=True, key="c2")
        chk_neumaticos = st.checkbox("Neumáticos (Tuercas de torque y bandas) OK", value=True, key="c3")
        chk_hidraulico = st.checkbox("Sistema Hidráulico de Tolva (Sin fugas) OK", value=True, key="c4")
        chk_luces = st.checkbox("Luces, Cinturón y Alarmas de retroceso OK", value=True, key="c5")
        
        if st.button("Enviar Registro de Inspección", type="primary", use_container_width=True):
            # Si falta marcar un checklist como BUENO, hay falla crítica
            if not all([chk_frenos, chk_direccion, chk_neumaticos, chk_hidraulico, chk_luces]):
                camion_sel['estado'] = "BLOQUEADO"
                st.error("🚨 INSPECCIÓN RECHAZADA: Se han detectado fallas operativas. El camión ha sido bloqueado en el ERP central. Proceda a generar una Orden de Taller.")
            else:
                camion_sel['estado'] = "OPERATIVO"
                st.success("✅ INSPECCIÓN APROBADA: Unidad en perfectas condiciones mecánicas para transitar.")

    # 4. TAB ÓRDENES DE TALLER (GENERADOR DE ORDENES DE TRABAJO - OT)
    with tab4:
        st.subheader("🛠️ Panel de Gestión: Órdenes de Taller")
        
        st.markdown("### ➕ Generar Nueva Orden de Taller")
        tipo_ot = st.selectbox("Tipo de Intervención:", ["Correctiva Crítica", "Preventiva Programada", "Predictiva / Análisis"])
        detalle_falla = st.text_area("Descripción de los Trabajos / Falla reportada:", placeholder="Ej: Pérdida de presión en balatas del tercer eje...")
        mecanico = st.text_input("Mecánico Especialista Asignado:", value="Taller Kaufmann Temuco")
        
        if st.button("Emitir Orden de Taller", type="primary", use_container_width=True):
            if detalle_falla:
                nueva_ot = {
                    "ID_OT": f"OT-{random.randint(1000, 9999)}",
                    "Tipo": tipo_ot,
                    "Detalle": detalle_falla,
                    "Estado": "Abierta / En Proceso",
                    "Fecha": str(datetime.date.today())
                }
                camion_sel['db_ot'].append(nueva_ot)
                st.success(f"📋 {nueva_ot['ID_OT']} emitida exitosamente en la base de datos cloud.")
            else:
                st.warning("Por favor describa el trabajo para poder aperturar la OT.")
                
        st.markdown("### 📂 Historial de Órdenes del Camión")
        if len(camion_sel['db_ot']) > 0:
            st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
            if st.button("Liberar Camión y Cerrar Órdenes Activas 🔓", use_container_width=True):
                for ot in camion_sel['db_ot']:
                    ot["Estado"] = "Cerrada"
                camion_sel['estado'] = "OPERATIVO"
                camion_sel['kms_para_mantencion'] = 10000 # Resetea la alerta de mantención periódica
                st.success("Unidad reparada con éxito. Estado actualizado a OPERATIVO.")
        else:
            st.write("No registra órdenes de reparación históricas.")

    # 5. TAB COMBUSTIBLE (GENERADOR DE DATOS DE CONSUMO)
    with tab5:
        st.subheader("⛽ Módulo de Control de Abastecimiento de Diésel")
        litros = st.number_input("Cantidad de Litros Cargados:", min_value=0, step=20)
        monto = st.number_input("Gasto de Combustible ($):", min_value=0, step=10000)
        
        if st.button("Registrar Carga de Combustible", type="primary", use_container_width=True):
            if litros > 0 and monto > 0:
                nueva_carga = {
                    "Fecha": str(datetime.date.today()),
                    "Litros": f"{litros} L",
                    "Costo": f"${monto:,}",
                    "Rendimiento": f"{round(random.uniform(1.1, 1.4), 1)} Km/L"
                }
                camion_sel['db_comb'].append(nueva_carga)
                st.success("Transacción de Combustible guardada.")
                
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. TAB INFORMES (INFORMES DE MANTENCIÓN CONSOLIDADOS)
    with tab6:
        st.subheader("📊 Informe Ejecutivo de Mantenimiento de Flota")
        st.write("Datos analíticos consolidados generados dinámicamente para la jefatura:")
        
        col_inf1, col_inf2 = st.columns(2)
        col_inf1.metric("Órdenes de Trabajo Ejecutadas", len(camion_sel['db_ot']))
        col_inf2.metric("Cargas de Combustible Registradas", len(camion_sel['db_comb']))
        
        st.markdown("#### 📝 Resumen del Informe Técnico")
        st.markdown(f"""
        - **Indicador Técnico de la Unidad:** El equipo `{camion_sel['id']}` registra un kilometraje acumulado de **{camion_sel['kms']:,} Km**.
        - **Estado Físico Actual:** Actualmente la unidad se encuentra clasificada como **{camion_sel['estado']}**.
        - **Mantenibilidad Periódica:** Al vehículo le restan **{camion_sel['kms_para_mantencion']:,} Km** para cumplir su próximo ciclo de mantenimiento preventivo crítico.
        - **Logística Operativa:** El camión registra un total de **{len(camion_sel['rutas'])} rutas controladas por GPS** en el presente ciclo operativo diario.
        """)
        
        st.button("📥 Descargar Informe Completo en PDF (Simulado)", use_container_width=True)

    st.divider()
    if st.button("Cerrar Sesión de Forma Segura", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()
