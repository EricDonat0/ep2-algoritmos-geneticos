from __future__ import annotations

import argparse
from pathlib import Path

from .cases.inventory_restocking import InventoryRestockingProblem
from .ga import GeneticAlgorithm
from .utils import markdown_table, mermaid_xy_chart


def parse_csv_ints(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def parse_csv_floats(raw: str) -> list[float]:
    return [float(item.strip()) for item in raw.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Estudo de hiperparâmetros do AG de reabastecimento de estoque."
    )
    parser.add_argument("--pop-values", default="80,120")
    parser.add_argument("--mut-values", default="0.03,0.08")
    parser.add_argument("--generations", type=int, default=150)
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
    parser.add_argument("--output", default="docs/hiperparametros.md")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    population_values = parse_csv_ints(args.pop_values)
    mutation_values = parse_csv_floats(args.mut_values)

    rows: list[list[object]] = []
    charts: list[str] = []

    for population_size in population_values:
        for mutation_rate in mutation_values:
            problem = InventoryRestockingProblem()
            ga = GeneticAlgorithm(
                problem=problem,
                population_size=population_size,
                generations=args.generations,
                mutation_rate=mutation_rate,
                crossover_rate=args.crossover_rate,
                selection_method=args.selection,
                crossover_method=args.crossover,
                elite_size=args.elite_size,
                tournament_size=args.tournament_size,
                patience=args.patience,
                seed=args.seed,
            )
            result = ga.run()
            violations = problem.violations(result.best_individual)
            rows.append(
                [
                    population_size,
                    f"{mutation_rate:.2f}",
                    f"{result.best_fitness:.2f}",
                    result.generations_executed,
                    sum(violations.values()),
                ]
            )
            charts.append(
                "\n".join(
                    [
                        f"## Convergência — pop={population_size}, mut={mutation_rate:.2f}",
                        "",
                        mermaid_xy_chart(
                            f"Evolução do Fitness — pop={population_size}, mut={mutation_rate:.2f}",
                            [stat.max_fitness for stat in result.history],
                        ),
                        "",
                    ]
                )
            )

    document = "\n".join(
        [
            "# Estudo de hiperparâmetros",
            "",
            "## Configuração experimental",
            "",
            markdown_table(
                ["Parâmetro", "Valor"],
                [
                    ["Populações testadas", ", ".join(str(value) for value in population_values)],
                    ["Taxas de mutação testadas", ", ".join(f"{value:.2f}" for value in mutation_values)],
                    ["Gerações máximas", args.generations],
                    ["Critério de convergência", f"Estagnação por {args.patience} gerações"],
                    ["Taxa de crossover", args.crossover_rate],
                    ["Seleção", args.selection],
                    ["Crossover", args.crossover],
                    ["Elitismo", args.elite_size],
                    ["Seed", args.seed],
                ],
            ),
            "",
            "## Resultados por combinação",
            "",
            markdown_table(
                [
                    "Tamanho da população",
                    "Taxa de mutação",
                    "Melhor fitness alcançado",
                    "Gerações até convergência",
                    "Número de violações da solução final",
                ],
                rows,
            ),
            "",
            "## Discussão",
            "",
            "- Populações maiores tendem a gerar diversidade adicional, mas aumentam o custo computacional por geração.",
            "- Taxas de mutação moderadas costumam equilibrar exploração e estabilidade; taxas muito baixas podem prender o AG em soluções com custo maior.",
            "- A combinação escolhida para o README deve priorizar zero violações e bom fitness final, não apenas convergência rápida.",
            "",
            *charts,
        ]
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(document)


if __name__ == "__main__":
    main()
