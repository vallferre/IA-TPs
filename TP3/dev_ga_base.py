'''
Condiciones
~~~~~~~~~~~
1. Hay 5 casas.
2. El Matematico vive en la casa roja.
3. El hacker programa en Python.
4. El Brackets es utilizado en la casa verde.
5. El analista usa Atom.
6. La casa verde esta a la derecha de la casa blanca.
7. La persona que usa Redis programa en Java
8. Cassandra es utilizado en la casa amarilla
9. Notepad++ es usado en la casa del medio.
10. El Desarrollador vive en la primer casa.
11. La persona que usa HBase vive al lado de la que programa en JavaScript.
12. La persona que usa Cassandra es vecina de la que programa en C#.
13. La persona que usa Neo4J usa Sublime Text.
14. El Ingeniero usa MongoDB.
15. EL desarrollador vive en la casa azul.

Quien usa vim?


Resumen:
Colores = Rojo, Azul, Verde, Blanco, Amarillo
Profesiones = Matematico, Hacker, Ingeniero, Analista, Desarrollador
Lenguaje = Python, C#, JAVA, C++, JavaScript
BD = Cassandra, MongoDB, Neo4j, Redis, HBase
editor = Brackets, Sublime Text, Atom, Notepad++, Vim
'''

import random
import time


colors =      {'001' : 'red',          '010' : 'blue',          '011' : 'green',    '100' : 'white',    '101' : 'yellow'}
prefession =  {'001' : 'Mathematician','010' : 'Hacker',        '011' : 'Engineer', '100' : 'Analyst',  '101' : 'Developer'}
languaje =    {'001' : 'Python',       '010' : 'C#',            '011' : 'Java',     '100' : 'C++',      '101' : 'JavaScript'}
database =    {'001' : 'Cassandra',    '010' : 'MongoDB',       '011' : 'HBase',    '100' : 'Neo4j',    '101' : 'Redis'}
editor =      {'001' : 'Brackets',     '010' : 'Sublime Text',  '011' : 'Vim',      '100' : 'Atom',     '101' : 'Notepad++'}

CODES = ('001', '010', '011', '100', '101')
N_HOUSES = 5
N_ATTRS = 5
GENE_COUNT = N_HOUSES * N_ATTRS
MAX_FITNESS = 14

rev_colors = {value: code for code, value in colors.items()}
rev_prefession = {value: code for code, value in prefession.items()}
rev_languaje = {value: code for code, value in languaje.items()}
rev_database = {value: code for code, value in database.items()}
rev_editor = {value: code for code, value in editor.items()}


