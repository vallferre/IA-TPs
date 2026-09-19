# TP2 — Búsqueda en Pacman
UADE · Inteligencia Artificial

Este documento explica **qué se hizo para que el proyecto funcione** y **cómo trabajan los algoritmos** implementados en `search.py`.

---

## 1. Qué se hizo para que funcione

El TP usa el proyecto Pacman de UC Berkeley (adaptado para UADE). La idea no es programar el juego entero, sino **completar los algoritmos de búsqueda** y dejar el resto del código tal cual.

### El problema inicial

Al principio la carpeta solo tenía `search.py`. Ese archivo hace:

```python
import util
```

`util` no es un paquete de pip ni un módulo de Python. Es un archivo del código base de Pacman (`util.py`) que trae las estructuras de datos de la frontera:

| Clase | Uso |
| --- | --- |
| `util.Stack()` | pila LIFO → DFS |
| `util.Queue()` | cola FIFO → BFS |
| `util.PriorityQueue()` | cola de prioridad → UCS y A* |

Sin el resto del proyecto, Python respondía:

```text
ModuleNotFoundError: No module named 'util'
```

No fallaba el `import` en sí: **faltaba el código base** (`util.py`, `pacman.py`, `game.py`, laberintos, etc.).

### Qué se armó

1. Se incorporó el código base de Pacman (juego, gráficos, layouts, agentes).
2. Se dejó el `search.py` propio, con DFS, BFS, UCS y A* ya implementados.
3. No se modificaron archivos del motor (`pacman.py`, `game.py`, `util.py`, etc.).

En este TP **solo se completa lo marcado con `*** YOUR CODE HERE ***`**.

| Archivo | Qué se edita |
| --- | --- |
| `search.py` | los 4 algoritmos de búsqueda (**ya está**) |
| `searchAgents.py` | problemas extra (esquinas, heurísticas, comida más cercana) si el enunciado lo pide |
| El resto | no se toca |

### Cómo se conectan las piezas

1. `pacman.py` arranca el juego y carga un laberinto.
2. `SearchAgent` (en `searchAgents.py`) arma un `PositionSearchProblem`: estado = posición `(x, y)`, meta = casilla objetivo.
3. Llama a una función de `search.py` (`dfs`, `bfs`, `ucs` o `astar`).
4. Esa función usa la interfaz del problema:
   - `getStartState()` → estado inicial
   - `isGoalState(state)` → ¿llegué?
   - `getSuccessors(state)` → lista de `(sucesor, acción, costo)`
   - `getCostOfActions(actions)` → costo total de un camino
5. Devuelve una lista de acciones (`North`, `South`, `East`, `West`).
6. Pacman recorre ese camino en pantalla.

Todos los algoritmos siguen el mismo esquema de **búsqueda en grafo**:

- hay una **frontera** (nodos por explorar)
- hay un conjunto de **visitados** (para no expandir dos veces el mismo estado)
- cada ítem de la frontera guarda `(estado, acciones_hasta_acá)`
- se sale cuando se encuentra un estado meta, devolviendo esas acciones

Lo único que cambia entre algoritmos es **cómo se elige el próximo nodo** (el tipo de frontera).

---

## 2. Cómo ejecutar el juego

Hay que correr **`pacman.py`** desde esta carpeta.

Juego clásico (control con teclado):

```text
python pacman.py
```

Ver los algoritmos en el laberinto:

```text
python pacman.py -l tinyMaze -p SearchAgent -a fn=dfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
```

Si `python` no está en el PATH:

```text
C:\Python313\python.exe pacman.py -l tinyMaze -p SearchAgent -a fn=bfs
```

No usar `-q` si se quiere ver la ventana gráfica. Más comandos están en `commands.txt`.

---

## 3. Los algoritmos

### Idea común

Se busca un camino desde la posición de Pacman hasta la meta. El laberinto es un grafo: cada casilla libre es un nodo, y moverse a una casilla vecina es una arista.

```text
inicio ──► frontera ──► expandir sucesores ──► ¿es meta? ──sí──► devolver acciones
                ▲                                    │
                └──────── si no, seguir buscando ────┘
```

---

### DFS — Búsqueda en profundidad (`depthFirstSearch`)

**Estructura:** pila (`util.Stack`), política LIFO: último en entrar, primero en salir.

**Estrategia:** entra lo más profundo posible por una rama. Si se traba, retrocede (backtrack) y prueba otra.

**En el código:** se saca un estado de la pila; si no es meta y no estaba visitado, se marcan visitados sus sucesores y se los apila.

**Propiedades:**

- Completo en grafo (con visitados): si hay solución, la encuentra.
- **No es óptimo:** el primer camino que encuentra no tiene por qué ser el más corto.
- Usa relativamente poca memoria, porque guarda sobre todo la rama actual.

