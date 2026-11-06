# PMAC — Análise de Formação e Unidade

Aplicativo desktop portátil para Windows x64 que executa localmente a análise do notebook `ferramenta_preditiva_pmac.ipynb`. A interface permite selecionar uma base CSV ou Excel, acompanhar as etapas, visualizar tabelas e gráficos e gravar os resultados em uma pasta escolhida.

## Estado desta versão

Este repositório contém o código-fonte, a interface desktop e a configuração de build Windows. O `.exe` de produção precisa ser compilado e testado em Windows x64; uma compilação executada em Linux não produz um executável Windows confiável. O workflow `.github/workflows/build-windows.yml` faz esse build quando acionado no GitHub Actions.

A distribuição escolhida é **portátil em pasta compactada**: o usuário extrai o ZIP e abre `PMAC-Analise-Formacao.exe`. Não exige instalação de Python nem de bibliotecas. O ZIP inclui as bibliotecas e o modelo semântico, por isso será grande e requer espaço em disco suficiente.

## Funcionalidade mantida

O módulo `analysis_runtime.py` executa as células de análise do notebook original, sem reescrevê-las. A camada desktop apenas adapta:

- `files.upload()` para o arquivo que a pessoa selecionou;
- o diretório de trabalho do notebook para a pasta de saída escolhida;
- `display()` para uma prévia de tabela na interface;
- `plt.show()` para salvar e exibir os gráficos em PNG;
- a barra tqdm de embeddings para mostrar o progresso por lotes;
- a carga do modelo pelo caminho local, usando os mesmos pesos fixados neste repositório.

A lista de formação, as palavras-chave, a ordem de regras, os níveis alta/moderada/baixa, a precedência alta > moderada > baixa, os filtros de aplicabilidade, as métricas e os parâmetros de treino/teste continuam nos mesmos códigos do notebook. A leitura de XLS é incluída por meio do `xlrd`, pois esse formato é aceito pelo notebook e o mecanismo de leitura precisa estar empacotado para funcionar no Windows.

## Etapas visíveis

1. Preparação das bibliotecas e dos parâmetros.
2. Leitura do arquivo e identificação dos campos obrigatórios.
3. Normalização dos textos e remoção de colunas identificadoras diretas.
4. Estatística descritiva e composição da base.
5. Classificação das áreas de formação.
6. Classificação funcional das unidades e auditoria.
7. Verificação estrutural da matriz.
8. Aplicação da matriz e cálculo da aderência.
9. TF-IDF, regressão logística, baseline e matriz de confusão.
10. Sentence embeddings, classificação e similaridade por cosseno.
11. Comparação dos modelos.
12. Exportação dos resultados.

A interface mostra o estado da célula que está sendo executada. Na etapa de embeddings, também acompanha os lotes do modelo. O cancelamento é cooperativo: é reconhecido entre células ou lotes; um cálculo que esteja dentro de uma chamada longa a scikit-learn pode terminar antes da interrupção.

## Instalação de desenvolvimento

Requisitos para desenvolver, não para a pessoa usuária do `.exe`:

- Windows 10/11 x64;
- Python 3.12.3 x64;
- espaço para o ambiente de desenvolvimento e o modelo;
- acesso à internet somente durante a preparação das dependências e pesos, se ainda não estiverem disponíveis localmente.

