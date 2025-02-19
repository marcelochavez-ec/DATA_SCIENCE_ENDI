import vizro as vz
import pandas as pd
import numpy as np

# 📌 Cargar datos de ejemplo (Ventas)
df = pd.DataFrame({
    "Fecha": pd.date_range(start="2023-01-01", periods=100, freq="D"),
    "País": ["Ecuador", "Colombia", "Perú", "Bolivia"] * 25,
    "Categoría": ["Electrónica", "Moda", "Hogar", "Deportes"] * 25,
    "Ventas": (np.random.rand(100) * 5000).astype(int)
})

# 📊 Página 1: Resumen de Ventas
page1 = vz.Page(
    title="Resumen de Ventas",
    content=[
        vz.Card(
            title="Ventas Totales",
            content=df["Ventas"].sum(),
            description="Total de ventas en todos los países."
        ),
        vz.Figure(
            title="Ventas por País",
            content=vz.Charts.bar(
                data=df,
                x="País",
                y="Ventas",
                color="País"
            )
        ),
        vz.Figure(
            title="Tendencia de Ventas",
            content=vz.Charts.line(
                data=df,
                x="Fecha",
                y="Ventas",
                color="País"
            )
        )
    ]
)

# 📊 Página 2: Análisis por Categoría
page2 = vz.Page(
    title="Análisis por Categoría",
    content=[
        vz.Figure(
            title="Ventas por Categoría",
            content=vz.Charts.bar(
                data=df,
                x="Categoría",
                y="Ventas",
                color="Categoría"
            )
        ),
        vz.Table(
            title="Datos de Ventas",
            data=df
        )
    ]
)

# 🎛️ Filtros Globales
filters = [
    vz.Filter(column="País", title="Selecciona un País"),
    vz.Filter(column="Categoría", title="Selecciona una Categoría")
]

# 🖥️ Configurar el Dashboard
dashboard = vz.Dashboard(
    title="Dashboard de Ventas",
    pages=[page1, page2],
    filters=filters
)

# 🚀 Lanzar la Aplicación
vz.run(dashboard)
