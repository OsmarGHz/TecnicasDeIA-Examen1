import os

def leer_tableros(ruta_archivo):
    """
    Lee el archivo de texto y extrae la dimensión y los tableros.
    Convierte las matrices 2D en tuplas 1D inmutables para 
    optimizar el hashing en la memoria del IDA*.
    """
    try:
        with open(ruta_archivo, 'r') as f:
            # Leemos y limpiamos saltos de línea o espacios extra
            lineas = [linea.strip() for linea in f.readlines() if linea.strip()]
            
        n = int(lineas[0])
        
        # Procesar estado inicial
        estado_inicial = []
        for i in range(1, n + 1):
            fila = [int(x) for x in lineas[i].split(',')]
            estado_inicial.extend(fila)
            
        # Procesar estado meta
        estado_meta = []
        for i in range(n + 1, 2 * n + 1):
            fila = [int(x) for x in lineas[i].split(',')]
            estado_meta.extend(fila)
            
        return n, tuple(estado_inicial), tuple(estado_meta)
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta {ruta_archivo}")
        return None, None, None
    except Exception as e:
        print(f"Error procesando el archivo: {e}")
        return None, None, None

def formatear_salida(secuencia_movimientos):
    """
    Toma una lista de movimientos ['U', 'R', 'D'] y 
    la formatea exactamente como pide el examen: U,R,D
    """
    if not secuencia_movimientos:
        return "No se encontraron movimientos."
    
    salida_formateada = ",".join(secuencia_movimientos)
    print(f"Salida: {salida_formateada}")
    return salida_formateada

# ==========================================
# Ejemplo de uso (Bloque principal)
# ==========================================
if __name__ == "__main__":
    # Suponiendo que tu archivo se llama "prueba1.txt"
    archivo_prueba = "prueba1.txt"
    
    # Simulación de creación del archivo para que lo puedas probar ahorita
    with open(archivo_prueba, "w") as f:
        f.write("3\n1,2,3\n8,4,5\n7,6,0\n1,2,3\n8,0,4\n7,6,5\n")
        
    print("Leyendo archivo...")
    n, inicial, meta = leer_tableros(archivo_prueba)
    
    if n:
        print(f"Dimensión: {n}x{n}")
        print(f"Estado Inicial (1D): {inicial}")
        print(f"Estado Meta (1D): {meta}")
        
        # Simulación de la salida del IDA*
        movimientos_simulados = ['U', 'R', 'D']
        formatear_salida(movimientos_simulados)