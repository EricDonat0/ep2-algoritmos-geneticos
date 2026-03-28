from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
import random


Individual = Any
Violations = Dict[str, int]


class Problem(ABC):
    """Contrato mínimo para um problema resolvido por Algoritmo Genético."""

    @abstractmethod
    def random_individual(self, rng: random.Random) -> Individual:
        """Gera um indivíduo inicial válido ou reparável."""

    @abstractmethod
    def fitness(self, individual: Individual) -> float:
        """Calcula a aptidão do indivíduo."""

    @abstractmethod
    def violations(self, individual: Individual) -> Violations:
        """Retorna a contagem de violações por restrição."""

    @abstractmethod
    def mutate(
        self,
        individual: Individual,
        mutation_rate: float,
        rng: random.Random,
    ) -> Individual:
        """Aplica mutação específica do problema."""

    @abstractmethod
    def crossover(
        self,
        parent_a: Individual,
        parent_b: Individual,
        method: str,
        rng: random.Random,
    ) -> tuple[Individual, Individual]:
        """Aplica crossover e garante indivíduos válidos ou reparáveis."""

    @abstractmethod
    def format_solution_report(self, individual: Individual, fitness: float) -> str:
        """Retorna a solução final em Markdown/tabelas de texto."""

    @abstractmethod
    def chromosome_description(self) -> str:
        """Descrição textual do cromossomo."""

    def total_violations(self, individual: Individual) -> int:
        return sum(self.violations(individual).values())

    def is_valid(self, individual: Individual) -> bool:
        return self.total_violations(individual) == 0
