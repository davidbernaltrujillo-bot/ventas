# Dashboard Ejecutivo de Ventas

Aplicación desarrollada en **Python con Streamlit** para realizar un análisis general de archivos Excel de ventas.

## Indicadores incluidos

La aplicación calcula automáticamente:

- Ventas totales
- Unidades vendidas
- Costo total
- Utilidad total
- Margen ponderado
- Descuento promedio
- Número de documentos
- Número de clientes
- Ticket promedio
- Costo sobre ventas
- Utilidad promedio por documento

También incluye:

- Filtro por rango de fechas
- Filtro por marca
- Filtro por vendedor
- Filtro por segmento
- Filtro por ciudad
- Evolución diaria de ventas
- Visualización de los registros filtrados
- Descarga de los datos filtrados en CSV UTF-8 con BOM

## Archivos del proyecto

```text
dashboard_ventas.py
requirements.txt
README.md
```

## Columnas requeridas en el Excel

El archivo debe contener, como mínimo, las siguientes columnas:

```text
Cantidad inv.
Valor subtotal local
Costo promedio total
Utilidad promedio
Margen promedio
Dscto. promedio %
Nro documento
Cliente factura
```

La aplicación también aprovecha, cuando existen:

```text
Fecha
MARCA
Nombre vendedor
SEGMENTO
Ciudad
Item
Referencia
```

## Ejecutar en el computador

### 1. Instalar Python

Se recomienda Python 3.10 o superior.

### 2. Instalar dependencias

Abra una terminal dentro de la carpeta del proyecto y ejecute:

```bash
pip install -r requirements.txt
```

### 3. Ejecutar Streamlit

```bash
streamlit run dashboard_ventas.py
```

Streamlit abrirá automáticamente la aplicación en el navegador.

## Publicar en Streamlit Community Cloud

1. Cree un repositorio en GitHub.
2. Suba estos tres archivos:
   - `dashboard_ventas.py`
   - `requirements.txt`
   - `README.md`
3. Ingrese a Streamlit Community Cloud.
4. Seleccione **Crear aplicación**.
5. Conecte el repositorio de GitHub.
6. Seleccione como archivo principal:

```text
dashboard_ventas.py
```

7. Pulse **Deploy** o **Implementar**.

## Uso

Una vez abierta la aplicación:

1. Pulse el botón para cargar el archivo.
2. Seleccione el Excel de ventas.
3. La aplicación eliminará automáticamente filas completamente vacías.
4. Si encuentra una fila con el texto `Gran total`, la excluirá del análisis para evitar duplicar los totales.
5. Los indicadores se recalcularán automáticamente.
6. Utilice los filtros de la barra lateral para analizar segmentos específicos.
7. Puede descargar los datos filtrados como CSV.

## Nota sobre los datos

Los archivos se procesan durante la sesión de Streamlit. Se recomienda evitar cargar información personal, confidencial o sensible en una aplicación pública.

El dashboard realiza análisis exploratorio y no reemplaza la interpretación financiera, comercial o contable de la empresa.