class Phenotype:

    def __init__(self, chromosome=None):
        if chromosome is None:
            self.chromosome = self._random_chromosome()
        else:
            self.chromosome = list(chromosome)
        self.score = 0

    def _random_chromosome(self):
        ''' cada atributo es una permutación: no hay valores repetidos al nacer '''
        chromosome = [None] * GENE_COUNT
        for attr in range(N_ATTRS):
            perm = random.sample(CODES, N_HOUSES)
            for house in range(N_HOUSES):
                chromosome[house * N_ATTRS + attr] = perm[house]
        return chromosome

    def decode(self):
        ''' traduce 0's y 1's (conjunto de genes: 3) en valores segun un diccionario '''
        return [[colors[self.chromosome[i*5+0]],
                 prefession[self.chromosome[i*5+1]],
                 languaje[self.chromosome[i*5+2]],
                 database[self.chromosome[i*5+3]],
                 editor[self.chromosome[i*5+4]]] for i in range(5)]

    def encode(self, decoded=None):
        ''' inversa de decode: cada casa vuelve a sus 5 códigos de 3 bits '''
        if decoded is None:
            return list(self.chromosome)

        self.chromosome = []
        for house in decoded:
            self.chromosome.extend([
                rev_colors[house[0]],
                rev_prefession[house[1]],
                rev_languaje[house[2]],
                rev_database[house[3]],
                rev_editor[house[4]],
            ])
        return self.chromosome

    def repair(self):
        ''' completa los valores que el cruce dejó repetidos dentro de un atributo '''
        for attr in range(N_ATTRS):
            positions = [house * N_ATTRS + attr for house in range(N_HOUSES)]
            seen = set()
            duplicates = []
            for pos in positions:
                gene = self.chromosome[pos]
                if gene in seen:
                    duplicates.append(pos)
                else:
                    seen.add(gene)
            missing = [code for code in CODES if code not in seen]
            random.shuffle(missing)
            for pos, gene in zip(duplicates, missing):
                self.chromosome[pos] = gene

    def mutate(self):
        ''' muta un fenotipo, optimizado: intercambia un atributo entre dos casas y solo lo deja si no empeora '''
        self.fitness_function()
        for _ in range(6):
            if self.score >= MAX_FITNESS:
                return

            attr = random.randrange(N_ATTRS)
            house_a, house_b = random.sample(range(N_HOUSES), 2)
            index_a = house_a * N_ATTRS + attr
            index_b = house_b * N_ATTRS + attr
            self.chromosome[index_a], self.chromosome[index_b] = (
                self.chromosome[index_b],
                self.chromosome[index_a],
            )

            previous = self.score
            self.fitness_function()
            if self.score < previous:
                self.chromosome[index_a], self.chromosome[index_b] = (
                    self.chromosome[index_b],
                    self.chromosome[index_a],
                )
                self.score = previous

    def fitness_function(self):
        ''' calcula el valor de fitness del cromosoma segun el problema en particular '''

        self.score = 0

        ok_score = 1
        fail_score = -1
        punish_score = -1

        chromosome = self.decode()

        def award(condition):
            self.score += ok_score if condition else fail_score

        def find(attr, value):
            for index, house in enumerate(chromosome):
                if house[attr] == value:
                    return index
            return None

        for attr in range(N_ATTRS):
            values = [house[attr] for house in chromosome]
            repeated = len(values) - len(set(values))
            self.score += punish_score * repeated

        # 2. El matematico vive en la casa roja.
        award(any(house[0] == 'red' and house[1] == 'Mathematician' for house in chromosome))
        # 3. El hacker programa en Python.
        award(any(house[1] == 'Hacker' and house[2] == 'Python' for house in chromosome))
        # 4. Brackets se usa en la casa verde.
        award(any(house[0] == 'green' and house[4] == 'Brackets' for house in chromosome))
        # 5. El analista usa Atom.
        award(any(house[1] == 'Analyst' and house[4] == 'Atom' for house in chromosome))
        # 6. La casa verde está inmediatamente a la derecha de la blanca.
        white = find(0, 'white')
        green = find(0, 'green')
        award(white is not None and green is not None and green == white + 1)
        # 7. Quien usa Redis programa en Java.
        award(any(house[3] == 'Redis' and house[2] == 'Java' for house in chromosome))
        # 8. Cassandra está en la casa amarilla.
        award(any(house[0] == 'yellow' and house[3] == 'Cassandra' for house in chromosome))
        # 9. Notepad++ está en la casa del medio.
        award(chromosome[2][4] == 'Notepad++')
        # 10. El desarrollador vive en la primera casa.
        award(chromosome[0][1] == 'Developer')
        # 11. HBase es vecino de quien programa en JavaScript.
        hbase = find(3, 'HBase')
        javascript = find(2, 'JavaScript')
        award(hbase is not None and javascript is not None and abs(hbase - javascript) == 1)
        # 12. Cassandra es vecina de quien programa en C#.
        cassandra = find(3, 'Cassandra')
        csharp = find(2, 'C#')
        award(cassandra is not None and csharp is not None and abs(cassandra - csharp) == 1)
        # 13. Quien usa Neo4j usa Sublime Text.
        award(any(house[3] == 'Neo4j' and house[4] == 'Sublime Text' for house in chromosome))
        # 14. El ingeniero usa MongoDB.
        award(any(house[1] == 'Engineer' and house[3] == 'MongoDB' for house in chromosome))
        # 15. El desarrollador vive en la casa azul.
        award(any(house[1] == 'Developer' and house[0] == 'blue' for house in chromosome))

        return self.score

