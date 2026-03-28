from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import List, Sequence
import copy
import random

from .problem_base import Individual, Problem


@dataclass
class GenerationStats:
    generation: int
    min_fitness: float
    avg_fitness: float
    max_fitness: float


@dataclass
class GAResult:
    best_individual: Individual
    best_fitness: float
    history: List[GenerationStats]
    generations_executed: int
    best_generation: int


class GeneticAlgorithm:
    def __init__(
        self,
        problem: Problem,
        population_size: int,
        generations: int,
        mutation_rate: float,
        crossover_rate: float,
        selection_method: str = "tournament",
        crossover_method: str = "two_point",
        elite_size: int = 1,
        tournament_size: int = 3,
        patience: int | None = None,
        seed: int | None = None,
    ) -> None:
        self.problem = problem
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.selection_method = selection_method
        self.crossover_method = crossover_method
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.rng = random.Random(seed)
        self.patience = patience

        if self.population_size < 2:
            raise ValueError("population_size deve ser >= 2")
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError("mutation_rate deve estar em [0, 1]")
        if not 0.0 <= self.crossover_rate <= 1.0:
            raise ValueError("crossover_rate deve estar em [0, 1]")
        if self.elite_size < 0 or self.elite_size >= self.population_size:
            raise ValueError("elite_size deve estar entre 0 e population_size - 1")

    def _initial_population(self) -> List[Individual]:
        return [self.problem.random_individual(self.rng) for _ in range(self.population_size)]

    def _evaluate(self, population: Sequence[Individual]) -> List[float]:
        return [self.problem.fitness(individual) for individual in population]

    def _sort_by_fitness(
        self,
        population: Sequence[Individual],
        fitnesses: Sequence[float],
    ) -> List[tuple[Individual, float]]:
        combined = list(zip(population, fitnesses))
        combined.sort(key=lambda item: item[1], reverse=True)
        return combined

    def _select_parent(
        self,
        population: Sequence[Individual],
        fitnesses: Sequence[float],
    ) -> Individual:
        if self.selection_method == "tournament":
            return self._tournament_selection(population, fitnesses)
        if self.selection_method == "roulette":
            return self._roulette_selection(population, fitnesses)
        raise ValueError(f"Método de seleção inválido: {self.selection_method}")

    def _tournament_selection(
        self,
        population: Sequence[Individual],
        fitnesses: Sequence[float],
    ) -> Individual:
        indices = [self.rng.randrange(len(population)) for _ in range(self.tournament_size)]
        best_index = max(indices, key=lambda idx: fitnesses[idx])
        return copy.deepcopy(population[best_index])

    def _roulette_selection(
        self,
        population: Sequence[Individual],
        fitnesses: Sequence[float],
    ) -> Individual:
        min_fit = min(fitnesses)
        shift = -min_fit + 1.0 if min_fit <= 0 else 0.0
        weights = [fitness + shift for fitness in fitnesses]
        total = sum(weights)

        if total <= 0.0:
            return copy.deepcopy(population[self.rng.randrange(len(population))])

        pick = self.rng.uniform(0.0, total)
        cumulative = 0.0
        for individual, weight in zip(population, weights):
            cumulative += weight
            if cumulative >= pick:
                return copy.deepcopy(individual)
        return copy.deepcopy(population[-1])

    def run(self) -> GAResult:
        population = self._initial_population()
        history: List[GenerationStats] = []

        best_individual: Individual | None = None
        best_fitness = float("-inf")
        best_generation = 0
        generations_without_improvement = 0

        for generation in range(self.generations + 1):
            fitnesses = self._evaluate(population)
            ordered = self._sort_by_fitness(population, fitnesses)
            current_best, current_best_fitness = ordered[0]

            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = copy.deepcopy(current_best)
                best_generation = generation
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1

            history.append(
                GenerationStats(
                    generation=generation,
                    min_fitness=min(fitnesses),
                    avg_fitness=mean(fitnesses),
                    max_fitness=max(fitnesses),
                )
            )

            if generation == self.generations:
                break
            if self.patience is not None and generations_without_improvement >= self.patience:
                break

            next_population: List[Individual] = [
                copy.deepcopy(individual) for individual, _ in ordered[: self.elite_size]
            ]

            while len(next_population) < self.population_size:
                parent_a = self._select_parent(population, fitnesses)
                parent_b = self._select_parent(population, fitnesses)

                if self.rng.random() < self.crossover_rate:
                    child_a, child_b = self.problem.crossover(
                        parent_a,
                        parent_b,
                        self.crossover_method,
                        self.rng,
                    )
                else:
                    child_a, child_b = copy.deepcopy(parent_a), copy.deepcopy(parent_b)

                child_a = self.problem.mutate(child_a, self.mutation_rate, self.rng)
                child_b = self.problem.mutate(child_b, self.mutation_rate, self.rng)

                next_population.append(child_a)
                if len(next_population) < self.population_size:
                    next_population.append(child_b)

            population = next_population

        if best_individual is None:
            raise RuntimeError("Nenhum indivíduo foi produzido pelo AG.")

        return GAResult(
            best_individual=best_individual,
            best_fitness=best_fitness,
            history=history,
            generations_executed=history[-1].generation,
            best_generation=best_generation,
        )
