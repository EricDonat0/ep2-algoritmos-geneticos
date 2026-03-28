from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import ceil
from typing import Dict, List, Tuple
import copy
import random

from ..problem_base import Problem, Violations
from ..utils import DAY_NAMES, format_currency, markdown_table


@dataclass(frozen=True)
class Branch:
    code: str
    name: str
    capacity: int
    allowed_days: tuple[int, ...]


@dataclass(frozen=True)
class Product:
    code: str
    name: str
    validity_days: int
    supplier: str
    min_order: int
    unit_cost: float
    order_cost: float


Gene = tuple[int, int]
Individual = List[Gene]


BRANCHES: tuple[Branch, ...] = (
    Branch("F1", "Centro", 2000, (1, 3, 5)),
    Branch("F2", "Norte", 1500, (2, 4, 6)),
    Branch("F3", "Sul", 1800, (1, 3, 5)),
    Branch("F4", "Leste", 1200, (2, 4, 7)),
)

PRODUCTS: tuple[Product, ...] = (
    Product("PR01", "Arroz 5kg", 180, "FO1", 50, 18.0, 35.0),
    Product("PR02", "Feijão 1kg", 120, "FO1", 30, 7.5, 35.0),
    Product("PR03", "Óleo de soja 1L", 90, "FO2", 40, 6.0, 28.0),
    Product("PR04", "Açúcar 1kg", 180, "FO1", 60, 4.2, 35.0),
    Product("PR05", "Sal 1kg", 365, "FO3", 20, 1.8, 20.0),
    Product("PR06", "Macarrão 500g", 120, "FO2", 30, 3.5, 28.0),
    Product("PR07", "Leite UHT 1L", 60, "FO4", 100, 4.8, 45.0),
    Product("PR08", "Iogurte 170g", 21, "FO4", 80, 2.2, 45.0),
    Product("PR09", "Queijo 200g", 30, "FO4", 40, 9.5, 45.0),
    Product("PR10", "Manteiga 200g", 45, "FO4", 30, 8.0, 45.0),
    Product("PR11", "Frango kg", 5, "FO5", 50, 12.0, 60.0),
    Product("PR12", "Carne bovina kg", 7, "FO5", 30, 38.0, 60.0),
    Product("PR13", "Pão de forma", 7, "FO5", 40, 5.5, 60.0),
    Product("PR14", "Biscoito 200g", 90, "FO2", 50, 2.8, 28.0),
    Product("PR15", "Café 250g", 180, "FO1", 40, 9.0, 35.0),
    Product("PR16", "Sabão em pó 1kg", 365, "FO3", 30, 7.2, 20.0),
    Product("PR17", "Detergente 500ml", 365, "FO3", 50, 2.5, 20.0),
    Product("PR18", "Shampoo 350ml", 365, "FO3", 20, 11.0, 20.0),
    Product("PR19", "Papel higiênico", 365, "FO3", 60, 3.8, 20.0),
    Product("PR20", "Refrigerante 2L", 120, "FO2", 40, 6.5, 28.0),
)

DEMANDS: dict[str, dict[str, tuple[int, int]]] = {
    "F1": {
        "PR01": (120, 25), "PR02": (80, 15), "PR03": (90, 20), "PR04": (100, 18),
        "PR05": (60, 8), "PR06": (70, 14), "PR07": (150, 35), "PR08": (100, 22),
        "PR09": (60, 12), "PR10": (50, 10), "PR11": (80, 20), "PR12": (60, 15),
        "PR13": (70, 18), "PR14": (90, 16), "PR15": (80, 14), "PR16": (70, 10),
        "PR17": (100, 15), "PR18": (50, 8), "PR19": (120, 20), "PR20": (90, 18),
    },
    "F2": {
        "PR01": (80, 18), "PR02": (50, 10), "PR03": (60, 14), "PR04": (70, 12),
        "PR05": (40, 5), "PR06": (45, 9), "PR07": (100, 24), "PR08": (65, 14),
        "PR09": (40, 8), "PR10": (30, 6), "PR11": (50, 13), "PR12": (40, 10),
        "PR13": (45, 11), "PR14": (60, 10), "PR15": (50, 9), "PR16": (45, 6),
        "PR17": (65, 10), "PR18": (30, 5), "PR19": (80, 13), "PR20": (60, 12),
    },
    "F3": {
        "PR01": (100, 22), "PR02": (70, 13), "PR03": (80, 17), "PR04": (90, 16),
        "PR05": (50, 7), "PR06": (60, 12), "PR07": (130, 30), "PR08": (85, 18),
        "PR09": (50, 10), "PR10": (40, 8), "PR11": (70, 17), "PR12": (50, 12),
        "PR13": (60, 15), "PR14": (75, 13), "PR15": (65, 11), "PR16": (55, 8),
        "PR17": (85, 13), "PR18": (40, 6), "PR19": (100, 17), "PR20": (75, 15),
    },
    "F4": {
        "PR01": (60, 14), "PR02": (40, 8), "PR03": (50, 11), "PR04": (55, 10),
        "PR05": (30, 4), "PR06": (35, 7), "PR07": (80, 18), "PR08": (50, 11),
        "PR09": (30, 6), "PR10": (25, 5), "PR11": (40, 10), "PR12": (30, 7),
        "PR13": (35, 9), "PR14": (45, 8), "PR15": (40, 7), "PR16": (35, 5),
        "PR17": (50, 8), "PR18": (25, 4), "PR19": (60, 10), "PR20": (45, 9),
    },
}