**En Pacman:** suele llegar, pero a veces con un recorrido largo y “de zigzag”. En `tinyMaze` el costo típico de DFS fue 10, mientras que el óptimo es 8.

---

### BFS — Búsqueda en anchura (`breadthFirstSearch`)

**Estructura:** cola (`util.Queue`), política FIFO: primero en entrar, primero en salir.

**Estrategia:** explora nivel por nivel. Primero todos los vecinos a 1 paso, después a 2, después a 3, y así.

**En el código:** el estado inicial se marca visitado al encolarlo. Cuando se descubre un sucesor que es meta, se devuelve el camino en el acto (sin esperar a expanderlo).

**Propiedades:**

- Completo.
- **Óptimo en cantidad de pasos**, si todas las acciones cuestan lo mismo (en el laberinto normal, cada movimiento vale 1).
- Usa más memoria que DFS: guarda toda la “franja” del nivel actual.

**En Pacman:** encuentra el camino más corto en número de movimientos. En `tinyMaze` el costo fue 8.

---

### UCS — Búsqueda de costo uniforme (`uniformCostSearch`)

**Estructura:** cola de prioridad (`util.PriorityQueue`), ordenada por el costo acumulado **g(n)**.

**Estrategia:** siempre expande el nodo más barato hasta ahora. Si todos los pasos cuestan 1, se parece a BFS. Si hay costos distintos, elige el de menor suma, no el de menos pasos.

**En el código:** cada ítem de la frontera es `(estado, acciones, costo_acumulado)` y la prioridad es ese costo. Un estado se marca visitado **al expanderlo**, no al descubrirlo, para no perder un camino más barato que llegue después.

**Propiedades:**

- Completo (con costos ≥ 0).
- **Óptimo en costo total**, no solo en cantidad de pasos.
- Puede expandir más nodos que BFS/A* si hay muchos caminos de costo similar.

**En Pacman:** en el laberinto común coincide con BFS (costo 8 en `tinyMaze`). Se nota la diferencia en mapas con costos distintos, por ejemplo `StayEastSearchAgent` / `StayWestSearchAgent`.

---

### A* (`aStarSearch`)

**Estructura:** cola de prioridad, igual que UCS, pero ordenada por

```text
f(n) = g(n) + h(n)
```

- **g(n):** costo real acumulado desde el inicio hasta n (igual que UCS).
- **h(n):** heurística, estimación del costo que falta hasta la meta.

**Estrategia:** prioriza nodos que ya costaron poco **y** que parecen estar cerca de la meta.

**Heurísticas en este proyecto:**

| Heurística | Qué hace |
| --- | --- |
| `nullHeuristic` | siempre 0 → A* se comporta como UCS |
| `manhattanHeuristic` | \|x1 − x2\| + \|y1 − y2\|, ignorando paredes |

Manhattan es **admisible** en esta grilla: nunca sobreestima el costo real, porque Pacman no puede ir en diagonal y cada paso cuesta al menos 1.

**Propiedades (si h es admisible):**

- Completo.
- **Óptimo.**
- En general **expande menos nodos** que UCS, porque descarta antes ramas que se alejan de la meta.

**En Pacman:** en `tinyMaze` el costo también fue 8, pero expandió 14 nodos contra 15 de UCS/BFS. En laberintos grandes la diferencia se nota más.

---

## 4. Comparación rápida

| | DFS | BFS | UCS | A* |
| --- | --- | --- | --- | --- |
| Frontera | pila | cola | cola de prioridad | cola de prioridad |
| Elige según | el más reciente | el más antiguo | menor **g(n)** | menor **g(n) + h(n)** |
| ¿Encuentra solución? | sí (con visitados) | sí | sí | sí |
| ¿Camino más corto? | no | sí, si el costo es uniforme | sí, en costo total | sí, si h es admisible |
| Memoria | baja | alta | alta | alta, pero suele explorar menos |
| Uso típico | “cualquier camino” | menos pasos | costos distintos | mismo objetivo que UCS, más guiado |

Los cuatro algoritmos son casi el mismo código. Cambia la frontera y, en UCS/A*, el valor con el que se ordena.

---

## 5. Qué falta (si el enunciado lo pide)

`search.py` ya cubre la parte de búsqueda genérica. En `searchAgents.py` siguen huecos `*** YOUR CODE HERE ***` para:

- `CornersProblem` — visitar las 4 esquinas
- `cornersHeuristic`
- `foodHeuristic` — comer todos los dots
- `findPathToClosestDot`
- `AnyFoodSearchProblem.isGoalState`

Eso no hace falta para ver DFS/BFS/UCS/A* en `tinyMaze` / `mediumMaze` / `bigMaze`.
