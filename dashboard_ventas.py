import streamlit as st
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard de Ventas",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Ejecutivo de Ventas")
st.caption("Análisis general de ventas")

st.info(
    "Los datos se procesan únicamente durante la sesión. "
    "Evite cargar información personal, confidencial o sensible. "
    "El análisis es exploratorio y debe complementarse con criterio experto."
)

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_numerico(serie):
    """Convierte una serie a valores numéricos."""
    return pd.to_numeric(serie, errors="coerce")


def formato_pesos(valor):
    """Formato monetario colombiano sin decimales."""
    if pd.isna(valor):
        return "$0"
    return f"${valor:,.0f}".replace(",", ".")


def formato_numero(valor):
    """Formato entero con separador de miles."""
    if pd.isna(valor):
        return "0"
    return f"{valor:,.0f}".replace(",", ".")


def formato_porcentaje(valor):
    """Formato porcentual."""
    if pd.isna(valor):
        return "0,00 %"
    return f"{valor:.2f} %".replace(".", ",")


def eliminar_gran_total(dataframe):
    """Elimina filas que contengan el texto 'Gran total'."""
    if dataframe.empty:
        return dataframe

    mascara_total = dataframe.astype(str).apply(
        lambda fila: fila.str.contains(
            "gran total",
            case=False,
            na=False
        ).any(),
        axis=1
    )
    return dataframe.loc[~mascara_total].copy()


def normalizar_porcentaje(serie):
    """
    Normaliza una columna porcentual.
    Si sus valores parecen estar expresados como decimales (ej. 0.25),
    los convierte a porcentaje (25).
    """
    s = pd.to_numeric(serie, errors="coerce")
    valores_validos = s.dropna()

    if not valores_validos.empty:
        mediana_abs = valores_validos.abs().median()
        if mediana_abs <= 1:
            s = s * 100

    return s


# ============================================================
# CARGA DEL ARCHIVO
# ============================================================

archivo = st.file_uploader(
    "Seleccione el archivo Excel de ventas",
    type=["xlsx", "xls"]
)

if archivo is None:
    st.warning("👆 Cargue el archivo Excel de ventas para iniciar el análisis.")
    st.stop()

try:
    df = pd.read_excel(archivo)
except Exception as error:
    st.error("No fue posible leer el archivo Excel.")
    st.exception(error)
    st.stop()

# ============================================================
# LIMPIEZA INICIAL
# ============================================================

df.columns = df.columns.astype(str).str.strip()
df = df.dropna(how="all").copy()
df = eliminar_gran_total(df)

# ============================================================
# VALIDACIÓN DE COLUMNAS
# ============================================================

columnas_necesarias = [
    "Cantidad inv.",
    "Valor subtotal local",
    "Costo promedio total",
    "Utilidad promedio",
    "Margen promedio",
    "Dscto. promedio %",
    "Nro documento",
    "Cliente factura"
]

columnas_faltantes = [
    columna for columna in columnas_necesarias
    if columna not in df.columns
]

if columnas_faltantes:
    st.error("El archivo no contiene todas las columnas necesarias.")
    st.write("Columnas faltantes:")
    for columna in columnas_faltantes:
        st.write(f"- {columna}")

    with st.expander("Ver columnas detectadas en el archivo"):
        st.write(list(df.columns))

    st.stop()

# ============================================================
# CONVERSIÓN DE DATOS
# ============================================================

columnas_numericas = [
    "Cantidad inv.",
    "Valor subtotal local",
    "Costo promedio total",
    "Utilidad promedio",
    "Margen promedio"
]

for columna in columnas_numericas:
    df[columna] = convertir_numerico(df[columna])

df["Dscto. promedio %"] = normalizar_porcentaje(df["Dscto. promedio %"])

if "Fecha" in df.columns:
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("🔎 Filtros")
df_filtrado = df.copy()

if "Fecha" in df.columns:
    fechas_validas = df["Fecha"].dropna()

    if not fechas_validas.empty:
        fecha_min = fechas_validas.min().date()
        fecha_max = fechas_validas.max().date()

        rango_fecha = st.sidebar.date_input(
            "Rango de fechas",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )

        if isinstance(rango_fecha, (tuple, list)) and len(rango_fecha) == 2:
            fecha_inicio = pd.Timestamp(rango_fecha[0])
            fecha_fin = pd.Timestamp(rango_fecha[1]) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

            df_filtrado = df_filtrado[
                (df_filtrado["Fecha"] >= fecha_inicio)
                & (df_filtrado["Fecha"] <= fecha_fin)
            ]


def aplicar_multifiltro(dataframe, columna, etiqueta):
    if columna not in dataframe.columns:
        return dataframe

    opciones = sorted(
        dataframe[columna]
        .dropna()
        .astype(str)
        .unique()
    )

    seleccion = st.sidebar.multiselect(etiqueta, opciones)

    if seleccion:
        return dataframe[
            dataframe[columna]
            .astype(str)
            .isin(seleccion)
        ]

    return dataframe


