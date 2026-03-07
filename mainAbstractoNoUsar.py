import os

def leer_tableros(ruta_archivo):
    """Lee el archivo de entrada y regresa la dimension, estado inicial y estado meta."""
    try:
        with open(ruta_archivo, 'r') as f:
            lineas = [linea.strip() for linea in f.readlines() if linea.strip()]
            
        n = int(lineas[0])
        
        estado_inicial = []
        for i in range(1, n + 1):
            fila = [int(x) for x in lineas[i].split(',')]
            estado_inicial.extend(fila)
            
        estado_meta = []
        for i in range(n + 1, 2 * n + 1):
            fila = [int(x) for x in lineas[i].split(',')]
            estado_meta.extend(fila)
            
        return n, tuple(estado_inicial), tuple(estado_meta)
        
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo {ruta_archivo}")
        return None, None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def formatear_salida(movimientos):
    """Imprime los movimientos separados por comas."""
    if not movimientos:
        return "No se encontraron movimientos."
    
    salida = ",".join(movimientos)
    print(f"Salida: {salida}")
    return salida

if __name__ == "__main__":
    archivo = "prueba1.txt"
    
    # Crear archivo de prueba
    with open(archivo, "w") as f:
        f.write("3\n1,2,3\n8,4,5\n7,6,0\n1,2,3\n8,0,4\n7,6,5\n")
        
    print("Leyendo archivo...")
    n, inicial, meta = leer_tableros(archivo)
    
    if n:
        print(f"Dimension: {n}x{n}")
        print(f"Inicial: {inicial}")
        print(f"Meta: {meta}")
        
        movimientos_test = ['U', 'R', 'D']
        formatear_salida(movimientos_test)