class Riddle:

    def __init__(self):
        self.start_time = time.time()
        self.population = []


    '''
    proceso general
    '''
    def solve(self, n_population):

        self.generate(n_population)
        print(f"Población creada con {len(self.population)} individuos")

        ''' descomentame '''
        #print(self.population[0].chromosome)
        #print(self.population[0].decode())

        print("Inicio del proceso iterativo")
        fit, indi = self.iterar()

        print(f"Fin del proceso, mejor resultado \n - Fitness: {fit} \n - Individuo {indi.chromosome} \n - Individuo {indi.decode()}")

        for number, house in enumerate(indi.decode(), start=1):
            if house[4] == 'Vim':
                print(f"Quien usa Vim: {house[1]} (casa {number})")
                print(f"Casa {number}: color={house[0]}, profesion={house[1]}, lenguaje={house[2]}, bd={house[3]}, editor={house[4]}")


    def iterar(self):

        counter = 0
        break_condition = False

        crossover_prop = 0.80
        N = len(self.population)
        N2 = 3000
        elite = 40
        immigrants = 40
        best_score = None

        while not(break_condition):

            # seleccion: fitness y quedan ordenados de mejor a peor
            for i, x in enumerate(self.population):
                x.fitness_function()

            self.population.sort(key=lambda individual: individual.score, reverse=True)

            current = self.population[0].score
            if counter % 100 == 0 or best_score is None or current > best_score:
                best_score = current
                print("--------------------------------")
                print(counter)
                print(f"fitness {best_score}")
                print(self.population[0].decode())

            if self.population[0].score >= MAX_FITNESS:
                break_condition = True
                break

            # crossover: los mejores se conservan; el resto se rehace con padres del mejor tercio
            parent_pool = max(2, N // 3)
            for s in range(elite, N - immigrants, 2):
                if random.random() < crossover_prop:
                    progenitor_1 = max(random.sample(self.population[:parent_pool], 2), key=lambda individual: individual.score)
                    progenitor_2 = max(random.sample(self.population[:parent_pool], 2), key=lambda individual: individual.score)
                    limit = random.randint(1, GENE_COUNT - 1)
                    child_1, child_2 = self.crossOver(progenitor_1, progenitor_2, limit)
                    self.population[s] = child_1
                    if s + 1 < N - immigrants:
                        self.population[s + 1] = child_2

            for index in range(N - immigrants, N):
                self.population[index] = Phenotype()

            # mutate (el mejor queda igual)
            for individual in self.population[1:]:
                self.mutate(individual, prob=0.5)

            # condicion de corte
            if counter > N2:
                for individual in self.population:
                    individual.fitness_function()
                self.population.sort(key=lambda individual: individual.score, reverse=True)
                break_condition = True

            counter += 1

        return self.population[0].score, self.population[0]

    '''
    operacion: generar individuos y agregarlos a la poblacion
    '''
    def generate(self, i):
        for x in range(0,i):
            newbie = Phenotype()
            self.population.append(newbie)

    '''
    operacion: mutación. Cambiar la configuración fenotipica de un individuo
    '''
    def mutate(self, crossed, prob=0.5):
        if random.random() < prob:
            crossed.mutate()


    '''
    operacion: cruazamiento. Intercambio de razos fenotipicos entre individuos
    '''
    def crossOver(self, progenitor_1, progenitor_2, limit):
        genes_1 = progenitor_1.chromosome
        genes_2 = progenitor_2.chromosome
        child_1 = Phenotype(genes_1[:limit] + genes_2[limit:])
        child_2 = Phenotype(genes_2[:limit] + genes_1[limit:])
        child_1.repair()
        child_2.repair()
        return child_1, child_2

start = time.time()

rid = Riddle()
rid.solve(n_population = 2000)

end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print("Tiempo transcurrido {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
