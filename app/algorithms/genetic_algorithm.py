import random
from typing import List, Dict, Set
from ..models import TimeTable, TimeTableMain, Instructor, Venue, CourseName
from datetime import datetime, timedelta

class TimetableGene:
    def __init__(self, course, instructor, venue, time_start, time_end, day, session_type):
        self.course = course
        self.instructor = instructor
        self.venue = venue
        self.time_start = time_start
        self.time_end = time_end
        self.day = day
        self.session_type = session_type

class TimetableChromosome:
    def __init__(self, genes):
        self.genes = genes
        self.fitness = 0
        self.lectures_per_day = self._count_lectures_per_day()

    def _count_lectures_per_day(self):
        day_counts = {'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0}
        for gene in self.genes:
            day_counts[gene.day] += 1
        return day_counts

class GeneticTimetableAlgorithm:
    def __init__(self, 
                 population_size=50, 
                 mutation_rate=0.1, 
                 elite_size=2,
                 generations=100):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size
        self.generations = generations
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        # Continuous time slots from 10:00 to 17:00 with lunch break
        self.time_slots = [
            ('10:00', '11:00'),
            ('11:00', '12:00'),
            ('12:00', '13:00'),
            # Lunch break 13:00-14:00
            ('14:00', '15:00'),
            ('15:00', '16:00'),
            ('16:00', '17:00'),
        ]
        self.min_lectures_per_day = 6
        self.max_lectures_per_day = 7

    def initialize_population(self, programme, semester, year_of_study) -> List[TimetableChromosome]:
        population = []
        
        try:
            timetable_main = TimeTableMain.objects.get(
                Programme=programme,
                Semister=semester,
                YearOfStudy=year_of_study
            )
            
            department = timetable_main.Department
            dept_prefix = department.DepartmentName.split()[0][:2].upper()
            
            courses = CourseName.objects.filter(CourseCode__startswith=dept_prefix)
            if not courses.exists():
                courses = CourseName.objects.all()
            
            instructors = Instructor.objects.filter(Department=department)
            if not instructors.exists():
                instructors = Instructor.objects.all()
            
            venues = Venue.objects.all()
            
            print(f"Found {courses.count()} courses, {instructors.count()} instructors, {venues.count()} venues")

            for _ in range(self.population_size):
                genes = []
                # Create balanced schedule for each day
                for day in self.days:
                    day_slots = self.time_slots.copy()
                    num_lectures = random.randint(self.min_lectures_per_day, self.max_lectures_per_day)
                    
                    for _ in range(num_lectures):
                        if not day_slots:  # No more available time slots
                            break
                            
                        course = random.choice(courses)
                        instructor = random.choice(instructors)
                        venue = random.choice(venues)
                        time_slot = random.choice(day_slots)
                        day_slots.remove(time_slot)  # Remove used time slot
                        
                        gene = TimetableGene(
                            course=course,
                            instructor=instructor,
                            venue=venue,
                            time_start=time_slot[0],
                            time_end=time_slot[1],
                            day=day,
                            session_type=random.choice(['Lecture', 'Tutorial', 'Lab'])
                        )
                        genes.append(gene)
                
                chromosome = TimetableChromosome(genes)
                population.append(chromosome)
            
            return population
            
        except Exception as e:
            print(f"Error in initialize_population: {str(e)}")
            raise

    def calculate_fitness(self, chromosome: TimetableChromosome) -> float:
        conflicts = 0
        
        # Check basic constraints (same as before)
        for i, gene1 in enumerate(chromosome.genes):
            for j, gene2 in enumerate(chromosome.genes[i+1:]):
                if gene1.day == gene2.day:
                    # Same instructor at same time
                    if (gene1.instructor == gene2.instructor and 
                        gene1.time_start == gene2.time_start):
                        conflicts += 1
                    
                    # Same venue at same time
                    if (gene1.venue == gene2.venue and 
                        gene1.time_start == gene2.time_start):
                        conflicts += 1
                    
                    # Same course at same time
                    if (gene1.course == gene2.course and 
                        gene1.time_start == gene2.time_start):
                        conflicts += 1

        # Check lectures per day constraints
        for day, count in chromosome.lectures_per_day.items():
            if count < self.min_lectures_per_day:
                conflicts += (self.min_lectures_per_day - count)
            elif count > self.max_lectures_per_day:
                conflicts += (count - self.max_lectures_per_day)

        # Calculate fitness (inverse of conflicts)
        fitness = 1 / (conflicts + 1)
        chromosome.fitness = fitness
        return fitness

    def select_parents(self, population: List[TimetableChromosome]) -> List[TimetableChromosome]:
        # Tournament selection
        tournament_size = 3
        selected = []
        
        for _ in range(len(population)):
            tournament = random.sample(population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected

    def crossover(self, parent1: TimetableChromosome, parent2: TimetableChromosome) -> tuple:
        if len(parent1.genes) != len(parent2.genes):
            raise ValueError("Parents must have same number of genes")
        
        crossover_point = random.randint(0, len(parent1.genes)-1)
        
        child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
        
        return (TimetableChromosome(child1_genes), TimetableChromosome(child2_genes))

    def mutate(self, chromosome: TimetableChromosome):
        for gene in chromosome.genes:
            if random.random() < self.mutation_rate:
                # Randomly change one attribute
                mutation_type = random.choice(['time', 'day', 'venue', 'instructor'])
                
                if mutation_type == 'time':
                    time_slot = random.choice(self.time_slots)
                    gene.time_start = time_slot[0]
                    gene.time_end = time_slot[1]
                elif mutation_type == 'day':
                    gene.day = random.choice(self.days)
                elif mutation_type == 'venue':
                    gene.venue = random.choice(Venue.objects.all())
                elif mutation_type == 'instructor':
                    gene.instructor = random.choice(Instructor.objects.all())

    def evolve(self, programme, semester, year_of_study) -> TimetableChromosome:
        # Initialize population
        population = self.initialize_population(programme, semester, year_of_study)
        
        # Evolution loop
        for generation in range(self.generations):
            # Calculate fitness for all chromosomes
            for chromosome in population:
                self.calculate_fitness(chromosome)
            
            # Sort population by fitness
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Keep elite chromosomes
            new_population = population[:self.elite_size]
            
            # Selection
            parents = self.select_parents(population)
            
            # Crossover
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(parents, 2)
                child1, child2 = self.crossover(parent1, parent2)
                new_population.extend([child1, child2])
            
            # Trim population to original size
            new_population = new_population[:self.population_size]
            
            # Mutation
            for chromosome in new_population[self.elite_size:]:
                self.mutate(chromosome)
            
            population = new_population
            
            # Print progress
            best_fitness = max(population, key=lambda x: x.fitness).fitness
            print(f"Generation {generation}: Best Fitness = {best_fitness}")
        
        # Return best solution
        return max(population, key=lambda x: x.fitness) 