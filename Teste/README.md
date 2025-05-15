# Conversor de Arquivos - Python

Este projeto é um conversor de arquivos entre diferentes layouts (CSV, JSON, XML, TXT, etc.).

## Como funciona
- O usuário fornece um arquivo de entrada e escolhe o layout de saída desejado.
- O projeto é modular, facilitando a adição de novos layouts.

## Como executar
1. Instale as dependências (se houver).
2. Execute o arquivo principal do projeto (exemplo: `python main.py`).
3. Siga as instruções no terminal para selecionar o arquivo de entrada e o layout de saída.

## Estrutura sugerida
- `main.py`: ponto de entrada do programa.
- `converters/`: módulo com conversores para cada layout.
- `utils/`: funções utilitárias.

## Exemplo de uso
```
python main.py --input arquivo.csv --from csv --to json --output arquivo.json
```

## Requisitos
- Python 3.8+

## Expansão
Para adicionar novos layouts, basta criar um novo conversor no diretório `converters/`.
