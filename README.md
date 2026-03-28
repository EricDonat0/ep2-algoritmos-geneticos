# ep-algoritmos-geneticos

## Estudo de caso

**Otimização de Reabastecimento de Estoque em Rede de Supermercados**.

Este repositório implementa um **Algoritmo Genético (AG)** para gerar um plano semanal de reabastecimento de estoque para 4 filiais e 20 produtos, buscando minimizar:

- custo de compra dos produtos;
- custo fixo de pedidos consolidados por fornecedor;
- multas por ruptura de estoque;
- penalidades por excesso de estoque no fim da semana.

O modelo respeita as restrições de:

- dias de entrega permitidos por filial;
- pedido mínimo por produto;
- validade dos produtos;
- capacidade de armazenamento;
- estoque máximo de segurança;
- ausência de ruptura de estoque ao longo da semana.

## Estrutura do repositório

```text
/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── problem_base.py
│   ├── ga.py
│   ├── utils.py
│   ├── main.py
│   ├── experiments.py
│   └── cases/
│       ├── __init__.py
│       └── inventory_restocking.py
└── docs/
    ├── modelagem.md
    └── hiperparametros.md
```


## Como executar

### Execução principal

A execução principal é feita por um único comando. A combinação abaixo usa a melhor configuração entre as combinações testadas no estudo de hiperparâmetros:

```bash
python -m src.main \
  --population-size 120 \
  --generations 180 \
  --mutation-rate 0.03 \
  --crossover-rate 0.85 \
  --selection tournament \
  --crossover two_point \
  --elite-size 4 \
  --tournament-size 3 \
  --patience 40 \
  --seed 42
```

### Parâmetros configuráveis

- `--population-size`: tamanho da população
- `--generations`: número máximo de gerações
- `--mutation-rate`: taxa de mutação
- `--crossover-rate`: taxa de crossover
- `--selection`: `tournament` ou `roulette`
- `--crossover`: `single_point`, `two_point` ou `uniform`
- `--elite-size`: quantidade de indivíduos preservados por elitismo
- `--tournament-size`: tamanho do torneio
- `--patience`: critério de parada por estagnação
- `--seed`: semente para reprodutibilidade

## Saída do programa

O programa imprime apenas **tabelas em Markdown** no terminal, incluindo:

1. evolução do fitness por geração;
2. resumo da execução;
3. plano consolidado de pedidos por filial, dia e fornecedor;
4. tabela completa da melhor solução encontrada;
5. evolução do estoque de cada produto ao longo da semana;
6. custos detalhados;
7. violações por restrição.

## Estudo de hiperparâmetros

Para gerar automaticamente o arquivo `docs/hiperparametros.md`:

```bash
python -m src.experiments \
  --pop-values 80,120 \
  --mut-values 0.03,0.08 \
  --generations 150 \
  --crossover-rate 0.85 \
  --selection tournament \
  --crossover two_point \
  --elite-size 4 \
  --patience 40 \
  --seed 42 \
  --output docs/hiperparametros.md
```

O documento gerado traz:

- tabela comparando combinações de hiperparâmetros;
- melhor fitness alcançado;
- gerações até convergência;
- número de violações da solução final;
- gráfico de convergência em **Mermaid XY Chart** para cada combinação.

## Decisões de modelagem importantes

- Cada combinação `filial x produto` possui **um gene** com `(dia, quantidade)`.
- `dia = 0` e `quantidade = 0` representam ausência de pedido.
- A restrição de consolidação por fornecedor (R6) foi tratada no **cálculo do custo fixo**, incentivando o agrupamento de entregas no mesmo dia.
- Os produtos `PR11`, `PR12` e `PR13` foram tratados como perecíveis críticos de validade curta, seguindo a lista explícita do enunciado.

## Documentação técnica

- [docs/modelagem.md](docs/modelagem.md)
- [docs/hiperparametros.md](docs/hiperparametros.md)

## Observação

O repositório foi preparado para atender ao formato pedido no trabalho:

- código em Python;
- execução com um único comando;
- parâmetros configuráveis por linha de comando;
- elitismo;
- exibição do fitness por geração;
- saída estruturada em Markdown;
- documentação técnica em `docs/`.


## Declaração de uso de inteligência artificial

Neste projeto, houve uso pontual de ferramentas de inteligência artificial apenas como apoio auxiliar para consultas de sintaxe, esclarecimento de dúvidas específicas de implementação e suporte durante o desenvolvimento do código.

A modelagem do problema, a definição da solução, a implementação principal do algoritmo, os testes realizados e a análise dos resultados foram conduzidos pelo alunos Eric Donato, Paula Martins e Matheus Henrique. Assim, a inteligência artificial não foi utilizada para realizar o trabalho de forma autônoma, mas somente como ferramenta de apoio complementar, de maneira compatível com as orientações do professor.