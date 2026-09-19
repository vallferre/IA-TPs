# search.py
# ---------
# Implementación de los algoritmos de búsqueda para el TP2 - Pacman
# UADE - Inteligencia Artificial
#
# Este archivo respeta la interfaz estándar del proyecto Pacman (Berkeley AI):
#   problem.getStartState()            -> estado inicial
#   problem.isGoalState(state)         -> True/False
#   problem.getSuccessors(state)       -> lista de (sucesor, accion, costo)
#   problem.getCostOfActions(actions)  -> costo total de una secuencia de acciones
#
# Si tu código base ya trae un search.py con clases SearchProblem, Node, etc.,
# reemplazá únicamente el cuerpo de las 4 funciones (depthFirstSearch,
# breadthFirstSearch, uniformCostSearch, aStarSearch) por lo que está acá abajo,
# manteniendo las firmas y los imports de util (Stack, Queue, PriorityQueue)
# que ya existan en tu proyecto.

import util


class SearchProblem:
    """
    Clase abstracta que define la estructura de un problema de búsqueda.
    Si tu proyecto ya tiene esta clase en pacman.py o searchAgents.py, no la
    dupliques: dejá solo las funciones de más abajo.
    """

    def getStartState(self):
        util.raiseNotDefined()

    def isGoalState(self, state):
        util.raiseNotDefined()

    def getSuccessors(self, state):
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Devuelve una secuencia de movimientos que resuelve tinyMaze.
    (Función de ejemplo que suele venir ya resuelta en el TP)
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem):
    """
    Búsqueda en Profundidad (DFS).

    Estrategia: explora lo más profundo posible por cada rama antes de
    retroceder (backtrack). Usa una PILA (LIFO) como frontera.

    No garantiza el camino más corto ni el de menor costo, pero suele
    usar poca memoria.
    """
    frontera = util.Stack()
    visitados = set()

    estado_inicial = problem.getStartState()
    # cada elemento de la frontera: (estado, lista_de_acciones_hasta_aca)
    frontera.push((estado_inicial, []))

    while not frontera.isEmpty():
        estado, acciones = frontera.pop()

        if problem.isGoalState(estado):
            return acciones

        if estado not in visitados:
            visitados.add(estado)

            for sucesor, accion, costo in problem.getSuccessors(estado):
                if sucesor not in visitados:
                    frontera.push((sucesor, acciones + [accion]))

    return []  # no se encontró solución


def breadthFirstSearch(problem):
    """
    Búsqueda en Anchura (BFS).

    Estrategia: explora todos los nodos de un nivel antes de pasar al
    siguiente. Usa una COLA (FIFO) como frontera.

    Garantiza el camino con MENOR CANTIDAD DE PASOS (óptimo cuando todos
    los costos de las acciones son iguales).
    """
    frontera = util.Queue()
    visitados = set()

    estado_inicial = problem.getStartState()

    if problem.isGoalState(estado_inicial):
        return []

    frontera.push((estado_inicial, []))
    visitados.add(estado_inicial)

    while not frontera.isEmpty():
        estado, acciones = frontera.pop()

        for sucesor, accion, costo in problem.getSuccessors(estado):
            if sucesor not in visitados:
                nuevas_acciones = acciones + [accion]

                if problem.isGoalState(sucesor):
                    return nuevas_acciones

                visitados.add(sucesor)
                frontera.push((sucesor, nuevas_acciones))

    return []  # no se encontró solución


def uniformCostSearch(problem):
    """
    Búsqueda de Costo Uniforme (UCS).

    Estrategia: expande siempre el nodo con MENOR costo acumulado g(n).
    Usa una COLA DE PRIORIDAD ordenada por g(n).

    Garantiza el camino de MENOR COSTO TOTAL (óptimo), a diferencia de BFS
    que solo garantiza menor cantidad de pasos.
    """
    frontera = util.PriorityQueue()
    visitados = set()

    estado_inicial = problem.getStartState()
    # se guarda (estado, acciones, costo_acumulado); la prioridad es el costo
    frontera.push((estado_inicial, [], 0), 0)

    while not frontera.isEmpty():
        estado, acciones, costo_acumulado = frontera.pop()

        if problem.isGoalState(estado):
            return acciones

        if estado not in visitados:
            visitados.add(estado)

            for sucesor, accion, costo in problem.getSuccessors(estado):
                if sucesor not in visitados:
                    nuevo_costo = costo_acumulado + costo
                    frontera.push(
                        (sucesor, acciones + [accion], nuevo_costo),
                        nuevo_costo
                    )

    return []  # no se encontró solución


def nullHeuristic(state, problem=None):
    """
    Heurística trivial: siempre devuelve 0.
    Con esta heurística, A* se comporta exactamente igual que UCS.
    """
    return 0


def aStarSearch(problem, heuristic=nullHeuristic):
    """
    Búsqueda A*.

    Estrategia: como UCS, pero prioriza por f(n) = g(n) + h(n), donde:
      - g(n): costo acumulado real desde el inicio hasta n
      - h(n): estimación heurística del costo desde n hasta la meta

    Si la heurística es admisible (nunca sobreestima el costo real
    restante), A* es óptimo y generalmente explora muchos menos nodos
    que UCS.
    """
    frontera = util.PriorityQueue()
    visitados = set()

    estado_inicial = problem.getStartState()
    h_inicial = heuristic(estado_inicial, problem)
    # se guarda (estado, acciones, costo_acumulado); prioridad = f(n) = g(n)+h(n)
    frontera.push((estado_inicial, [], 0), h_inicial)

    while not frontera.isEmpty():
        estado, acciones, costo_acumulado = frontera.pop()

        if problem.isGoalState(estado):
            return acciones

        if estado not in visitados:
            visitados.add(estado)

            for sucesor, accion, costo in problem.getSuccessors(estado):
                if sucesor not in visitados:
                    g = costo_acumulado + costo
                    f = g + heuristic(sucesor, problem)
                    frontera.push(
                        (sucesor, acciones + [accion], g),
                        f
                    )

    return []  # no se encontró solución


# Abreviaturas (así suelen invocarse desde la consola del proyecto)
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch