import os
import sys

def leer_tableros(ruta_archivo):
    """Lee el archivo de entrada y regresa la dimension, estado inicial y estado meta como tuplas 1D."""
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
        print(f"Error: No se encontró el archivo en la ruta {ruta_archivo}")
        return None, None, None
    except Exception as e:
        print(f"Error procesando el archivo: {e}")
        return None, None, None

def formatear_salida(movimientos):
    """Formatea la lista de movimientos como cadena separada por comas."""
    if not movimientos:
        return "No se encontraron movimientos."
    
    salida = ",".join(movimientos)
    print(f"Salida: {salida}")
    return salida


class Nodo:
    def __init__(self, estado, g=0, movimiento=None, padre=None):
        self.estado = estado
        self.g = g
        self.h = 0
        self.f = 0
        self.movimiento = movimiento
        self.padre = padre

    def __lt__(self, otro):
        return self.f < otro.f

class IDAStar:
    def __init__(self, estado_inicial, estado_meta, dimension):
        self.estado_inicial = estado_inicial
        self.estado_meta = estado_meta
        self.N = dimension
        self.T = dimension * dimension - 1
        self.tabla_transposicion = {}

    def calcular_f(self, nodo, g_max):
        estado = nodo.estado
        meta = self.estado_meta
        N, T = self.N, self.T

        pos_meta = {meta[i]: i for i in range(N * N)}

        # g normalizado
        g_norm = nodo.g / g_max if g_max > 0 else 0

        # Manhattan y Hamming
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

        # Inversiones
        sin_cero = [v for v in estado if v != 0]
        inversiones = 0
        for i in range(len(sin_cero)):
            for j in range(i + 1, len(sin_cero)):
                if sin_cero[i] > sin_cero[j]:
                    inversiones += 1
        max_inv = T * (T - 1) / 2
        h_inv = inversiones / max_inv if max_inv > 0 else 0

        # Conflicto lineal
        conflictos = 0
        for fila in range(N):
            piezas = []
            for c in range(N):
                val = estado[fila * N + c]
                if val == 0:
                    continue
                f_meta, c_meta = divmod(pos_meta[val], N)
                if f_meta == fila:
                    piezas.append((c, c_meta))
            for i in range(len(piezas)):
                for j in range(i + 1, len(piezas)):
                    if piezas[i][0] < piezas[j][0] and piezas[i][1] > piezas[j][1]:
                        conflictos += 2
        for col in range(N):
            piezas = []
            for f in range(N):
                val = estado[f * N + col]
                if val == 0:
                    continue
                f_meta, c_meta = divmod(pos_meta[val], N)
                if c_meta == col:
                    piezas.append((f, f_meta))
            for i in range(len(piezas)):
                for j in range(i + 1, len(piezas)):
                    if piezas[i][0] < piezas[j][0] and piezas[i][1] > piezas[j][1]:
                        conflictos += 2
        h_lin = conflictos / (4 * N) if N > 0 else 0

        # Penalizacion por secuencia
        pen_sec = 0
        for i in range(len(sin_cero) - 1):
            if sin_cero[i] + 1 != sin_cero[i + 1]:
                pen_sec += 3
        h_sec = pen_sec / (3 * T) if T > 0 else 0

        # Pesos de la funcion combinada
        f = (0.25 * g_norm) + (0.40 * h_man) + (0.15 * h_lin) + (0.10 * h_inv) + (0.07 * h_sec) + (0.03 * h_ham)
        return f

    def generar_sucesores(self, nodo):
        sucesores = []
        idx = nodo.estado.index(0)
        fila, col = divmod(idx, self.N)
        movimientos = [('U', -1, 0), ('D', 1, 0), ('L', 0, -1), ('R', 0, 1)]
        for dir, df, dc in movimientos:
            nf, nc = fila + df, col + dc
            if 0 <= nf < self.N and 0 <= nc < self.N:
                nuevo_idx = nf * self.N + nc
                tmp = list(nodo.estado)
                tmp[idx], tmp[nuevo_idx] = tmp[nuevo_idx], tmp[idx]
                sucesores.append(Nodo(tuple(tmp), g=nodo.g + 1, movimiento=dir, padre=nodo))
        return sucesores

    def busqueda_recursiva(self, nodo, umbral, nivel_max, tabu, g_max):
        if nodo.g > nivel_max:
            return "FALLO", float('inf'), None

        nodo.f = self.calcular_f(nodo, g_max)
        
        if nodo.f > umbral:
            return "FALLO", nodo.f, None
            
        if nodo.estado == self.estado_meta:
            return "EXITO", umbral, nodo

        # Revisar tabla de transposicion
        if nodo.estado in self.tabla_transposicion:
            f_prev, g_prev = self.tabla_transposicion[nodo.estado]
            if f_prev <= nodo.f and g_prev <= nodo.g:
                return "FALLO", float('inf'), None
                
        self.tabla_transposicion[nodo.estado] = (nodo.f, nodo.g)

        min_exceso = float('inf')
        sucesores = self.generar_sucesores(nodo)
        
        # Ordenar sucesores por f
        for s in sucesores:
            s.f = self.calcular_f(s, g_max)
        sucesores.sort() 

        for suc in sucesores:
            if suc.estado not in tabu:
                tabu.add(suc.estado)
                
                resultado, nuevo_umbral, nodo_sol = self.busqueda_recursiva(
                    suc, umbral, nivel_max, tabu, g_max
                )
                
                if resultado == "EXITO":
                    return "EXITO", umbral, nodo_sol
                    
                if nuevo_umbral < min_exceso:
                    min_exceso = nuevo_umbral
                    
                tabu.remove(suc.estado)

        return "FALLO", min_exceso, None

    def resolver(self, limite_prof=50):
        raiz = Nodo(self.estado_inicial)
        raiz.f = self.calcular_f(raiz, limite_prof)
        umbral = raiz.f
        
        iteracion = 1
        
        while True:
            tabu = {raiz.estado}
            self.tabla_transposicion = {}
            
            resultado, nuevo_umbral, nodo_sol = self.busqueda_recursiva(
                raiz, umbral, limite_prof, tabu, limite_prof
            )
            
            if resultado == "EXITO":
                return self._reconstruir(nodo_sol)
                
            if nuevo_umbral == float('inf'):
                break
                
            umbral = nuevo_umbral
            iteracion += 1
            
        return None

    def _reconstruir(self, nodo):
        camino = []
        actual = nodo
        while actual.padre is not None:
            camino.append(actual.movimiento)
            actual = actual.padre
        return camino[::-1]

if __name__ == "__main__":
    archivo = sys.argv[1] if len(sys.argv) > 1 else "prueba1.txt"
    
    print(f"Leyendo archivo: {archivo}...")
    n, inicial, meta = leer_tableros(archivo)
    
    if n:
        print(f"Dimension: {n}x{n}")
        
        solver = IDAStar(inicial, meta, n)
        
        print("Buscando solucion...")
        movimientos = solver.resolver(limite_prof=50)
        
        print("\nResultados:")
        if movimientos:
            formatear_salida(movimientos)
        else:
            print("No se encontro solucion dentro del limite de profundidad.")