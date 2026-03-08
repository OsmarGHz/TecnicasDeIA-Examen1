import os
import time
import csv
import multiprocessing

from algoritmo import leer_tableros, IDAStar

def worker_solver(inicial, meta, dimension, queue):
    try:
        solver = IDAStar(inicial, meta, dimension)
        movimientos = solver.resolver(limite_prof=50)
        queue.put(movimientos)
    except Exception as e:
        queue.put(f"ERROR: {str(e)}")

def ejecutarPrueba(rutaArchivo, dimension, limite_tiempo):
    n, inicial, meta = leer_tableros(rutaArchivo)
    if not n:
        return False, 0.0, "Error de lectura de archivo"
        
    queue = multiprocessing.Queue()
    proceso = multiprocessing.Process(target=worker_solver, args=(inicial, meta, dimension, queue))
    
    tiempoInicio = time.perf_counter()
    proceso.start()
    
    # El programa principal espera aquí hasta que pase el limite_tiempo (120s)
    proceso.join(limite_tiempo)
    
    if proceso.is_alive():
        proceso.terminate()
        proceso.join()
        return False, limite_tiempo, "Timeout (Tiempo Excedido)"
        
    tiempoEjecucion = time.perf_counter() - tiempoInicio
    
    if not queue.empty():
        resultado = queue.get()
        if isinstance(resultado, list):
            return True, tiempoEjecucion, len(resultado)
        elif isinstance(resultado, str) and resultado.startswith("ERROR"):
            return False, tiempoEjecucion, resultado
        else:
            return False, tiempoEjecucion, "No resuelto (Superó 50 movs)"
    else:
        return False, tiempoEjecucion, "Fallo interno"

def procesarDimension(dimension, archivoCsv, limite_tiempo):
    carpetaBase = f"Instancias_{dimension}x{dimension}"
    dificultades = ['buenos_10', 'regulares_20', 'malos_50']
    
    if not os.path.exists(carpetaBase):
        print(f"\n[AVISO] No se encontró la carpeta {carpetaBase}")
        return

    print(f"\nEvaluando tableros {dimension}x{dimension} (Timeout: {limite_tiempo}s)")
    
    with open(archivoCsv, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        for dificultad in dificultades:
            rutaSubcarpeta = os.path.join(carpetaBase, dificultad)
            if not os.path.exists(rutaSubcarpeta):
                continue
                
            archivos = [f for f in os.listdir(rutaSubcarpeta) if f.endswith('.txt')]
            print(f"  Procesando {len(archivos)} instancias de nivel: {dificultad}...")
            
            exitos = 0
            fallos_tiempo = 0
            fallos_profundidad = 0
            
            for archivo in archivos:
                rutaCompleta = os.path.join(rutaSubcarpeta, archivo)
                resuelto, tiempo, info = ejecutarPrueba(rutaCompleta, dimension, limite_tiempo)
                
                if resuelto:
                    exitos += 1
                elif info == "Timeout (Tiempo Excedido)":
                    fallos_tiempo += 1
                else:
                    fallos_profundidad += 1
                    

                writer.writerow([f"{dimension}x{dimension}", dificultad, archivo, resuelto, round(tiempo, 4), info])

                file.flush() 
                os.fsync(file.fileno())
                
            print(f"    -> {exitos} Resueltos | {fallos_tiempo} Timeouts | {fallos_profundidad} Sin Solución")


def menuAnalizador():
    nombreCsv = "resultados_analisis_ida_star.csv"
    if not os.path.exists(nombreCsv):
        with open(nombreCsv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Dimension", "Dificultad", "Archivo", "SolucionEncontrada", "TiempoSegundos", "MovimientosRealizados_o_Fallo"])
    limite_tiempo_segundos = 120.0 

    while True:
        print("\n== Analizador IDA* ==")
        print("1. Evaluar una dimension especifica")
        print("2. Evaluar todo el dataset (3x3 a 8x8)")
        print(f"3. Configurar timeout (Actual: {limite_tiempo_segundos}s)")
        print("4. Salir")
        
        opcion = input("Opcion (1-4): ")
        
        if opcion == '1':
            try:
                dim = int(input("Ingresa la dimensión a evaluar (Ej. 3 para 3x3): "))
                if dim >= 3:
                    procesarDimension(dim, nombreCsv, limite_tiempo_segundos)
                    print(f"\nResultados guardados en: {nombreCsv}")
                else:
                    print("[ERROR] Dimensión inválida.")
            except ValueError:
                print("[ERROR] Ingresa un número válido.")
                
        elif opcion == '2':
            confirmar = input("Esto puede tardar bastante. Continuar? (s/n): ")
            if confirmar.lower() == 's':
                for dim in range(3, 9):
                    procesarDimension(dim, nombreCsv, limite_tiempo_segundos)
                print(f"\nResultados guardados en: {nombreCsv}")
                
        elif opcion == '3':
            try:
                nuevo_tiempo = float(input("Nuevo limite en segundos: "))
                if nuevo_tiempo > 0:
                    limite_tiempo_segundos = nuevo_tiempo
                    print(f"Limite actualizado a {limite_tiempo_segundos}s.")
                else:
                    print("[ERROR] El tiempo debe ser mayor a 0.")
            except ValueError:
                print("[ERROR] Ingresa un número válido.")
                
        elif opcion == '4':
            print("Saliendo...")
            break
            
        else:
            print("\n[ERROR] Opción no válida.\n")

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    menuAnalizador()