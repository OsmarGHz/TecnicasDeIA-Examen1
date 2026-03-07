import random
import os


def obtenerMovimientosValidos(estado, dimension):
    sucesores = []
    idx = estado.index(0) # Buscamos dónde está el espacio en blanco (0)
    fila, col = divmod(idx, dimension)
    
    movimientos = [('U', -1, 0), ('D', 1, 0), ('L', 0, -1), ('R', 0, 1)]
    for dirMov, df, dc in movimientos:
        nf, nc = fila + df, col + dc
        if 0 <= nf < dimension and 0 <= nc < dimension:
            nuevoIdx = nf * dimension + nc
            tmp = list(estado)
            tmp[idx], tmp[nuevoIdx] = tmp[nuevoIdx], tmp[idx]
            sucesores.append((dirMov, tuple(tmp)))
            
    return sucesores

def generarTablero(numMovimientos, dimension, estadoMeta):
    estadoActual = estadoMeta
    ultimoMov = None
    opuestos = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}
    
    for _ in range(numMovimientos):
        movimientosPosibles = obtenerMovimientosValidos(estadoActual, dimension)
        
        movimientosPermitidos = []
        for mov, nuevoEstado in movimientosPosibles:
            # Regla Tabú: No deshacer el movimiento que acabamos de hacer
            if ultimoMov is None or mov != opuestos[ultimoMov]:
                movimientosPermitidos.append((mov, nuevoEstado))
        
        movElegido, estadoActual = random.choice(movimientosPermitidos)
        ultimoMov = movElegido
        
    return estadoActual

def generarEstadoMeta(dimension):
    """Genera el estado meta para la dimensión N dada."""
    totalPiezas = dimension * dimension
    # Creamos una lista del 1 hasta el N^2 - 1, y le agregamos el 0 al final
    elementos = list(range(1, totalPiezas)) + [0]
    return tuple(elementos)


def exportarArchivoTxt(estadoInicial, estadoMeta, dimension, rutaArchivo):
    try:
        with open(rutaArchivo, 'w') as f:
            f.write(f"{dimension}\n")
            
            # Imprimimos el estado inicial
            for i in range(dimension):
                fila = estadoInicial[i*dimension : (i+1)*dimension]
                f.write(",".join(map(str, fila)) + "\n")
                
            # Imprimimos el estado meta
            for i in range(dimension):
                fila = estadoMeta[i*dimension : (i+1)*dimension]
                f.write(",".join(map(str, fila)) + "\n")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo {rutaArchivo}: {e}")

def procesarDimension(dimension, totalInstancias):
    print(f"\nGenerando tableros {dimension}x{dimension}...")
    
    estadoMeta = generarEstadoMeta(dimension)
    
    # Niveles de dificultad con sus respectivos movimientos hacia atrás
    dificultades = {
        'buenos_10': 10,
        'regulares_20': 20,
        'malos_50': 50
    }
    
    carpetaBase = f"Instancias_{dimension}x{dimension}"
    if not os.path.exists(carpetaBase):
        os.makedirs(carpetaBase)
        
    for nombreCarpeta, numMovimientos in dificultades.items():
        rutaSubcarpeta = os.path.join(carpetaBase, nombreCarpeta)
        if not os.path.exists(rutaSubcarpeta):
            os.makedirs(rutaSubcarpeta)
            
        print(f"  Creando {totalInstancias} instancias en la carpeta '{nombreCarpeta}'...")
        
        for i in range(1, totalInstancias + 1):
            tablero = generarTablero(numMovimientos, dimension, estadoMeta)
            nombreArchivo = f"instancia_{i}.txt"
            rutaCompleta = os.path.join(rutaSubcarpeta, nombreArchivo)
            
            exportarArchivoTxt(tablero, estadoMeta, dimension, rutaCompleta)
            
    print(f"[OK] Dimensión {dimension}x{dimension} completada.")

def generarTodoElDataset():
    totalInstanciasPorDificultad = 100
    print("\nCreando dataset completo (3x3 a 8x8)...")
    
    for dimension in range(3, 9):
        procesarDimension(dimension, totalInstanciasPorDificultad)
        
    print("\nDataset generado correctamente.\n")


def menuCiclado():
    while True:
        print("\n== Generador de Instancias ==")
        print("1. Generar dataset completo (3x3 a 8x8)")
        print("2. Generar una dimensión específica")
        print("3. Salir")
        
        opcion = input("Elige una opción (1-3): ")
        
        if opcion == '1':
            generarTodoElDataset()
            
        elif opcion == '2':
            try:
                dim = int(input("Ingresa la dimensión deseada (Ej. 3 para 3x3): "))
                if dim >= 2:
                    procesarDimension(dim, 100)
                else:
                    print("[ERROR] La dimensión debe ser mayor o igual a 2.")
            except ValueError:
                print("[ERROR] Por favor, ingresa un número válido.")
                
        elif opcion == '3':
            print("Saliendo...")
            break
            
        else:
            print("\n[ERROR] Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    menuCiclado()