import streamlit as st  
import pandas as pd  
from datetime import datetime  
from streamlit\_gsheets import GSheetsConnection

### Configuración profesional del sistema

st.set\_page\_config(page\_title="Negocio Técnico Matías", page\_icon="🔧", layout="wide")

### Enlace oficial de tu documento conectado directamente

URL\_DE\_TU\_HOJA = "google.com"

@st.cache\_data(ttl=0)  
def cargar\_datos\_taller():  
try:  
conn = st.connection("gsheets", type=GSheetsConnection)  
t = conn.read(spreadsheet=URL\_DE\_TU\_HOJA, worksheet="Trabajos")  
c = conn.read(spreadsheet=URL\_DE\_TU\_HOJA, worksheet="Clientes")  
caj = conn.read(spreadsheet=URL\_DE\_TU\_HOJA, worksheet="Caja")  
return t, c, caj  
except Exception as e:  
st.error(f"Error al conectar con las pestañas de Google Sheets: {e}")  
return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df\_trabajos, df\_clientes, df\_caja = cargar\_datos\_taller()  
conn = st.connection("gsheets", type=GSheetsConnection)

### Limpieza automática de datos numéricos para fórmulas del taller

columnas\_numericas = \["Precio Cobrado", "Costo Repuesto", "Otros Costos", "Ganancia", "Seña", "Saldo"\]  
for col in columnas\_numericas:  
if not df\_trabajos.empty and col in df\_trabajos.columns:  
df\_trabajos\[col\] = pd.to\_numeric(df\_trabajos\[col\], errors='coerce').fillna(0)

### Menú de navegación lateral

menu = st.sidebar.radio("Navegación", \["📊 Dashboard Resumen", "🔧 Control de Trabajos", "👥 Base de Clientes", "💰 Caja Diaria"\])

st.sidebar.markdown("---")  
st.sidebar.subheader("🚨 Alertas Rápidas")  
if not df\_trabajos.empty and "Saldo" in df\_trabajos.columns:  
saldos\_pendientes = df\_trabajos\[df\_trabajos\["Saldo"\] > 0\]  
st.sidebar.warning(f"💵 Clientes con Saldo Pendiente: {len(saldos\_pendientes)}")

### \==========================================

### 1\. DASHBOARD RESUMEN

### \==========================================

if menu == "📊 Dashboard Resumen":  
st.title("📊 Resumen General del Negocio")  
st.markdown("---")

if not df\_trabajos.empty:  
total\_trabajos = len(df\_trabajos)  
facturacion\_total = df\_trabajos\["Precio Cobrado"\].sum()  
ganancia\_total = df\_trabajos\["Ganancia"\].sum()  
senas\_cobradas = df\_trabajos\["Seña"\].sum()  
saldos\_totales = df\_trabajos\["Saldo"\].sum()

\# Fila superior de métricas  
col1, col2, col3 = st.columns(3)  
col1.metric("🔧 Total Trabajos", total\_trabajos)  
col2.metric("💵 Facturación Total", f"${facturacion\_total:,.2f}")  
col3.metric("💰 Ganancia Total", f"${ganancia\_total:,.2f}")

st.markdown("---")  
\# Fila inferior de métricas  
col4, col5, col6 = st.columns(3)  
col4.metric("📥 Señas Cobradas", f"${senas\_cobradas:,.2f}")  
col5.metric("⏳ Saldos Pendientes", f"${saldos\_totales:,.2f}")

if "Rubro" in df\_trabajos.columns and not df\_trabajos\["Rubro"\].mode().empty:  
col6.metric("🏆 Rubro más Frecuente", df\_trabajos\["Rubro"\].mode().iloc\[0\])  
else:  
st.info("Aún no hay datos cargados en la pestaña 'Trabajos'.")

### \==========================================

### 2\. CONTROL DE TRABAJOS

### \==========================================

elif menu == "🔧 Control de Trabajos":  
st.title("🔧 Registro y Seguimiento de Órdenes")

tab1, tab2 = st.tabs(\["➕ Registrar Trabajo", "📋 Historial y Estados"\])

with tab1:  
with st.form("nuevo\_trabajo", clear\_on\_submit=True):  
c1, c2 = st.columns(2)  
with c1:  
cliente = st.text\_input("Nombre del Cliente")  
telefono = st.text\_input("Teléfono")  
rubro = st.selectbox("Rubro", \["Celulares", "Netbook/Notebook", "Electrodoméstico", "Otros"\])  
equipo = st.text\_input("Equipo (Ej: Tcl 408, Dell...)")  
marca\_modelo = st.text\_input("Marca / Modelo (Opcional)")  
trabajo = st.text\_area("Trabajo a realizar")  
with c2:  
costo\_rep = st.number\_input("Costo Repuesto ($)", min\_value=0.0, step=100.0)  
otros\_costos = st.number\_input("Otros Costos ($)", min\_value=0.0, step=100.0)  
precio\_cob = st.number\_input("Precio Cobrado ($)", min\_value=0.0, step=100.0)  
sena = st.number\_input("Seña Dejada ($)", min\_value=0.0, step=100.0)  
estado = st.selectbox("Estado", \["Pendiente", "En Proceso", "Listo para Entregar", "pagado", "Entregado"\])  
garantia = st.text\_input("Garantía hasta", value="N/A")  
notas = st.text\_input("Notas adicionales")  
recurrente = st.selectbox("¿Cliente Recurrente?", \["No", "Sí"\])

