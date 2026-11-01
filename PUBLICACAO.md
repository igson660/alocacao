# Publicação — PMAC | Consulta funcional

Este guia descreve como preparar, implantar, verificar e atualizar o app. O projeto foi testado com Yarn Classic 1.22.22, Node.js 20.9 ou superior e Next.js 15. A aplicação é uma ferramenta acadêmica de consulta, não um sistema institucional de movimentação de pessoal.

## 1. O que é necessário antes de publicar

- Acesso ao repositório Git que conterá o projeto.
- Conta em uma hospedagem compatível com Next.js. A opção mais simples é Vercel; também é possível hospedar em servidor Node.js.
- Node.js 20.9+ e Yarn Classic 1.22.22 para desenvolvimento local.
- Confirmação de que o organograma e as correspondências exibidas podem ser disponibilizados publicamente.
- Revisão institucional da matriz formação–função. O organograma é fonte para nomes, subordinação e atribuições; ele não estabelece as correspondências entre cursos e unidades que o app calcula.

O app não exige chave de API, banco, login ou segredo para funcionar. Não configure variáveis de ambiente desnecessárias.

Se Yarn Classic não estiver instalado no computador de desenvolvimento, instale e confirme a versão:

```bash
npm install --global yarn@1.22.22
yarn --version
```

## 2. Preparar e validar o projeto

Na raiz do repositório, execute:

```bash
yarn install --frozen-lockfile --non-interactive
yarn validate
yarn audit --groups dependencies --level moderate
```

`yarn validate` executa a checagem TypeScript e o build de produção. O `yarn.lock` é o lockfile canônico e deve permanecer versionado.

Para conferir o build localmente:

```bash
NODE_ENV=production yarn start
```

Abra `http://localhost:3000`. No PowerShell, use `$env:NODE_ENV="production"; yarn start`.

## 3. Publicar na Vercel

1. Envie o conteúdo deste projeto para um repositório Git privado ou público, conforme a política institucional. Inclua `app/`, `components/`, `public/`, `package.json`, `yarn.lock`, `next.config.mjs`, `postcss.config.mjs`, `tailwind.config.ts`, `tsconfig.json` e os documentos do projeto. Não inclua `node_modules/`, `.next/`, arquivos `.env*`, logs ou configurações locais da plataforma.
2. Na Vercel, crie um projeto importando esse repositório.
3. Defina a raiz do projeto como a raiz do repositório, onde está `package.json`.
4. Se a Vercel não detectar automaticamente, escolha o framework **Next.js**.
5. Use **Yarn** para instalar dependências. Comando de instalação recomendado: `yarn install --frozen-lockfile --non-interactive`.
6. Use `yarn build` como comando de build. Mantenha o diretório padrão de saída do Next.js; não defina `out/` ou `dist/` como diretório de publicação.
7. Use Node.js 20.9 ou superior. Não há variáveis de ambiente obrigatórias.
8. Gere primeiro uma implantação de pré-visualização e execute o checklist da seção 5. Depois, promova essa versão à produção pelo painel da hospedagem.
9. Para domínio próprio, associe-o ao projeto pelo painel da hospedagem, configure os registros DNS solicitados e aguarde a emissão/validação de HTTPS antes de divulgar o endereço.

A página é pré-renderizada, mas inclui lógica React no navegador. A configuração atual é um app Next.js padrão e requer o adaptador/runtime Next.js da Vercel; não publique apenas uma pasta de arquivos HTML sem configurar e validar uma exportação estática.

## 4. Alternativa: servidor Node.js próprio

No servidor de produção:

```bash
# versão de Node compatível e Yarn Classic instalados
git clone <URL-DO-REPOSITORIO>
cd <DIRETORIO-DO-PROJETO>
yarn install --frozen-lockfile --non-interactive
yarn validate
NODE_ENV=production yarn start
```

O Next.js escuta a porta `3000` por padrão. Se o provedor disponibilizar outra porta, exporte `PORT` antes de iniciar, por exemplo `PORT=8080 NODE_ENV=production yarn start`. Mantenha o processo sob um supervisor adequado ao ambiente (serviço do sistema, contêiner ou gerenciador de processos), configure um proxy reverso para encaminhar HTTPS à porta local e habilite logs e monitoramento operacional. O repositório não inclui Dockerfile nem configuração de infraestrutura; esses itens devem seguir a política do ambiente de destino.

## 5. Checklist pós-publicação

- A página inicial abre por HTTPS e o título apresentado é “PMAC | Consulta Funcional”.
- A assinatura horizontal e o brasão carregam corretamente no cabeçalho, no hero e no ícone do navegador.
- O campo aceita as áreas de teste “Direito”, “Enfermagem” e “Sistemas de Informação”.
- A ação de consulta separa resultados de correspondência alta e moderada; para o mesmo domínio funcional, a prioridade alta prevalece.
- Os filtros “Todas”, “Operacionais” e “Administrativas” alteram o conjunto exibido sem misturar esse agrupamento analítico com os níveis formais do organograma.
- Os detalhes expansíveis apresentam unidade, vínculo hierárquico e atribuição; o painel “Base organizacional” contém a fonte e a ressalva de atualização.
- Uma entrada não reconhecida e uma entrada como “Ensino Médio” pedem revisão humana; não devem gerar encaminhamento automático.
- A interface funciona em desktop e celular, e os controles podem ser acionados por teclado, com foco visível.
- O texto de privacidade permanece visível: não inserir dados pessoais; a análise de correspondência é local no navegador.
- A versão de produção não mostra mensagens de erro no console do navegador nem falhas de carregamento dos assets.

## 6. Privacidade, fontes externas e uso responsável

O código ativo não contém chamadas a API, backend, analytics, armazenamento local ou banco de dados. A área digitada é processada no navegador e não é enviada pela lógica da aplicação. A folha de estilos referencia Google Fonts para tipografia; essa requisição comunica ao provedor os metadados técnicos habituais de acesso a uma fonte externa, mas não envia o conteúdo do campo. Se a política de privacidade exigir nenhuma dependência externa no carregamento, hospede as fontes localmente, faça uma nova revisão de licenças e teste novamente o build.

Não introduza nomes, matrículas, CPF, prontuários, histórico funcional ou outros dados pessoais. A aplicação não deve ser tratada como decisão automatizada nem ser usada isoladamente para alocação. As correspondências são exploratórias e necessitam de validação humana e institucional. A referência organizacional incluída é a Instrução Normativa nº 01/2021; confirme eventuais atos posteriores antes de apresentar o conteúdo como estrutura vigente.

## 7. Atualizações e manutenção

Para cada alteração de código ou conteúdo:

```bash
yarn install --frozen-lockfile --non-interactive
yarn validate
yarn audit --groups dependencies --level moderate
```

Revise os resultados em pré-visualização antes de promovê-los à produção. Ao atualizar dependências, verifique eventuais avisos de segurança, atualize o `yarn.lock` com Yarn e repita todos os comandos. Mudanças no organograma ou na matriz precisam de fonte/validação documentada, não apenas de alteração de texto na interface.

## 8. Arquivos de documentação

- `README.md`: resumo, arquitetura, instalação e uso local.
- `PUBLICACAO.md`: procedimentos de implantação e checklist de operação.
