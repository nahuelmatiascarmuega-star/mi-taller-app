import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración del sistema
st.set_page_config(page_title="Negocio Técnico Matías", page_icon="🔧", layout="wide")

# --- CONEXIÓN DIRECTA POR ENLACE ABIERTO (EVITA EL CACHÉ DE GOOGLE) ---
# Extraemos el ID único de tu documento para leerlo sin intermediarios
SHEET_ID = "1z9kT1uHJVZuFXCWH9-SmTS9dNGQcuUxgbIReNxvCB3E"

def cargar_datos_directos():
    try:
        # Enlaces de descarga directa en formato CSV para saltar el bloqueo de Google
        url_trabajos = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Trabajos"
        url_clientes = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Clientes"
        url_caja = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Caja"
        
        # Lectura directa de las hojas
        t = pd.read_csv(url_trabajos).fillna("")
        c = pd.read_csv(url_clientes).fillna("")
        caj = pd.read_csv(url_caja).fillna("")
        
        return t, c, caj
    except Exception as e:
        st.error(f"Asegúrate de que el botón 'Compartir' en tu Google Sheets esté configurado como 'Cualquier persona con el enlace puede editar'. Error: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_trabajos, df_clientes, df_caja = cargar_datos_directos()

# Limpieza rápida de nombres de columnas (borra el símbolo # y espacios que agrega Google)
for df in [df_trabajos, df_clientes, df_caja]:
    if not df.empty:
        df.columns = df.columns.str.replace('#', '').str.strip()

# Convertir columnas clave a números para que el Dashboard no falle
columnas_numericas = ["Precio Cobrado", "Costo Repuesto", "Otros Costos", "Ganancia", "Seña", "Saldo"]
for col in columnas_numericas:
    if not df_trabajos.empty and col in df_trabajos.columns:
        df_trabajos[col] = pd.to_numeric(df_trabajos[col], errors='coerce').fillna(0)

# Menú de navegación lateral
menu = st.sidebar.radio("Navegación", ["📊 Dashboard Resumen", "🔧 Control de Trabajos", "👥 Base de Clientes", "💰 Caja Diaria"])

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Alertas Rápidas")
if not df_trabajos.empty and "Saldo" in df_trabajos.columns:
    saldos_pendientes = df_trabajos[df_trabajos["Saldo"] > 0]
    st.sidebar.warning(f"💵 Clientes con Saldo Pendiente: {len(saldos_pendientes)}")

# ==========================================
# 1. DASHBOARD RESUMEN
# ==========================================
if menu == "📊 Dashboard Resumen":
    st.title("📊 Resumen General del Negocio")
    st.markdown("---")
    
    if not df_trabajos.empty:
        total_trabajos = len(df_trabajos)
        facturacion_total = df_trabajos["Precio Cobrado"].sum()
        ganancia_total = df_trabajos["Ganancia"].sum()
        senas_cobradas = df_trabajos["Seña"].sum()
        saldos_totales = df_trabajos["Saldo"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🔧 Total Trabajos", total_trabajos)
        col2.metric("💵 Facturación Total", f"${facturacion_total:,.2f}")
        col3.metric("💰 Ganancia Total", f"${ganancia_total:,.2f}")
        
        st.markdown("---")
        col4, col5, col6 = st.columns(3)
        col4.metric("📥 Señas Cobradas", f"${senas_cobradas:,.2f}")
        col5.metric("⏳ Saldos Pendientes", f"${saldos_totales:,.2f}")
        
        if "Rubro" in df_trabajos.columns and not df_trabajos["Rubro"].mode().empty:
            col6.metric("🏆 Rubro más Frecuente", df_trabajos["Rubro"].mode().iloc[0])
    else:
        st.info("Aún no hay datos cargados en la pestaña 'Trabajos'.")

# ==========================================
# 2. CONTROL DE TRABAJOS
# ==========================================
elif menu == "🔧 Control de Trabajos":
    st.title("🔧 Registro y Seguimiento de Órdenes")
    
    tab1, tab2 = st.tabs(["➕ Registrar Trabajo", "📋 Historial y Estados"])
    
    with tab1:
        st.info("💡 Como tu base de datos está protegida, registra tus nuevos trabajos directamente en tu Google Sheets. La aplicación los mostrará aquí en tiempo real de forma inmediata.")

    with tab2:
        if not df_trabajos.empty:
            st.dataframe(df_trabajos, use_container_width=True)
        else:
            st.info("No hay órdenes guardadas para mostrar.")

# ==========================================
# 3. BASE DE CLIENTES
# ==========================================
elif menu == "👥 Base de Clientes":
    st.title("👥 Control de Clientes")
    if not df_clientes.empty:
        st.dataframe(df_clientes, use_container_width=True)
    else:
        st.info("La pestaña 'Clientes' de tu Google Sheets está vacía o cargando.")
    
    if not df_trabajos.empty and "Cliente" in df_trabajos.columns:
        st.subheader("🔍 Buscador de Historial")
        cliente_sel = st.selectbox("Selecciona un cliente para ver su historial", df_trabajos["Cliente"].unique())
        st.write(df_trabajos[df_trabajos["Cliente"] == cliente_sel])

# ==========================================
# 4. CAJA DIARIA
# ==========================================
elif menu == "💰 Caja Diaria":
    st.title("💰 Caja del Negocio")
    if not df_caja.empty:
        st.dataframe(df_caja, use_container_width=True)
    else:
        st.info("No hay movimientos registrados en la pestaña 'Caja'.")
