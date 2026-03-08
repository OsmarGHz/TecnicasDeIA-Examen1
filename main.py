import sys
from algoritmo import leer_tableros, IDAStar, formatear_salida

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else "prueba1.txt"
    
    n, inicial, meta = leer_tableros(archivo)
    
    if n:
        solver = IDAStar(inicial, meta, n)
        movimientos = solver.resolver(limite_prof=50)
        
        if movimientos:
            formatear_salida(movimientos)
        else:
            print("No se encontro solucion dentro del limite de profundidad.")
