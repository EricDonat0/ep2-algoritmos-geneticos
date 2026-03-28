# Modelagem do problema

## Cromossomo

O cromossomo tem **80 genes**, um para cada combinação **filial x produto** (4 filiais x 20 produtos).

Cada gene é representado por uma tupla:

- `dia_entrega`: inteiro em `{0, 1, 2, 3, 4, 5, 6, 7}`
- `quantidade`: inteiro `>= 0`

Interpretação:

- `dia_entrega = 0` e `quantidade = 0` significam **sem pedido naquela semana**.
- `dia_entrega > 0` representa o dia da semana em que a entrega ocorre.
- `quantidade` representa o total de unidades pedidas daquele produto para a filial.

A ordem fixa dos genes é:

1. F1–PR01 até F1–PR20
2. F2–PR01 até F2–PR20
3. F3–PR01 até F3–PR20
4. F4–PR01 até F4–PR20

Essa modelagem facilita crossover e mutação porque mantém independência semântica por gene e permite reparo local após os operadores.

## Função de aptidão

O AG maximiza a função:

```text
f = V - C_total - penalidades
```

onde:

- `V = 10.000.000`
- `C_total = C_produtos + C_pedidos + C_ruptura + C_excesso`
- `penalidades = Σ(p_i * n_i)`

### Componentes de custo

- `C_produtos = Σ quantidade * custo_unitário`
- `C_pedidos = custo fixo consolidado por (filial, dia, fornecedor)`
- `C_ruptura = Σ max(0, -estoque_dia) * 50`
- `C_excesso = Σ max(0, estoque_final - 10 * demanda_dia) * 2`

### Pesos de penalidade adotados

| Restrição | Peso | Justificativa |
|---|---:|---|
| R1 – sem ruptura | 100000 | É a restrição mais crítica do enunciado; prateleira vazia impacta venda e satisfação. |
| R2 – capacidade | 40000 | Excesso de estoque inviabiliza o plano operacionalmente. |
| R3 – dia inválido | 30000 | Entrega fora da janela logística não pode ser executada. |
| R4 – pedido mínimo | 25000 | Violação contratual/comercial com fornecedor. |
| R5 – validade | 30000 | Evita compra acima da janela de consumo e reforça perecíveis críticos. |
| R6 – consolidação | 0 | Foi modelada diretamente no custo, não como restrição dura. |
| R7 – estoque máximo de segurança | 20000 | Evita desperdício e estoque acima de 20 dias de demanda. |

### Observação sobre perecíveis curtos

O enunciado menciona “validade inferior a 7 dias”, mas lista explicitamente **PR11, PR12 e PR13**. Como PR12 e PR13 têm validade igual a 7 dias, a implementação tratou **os três itens explicitamente listados** como grupo crítico de perecíveis curtos.

## Operadores

### Seleção

O sistema suporta dois métodos:

- **Torneio**: seleciona `k=3` indivíduos aleatórios e escolhe o melhor.
- **Roleta**: usa fitness ajustado para valores positivos, preservando proporcionalidade.

O padrão adotado no repositório é **torneio**, por ser mais estável em problemas com penalidades altas.

### Crossover

O sistema suporta três operadores:

- **single_point**
- **two_point**
- **uniform**

Todos operam sobre a lista de genes `(dia, quantidade)` e, após o cruzamento, o indivíduo gerado passa por **reparo completo**.

### Mutação

A mutação é específica do problema e atua sobre genes individuais:

- deslocamento do dia de entrega para o dia permitido anterior ou posterior;
- ativação ou remoção de pedido (`0,0`);
- ajuste da quantidade em torno de `±10%` do lote mínimo;
- ajuste da quantidade em passos de um lote mínimo.

Após cada mutação, o gene passa por reparo.

### Tratamento das restrições

As restrições são tratadas por duas estratégias combinadas:

1. **Reparo pós-operador**
   - dia é projetado para um dia permitido da filial;
   - produtos com necessidade de pedido recebem o último dia viável antes da ruptura;
   - a quantidade é limitada por validade e estoque máximo de segurança;
   - quando necessário, a quantidade é elevada até o mínimo entre cobertura da semana e pedido mínimo.

2. **Penalização na aptidão**
   - qualquer violação residual ainda presente após o reparo entra na função de aptidão com peso alto.

## Inicialização

Foi adotada uma **inicialização heurística reparável**.

Para cada gene:

1. calcula-se o dia máximo viável de entrega antes da ruptura;
2. se o estoque inicial já cobre a semana, o gene tende a começar como sem pedido;
3. se o pedido é necessário, escolhe-se um dia permitido próximo ao limite de ruptura;
4. a quantidade inicial é calculada para cobrir a semana, respeitando:
   - pedido mínimo;
   - limite por validade;
   - limite por estoque máximo de segurança.

Essa estratégia reduz fortemente o número de indivíduos inviáveis na geração inicial e acelera a convergência.

## Critério de parada

O projeto suporta dois critérios combinados:

- **número máximo de gerações**;
- **estagnação do melhor fitness por `patience` gerações**.

Na configuração padrão:

- gerações máximas: `180`
- `patience`: `40`

Assim, o algoritmo para quando atinge o limite de gerações ou quando deixa de melhorar por 40 gerações consecutivas.