SHORT_SHELF_CODES = {"PR11", "PR12", "PR13"}
PENALTY_WEIGHTS = {
    "R1_sem_ruptura": 100_000,
    "R2_capacidade": 40_000,
    "R3_dia_invalido": 30_000,
    "R4_pedido_minimo": 25_000,
    "R5_validade": 30_000,
    "R6_consolidacao": 0,
    "R7_estoque_seguranca": 20_000,
}
BASE_FITNESS = 10_000_000.0


class InventoryRestockingProblem(Problem):
    def __init__(self) -> None:
        self.branches = list(BRANCHES)
        self.products = list(PRODUCTS)
        self.gene_keys: list[tuple[str, str]] = [
            (branch.code, product.code)
            for branch in self.branches
            for product in self.products
        ]
        self.branch_map = {branch.code: branch for branch in self.branches}
        self.product_map = {product.code: product for product in self.products}

    def chromosome_description(self) -> str:
        return (
            "80 genes (4 filiais x 20 produtos). Cada gene é uma tupla (dia_entrega, quantidade). "
            "Dia 0 e quantidade 0 significam ausência de pedido naquela semana."
        )

    def random_individual(self, rng: random.Random) -> Individual:
        individual: Individual = []
        for branch_code, product_code in self.gene_keys:
            branch = self.branch_map[branch_code]
            product = self.product_map[product_code]
            stock0, demand = DEMANDS[branch_code][product_code]
            latest_day = self._latest_feasible_day(branch, stock0, demand)
            needed = self._min_qty_to_finish_week(stock0, demand)
            upper = self._upper_bound_qty(branch, product, stock0, demand, latest_day)
            must_order = stock0 <= demand * 7

            if not must_order and rng.random() < 0.80:
                day = 0
                qty = 0
            else:
                feasible_days = [day for day in branch.allowed_days if day <= latest_day]
                if not feasible_days:
                    feasible_days = [branch.allowed_days[0]]
                day_candidates = feasible_days[-2:] if len(feasible_days) >= 2 else feasible_days
                day = rng.choice(day_candidates)

                if upper <= 0:
                    day, qty = 0, 0
                else:
                    target = max(needed, product.min_order)
                    buffer = rng.choice([0, 0, 0, product.min_order, -product.min_order])
                    qty = max(0, target + buffer)
                    qty = min(qty, upper)
                    if qty < product.min_order and qty > 0:
                        if upper >= product.min_order:
                            qty = product.min_order
                        else:
                            qty = upper
                    if not must_order and rng.random() < 0.50:
                        day, qty = 0, 0

            individual.append(self._repair_gene(branch, product, stock0, demand, (day, qty)))
        return individual

    def fitness(self, individual: Individual) -> float:
        analysis = self._analyze(self._as_hashable(individual))
        penalties = sum(
            PENALTY_WEIGHTS[name] * count
            for name, count in analysis["violations"].items()
        )
        total_cost = analysis["total_cost"]
        return BASE_FITNESS - total_cost - penalties

    def violations(self, individual: Individual) -> Violations:
        analysis = self._analyze(self._as_hashable(individual))
        return dict(analysis["violations"])

    def mutate(
        self,
        individual: Individual,
        mutation_rate: float,
        rng: random.Random,
    ) -> Individual:
        offspring = copy.deepcopy(individual)
        mutated = False

        for index, (branch_code, product_code) in enumerate(self.gene_keys):
            if rng.random() >= mutation_rate:
                continue
            mutated = True
            branch = self.branch_map[branch_code]
            product = self.product_map[product_code]
            stock0, demand = DEMANDS[branch_code][product_code]
            day, qty = offspring[index]

            move = rng.random()
            if move < 0.25:
                if qty > 0 and rng.random() < 0.25:
                    day, qty = 0, 0
                else:
                    latest_day = self._latest_feasible_day(branch, stock0, demand)
                    feasible_days = [value for value in branch.allowed_days if value <= latest_day]
                    if not feasible_days:
                        feasible_days = list(branch.allowed_days)
                    if day == 0:
                        day = rng.choice(feasible_days)
                    else:
                        pos = feasible_days.index(day) if day in feasible_days else len(feasible_days) - 1
                        delta = rng.choice([-1, 1])
                        pos = max(0, min(len(feasible_days) - 1, pos + delta))
                        day = feasible_days[pos]
            elif move < 0.60:
                step = max(1, round(product.min_order * 0.10))
                qty = max(0, qty + rng.choice([-1, 1]) * step)
            else:
                if qty == 0:
                    day = rng.choice(branch.allowed_days)
                    qty = product.min_order
                else:
                    step = product.min_order
                    qty = max(0, qty + rng.choice([-1, 1]) * step)

            offspring[index] = self._repair_gene(branch, product, stock0, demand, (day, qty))

        if not mutated:
            idx = rng.randrange(len(offspring))
            branch_code, product_code = self.gene_keys[idx]
            branch = self.branch_map[branch_code]
            product = self.product_map[product_code]
            stock0, demand = DEMANDS[branch_code][product_code]
            day, qty = offspring[idx]
            day = branch.allowed_days[0] if day == 0 else day
            qty += max(1, round(product.min_order * 0.10))
            offspring[idx] = self._repair_gene(branch, product, stock0, demand, (day, qty))

        return offspring

    def crossover(
        self,
        parent_a: Individual,
        parent_b: Individual,
        method: str,
        rng: random.Random,
    ) -> tuple[Individual, Individual]:
        n = len(parent_a)
        if method == "single_point":
            cut = rng.randint(1, n - 2)
            child_a = parent_a[:cut] + parent_b[cut:]
            child_b = parent_b[:cut] + parent_a[cut:]
        elif method == "two_point":
            left, right = sorted(rng.sample(range(1, n - 1), 2))
            child_a = parent_a[:left] + parent_b[left:right] + parent_a[right:]
            child_b = parent_b[:left] + parent_a[left:right] + parent_b[right:]
        elif method == "uniform":
            child_a = []
            child_b = []
            for gene_a, gene_b in zip(parent_a, parent_b):
                if rng.random() < 0.5:
                    child_a.append(gene_a)
                    child_b.append(gene_b)
                else:
                    child_a.append(gene_b)
                    child_b.append(gene_a)
        else:
            raise ValueError(f"Crossover inválido: {method}")

        return self._repair_individual(child_a), self._repair_individual(child_b)

    def format_solution_report(self, individual: Individual, fitness: float) -> str:
        analysis = self._analyze(self._as_hashable(individual))
        lines: list[str] = []

        lines.append("# Melhor solução encontrada")
        lines.append("")
        lines.append("## Plano consolidado por filial, dia e fornecedor")
        lines.append("")
        lines.append(self._format_consolidated_plan(analysis))
        lines.append("")
        lines.append("## Tabela da melhor solução encontrada")
        lines.append("")
        lines.append(self._format_solution_table(individual))
        lines.append("")
        lines.append("## Evolução do estoque de cada produto ao longo da semana")
        lines.append("")
        lines.append(self._format_stock_table(analysis))
        lines.append("")
        lines.append("## Custos detalhados")
        lines.append("")
        lines.append(
            markdown_table(
                ["Componente", "Valor"],
                [
                    ["Produtos", format_currency(analysis["cost_products"])],
                    ["Pedidos consolidados", format_currency(analysis["cost_orders"])],
                    ["Rupturas", format_currency(analysis["cost_shortage"])],
                    ["Excesso final", format_currency(analysis["cost_excess"])],
                    ["Custo total", format_currency(analysis["total_cost"])],
                ],
            )
        )
        lines.append("")
        lines.append("## Violações por restrição")
        lines.append("")
        lines.append(
            markdown_table(
                ["Restrição", "Violações"],
                [[name, count] for name, count in analysis["violations"].items()],
            )
        )
        lines.append("")
        lines.append("## Resumo final")
        lines.append("")
        lines.append(
            markdown_table(
                ["Métrica", "Valor"],
                [
                    ["Fitness da melhor solução", f"{fitness:.2f}"],
                    ["Valor da função de aptidão", f"{fitness:.2f}"],
                    ["Número total de violações", sum(analysis["violations"].values())],
                    ["Cromossomo", self.chromosome_description()],
                ],
            )
        )
        return "\n".join(lines)

    def _format_solution_table(self, individual: Individual) -> str:
        rows: list[list[object]] = []
        for index, (day, qty) in enumerate(individual):
            branch_code, product_code = self.gene_keys[index]
            branch = self.branch_map[branch_code]
            product = self.product_map[product_code]
            rows.append(
                [
                    branch.code,
                    branch.name,
                    product.code,
                    product.name,
                    product.supplier,
                    DAY_NAMES[day],
                    qty,
                ]
            )
        return markdown_table(
            ["Filial", "Bairro", "Produto", "Nome", "Fornecedor", "Dia", "Quantidade"],
            rows,
        )

    def _format_consolidated_plan(self, analysis: dict) -> str:
        grouped_rows: list[list[object]] = []
        for branch in self.branches:
            entries = analysis["grouped_orders"].get(branch.code, [])
            if not entries:
                grouped_rows.append([branch.code, branch.name, "-", "-", "Sem pedidos", format_currency(0.0)])
                continue
            for entry in entries:
                grouped_rows.append(
                    [
                        branch.code,
                        branch.name,
                        f"{entry['day']} ({DAY_NAMES[entry['day']]})",
                        entry["supplier"],
                        "; ".join(entry["items"]),
                        format_currency(entry["order_cost"]),
                    ]
                )
        return markdown_table(
            ["Filial", "Bairro", "Dia", "Fornecedor", "Produtos", "Custo pedido"],
            grouped_rows,
        )

    def _format_stock_table(self, analysis: dict) -> str:
        rows: list[list[object]] = []
        stocks = analysis["stocks"]
        for branch in self.branches:
            for product in self.products:
                history = stocks[(branch.code, product.code)]
                day, qty = analysis["plan_map"][(branch.code, product.code)]
                rows.append(
                    [
                        branch.code,
                        product.code,
                        product.name,
                        DAY_NAMES[day],
                        qty,
                        *history,
                    ]
                )
        return markdown_table(
            [
                "Filial", "Produto", "Nome", "Entrega", "Qtd",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
            ],
            rows,
        )

    def _repair_individual(self, individual: Individual) -> Individual:
        repaired: Individual = []
        for gene, (branch_code, product_code) in zip(individual, self.gene_keys):
            branch = self.branch_map[branch_code]
            product = self.product_map[product_code]
            stock0, demand = DEMANDS[branch_code][product_code]
            repaired.append(self._repair_gene(branch, product, stock0, demand, gene))
        return repaired

    def _repair_gene(
        self,
        branch: Branch,
        product: Product,
        stock0: int,
        demand: int,
        gene: Gene,
    ) -> Gene:
        raw_day, raw_qty = gene
        day = int(raw_day)
        qty = max(0, int(round(raw_qty)))

        need_order = stock0 <= demand * 7
        latest_day = self._latest_feasible_day(branch, stock0, demand)
        feasible_days = [value for value in branch.allowed_days if value <= latest_day]
        if not feasible_days:
            feasible_days = list(branch.allowed_days)

        if qty == 0:
            if need_order:
                day = feasible_days[-1]
                qty = self._bounded_qty(
                    branch,
                    product,
                    stock0,
                    demand,
                    day,
                    max(product.min_order, self._min_qty_to_finish_week(stock0, demand)),
                )
                if qty <= 0:
                    return (0, 0)
            else:
                return (0, 0)

        if day == 0:
            day = feasible_days[-1]

        if day not in branch.allowed_days:
            day = min(branch.allowed_days, key=lambda candidate: abs(candidate - day))

        if day > latest_day and feasible_days:
            day = feasible_days[-1]

        if product.code in SHORT_SHELF_CODES:
            day = feasible_days[-1]

        lower_bound = max(product.min_order, self._min_qty_to_finish_week(stock0, demand))
        qty = max(qty, lower_bound)
        qty = self._bounded_qty(branch, product, stock0, demand, day, qty)

        if not need_order and qty <= 0:
            return (0, 0)
        if qty <= 0:
            return (0, 0)
        return (day, qty)

    def _bounded_qty(
        self,
        branch: Branch,
        product: Product,
        stock0: int,
        demand: int,
        day: int,
        qty: int,
    ) -> int:
        upper = self._upper_bound_qty(branch, product, stock0, demand, day)
        if upper <= 0:
            return 0
        qty = min(qty, upper)
        if 0 < qty < product.min_order:
            if upper >= product.min_order:
                qty = product.min_order
            else:
                qty = upper
        return max(0, qty)

    def _latest_feasible_day(self, branch: Branch, stock0: int, demand: int) -> int:
        if demand <= 0:
            return branch.allowed_days[-1]
        stockout_day = ceil(stock0 / demand)
        feasible = [day for day in branch.allowed_days if day <= stockout_day]
        if feasible:
            return feasible[-1]
        return branch.allowed_days[0]

    def _min_qty_to_finish_week(self, stock0: int, demand: int) -> int:
        return max(0, demand * 7 - stock0 + 1)

    def _upper_bound_qty(
        self,
        branch: Branch,
        product: Product,
        stock0: int,
        demand: int,
        day: int,
    ) -> int:
        validity_cap = demand * min(product.validity_days, 14)
        safety_cap = (20 * demand) - (stock0 - demand * day)
        return max(0, min(validity_cap, safety_cap))

    def _as_hashable(self, individual: Individual) -> tuple[Gene, ...]:
        return tuple((int(day), int(qty)) for day, qty in individual)

    @lru_cache(maxsize=4096)
    def _analyze(self, individual: tuple[Gene, ...]) -> dict:
        violations = {
            "R1_sem_ruptura": 0,
            "R2_capacidade": 0,
            "R3_dia_invalido": 0,
            "R4_pedido_minimo": 0,
            "R5_validade": 0,
            "R6_consolidacao": 0,
            "R7_estoque_seguranca": 0,
        }
        plan_map: dict[tuple[str, str], Gene] = {}
        stocks: dict[tuple[str, str], list[int]] = {}
        grouped_orders: dict[str, list[dict]] = {branch.code: [] for branch in self.branches}

        cost_products = 0.0
        cost_shortage = 0.0
        cost_excess = 0.0
        cost_orders = 0.0

        # Verificações por gene e simulação de estoque
        for gene, (branch_code, product_code) in zip(individual, self.gene_keys):
            day, qty = gene
            branch = self.branch_map[branch_code]
            product = self.product_map[product_code]
            stock0, demand = DEMANDS[branch_code][product_code]
            plan_map[(branch_code, product_code)] = (day, qty)

            if qty > 0 and day not in branch.allowed_days:
                violations["R3_dia_invalido"] += 1
            if 0 < qty < product.min_order:
                violations["R4_pedido_minimo"] += 1

            q_max = demand * min(product.validity_days, 14)
            if qty > q_max:
                violations["R5_validade"] += 1

            latest_day = self._latest_feasible_day(branch, stock0, demand)
            if qty > 0 and day > latest_day:
                violations["R5_validade"] += 1 if product.code in SHORT_SHELF_CODES else 0

            history = [stock0]
            for current_day in range(1, 8):
                current_stock = stock0 + (qty if day > 0 and day <= current_day else 0) - demand * current_day
                history.append(current_stock)
                if current_stock <= 0:
                    violations["R1_sem_ruptura"] += 1
                    cost_shortage += abs(min(0, current_stock)) * 50.0
                if current_stock > demand * 20:
                    violations["R7_estoque_seguranca"] += 1
            stocks[(branch_code, product_code)] = history
            cost_products += qty * product.unit_cost
            final_stock = history[7]
            cost_excess += max(0, final_stock - (10 * demand)) * 2.0

        # Capacidade por filial/dia
        for branch in self.branches:
            for current_day in range(1, 8):
                total_stock = sum(
                    stocks[(branch.code, product.code)][current_day] for product in self.products
                )
                if total_stock > branch.capacity:
                    violations["R2_capacidade"] += 1

        # Consolidação de pedidos por filial/dia/fornecedor
        grouped_map: dict[tuple[str, int, str], list[tuple[str, int]]] = {}
        for (branch_code, product_code), (day, qty) in plan_map.items():
            if qty <= 0 or day <= 0:
                continue
            product = self.product_map[product_code]
            grouped_map.setdefault((branch_code, day, product.supplier), []).append((product_code, qty))

        for (branch_code, day, supplier), items in sorted(grouped_map.items()):
            sample_product = self.product_map[items[0][0]]
            order_cost = sample_product.order_cost
            cost_orders += order_cost
            grouped_orders[branch_code].append(
                {
                    "day": day,
                    "supplier": supplier,
                    "items": [
                        f"{product_code} ({qty} un.)" for product_code, qty in sorted(items)
                    ],
                    "order_cost": order_cost,
                }
            )

        total_cost = cost_products + cost_orders + cost_shortage + cost_excess
        return {
            "violations": violations,
            "stocks": stocks,
            "plan_map": plan_map,
            "cost_products": cost_products,
            "cost_orders": cost_orders,
            "cost_shortage": cost_shortage,
            "cost_excess": cost_excess,
            "total_cost": total_cost,
            "grouped_orders": grouped_orders,
        }
