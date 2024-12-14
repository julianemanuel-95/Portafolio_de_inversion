# Importamos las librerias necesarias
import sqlite3
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Creamos la conexión a la base de datos SQLite
conexion = sqlite3.connect('portafolio.db')  # Establece la conexión con la base de datos 'portafolio.db'

# Verificaramos y agregamos las columnas si no existen
def agregar_columnas_si_no_existen(conexion): # Declaramos la funcion
    cursor = conexion.cursor()  # Creamos un cursor para interactuar con la base de datos
    cursor.execute("PRAGMA table_info(Portafolio_de_prueba)")  # Obtenmos la información de las columnas de la tabla
    columnas = [columna[1] for columna in cursor.fetchall()]  # Extraemos los nombres de las columnas existentes

    if 'precio_actual' not in columnas:  # Verificamos si la columna 'precio_actual' no existe
        cursor.execute("ALTER TABLE Portafolio_de_prueba ADD COLUMN precio_actual REAL")  # Agregamos la columna 'precio_actual'
    if 'valor_actual' not in columnas:  # Verificamos si la columna 'valor_actual' no existe
        cursor.execute("ALTER TABLE Portafolio_de_prueba ADD COLUMN valor_actual REAL")  # Agregamos la columna 'valor_actual'
    if 'ganancia_perdida_porcentaje' not in columnas:  # Verificamos si la columna 'ganancia_perdida_porcentaje' no existe
        cursor.execute("ALTER TABLE Portafolio_de_prueba ADD COLUMN ganancia_perdida_porcentaje REAL")  # Agregamos la columna 'ganancia_perdida_porcentaje'
    conexion.commit()  # Confirmamos los cambios en la base de datos

agregar_columnas_si_no_existen(conexion)  # Llamamos a la función para agregar columnas si no existen

# Cargamos los datos de la tabla 'Portafolio_de_prueba' a un DataFrame
query = "SELECT * FROM Portafolio_de_prueba"  # Definimos la consulta para seleccionar todos los datos de la tabla
portafolio_df = pd.read_sql_query(query, conexion)  # Ejecutamos la consulta y cargamos los datos en un DataFrame

# Verificamos si la tabla contiene datos
if portafolio_df.empty:  # Comprobamos si el DataFrame está vacío
    print("La tabla 'Portafolio_de_prueba' está vacía. Por favor, agrega datos.")  # Mostamos un mensaje si no hay datos
    conexion.close()  # Cerramos la conexión a la base de datos
    exit()  # Termina la ejecución del script

# Obtenemos los precios actuales de las acciones
precios_actuales = {}  # Creamos un diccionario para almacenar los precios actuales
for ticket in portafolio_df['ticket']:  # Itera sobre cada ticket en la columna 'ticket'
    accion = yf.Ticker(ticket)  # Creamos un objeto Ticker para el símbolo actual
    try:
        precios_actuales[ticket] = round(accion.history(period='1d')['Close'].iloc[-1], 2)  # Obtenemos el precio más reciente y lo redondeamos a 2 decimales
    except IndexError:  # Creamos una excepcion si no se encuentran datos
        print(f"No se pudo obtener el precio para {ticket}.")  # Muestrmos un mensaje de error
        precios_actuales[ticket] = None  # Asignamos un valor null en el caso de dar un error

# Actualizamos el DataFrame con los precios actuales y el valor actual de la inversion por ticket
portafolio_df['precio_actual'] = portafolio_df['ticket'].map(precios_actuales)  # Asignamos los precios actuales a una nueva columna
portafolio_df['valor_actual'] = (portafolio_df['precio_actual'] * portafolio_df['cantidad_nominales']).round(2)  # Calculamos el valor actual de cada ticket y lo redondea a 2 decimales
portafolio_df['ganancia_perdida_porcentaje'] = ((portafolio_df['valor_actual'] - portafolio_df['dinero_invertido']) / portafolio_df['dinero_invertido'] * 100).round(2)  # Calculamos el porcentaje de ganancia/pérdida y lo redondeamos a 2 decimales

# Actualizamos la base de datos con los nuevos valores
for index, row in portafolio_df.iterrows():  # Itera sobre cada fila del DataFrame
    conexion.execute(
        "UPDATE Portafolio_de_prueba SET precio_actual = ?, valor_actual = ?, ganancia_perdida_porcentaje = ? WHERE ticket = ?",  # Creamos una conexion con la base de datos para actualizar las columnas
        (row['precio_actual'], row['valor_actual'], row['ganancia_perdida_porcentaje'], row['ticket'])  # Le pasamos los valores a actualizar
    )
conexion.commit()  # Confirma los cambios en la base de datos haciendo un commit

# Calculamos el valor total actualizado del portafolio
valor_total = portafolio_df['valor_actual'].sum()  # Suma el valor actual de todas las acciones
print(f"Valor total del portafolio: ${valor_total:,.2f}")  # Muestra el valor total del portafolio

# Creamos un gráfico de torta para la distribución del portafolio
plt.figure(figsize=(8, 8))  # Configura el tamaño de la figura
plt.pie(
    portafolio_df['valor_actual'],  # Datos para el gráfico
    labels=portafolio_df['accion'],  # Etiquetas de las acciones
    autopct='%1.1f%%',  # Formato de los porcentajes
    startangle=140  # Ángulo inicial del gráfico
)
plt.title('Distribución del Portafolio')  # Le agregamos un título del gráfico
plt.show()  # Lo mostramos

# Cerraramos la conexión con la base de datos
conexion.close()

