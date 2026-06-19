import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración del sistema
st.set_page_config(page_title="Negocio Técnico Matías", page_icon="🔧", layout="wide")

# Enlace de tu hoja de cálculo
URL_DE_TU_HOJA = "https://google.com"

@st.cache_data(ttl=0)
def cargar_datos_taller():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        t = conn.read(spreadsheet=URL_DE_TU_HOJA, worksheet="Trabajos")
        c = conn.read(spreadsheet=URL_DE_TU_HOJA, worksheet="Clientes")
        caj = conn.read(spreadsheet=URL_DE_TU_HOJA, worksheet="Caja")
        return t, c, caj
    except Exception as e:
        st.error(f"Error al conectar con las pestañas de Google Sheets: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_trabajos, df_clientes, df_caja = cargar_datos_taller()
conn = st.connection("gsheets", type=GSheetsConnection)

# Limpieza automática de datos numéricos
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
        with st.form("nuevo_trabajo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                cliente = st.text_input("Nombre del Cliente")
                telefono = st.text_input("Teléfono")
                rubro = st.selectbox("Rubro", ["Celulares", "Netbook/Notebook", "Electrodoméstico", "Otros"])
                equipo = st.text_input("Equipo (Ej: Tcl 408, Dell...)")
                marca_modelo = st.text_input("Marca / Modelo (Opcional)")
                trabajo = st.text_area("Trabajo a realizar")
            with c2:
                costo_rep = st.number_input("Costo Repuesto ($)", min_value=0.0, step=100.0)
                otros_costos = st.number_input("Otros Costos ($)", min_value=0.0, step=100.0)
                precio_cob = st.number_input("Precio Cobrado ($)", min_value=0.0, step=100.0)
                sena = st.number_input("Seña Dejada ($)", min_value=0.0, step=100.0)
                estado = st.selectbox("Estado", ["Pendiente", "En Proceso", "Listo para Entregar", "pagado", "Entregado"])
                garantia = st.text_input("Garantía hasta", value="N/A")
                notas = st.text_input("Notas adicionales")
                recurrente = st.selectbox("¿Cliente Recurrente?", ["No", "Sí"])
                
            if st.form_submit_button("Guardar Trabajo"):
                if cliente and equipo:
                    nuevo_id = int(df_trabajos["ID"].max()) + 1 if (not df_trabajos.empty and "ID" in df_trabajos.columns) else 1
                    ganancia = precio_cob - (costo_rep + otros_costos)
                    saldo = precio_cob - sena
                    
                    nueva_fila = pd.DataFrame([{
                        "ID": nuevo_id, "Fecha": datetime.now().strftime("%d/%m"), "Cliente": cliente, 
                        "Teléfono": telefono, "Rubro": rubro, "Equipo": equipo, "Marca/Modelo": marca_modelo,
                        "Trabajo": trabajo, "Costo Repuesto": costo_rep, "Otros Costos": otros_costos, 
                        "Precio Cobrado": precio_cob, "Ganancia": ganancia, "Seña": sena, "Saldo": saldo, 
                        "Estado": estado, "Entrega": "mismo día" if estado == "Entregado" else "Pendiente", 
                        "Garantía hasta": garantia, "Notas": notas, "Recurrente": recurrente
                    }])
                    
                    df_final = pd.concat([df_trabajos, nueva_fila], ignore_index=True)
                    conn.update(spreadsheet=URL_DE_TU_HOJA, worksheet="Trabajos", data=df_final)
                    st.success(f"¡Trabajo #{nuevo_id} registrado exitosamente!")
                    st.rerun()
                else:
                    st.error("Por favor, completa los campos obligatorios: Cliente y Equipo.")

    with tab2:
        if not df_trabajos.empty:
            st.dataframe(df_trabajos, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🔄 Actualizar Estado / Pagos")
            id_mod = st.number_input("Ingresa el ID del trabajo a modificar", min_value=1, step=1)
            nuevo_est = st.selectbox("Nuevo Estado", ["Pendiente", "En Proceso", "Listo para Entregar", "pagado", "Entregado"], key="est")
            nuevo_saldo = st.number_input("Actualizar Saldo Pendiente ($)", min_value=0.0, step=100.0, key="sal")
            
            if st.button("Aplicar Cambios"):
                if id_mod in df_trabajos["ID"].astype(int).values:
                    df_trabajos.loc[df_trabajos["ID"].astype(int) == id_mod, "Estado"] = nuevo_est
                    df_trabajos.loc[df_trabajos["ID"].astype(int) == id_mod, "Saldo"] = nuevo_saldo
                    if nuevo_est in ["pagado", "Entregado"]:
                        df_trabajos.loc[df_trabajos["ID"].astype(int) == id_mod, "Saldo"] = 0
                    
                    conn.update(spreadsheet=URL_DE_TU_HOJA, worksheet="Trabajos", data=df_trabajos)
                    st.success(f"¡Trabajo #{id_mod} actualizado!")
                    st.rerun()
                else:
                    st.error("El ID introducido no existe.")
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
    
    if not df_trabajos.empty:
        st.subheader("🔍 Buscador de Historial")
        cliente_sel = st.selectbox("Selecciona un cliente para ver su historial", df_trabajos["Cliente"].unique())
        st.write(df_trabajos[df_trabajos["Cliente"] == cliente_sel][["ID", "Fecha", "Equipo", "Trabajo", "Precio Cobrado", "Estado"]])

# ==========================================
# 4. CAJA DIARIA
# ==========================================
elif menu == "💰 Caja Diaria":
    st.title("💰 Caja del Negocio")
    st.info("Registra aquí egresos o ingresos generales del taller (repuestos generales, limpieza, herramientas, etc.).")
    if not df_caja.empty:
        st.dataframe(df_caja, use_container_width=True)
    else:
        st.info("No hay movimientos registrados en la pestaña 'Caja'.")
