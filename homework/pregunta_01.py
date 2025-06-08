"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""

import pandas as pd
from datetime import datetime
import os

def show_uniques(df):
    for col in df.columns:
        print(col+':', df[col].unique())

def save_df(ruta,nombre_archivo,df):
    if not os.path.exists(ruta):
        os.mkdir(ruta)
    df.to_csv(os.path.join(ruta,nombre_archivo),sep=';')


def create_key(df, n, col):
    """Cree una nueva columna en el DataFrame que contenga el key de la
    columna 'text'"""

    df = df.copy()
    df["key"] = df[col]
    df["key"] = df["key"].str.strip()
    df["key"] = df["key"].str.lower()
    df["key"] = df["key"].str.replace("-", "")
    df["key"] = df["key"].str.translate(
        str.maketrans("", "", "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
    )
    df["key"] = df["key"].str.split()

    # ------------------------------------------------------
    # Esta es la parte especifica del algoritmo de n-gram:
    #
    # - Una el texto sin espacios en blanco
    df["key"] = df["key"].str.join("")
    #
    # - Convierta el texto a una lista de n-gramas
    df["key"] = df["key"].map(
        lambda x: [x[t : t + n] for t in range(len(x))],
    )
    #
    # - Ordene la lista de n-gramas y remueve duplicados
    df["key"] = df["key"].apply(lambda x: sorted(set(x)))
    #
    # - Convierta la lista de ngramas a una cadena
    df["key"] = df["key"].str.join("")
    # ------------------------------------------------------
    return df

def generate_cleaned_column(df,col):
    """Crea la columna 'cleaned' en el DataFrame"""

    #
    # Este código es identico al anteior
    #
    keys = df.copy()
    keys = keys.sort_values(by=["key", col], ascending=[True, True])
    keys = keys.drop_duplicates(subset="key", keep="first")
    key_dict = dict(zip(keys["key"], keys[col]))
    df[col] = df["key"].map(key_dict)

    df = df.drop(columns='key')

    return df

def pregunta_01():
    """
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv"

    """
file = 'files\input\solicitudes_de_credito.csv'

df = pd.read_csv(file, encoding='utf-8', delimiter=';')
# # Explorar el dataframe
# print(df.shape)

# print(df.isna().sum())

# print(df.dtypes)
# print(df.describe())

# show_uniques(df)

# print("""
# ******************************
# ******************************
#       """)

# # Elimianr columna indice
df = df.drop(columns='Unnamed: 0')

# # Eliminar registros con información faltante
df = df.dropna()
# print(df.shape)

# # Vamos a llevar todo a minuscula
# # columnas string
col_string = df.select_dtypes(include=['object']).columns

for col in col_string:
    df[col] = df[col].str.lower()

# for col in col_string:
for col in ['idea_negocio','línea_credito']:
    df = create_key(df, 2, col)
    df = generate_cleaned_column(df,col)

# Corrección formato de fechas
date_col = []
for date in df['fecha_de_beneficio']:
    date_split = date.split("/")
    if len(date_split[0]) == 1 or len(date_split[0]) == 2:
        date_col.append(datetime.strptime(date, "%d/%m/%Y").date())
    else:
        date_col.append(datetime.strptime(date, "%Y/%m/%d").date())
df['fecha_de_beneficio'] = date_col


# corrección de caracteres en cifras
df['monto_del_credito'] = df['monto_del_credito'].str.replace('$ ', '', regex=False)
df['monto_del_credito'] = df['monto_del_credito'].str.replace('.00', '', regex=False)
df['monto_del_credito'] = df['monto_del_credito'].str.replace(',', '', regex=False)

# corrección de entrada en texto por _ y -
df['barrio'] = df['barrio'].str.replace('-',' ')
df['barrio'] = df['barrio'].str.replace('_',' ')

df = df.drop_duplicates()
# show_uniques(df)
save_df('./files/output/','solicitudes_de_credito.csv',df)