if st.form\_submit\_button("Guardar Trabajo"):  
if cliente and equipo:  
nuevo\_id = int(df\_trabajos\["ID"\].max()) + 1 if (not df\_trabajos.empty and "ID" in df\_trabajos.columns) else 1  
ganancia = precio\_cob - (costo\_rep + otros\_costos)  
saldo = precio\_cob - sena

nueva\_fila = pd.DataFrame(\[{  
"ID": nuevo\_id, "Fecha": datetime.now().strftime("%d/%m"), "Cliente": cliente,  
"Teléfono": telefono, "Rubro": rubro, "Equipo": equipo, "Marca/Modelo": marca\_modelo,  
"Trabajo": trabajo, "Costo Repuesto": costo\_rep, "Otros Costos": otros\_costos,  
"Precio Cobrado": precio\_cob, "Ganancia": ganancia, "Seña": sena, "Saldo": saldo,  
"Estado": estado, "Entrega": "mismo día" if estado == "Entregado" else "Pendiente",  
"Garantía hasta": garantia, "Notas": notas, "Recurrente": recurrente  
}\])

df\_final = pd.concat(\[df\_trabajos, nueva\_fila\], ignore\_index=True)  
conn.update(spreadsheet=URL\_DE\_TU\_HOJA, worksheet="Trabajos", data=df\_final)  
st.success(f"¡Trabajo #{nuevo\_id} registrado exitosamente!")  
st.rerun()  
else:  
st.error("Por favor, completa los campos obligatorios: Cliente y Equipo.")

with tab2:  
if not df\_trabajos.empty:  
st.dataframe(df\_trabajos, use\_container\_width=True)

st.markdown("---")  
st.subheader("🔄 Actualizar Estado / Pagos")  
id\_mod = st.number\_input("Ingresa el ID del trabajo a modificar", min\_value=1, step=1)  
nuevo\_est = st.selectbox("Nuevo Estado", \["Pendiente", "En Proceso", "Listo para Entregar", "pagado", "Entregado"\], key="est")  
nuevo\_saldo = st.number\_input("Actualizar Saldo Pendiente ($)", min\_value=0.0, step=100.0, key="sal")

if st.button("Aplicar Cambios"):  
if id\_mod in df\_trabajos\["ID"\].astype(int).values:  
df\_trabajos.loc\[df\_trabajos\["ID"\].astype(int) == id\_mod, "Estado"\] = nuevo\_est  
df\_trabajos.loc\[df\_trabajos\["ID"\].astype(int) == id\_mod, "Saldo"\] = nuevo\_saldo  
if nuevo\_est in \["pagado", "Entregado"\]:  
df\_trabajos.loc\[df\_trabajos\["ID"\].astype(int) == id\_mod, "Saldo"\] = 0

conn.update(spreadsheet=URL\_DE\_TU\_HOJA, worksheet="Trabajos", data=df\_trabajos)  
st.success(f"¡Trabajo #{id\_mod} actualizado!")  
st.rerun()  
else:  
st.error("El ID introducido no existe.")  
else:  
st.info("No hay órdenes guardadas para mostrar.")

### \==========================================

### 3\. BASE DE CLIENTES

### \==========================================

elif menu == "👥 Base de Clientes":  
st.title("👥 Control de Clientes")  
if not df\_clientes.empty:  
st.dataframe(df\_clientes, use\_container\_width=True)  
else:  
st.info("La pestaña 'Clientes' de tu Google Sheets está vacía.")

if not df\_trabajos.empty:  
st.subheader("🔍 Buscador de Historial")  
cliente\_sel = st.selectbox("Selecciona un cliente para ver su historial", df\_trabajos\["Cliente"\].unique())  
st.write(df\_trabajos\[df\_trabajos\["Cliente"\] == cliente\_sel\]\[\["ID", "Fecha", "Equipo", "Trabajo", "Precio Cobrado", "Estado"\]\])

### \==========================================

### 4\. CAJA DIARIA

### \==========================================

elif menu == "💰 Caja Diaria":  
st.title("💰 Caja del Negocio")  
st.info("Registra aquí egresos o ingresos generales del taller (repuestos generales, limpieza, herramientas, etc.).")  
if not df\_caja.empty:  
st.dataframe(df\_caja, use\_container\_width=True)  
else:  
st.info("No hay movimientos registrados en la pestaña 'Caja'.")