import matplotlib.pyplot as plt
from sklearn.datasets import load_iris

def plot_iris_scatter(x_var=0, y_var=1, title="Gráfico de Dispersión", 
                      subtitle="Comparación entre dos características", 
                      footnote="Fuente: Conjunto de datos Iris"):
    """
    Genera un gráfico de dispersión del conjunto de datos Iris.

    Parámetros:
    - x_var (int): Índice de la característica en el eje X (0-3).
    - y_var (int): Índice de la característica en el eje Y (0-3).
    - title (str): Título principal del gráfico.
    - subtitle (str): Subtítulo del gráfico.
    - footnote (str): Nota al pie del gráfico.
    """

    # Cargar dataset Iris
    iris_dataset = load_iris()
    iris_data = iris_dataset.data

    # Crear la figura y los ejes
    fig, ax = plt.subplots(figsize=(7, 5))

    # Graficar los puntos
    scatter = ax.scatter(iris_data[:, x_var], iris_data[:, y_var], 
                         c=iris_dataset.target, cmap='viridis', edgecolors='k')

    # Etiquetas de los ejes
    ax.set_xlabel(iris_dataset.feature_names[x_var])
    ax.set_ylabel(iris_dataset.feature_names[y_var])

    # Configurar ticks internos en los ejes
    ax.tick_params(axis='both', direction='in', length=6)

    # Agregar título y subtítulo
    plt.suptitle(title, fontsize=14, fontweight="bold", x=0.126, y=1, ha="left")
    plt.title(subtitle, fontsize=10, pad=10, loc="left")

    # Agregar footnote alineado a la izquierda, debajo del gráfico
    plt.figtext(0.125, -0.05, footnote, ha="left", fontsize=8)

    # Crear leyenda con los nombres de las etiquetas
    legend_labels = [iris_dataset.target_names[i] for i in range(len(iris_dataset.target_names))]
    ax.legend(handles=scatter.legend_elements()[0], labels=legend_labels, title="Especies", loc="upper right")

    # Ajustar límites para que los puntos queden dentro del gráfico
    ax.set_xlim(iris_data[:, x_var].min() - 0.5, iris_data[:, x_var].max() + 0.5)
    ax.set_ylim(iris_data[:, y_var].min() - 0.5, iris_data[:, y_var].max() + 0.5)

    # Mostrar el gráfico
    plt.show()