df_filtrado = aplicar_multifiltro(df_filtrado, "MARCA", "Marca")
df_filtrado = aplicar_multifiltro(df_filtrado, "Nombre vendedor", "Vendedor")
df_filtrado = aplicar_multifiltro(df_filtrado, "SEGMENTO", "Segmento")
df_filtrado = aplicar_multifiltro(df_filtrado, "Ciudad", "Ciudad")

if df_filtrado.empty:
    st.warning("No existen registros para los filtros seleccionados.")
    st.stop()

# ============================================================
# CÁLCULO DE INDICADORES
# ============================================================

ventas_totales = df_filtrado["Valor subtotal local"].sum()
unidades_vendidas = df_filtrado["Cantidad inv."].sum()
costo_total = df_filtrado["Costo promedio total"].sum()
utilidad_total = df_filtrado["Utilidad promedio"].sum()

margen_ponderado = (
    (utilidad_total / ventas_totales) * 100
    if ventas_totales != 0
    else 0
)

descuento_promedio = df_filtrado["Dscto. promedio %"].mean()

numero_documentos = (
    df_filtrado["Nro documento"]
    .dropna()
    .nunique()
)

numero_clientes = (
    df_filtrado["Cliente factura"]
    .dropna()
    .nunique()
)

ticket_promedio = (
    ventas_totales / numero_documentos
    if numero_documentos > 0
    else 0
)

# ============================================================
# RESUMEN EJECUTIVO
# ============================================================

st.subheader("📌 Resumen ejecutivo")

c1, c2, c3, c4 = st.columns(4)

c1.metric("💰 Ventas totales", formato_pesos(ventas_totales))
c2.metric("📦 Unidades vendidas", formato_numero(unidades_vendidas))
c3.metric("💵 Utilidad total", formato_pesos(utilidad_total))
c4.metric("📊 Margen ponderado", formato_porcentaje(margen_ponderado))

c5, c6, c7, c8 = st.columns(4)

c5.metric("🏷️ Descuento promedio", formato_porcentaje(descuento_promedio))
c6.metric("🧾 Documentos", formato_numero(numero_documentos))
c7.metric("👥 Clientes", formato_numero(numero_clientes))
c8.metric("🛒 Ticket promedio", formato_pesos(ticket_promedio))

st.divider()

# ============================================================
# INDICADORES COMPLEMENTARIOS
# ============================================================

c9, c10, c11 = st.columns(3)

participacion_costo = (
    costo_total / ventas_totales * 100
    if ventas_totales != 0
    else 0
)

utilidad_por_documento = (
    utilidad_total / numero_documentos
    if numero_documentos > 0
    else 0
)

c9.metric("Costo total", formato_pesos(costo_total))
c10.metric("Costo / Ventas", formato_porcentaje(participacion_costo))
c11.metric("Utilidad promedio por documento", formato_pesos(utilidad_por_documento))

# ============================================================
# EVOLUCIÓN DE VENTAS
# ============================================================

if "Fecha" in df_filtrado.columns:
    ventas_diarias = (
        df_filtrado
        .dropna(subset=["Fecha"])
        .assign(Fecha_dia=lambda x: x["Fecha"].dt.date)
        .groupby("Fecha_dia", as_index=False)["Valor subtotal local"]
        .sum()
        .rename(columns={
            "Fecha_dia": "Fecha",
            "Valor subtotal local": "Ventas"
        })
    )

    if not ventas_diarias.empty:
        st.divider()
        st.subheader("📈 Evolución diaria de ventas")
        st.line_chart(
            ventas_diarias,
            x="Fecha",
            y="Ventas",
            use_container_width=True
        )

# ============================================================
# INFORMACIÓN DEL CONJUNTO DE DATOS
# ============================================================

st.divider()
st.subheader("📋 Información de los datos analizados")

i1, i2, i3 = st.columns(3)

i1.metric("Registros analizados", formato_numero(len(df_filtrado)))
i2.metric("Variables", formato_numero(len(df_filtrado.columns)))

if "Item" in df_filtrado.columns:
    referencias = df_filtrado["Item"].dropna().nunique()
    i3.metric("Ítems diferentes", formato_numero(referencias))
elif "Referencia" in df_filtrado.columns:
    referencias = df_filtrado["Referencia"].dropna().nunique()
    i3.metric("Referencias diferentes", formato_numero(referencias))
else:
    i3.metric("Referencias diferentes", "N/D")

# ============================================================
# TABLA DE DATOS
# ============================================================

with st.expander("🔍 Ver datos utilizados"):
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# DESCARGA DE DATOS FILTRADOS
# ============================================================

csv = df_filtrado.to_csv(
    index=False,
    encoding="utf-8-sig"
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Descargar datos filtrados",
    data=csv,
    file_name="ventas_filtradas.csv",
    mime="text/csv"
)
