from __future__ import annotations

from typing import Iterable, Sequence


DAY_NAMES = {
    0: "-",
    1: "Seg",
    2: "Ter",
    3: "Qua",
    4: "Qui",
    5: "Sex",
    6: "Sáb",
    7: "Dom",
}


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    separator = "|" + "|".join(["---" for _ in headers]) + "|"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header_line, separator, *body])


def format_currency(value: float) -> str:
    text = f"{value:,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")


def mermaid_xy_chart(title: str, values: list[float]) -> str:
    if not values:
        values = [0.0]

    x_values = ", ".join(str(i) for i in range(len(values)))
    floor = int(min(values))
    ceiling = int(max(values))
    if floor == ceiling:
        ceiling = floor + 1
    series = ", ".join(f"{value:.2f}" for value in values)

    return "\n".join(
        [
            "```mermaid",
            "xychart-beta",
            f'    title "{title}"',
            f'    x-axis "Geração" [{x_values}]',
            f'    y-axis "Fitness" {floor} --> {ceiling}',
            f"    line [{series}]",
            "```",
        ]
    )
