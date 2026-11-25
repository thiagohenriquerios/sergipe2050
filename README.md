# Painel Sergipe 2050 – Desafios Estratégicos (Desenvolve-SE)

Painel local, em Python, com os dados, gráficos e comentários dos 12 desafios
estratégicos. Abre no navegador, mas roda só no seu computador (não fica on-line).

## 1. Instalar (uma única vez)

1. Ter o Python 3.10 ou mais recente instalado (marque "Add Python to PATH" na instalação).
2. Dê dois cliques em **instalar_pacotes.bat** (instala streamlit, plotly e pandas).

## 2. Abrir o painel

Dê dois cliques em **iniciar_painel.bat**. O navegador abre em `http://localhost:8501`.
Para fechar, feche a janela preta do Prompt de Comando.

(Alternativa: no Prompt, dentro de `D:\DESENVOLVESE\dasch`, rode `python -m streamlit run app.py`.)

## 3. Como está organizado

| Arquivo / pasta        | O que tem                                                              |
|------------------------|------------------------------------------------------------------------|
| `app.py`               | Navegação: página inicial (12 cartões), página de cada desafio, "Sobre" |
| `config.py`            | Cores da identidade visual e lista dos 12 desafios (título, enunciado, status) |
| `componentes.py`       | Visual: cabeçalho, banner, cartões, bloco "gráfico + comentário", rodapé |
| `graficos.py`          | Funções de gráfico reutilizáveis (linhas por UF, barras agrupadas, faixas, marcos) |
| `desafios/d12.py`      | Desafio 12: uma função por gráfico + lista `SECOES` com títulos, comentários e fontes |
| `desafios/modelo_desafio.py` | Modelo para criar a página de outro desafio            |
| `dados/d12/`           | Dados do Desafio 12 (JSON gerados pelos scripts de `bloco12/scripts_d12`) |
| `assets/`              | Coloque aqui `logo.png` (logotipo oficial) e ele substitui o "D" do cabeçalho |

## 4. Editar

- **Comentário de um gráfico:** abra `desafios/d12.py`, procure o título do gráfico em `SECOES`
  (final do arquivo) e edite o campo `comentario`. Aceita `<b>negrito</b>`.
- **Um gráfico:** procure a função `fig_...` correspondente no mesmo arquivo.
- **Cores:** `config.py` (`CORES` para o visual; `CORES_SERIES` para Sergipe/Nordeste/Brasil/líder).
- **Atualizar dados:** rode de novo os scripts de `bloco12/scripts_d12` e copie os `.json` de
  `bloco12/dados_d12` para `dados/d12`.

Depois de editar, salve o arquivo e clique em **Rerun** no canto superior direito do painel
(ou recarregue a página). Se a mudança não aparecer, feche e abra o painel de novo.

## 5. Incluir outro desafio (ex.: Desafio 8)

1. Copie `desafios/modelo_desafio.py` para `desafios/d08.py`.
2. Crie a pasta `dados/d08/` e coloque lá os dados (csv, xlsx ou json).
3. Em `d08.py`, escreva uma função por gráfico e preencha `INTRO`, `DESTAQUES` e `SECOES`.
4. Em `config.py`, mude o `status` do Desafio 8 para `"disponivel"`.

O nome do arquivo precisa ter dois dígitos: `d01.py`, `d02.py`, ..., `d12.py`.