No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-build.txt
python scripts\download_model.py
python -m py_compile main.py analysis_runtime.py
python main.py
```

## Testes de equivalência

Antes do build, execute `python scripts/smoke_test.py` para verificar três saídas CSV e os gráficos com uma base sintética. Para testar a janela e o worker, execute `python tests/ui_smoke.py`; para incluir embeddings na verificação, defina `PMAC_SMOKE_EMBEDDINGS=1` antes do comando.

O script `scripts/verify_parity.py` compara as três saídas do notebook com uma execução desktop sobre a mesma base. A verificação foi realizada com 2.317 registros: os três arquivos mantiveram dimensões, rótulos e valores categóricos; houve diferenças de até 0,0001 em parte dos escores semânticos, decorrentes da precisão numérica e do arredondamento do modelo. Nenhuma regra de categoria ou resultado de classificação divergiu. Os arquivos da base e das saídas de referência não são incluídos no repositório.

Para gerar a pasta portátil e o ZIP:

```powershell
.\scripts\build_windows.ps1
```

O resultado de desenvolvimento é gravado em `release/PMAC-Analise-Formacao-Windows-x64.zip`.

## Build pelo GitHub Actions

Neste repositório, o workflow fica em `.github/workflows/build-windows-portable.yml`, na raiz. Abra **Actions → Build PMAC Windows portable app → Run workflow** e selecione a branch que contém as alterações. O runner Windows instala as dependências, baixa o modelo pela revisão fixa, compila e testa o executável com a base sintética. Ao concluir, baixe `PMAC-Analise-Formacao-Windows-x64` nos artefatos da execução.

O ZIP fica disponível como artefato de CI por 30 dias; não é criada uma Release pública. Para usar este diretório como projeto autônomo, o workflow-modelo correspondente está em `.github/workflows/build-windows.yml` dentro da pasta-fonte. Teste o ZIP extraído em Windows antes de distribuí-lo.

## Entrada e saídas

Entradas aceitas: um arquivo `.csv`, `.xlsx` ou `.xls`, sujeito às validações do notebook e às quatro colunas requeridas para formação, unidade, tipo oficial de unidade e escolaridade.

Na pasta escolhida, a análise mantém os três CSVs do notebook:

- `resultado_analise_pmac_completo.csv`
- `resultado_analise_pmac_aplicavel.csv`
- `auditoria_classificacao_unidades.csv`

Os CSVs usam UTF-8 com BOM, não incluem coluna-índice e mantêm os campos produzidos pelo notebook. A interface também salva gráficos PNG em `graficos/`; esses gráficos são uma saída visual adicional para substituir as figuras mostradas interativamente no Colab. Se os três CSVs já existirem, o aplicativo pede confirmação antes de sobrescrevê-los.

## Privacidade e execução offline

A seleção de entrada, o processamento, o carregamento do modelo e a escrita das saídas acontecem localmente. A aplicação não envia a base a servidor, API ou nuvem. O modelo `paraphrase-multilingual-MiniLM-L12-v2`, commit `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`, acompanha o pacote e é carregado do diretório `models/`; a aplicação define os modos offline do Hugging Face e não deve baixar pesos durante o uso.

A ferramenta remove identificadores diretos conforme as regras de cabeçalho existentes no notebook, mas isso não comprova anonimização formal. Os CSVs de saída ainda podem conter códigos, nomes de unidade ou combinações que demandem controle de acesso. Compartilhe somente agregados aprovados e proteja os arquivos individuais.

## Limites de interpretação

A matriz fornece categorias exploratórias associadas a formação e unidade; não mede competência individual, desempenho ou aptidão e não recomenda automaticamente a lotação de uma pessoa. Os experimentos de aprendizado de máquina tentam reproduzir rótulos definidos pela própria matriz e não constituem validação independente. O resultado deve ser analisado por responsáveis humanos e submetido à validação institucional prevista para a pesquisa.

## Licenças e marca

O pacote inclui a licença Apache 2.0 e a atribuição do modelo multilíngue nos arquivos `Apache-2.0.txt` e `AVISOS-TERCEIROS.txt`. Preserve esses arquivos e os avisos das dependências. A lista de componentes e as ressalvas sobre o uso da marca estão em `LICENSES.md`. A presença do brasão não representa homologação nem autorização automática para distribuição externa.

## Estrutura do projeto

```text
main.py                              Interface PySide6 e processo worker
analysis_runtime.py                  Adaptadores locais para o notebook original
notebook/ferramenta_preditiva_pmac.ipynb
assets/                              Símbolos fornecidos para a PMAC
models/                              Snapshot local do modelo multilíngue
app.spec                             Empacotamento PyInstaller onedir
scripts/download_model.py            Aquisição do modelo por commit fixo
scripts/build_windows.ps1            Build local em Windows x64
.github/workflows/build-windows.yml Build de CI em Windows x64
```
