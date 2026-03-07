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


class NodoPuzzle:
    def __init__(self, estado, g=0, movimiento=None, padre=None):
        self.estado = estado # Tupla 1D, ej: (1, 2, 3, 8, 0, 4, 7, 6, 5)
        self.g = g           # Costo acumulado (profundidad)
        self.h = 0           # Valor heurístico ajustado
        self.f = 0           # f(n) = g_norm + h'
        self.movimiento = movimiento # 'U', 'D', 'L', 'R'
        self.padre = padre

    # Sobreescribimos los operadores de comparación para el Move Ordering
    def __lt__(self, otro):
        return self.f < otro.f

class IDAStarSolver:
    def __init__(self, estado_inicial, estado_meta, dimension):
        self.estado_inicial = estado_inicial
        self.estado_meta = estado_meta
        self.N = dimension
        self.T = dimension * dimension - 1
        self.memoria_global = {} # Tabla Hash para transposición entre iteraciones

    def calcular_f(self, nodo, g_max):
        estado = nodo.estado
        meta = self.estado_meta
        N, T = self.N, self.T

        # Pre-cálculo: posición de cada valor en la meta
        pos_meta = {meta[i]: i for i in range(N * N)}

        # 1. g normalizado
        g_norm = nodo.g / g_max if g_max > 0 else 0

        # 2. Manhattan y 3. Hamming (un solo recorrido)
        manhattan = 0
        hamming = 0
        for i in range(N * N):
            val = estado[i]
            if val == 0:
                continue
            idx_meta = pos_meta[val]
            f_act, c_act = divmod(i, N)
            f_meta, c_meta = divmod(idx_meta, N)
            manhattan += abs(f_act - f_meta) + abs(c_act - c_meta)
            if i != idx_meta:
                hamming += 1
        h_man = manhattan / (T * (2 * N - 2)) if T > 0 else 0
        h_ham = hamming / T if T > 0 else 0

        # 4. Inversiones
        lista_sin_cero = [v for v in estado if v != 0]
        inversiones = 0
        for i in range(len(lista_sin_cero)):
            for j in range(i + 1, len(lista_sin_cero)):
                if lista_sin_cero[i] > lista_sin_cero[j]:
                    inversiones += 1
        max_inv = T * (T - 1) / 2
        h_inv = inversiones / max_inv if max_inv > 0 else 0

        # 5. Conflicto lineal
        conflictos = 0
        for fila in range(N):
            # Piezas en esta fila que también pertenecen a esta fila en la meta
            piezas_fila = []
            for c in range(N):
                val = estado[fila * N + c]
                if val == 0:
                    continue
                f_meta, c_meta = divmod(pos_meta[val], N)
                if f_meta == fila:
                    piezas_fila.append((c, c_meta))
            for i in range(len(piezas_fila)):
                for j in range(i + 1, len(piezas_fila)):
                    if piezas_fila[i][0] < piezas_fila[j][0] and piezas_fila[i][1] > piezas_fila[j][1]:
                        conflictos += 2
        for col in range(N):
            piezas_col = []
            for f in range(N):
                val = estado[f * N + col]
                if val == 0:
                    continue
                f_meta, c_meta = divmod(pos_meta[val], N)
                if c_meta == col:
                    piezas_col.append((f, f_meta))
            for i in range(len(piezas_col)):
                for j in range(i + 1, len(piezas_col)):
                    if piezas_col[i][0] < piezas_col[j][0] and piezas_col[i][1] > piezas_col[j][1]:
                        conflictos += 2
        h_lin = conflictos / (4 * N) if N > 0 else 0

        # 6. Secuencia
        penalizacion_sec = 0
        for i in range(len(lista_sin_cero) - 1):
            if lista_sin_cero[i] + 1 != lista_sin_cero[i + 1]:
                penalizacion_sec += 3
        h_sec = penalizacion_sec / (3 * T) if T > 0 else 0

        # Integración final con pesos
        f = (0.25 * g_norm) + (0.40 * h_man) + (0.15 * h_lin) + (0.10 * h_inv) + (0.07 * h_sec) + (0.03 * h_ham)
        return f

    def generar_sucesores(self, nodo):
        sucesores = []
        idx = nodo.estado.index(0)
        fila, col = divmod(idx, self.N)
        # (dirección, delta_fila, delta_col)
        movimientos = [('U', -1, 0), ('D', 1, 0), ('L', 0, -1), ('R', 0, 1)]
        for dir, df, dc in movimientos:
            nf, nc = fila + df, col + dc
            if 0 <= nf < self.N and 0 <= nc < self.N:
                nuevo_idx = nf * self.N + nc
                tmp = list(nodo.estado)
                tmp[idx], tmp[nuevo_idx] = tmp[nuevo_idx], tmp[idx]
                sucesores.append(NodoPuzzle(tuple(tmp), g=nodo.g + 1, movimiento=dir, padre=nodo))
        return sucesores

    def busqueda_recursiva(self, nodo_actual, umbral_f, nivel_max, lista_tabu, g_max):
        # 1. Control interno estricto de profundidad
        if nodo_actual.g > nivel_max:
            return "FALLO", float('inf'), None

        # 2. Evaluación de la función maestra
        nodo_actual.f = self.calcular_f(nodo_actual, g_max)
        
        # 3. Poda por límite de costo
        if nodo_actual.f > umbral_f:
            return "FALLO", nodo_actual.f, None
            
        # 4. Condición de éxito
        if nodo_actual.estado == self.estado_meta:
            return "ÉXITO", umbral_f, nodo_actual

       # 5. Consulta a la memoria de iteraciones previas (Transposition Table)
        # Guardamos una tupla (f_actual, g_actual)
        if nodo_actual.estado in self.memoria_global:
            f_mem, g_mem = self.memoria_global[nodo_actual.estado]
            # Podamos SOLO si ya visitamos este estado con un costo igual o mejor,
            # Y con una profundidad igual o menor (es decir, teníamos más presupuesto de exploración)
            if f_mem <= nodo_actual.f and g_mem <= nodo_actual.g:
                return "FALLO", float('inf'), None
                
        # Registramos/Actualizamos el estado con su f y g actuales
        self.memoria_global[nodo_actual.estado] = (nodo_actual.f, nodo_actual.g)

        min_exceso = float('inf')
        sucesores = self.generar_sucesores(nodo_actual)
        
        # 6. Move Ordering (Ordenar por f menor a mayor)
        for suc in sucesores:
            suc.f = self.calcular_f(suc, g_max)
        sucesores.sort() 

        # 7. Criterio Tabú dinámico
        for sucesor in sucesores:
            if sucesor.estado not in lista_tabu:
                lista_tabu.add(sucesor.estado) # Agregar a memoria
                
                resultado, nuevo_umbral, nodo_meta = self.busqueda_recursiva(
                    sucesor, umbral_f, nivel_max, lista_tabu, g_max
                )
                
                if resultado == "ÉXITO":
                    return "ÉXITO", umbral_f, nodo_meta
                    
                if nuevo_umbral < min_exceso:
                    min_exceso = nuevo_umbral
                    
                lista_tabu.remove(sucesor.estado) # Backtracking

        return "FALLO", min_exceso, None

    def resolver(self, limite_profundidad_global=50):
        # Inicialización
        nodo_raiz = NodoPuzzle(self.estado_inicial)
        nodo_raiz.f = self.calcular_f(nodo_raiz, limite_profundidad_global)
        umbral_f = nodo_raiz.f
        
        nivel_max_iteracion = 1
        
        while nivel_max_iteracion <= limite_profundidad_global:
            print(f"Iteración Nivel: {nivel_max_iteracion} | Umbral f: {umbral_f:.4f}")
            lista_tabu_actual = {nodo_raiz.estado}
            
            resultado, nuevo_umbral, nodo_meta = self.busqueda_recursiva(
                nodo_raiz, umbral_f, nivel_max_iteracion, lista_tabu_actual, limite_profundidad_global
            )
            
            if resultado == "ÉXITO":
                return self._reconstruir_camino(nodo_meta)
                
            if nuevo_umbral == float('inf'):
                break
                
            umbral_f = nuevo_umbral
            nivel_max_iteracion += 1
            
        return None

    def _reconstruir_camino(self, nodo_meta):
        camino = []
        actual = nodo_meta
        while actual.padre is not None:
            camino.append(actual.movimiento)
            actual = actual.padre
        return camino[::-1] # Invertimos para que sea desde el inicio a la meta

if __name__ == "__main__":
    archivo_prueba = "prueba1.txt"
    
    print("1. Leyendo archivo...")
    n, inicial, meta = leer_tableros(archivo_prueba)
    
    if n:
        print(f"Dimensión: {n}x{n}")
        
        print("\n2. Iniciando el cerebro IDA*...")
        # Le pasamos los datos que leímos del archivo a la clase solver
        solver = IDAStarSolver(inicial, meta, n)
        
        print("Buscando solución (esto puede tardar unos segundos)...")
        # Mandamos a resolver con un límite de 50 movimientos (como pide el examen)
        movimientos_encontrados = solver.resolver(limite_profundidad_global=50)
        
        print("\n3. Resultados:")
        if movimientos_encontrados:
            formatear_salida(movimientos_encontrados)
        else:
            print("No se encontró solución dentro del límite de profundidad.")