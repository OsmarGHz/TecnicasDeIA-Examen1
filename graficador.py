import pandas as pd
import glob
import matplotlib.pyplot as plt
import numpy as np
import os

def generar_graficas_globales():
    archivos = glob.glob("resultados_IDA_star_*.csv")
    dfs = []
    
    for f in archivos:
        try:
            # Revisar si el archivo tiene los encabezados en la primera línea
            with open(f, 'r', encoding='utf-8') as file:
                primera_linea = file.readline().strip()
                
            if "Dimension" in primera_linea:
                df = pd.read_csv(f)
            else:
                # Si se generó sin encabezados, se los ponemos a la fuerza
                df = pd.read_csv(f, header=None)
                df.columns = ["Dimension", "Dificultad", "Archivo", "SolucionEncontrada", "TiempoSegundos", "MovimientosRealizados_o_Fallo"]
            dfs.append(df)
        except Exception as e:
            print(f"No se pudo leer {f}: {e}")

    if not dfs:
        print("No se encontraron archivos CSV.")
        return

    # Unimos todos los datos en una sola tabla masiva
    df_all = pd.concat(dfs, ignore_index=True)
    
    if not os.path.exists("graficas"):
        os.makedirs("graficas")

    print("Generando graficas...")

    # Tasa de exito por dimension y dificultad
    summary = df_all.groupby(['Dimension', 'Dificultad']).agg(
        Total=('SolucionEncontrada', 'count'),
        Resueltos=('SolucionEncontrada', 'sum')
    ).reset_index()
    
    summary['Porcentaje_Exito'] = (summary['Resueltos'] / summary['Total']) * 100

    dificultades = ['buenos_10', 'regulares_20', 'malos_50']
    dimensiones = ['3x3', '4x4', '5x5', '6x6', '7x7', '8x8']

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.25
    index = np.arange(len(dimensiones))

    colores = ['#4CAF50', '#FFC107', '#F44336'] # Verde, Amarillo, Rojo
    etiquetas = {'buenos_10': 'Fáciles (10 movs)', 'regulares_20': 'Medios (20 movs)', 'malos_50': 'Difíciles (50 movs)'}

    for i, dif in enumerate(dificultades):
        porcentajes = []
        for dim in dimensiones:
            val = summary[(summary['Dimension'] == dim) & (summary['Dificultad'] == dif)]
            if not val.empty:
                porcentajes.append(val['Porcentaje_Exito'].values[0])
            else:
                porcentajes.append(0)
        
        ax.bar(index + i * bar_width, porcentajes, bar_width, label=etiquetas[dif], color=colores[i], edgecolor='black')

    ax.set_xlabel('Dimensión del Tablero', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tasa de Éxito (%)', fontsize=12, fontweight='bold')
    ax.set_title('Tasa de exito del IDA* por dimension (Timeout: 120s)', fontsize=14, pad=15)
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(dimensiones)
    ax.set_ylim(0, 115)
    
    # Poner numeritos encima de las barras
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f%%', padding=3, fontsize=9)

    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('graficas/1_Tasa_Exito_Global.png', dpi=300)
    plt.close()

    print("Grafica guardada en graficas/")

if __name__ == "__main__":
    generar_graficas_globales()