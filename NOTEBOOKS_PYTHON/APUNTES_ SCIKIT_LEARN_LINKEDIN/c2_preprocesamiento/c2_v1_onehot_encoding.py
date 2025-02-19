import pandas as pd

from sklearn.compose import make_column_transformer
from sklearn.preprocessing import OneHotEncoder

# One hot usando OneHotEncoder
adult_df = pd.read_csv("SCIKIT_LEARN/c2_preprocesamiento/adult.csv")
adult_df.shape

print(adult_df.columns)
print(adult_df.head())

print(adult_df["sex"].unique())

adult_df.sex.value_counts(normalize=True).round(2)


frecuencias_var_sexo = pd.DataFrame([(v, round(100 * v / len(adult_df), 2)) 
                                      for v in adult_df['sex'].value_counts().values], 
                                      index=adult_df['sex'].value_counts().index, 
                                      columns=['Frecuencia Absoluta', 'Porcentaje (%)'])
frecuencias_var_sexo

# Instancia de la clase
one_hot_enconder = OneHotEncoder()

encode_adult_sex = one_hot_enconder.fit_transform(adult_df[["sex"]])
print(encode_adult_sex.toarray()) #Matriz de los valores o categorias binarizadas

# Impresión de los atributos de la estructura binarizada:
print(one_hot_enconder.categories_)

# Agregamos al df original:
adult_df[one_hot_enconder.categories_[0]] = encode_adult_sex.toarray()

# Imprimimos para ver las nuevas columnas
print(adult_df.columns)

# =============================================================================
# Otra forma de resolver el One Hot Encoding
# =============================================================================

# One hot usando OneHotEncoder y make_column_transformer
adult_df = pd.read_csv("adult.csv")
adult_df.shape

# Creo el objeto trasnformer que aplicará el One Hot Encoder sobre la variables sex
transformer = make_column_transformer(
    (OneHotEncoder(), ["sex"]),
    remainder='passthrough'
)

# Creo la estructura array de Numpy del transformer:
transformed_data = transformer.fit_transform(adult_df)
type(transformed_data)

# Aquí construyo el df final utilizando tanto el transformed_data y el objeto transformer para los nombres del nuevo adult_df:
transformed_adult_df = pd.DataFrame(
    transformed_data, 
    columns=transformer.get_feature_names_out()
)
type(transformed_adult_df)
transformed_adult_df.shape
transformed_adult_df.columns
adult_df.columns

# Esto ayuda eliminar de los nombres de las columnas del nuevo df la extensión remainder__:
transformed_adult_df = transformed_adult_df.rename(columns=lambda x: x.split("__")[-1])
transformed_adult_df.columns


help("keywords")


