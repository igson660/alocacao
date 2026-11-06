# PMAC — Consulta de correspondências funcionais

Aplicação web acadêmica para consultar correspondências exploratórias entre áreas de formação e domínios funcionais representados na estrutura organizacional da Polícia Militar do Estado do Acre (PMAC). A referência institucional incluída no app é a Instrução Normativa nº 01, de 30 de junho de 2021, publicada no Boletim Geral PMAC nº 125, de 13 de julho de 2021.

> A aplicação é um protótipo de apoio à consulta. Não avalia militares, não recomenda lotações, não oficializa movimentações e não substitui revisão humana ou decisão institucional. A matriz de correspondência não é estabelecida pelo organograma e depende de validação institucional.

## Recursos

- Campo de consulta por área de formação, com exemplos rápidos.
- Filtro analítico por grupo operacional, administrativo ou ambos.
- Resultados organizados em correspondência alta e moderada.
- Detalhes expansíveis com unidade, hierarquia e atribuições previstas no organograma.
- Aviso para não inserir dados pessoais; processamento da consulta inteiramente no navegador.
- Identidade visual com os símbolos fornecidos para a PMAC.

## Tecnologias

- Next.js 15 com App Router
- React 19 e TypeScript
- Tailwind CSS 3 e PostCSS
- Yarn Classic 1.22.22 (`yarn.lock` versionado)
- Lucide React para ícones

## Requisitos

- Node.js 20.9.0 ou superior
- Yarn Classic 1.22.22
- Git, se o projeto for clonado de um repositório

Se o Yarn Classic ainda não estiver instalado, instale-o com npm ou Corepack e confira a versão:

```bash
npm install --global yarn@1.22.22
yarn --version
```

Não são necessárias chaves de API, variáveis de ambiente, banco de dados ou serviços externos para calcular correspondências. A folha de estilos solicita fontes públicas ao Google Fonts; o texto da formação não é enviado a esse serviço.

## Instalação e desenvolvimento

Na raiz do projeto:

```bash
yarn install --frozen-lockfile --non-interactive
yarn dev
```

Abra `http://localhost:3000`. O servidor de desenvolvimento suporta recarga automática.

## Validação e build de produção

```bash
yarn validate
```

O comando gera primeiro os tipos de rota do Next.js durante o build e depois roda o typecheck rigoroso. Se executar as etapas manualmente em uma instalação limpa, use esta ordem:

```bash
yarn build
yarn typecheck
```

Para iniciar o build de produção localmente:

```bash
NODE_ENV=production yarn start
```

O servidor usa a porta 3000 por padrão. Em uma hospedagem que define a porta por variável de ambiente, configure `PORT` conforme as instruções do provedor, por exemplo `PORT=8080 NODE_ENV=production yarn start`.

## Estrutura do projeto

```text
app/
  apple-icon.png       Ícone Apple derivado do brasão fornecido
  globals.css          Identidade visual, responsividade e estilos globais
  icon.png             Ícone do navegador derivado do brasão fornecido
  layout.tsx           Layout raiz e metadados
  page.tsx             Interface principal e interação de consulta
components/
  allocation-engine.ts  Vocabulários, matriz funcional e motor determinístico
public/
  pmac-assinatura-horizontal.webp  Assinatura institucional fornecida
  pmac-brasao.webp                  Brasão institucional fornecido
```

O projeto é uma aplicação Next.js; não publique os arquivos fonte como um site HTML estático sem configurar e testar uma exportação estática específica. Para hospedagem comum, use Vercel ou um servidor compatível com Node.js.

## Como a consulta funciona

A formação informada é normalizada — incluindo remoção de acentos e padronização de maiúsculas — e comparada a palavras-chave agrupadas em domínios acadêmicos. As correspondências são cruzadas com domínios funcionais codificados no motor. Se houver correspondência alta e moderada para o mesmo domínio funcional, prevalece a alta. Os candidatos são ordenados primeiro por prioridade e depois pelo nome do domínio.

O filtro “Operacionais/Administrativas” identifica grupos analíticos do estudo. Não representa, por si só, os níveis de Direção Geral, Direção Setorial, Direção Executiva ou Execução do organograma. Os nomes, subordinações e atribuições exibidos são referências institucionais; as associações entre formação e função são regras exploratórias distintas.

Uma entrada que não representa formação comparável ou que não é reconhecida pelas palavras-chave não recebe recomendação automática: o app solicita revisão humana.

## Privacidade e segurança

- A aplicação não possui backend, banco de dados, autenticação, analytics ou endpoint de consulta.
- O cálculo é executado no navegador; a formação digitada não é enviada ao servidor pela lógica do app.
- Não insira nome, matrícula, CPF, prontuário, histórico funcional ou outra informação pessoal.
- A página carrega fontes via Google Fonts; essa requisição entrega metadados normais de navegação ao provedor de fontes, mas não inclui o texto digitado no campo.
- Antes de qualquer uso institucional, valide a matriz e confira se o organograma e as atribuições continuam atualizados.

## Publicação

As instruções de implantação no Vercel e em hospedagem Node.js estão em [`PUBLICACAO.md`](./PUBLICACAO.md).

## Aplicativo desktop Windows

O repositório também contém o protótipo desktop portátil em [`desktop-windows/`](./desktop-windows/). Para gerar o ZIP com executável, selecione a branch `windows-portable-app` e execute **Actions → Build PMAC Windows portable app → Run workflow**. O artefato `PMAC-Analise-Formacao-Windows-x64` fica disponível na execução por 30 dias. O build de CI executa o smoke test somente com uma base sintética; não usa nem publica bases individuais.
