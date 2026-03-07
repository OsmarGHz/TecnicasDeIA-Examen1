import os

def auditarArchivo(rutaArchivo):
    """Verifica que la estructura y piezas de una instancia sean correctas."""
    try:
        with open(rutaArchivo, 'r') as f:
            lineas = [linea.strip() for linea in f.readlines() if linea.strip()]
            
        dimension = int(lineas[0])
        totalPiezas = dimension * dimension
        
        estadoInicial = []
        for i in range(1, dimension + 1):
            fila = [int(x) for x in lineas[i].split(',')]
            estadoInicial.extend(fila)
            
        estadoMeta = []
        for i in range(dimension + 1, 2 * dimension + 1):
            fila = [int(x) for x in lineas[i].split(',')]
            estadoMeta.extend(fila)
            
        # Verificar longitud
        if len(estadoInicial) != totalPiezas or len(estadoMeta) != totalPiezas:
            return False, f"Longitud incorrecta. Se esperaban {totalPiezas} piezas."
            
        # Verificar que esten todos los numeros del 0 al N^2-1 sin repetir
        setEsperado = set(range(totalPiezas))
        if set(estadoInicial) != setEsperado:
            return False, "El estado inicial tiene numeros repetidos o faltantes."
        if set(estadoMeta) != setEsperado:
            return False, "El estado meta tiene numeros repetidos o faltantes."
            
        return True, "OK"
        
    except Exception as e:
        return False, f"Archivo corrupto o mal formateado: {e}"

def escanearCarpeta(rutaCarpeta, mostrarDetalles=True):
    if mostrarDetalles:
        print(f"\nEscaneando: {rutaCarpeta}")
    
    archivosTotales = 0
    archivosSanos = 0
    archivosCorruptos = []
    
    if not os.path.exists(rutaCarpeta):
        if mostrarDetalles:
            print(f"La carpeta '{rutaCarpeta}' no existe.")
        return 0, 0, []

    for raiz, subcarpetas, archivos in os.walk(rutaCarpeta):
        for nombreArchivo in archivos:
            if nombreArchivo.endswith('.txt'):
                archivosTotales += 1
                rutaCompleta = os.path.join(raiz, nombreArchivo)
                
                esValido, mensaje = auditarArchivo(rutaCompleta)
                
                if esValido:
                    archivosSanos += 1
                else:
                    archivosCorruptos.append((rutaCompleta, mensaje))
                    
    if mostrarDetalles:
        imprimirReporte(rutaCarpeta, archivosTotales, archivosSanos, archivosCorruptos)
        
    return archivosTotales, archivosSanos, archivosCorruptos

def imprimirReporte(titulo, totales, sanos, corruptos):
    print(f"\n-- Reporte: {titulo} --")
    print(f"Archivos analizados: {totales}")
    print(f"Validos: {sanos}")
    print(f"Con errores: {len(corruptos)}")
    
    if corruptos:
        print("\nProblemas encontrados:")
        for archivo, error in corruptos:
            print(f" -> {archivo}: {error}")
    elif totales > 0:
        print("Todas las instancias son correctas.")
    print()

def verificarTodoElDataset():
    print("\nVerificando dataset completo (3x3 a 8x8)...")
    granTotal = 0
    granSanos = 0
    granCorruptos = []
    
    for dim in range(3, 9):
        carpeta = f"Instancias_{dim}x{dim}"
        print(f"  Revisando {carpeta}...")
        t, s, c = escanearCarpeta(carpeta, mostrarDetalles=False)
        granTotal += t
        granSanos += s
        granCorruptos.extend(c)
        
    imprimirReporte("Dataset completo", granTotal, granSanos, granCorruptos)

def menuVerificador():
    while True:
        print("\n== Verificador de Instancias ==")
        print("1. Verificar todo el dataset")
        print("2. Verificar una dimension especifica")
        print("3. Salir")
        
        opcion = input("Opcion (1-3): ")
        
        if opcion == '1':
            verificarTodoElDataset()
        elif opcion == '2':
            dim = input("Dimension a verificar (ej. 3 para 3x3): ")
            carpeta = f"Instancias_{dim}x{dim}"
            escanearCarpeta(carpeta)
        elif opcion == '3':
            print("Saliendo...")
            break
        else:
            print("Opcion no valida.")

if __name__ == "__main__":
    menuVerificador()