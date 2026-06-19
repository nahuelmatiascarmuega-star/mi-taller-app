import streamlit as st
import pandas as pd
import urllib.request

# Configuración del sistema
st.set_page_config(page_title="Negocio Técnico Matías", page_icon="🔧", layout="wide")

# ID único de tu documento de Google Sheets
SHEET_ID = "1z9kT1uHJVZuFXCWH9-SmTS9dNGQcuUxgbIReNxvCB3E"

def cargar_datos_seguros():
    try:
        # Enlaces de exportación directa a formato CSV (método universal sin trabas)
        url_trabajos = f"https://google.com{SHEET_ID}/export?format=csv&sheet=Trabajos"
        url_clientes = f"https://google.com{SHEET_ID}/export?format=csv&sheet=Clientes"
        url_caja = f"https://google.com{SHEET_ID}/export?format=csv&sheet=Caja"
        
        # Lectura directa ignorando el bloqueo de conexiones de Google
        t = pd.read_csv(url_trabajos, on_bad_lines='skip').fillna("")
        c = pd.read_csv(url_clientes, on_bad_lines='skip').fillna("")
        caj = pd.read_csv(url_caja, on_bad_lines='skip').fillna("")
        
        return t, c, caj
    except Exception as e:
        st.error(f"Intentando reconectar con la base de datos... Por favor, presiona el botón 'Reiniciar' en el menú lateral. Detalle: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_trabajos, df_clientes, df_caja = cargar_datos_seguros()

# Limpiar encabezados de columnas de símbolos molestos (# o espacios)
for df in [df_trabajos, df_clientes, df_caja]:
    if not df.empty:
        df.columns = df.columns.str.replace('#', '').str.strip()

# Convertir columnas numéricas para las fórmulas matemáticas del Dashboard
columnas_numericas = ["Precio Cobrado", "Costo Repuesto", "Otros Costos", "Ganancia", "Seña", "Saldo"]
for col in columnas_numericas:
    if not df_trabajos.empty and col in df_trabajos.columns:
        df_trabajos[col] = pd.to_numeric(df_trabajos[col], errors='coerce').fillna(0)

# Menú lateral
menu = st.sidebar.radio("Navegación", ["📊 Dashboard Resumen", "🔧 Control de Trabajos", "👥 Base de Clientes", "💰 Caja Diaria"])

# Botón manual de actualización en la barra lateral
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Actualizar Datos"):
    st.rerun()

# Alertas en la barra lateral
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
        st.info("Aún no hay datos cargados o el servidor está reintentando la conexión.")

# ==========================================
# 2. CONTROL DE TRABAJOS
# ==========================================
elif menu == "🔧 Control de Trabajos":
    st.title("🔧 Registro y Seguimiento de Órdenes")
    
    tab1, tab2 = st.tabs(["➕ Registrar Trabajo", "📋 Historial y Estados"])
    
    with tab1:
        st.info("💡 Registra tus nuevos trabajos directamente en tu Google Sheets. La aplicación se actualizará automáticamente aquí en tiempo real.")

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
        st.info("La pestaña 'Clientes' de tu Google Sheets está vacía.")
    
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

