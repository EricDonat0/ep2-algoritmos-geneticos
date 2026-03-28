from __future__ import annotations

import argparse

from .cases.inventory_restocking import InventoryRestockingProblem
from .ga import GAResult, GeneticAlgorithm
from .utils import markdown_table


def print_history(result: GAResult) -> None:
    rows = [
        [
            stat.generation,
            f"{stat.min_fitness:.2f}",
            f"{stat.avg_fitness:.2f}",
            f"{stat.max_fitness:.2f}",
        ]
        for stat in result.history
    ]
    print("# Evolução do fitness por geração")
    print()
    print(markdown_table(["Geração", "Mínimo", "Médio", "Máximo"], rows))
    print()


def print_summary(problem: InventoryRestockingProblem, result: GAResult) -> None:
    violations = problem.violations(result.best_individual)
    rows = [
        ["Fitness da melhor solução", f"{result.best_fitness:.2f}"],
        ["Geração da melhor solução", result.best_generation],
        ["Gerações executadas", result.generations_executed],
        ["Total de violações", sum(violations.values())],
        ["Descrição do cromossomo", problem.chromosome_description()],
    ]
    print("# Resumo da execução")
    print()
    print(markdown_table(["Métrica", "Valor"], rows))
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AG para otimização de reabastecimento de estoque em rede de supermercados."
    )
    parser.add_argument("--population-size", type=int, default=120)
    parser.add_argument("--generations", type=int, default=180)
    parser.add_argument("--mutation-rate", type=float, default=0.03)
    parser.add_argument("--crossover-rate", type=float, default=0.85)
    parser.add_argument("--selection", choices=["tournament", "roulette"], default="tournament")
    parser.add_argument(
        "--crossover",
        choices=["single_point", "two_point", "uniform"],
        default="two_point",
    )
    parser.add_argument("--elite-size", type=int, default=4)
    parser.add_argument("--tournament-size", type=int, default=3)
    parser.add_argument("--patience", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> None:
    args = build_parser().parse_args()

    problem = InventoryRestockingProblem()
    ga = GeneticAlgorithm(
        problem=problem,
        population_size=args.population_size,
        generations=args.generations,
        mutation_rate=args.mutation_rate,
        crossover_rate=args.crossover_rate,
        selection_method=args.selection,
        crossover_method=args.crossover,
        elite_size=args.elite_size,
        tournament_size=args.tournament_size,
        patience=args.patience,
        seed=args.seed,
    )
    result = ga.run()

    print_history(result)
    print_summary(problem, result)
    print(problem.format_solution_report(result.best_individual, result.best_fitness))


if __name__ == "__main__":
    main()
