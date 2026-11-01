export type Priority = "Alta" | "Moderada";
export type UnitType = "Operacional" | "Administrativa";
export type FilterType = "Todos" | UnitType;

export type Placement = {
  unitType: UnitType;
  unitName: string;
  hierarchy: string;
  orgCategory: string;
  role: string;
};

export type Candidate = {
  domain: string;
  placements: Placement[];
  priority: Priority;
};

export type MatchResult = {
  foundDomains: string[];
  candidates: Candidate[];
  reviewMessage?: string;
};

type AcademicDomain = {
  name: string;
  keywords: string[];
};

type FunctionalDomain = {
  domain: string;
  high: string[];
  moderate: string[];
  placements: Placement[];
};

export const organizationReference = {
  title: "Instrução Normativa nº 01, de 30 de junho de 2021",
  publication: "Boletim Geral PMAC nº 125, de 13 de julho de 2021",
  note: "A estrutura exibida segue o documento de 2021; confirme eventuais atualizações antes de uso institucional.",
  methodologyNote: "O filtro Operacional/Administrativa é uma classificação analítica do estudo, não uma categoria equivalente à hierarquia do organograma. O art. 2º da IN nº 01/2021 organiza a PMAC em órgãos de Direção Geral, Direção Setorial e Execução; a própria IN também detalha órgãos de Direção Executiva. O organograma descreve órgãos, subordinação e missões, mas não estabelece correspondências entre cursos e unidades. A matriz formação–função é uma proposta analítica exploratória, separada da estrutura oficial.",
} as const;

export const organizationalLevels = [
  {
    level: "Direção Geral",
    organs: "Comando-Geral; Subcomando-Geral/Estado-Maior Geral; Diretoria Operacional (DIROP); Corregedoria; Diretorias de Saúde, Recursos Humanos, Logística e Patrimônio, Ensino e Planejamento.",
  },
  {
    level: "Direção Setorial",
    organs: "Ajudância Geral; Comissões permanentes: Promoção de Oficiais (CPO), Promoção de Praças (CPP), Mérito Policial Militar (CMPM) e Procedimentos Operacionais Padrão (CPOP); Assessorias Jurídica, de Inteligência e Análise Criminal e de Comunicação Social; Controladoria Interna.",
  },
  {
    level: "Direção Executiva",
    organs: "DIROP; CPCM; CPI; CPE; Coordenadoria de Policiamento Comunitário e Direitos Humanos; Coordenadoria da Patrulha Maria da Penha (CPMP); Coordenadoria de Comando e Controle de Operações (CCOPM); Coordenadoria de Gestão do Poder de Polícia Administrativa (CGPPA).",
  },
  {
    level: "Execução",
    organs: "CPCM: 1º, 2º e 3º BPM; CPI: 4º, 5º, 6º, 7º e 8º BPM; CPE: Batalhão de Operações Especiais (BOPE), Batalhão de Policiamento Ambiental (BPA) e BPTRAN, além das companhias, pelotões e grupos descritos na IN.",
  },
] as const;

// Vocabulário de áreas acadêmicas reproduzido do notebook fornecido pelo usuário.
export const academicDomains: AcademicDomain[] = [
  {
    name: "Jurídica",
    keywords: ["DIREITO", "JURID", "NOTAR", "CARTOR", "SERVICO JURIDICO", "ASSESSORIA JURIDICA"],
  },
  {
    name: "Gestão, administração, economia, contabilidade, logística e áreas afins",
    keywords: ["ADMINISTR", "GESTAO PUBLICA", "GESTAO DE POLITICAS", "POLITICAS PUBLICAS", "RECURSOS HUMANOS", "RECURSO HUMANO", "PROCESSOS GERENCIAIS", "GESTAO COMERCIAL", "GESTAO FINANCEIRA", "CONTABIL", "CIENCIAS ECONOMIC", "ECONOMIA", "LOGISTICA", "NEGOCIO", "MARKETING", "EMPREENDEDOR", "PROJETOS", "COMERCIO EXTERIOR", "GESTAO HOSPITALAR", "GESTAO DA QUALIDADE", "GESTAO EM SAUDE", "AGRONEGOCIO", "MEDIACAO", "SERVICO SOCIAL"],
  },
  {
    name: "Saúde",
    keywords: ["ENFERMAG", "MEDICINA", "ODONTO", "FISIOTER", "NUTRICAO", "RADIOLOG", "FARMAC", "BIOMEDIC", "SAUDE", "GERONTOLOG", "VETERINARIA"],
  },
  {
    name: "Humanidades e comunicação",
    keywords: ["PEDAGOG", "HISTORIA", "PORTUG", "VERNAC", "ESPANHOL", "INGLES", "FILOSOF", "SOCIOLOG", "CIENCIAS SOCIAIS", "MUSICA", "ARTES", "TEATRO", "JORNAL", "COMUNICACAO SOCIAL", "PUBLICIDADE", "PRODUCAO PUBLICITARIA", "SERVICOS SOCIAIS", "DESIGN GRAFICO", "GEOGRAF", "PSICOLOG", "TEOLOG", "LINGUA", "GASTRONOMIA"],
  },
  {
    name: "Educação física e esporte",
    keywords: ["EDUCACAO FISICA", "ESPORTE", "CIENCIAS DO ESPORTE"],
  },
  {
    name: "Ciências exatas, engenharias e tecnologia",
    keywords: ["MATEMAT", "QUIMICA", "CIENCIAS BIOLOG", "BIOLOG", "ENGENH", "ARQUITET", "SISTEMAS", "TECNOLOGIA", "COMPUT", "REDES", "SOFTWARE", "INTELIGENCIA ARTIFICIAL", "BANCO DE DADOS", "ESTATIST", "SEGURANCA DA INFORMACAO", "FISICA"],
  },
  {
    name: "Ciências ambientais e agropecuárias",
    keywords: ["AMBIENTAL", "FLORESTAL", "AGRONOM", "AGRICULT", "ZOOTECNIA", "RECURSOS NATURAIS"],
  },
  {
    name: "Segurança pública, privada e trânsito",
    keywords: ["SEGURANCA PUBLICA", "SEGURANCA PRIVADA", "DEFESA CIBERNETICA", "INVESTIGACAO FORENSE", "PERICIA CRIMINAL", "CIENCIAS POLICIAIS", "SEGURANCA DO TRABALHO", "GESTAO DE SEGURANCA", "GESTAO EM SEGURANCA", "SEGURANCA NO TRANSITO", "GESTAO DE TRANSITO", "TRANSITO"],
  },
];

const administrativeDirectoratePath = "Órgãos de Direção Geral · diretorias descritas no art. 4º";
const sectoralPath = "Órgãos de Direção Setorial · Seção III";
const operationalExecutionPath = "Órgãos de Execução · subordinados ao comando indicado";

const functionalDomains: FunctionalDomain[] = [
  {
    domain: "Policiamento territorial",
    high: ["Segurança pública, privada e trânsito"],
    moderate: ["Jurídica", "Educação física e esporte", "Humanidades e comunicação"],
    placements: [{
      unitType: "Operacional",
      unitName: "1º, 2º e 3º BPM · 4º, 5º, 6º, 7º e 8º BPM",
      hierarchy: "CPCM: 1º–3º BPM (Rio Branco) · CPI: 4º (Senador Guiomard), 5º (Brasiléia), 6º (Cruzeiro do Sul), 7º (Tarauacá) e 8º BPM (Sena Madureira)",
      orgCategory: `${operationalExecutionPath} ao CPCM e ao CPI`,
      role: "Polícia ostensiva e preservação da ordem pública nas regiões de responsabilidade dos batalhões.",
    }],
  },
  {
    domain: "Policiamento de trânsito",
    high: ["Segurança pública, privada e trânsito"],
    moderate: ["Ciências exatas, engenharias e tecnologia", "Gestão, administração, economia, contabilidade, logística e áreas afins"],
    placements: [{
      unitType: "Operacional",
      unitName: "Batalhão de Policiamento de Trânsito Urbano e Rodoviário (BPTRAN)",
      hierarchy: "Comando de Policiamento Especializado (CPE) · Companhias de Trânsito Urbano e Rodoviário",
      orgCategory: `${operationalExecutionPath} ao CPE`,
      role: "Missões de policiamento e fiscalização de trânsito urbano e rodoviário, nos termos e limites descritos na Instrução Normativa.",
    }],
  },
  {
    domain: "Policiamento ambiental",
    high: ["Ciências ambientais e agropecuárias"],
    moderate: ["Ciências exatas, engenharias e tecnologia", "Saúde"],
    placements: [{
      unitType: "Operacional",
      unitName: "Batalhão de Policiamento Ambiental (BPA)",
      hierarchy: "Comando de Policiamento Especializado (CPE) · Companhias e Pelotões de Policiamento Ambiental",
      orgCategory: `${operationalExecutionPath} ao CPE`,
      role: "Ações operacionais de proteção ao meio ambiente e policiamento florestal e de mananciais, conforme o documento.",
    }],
  },
  {
    domain: "Operações especiais e intervenção tática",
    high: ["Segurança pública, privada e trânsito", "Educação física e esporte"],
    moderate: ["Saúde", "Humanidades e comunicação"],
    placements: [{
      unitType: "Operacional",
      unitName: "Batalhão de Operações Especiais (BOPE)",
      hierarchy: "CPE · Companhia de Operações Especiais (COE) · Companhia de Policiamento de Choque (CPChoque) · CPCães · ROTAM · GIRO",
      orgCategory: `${operationalExecutionPath} ao CPE`,
      role: "Emprego em missões especiais e extraordinárias de polícia ostensiva e preservação da ordem pública, segundo a IN nº 01/2021.",
    }],
  },
  {
    domain: "Policiamento com cães",
    high: ["Saúde", "Ciências ambientais e agropecuárias", "Segurança pública, privada e trânsito"],
    moderate: ["Educação física e esporte", "Ciências exatas, engenharias e tecnologia"],
    placements: [{
      unitType: "Operacional",
      unitName: "Companhia de Policiamento com Cães (CPCães) · Grupos de Operações com Cães (GOC)",
      hierarchy: "CPCães: unidade do BOPE, no CPE · GOC: PPE/5º BPM e Companhia de Policiamento Especializado/6º BPM, conforme a IN",
      orgCategory: `${operationalExecutionPath} ao CPE e unidades especificadas`,
      role: "A IN nº 01/2021 prevê a CPCães no BOPE e menciona GOC nas estruturas especializadas do 5º e do 6º BPM; conferir a organização atual antes de qualquer uso institucional.",
    }],
  },
  {
    domain: "Gestão administrativa e de pessoas",
    high: ["Gestão, administração, economia, contabilidade, logística e áreas afins"],
    moderate: ["Jurídica", "Ciências exatas, engenharias e tecnologia"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Diretoria de Recursos Humanos (DRH)",
        hierarchy: "DDP · Recursos Humanos Militar (DRHM) · Recursos Humanos Civil (DRHC) · Proteção Social (DPS) · Folha de Pagamento (DFP)",
        orgCategory: administrativeDirectoratePath,
        role: "Responsável pelas políticas e estratégias de gestão de pessoal civil e militar; a DDP inclui qualificação e banco de talentos.",
      },
      {
        unitType: "Administrativa",
        unitName: "Diretoria de Logística e Patrimônio (DLP)",
        hierarchy: "Divisão de Logística (DL) · Divisão Financeira (DF) · Divisão de Patrimônio (DP) · Divisão de Manutenções Veiculares (DMV)",
        orgCategory: administrativeDirectoratePath,
        role: "Administração financeira, logística, orçamentária e patrimonial nos termos descritos pela Instrução Normativa.",
      },
      {
        unitType: "Administrativa",
        unitName: "Diretoria de Planejamento (DPLAN)",
        hierarchy: "DTIC · Divisão de Planejamento e Estudos (DPE) · Divisão de Convênios e Projetos (DCP) · Divisão de Planejamento Orçamentário (DPO)",
        orgCategory: administrativeDirectoratePath,
        role: "Planejamento institucional, tecnologia da informação e comunicação, estudos, projetos, convênios e orçamento.",
      },
      {
        unitType: "Administrativa",
        unitName: "Ajudância Geral",
        hierarchy: "Órgão de Direção Setorial · QCG · CCS · arquivo e boletins",
        orgCategory: sectoralPath,
        role: "Coordena serviços do Quartel do Comando Geral, Companhia de Comando e Serviços, protocolo e arquivo, publicação de boletins e Banda de Música.",
      },
      {
        unitType: "Operacional",
        unitName: "Coordenações Administrativas e seções dos batalhões",
        hierarchy: "BPMs e unidades especializadas · pessoal · logística e patrimônio · demais seções previstas por unidade",
        orgCategory: `${operationalExecutionPath} · estrutura administrativa interna`,
        role: "O organograma prevê coordenação administrativa e seções de apoio nos batalhões; a composição varia entre unidades e deve ser conferida no texto de referência.",
      },
    ],
  },
  {
    domain: "Ensino, instrução e prevenção",
    high: ["Humanidades e comunicação", "Educação física e esporte"],
    moderate: ["Gestão, administração, economia, contabilidade, logística e áreas afins", "Jurídica"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Diretoria de Ensino (DE) · DEI · Colégio Militar",
        hierarchy: "Divisão de Ensino e Instrução (DEI) · cursos de formação, habilitação e aperfeiçoamento · capacitação e especialização · Colégio Militar",
        orgCategory: administrativeDirectoratePath,
        role: "Planejamento e desenvolvimento das atividades de ensino e qualificação profissional, além da administração do Colégio Militar.",
      },
      {
        unitType: "Operacional",
        unitName: "Coordenadoria de Policiamento Comunitário e Direitos Humanos",
        hierarchy: "PROERD · Policiamento Escolar · Polícia Comunitária · projetos sociais",
        orgCategory: "Órgãos de Direção Executiva · art. 10, incisos IV e §4º",
        role: "Coordena programas e projetos de prevenção, educacionais e de implantação da filosofia de Polícia Comunitária.",
      },
      {
        unitType: "Operacional",
        unitName: "Coordenadoria da Patrulha Maria da Penha (CPMP)",
        hierarchy: "Equipes de fiscalização de medidas protetivas · equipe multidisciplinar · Patrulhas Maria da Penha",
        orgCategory: "Órgãos de Direção Executiva · art. 10, inciso V e §5º",
        role: "Coordena fiscalização de medidas protetivas e projetos de prevenção e enfrentamento à violência contra a mulher.",
      },
    ],
  },
  {
    domain: "Saúde",
    high: ["Saúde"],
    moderate: ["Gestão, administração, economia, contabilidade, logística e áreas afins", "Educação física e esporte"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Diretoria de Saúde (DS)",
        hierarchy: "Divisão da Policlínica · Divisão do Fundo de Saúde · Divisão das Clínicas (odontologia, fisioterapia, enfermagem, biopsicossocial e atendimento médico)",
        orgCategory: administrativeDirectoratePath,
        role: "Planeja, coordena, administra, fiscaliza e controla as atividades da Corporação ligadas à área de saúde.",
      },
      {
        unitType: "Operacional",
        unitName: "Seções de Saúde em unidades operacionais",
        hierarchy: "Seções administrativas previstas em alguns BPMs e unidades especializadas",
        orgCategory: `${operationalExecutionPath} · composição varia por unidade`,
        role: "O documento inclui Seções de Saúde em determinadas estruturas de batalhão; não as apresenta de forma idêntica em todas as unidades.",
      },
    ],
  },
  {
    domain: "Inteligência e análise criminal",
    high: ["Segurança pública, privada e trânsito", "Ciências exatas, engenharias e tecnologia"],
    moderate: ["Jurídica", "Humanidades e comunicação", "Gestão, administração, economia, contabilidade, logística e áreas afins"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Assessoria de Inteligência e Análise Criminal",
        hierarchy: "Assessoramento direto ao Comandante-Geral · Seções de Inteligência, Contrainteligência, Operacional e Análise Criminal",
        orgCategory: sectoralPath,
        role: "Assessora e integra atividades de inteligência de segurança pública e análise criminal no âmbito da PMAC.",
      },
      {
        unitType: "Operacional",
        unitName: "DIROP · CPCM · CPI · CCOPM · seções dos batalhões",
        hierarchy: "Divisão de Inteligência e Análise Criminal da DIROP · seções de Inteligência e Análise Criminal em comandos/batalhões · CCOPM (Seção de Inteligência e Análise Criminal)",
        orgCategory: "Direção Geral · Direção Executiva · Órgãos de Execução, conforme a subunidade mencionada",
        role: "A IN prevê essas divisões e seções em diferentes níveis; a subordinação apresentada varia conforme o órgão e deve ser conferida no organograma.",
      },
    ],
  },
  {
    domain: "Controle interno e correição",
    high: ["Jurídica"],
    moderate: ["Gestão, administração, economia, contabilidade, logística e áreas afins", "Ciências exatas, engenharias e tecnologia"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Controladoria Interna",
        hierarchy: "Órgão de Direção Setorial · controle de pessoal, patrimônio, contábil, orçamentário e financeiro",
        orgCategory: sectoralPath,
        role: "Exerce controle interno e avaliação de atos de gestão segundo legalidade, legitimidade, economicidade, eficiência e eficácia.",
      },
      {
        unitType: "Administrativa",
        unitName: "Corregedoria Geral · Divisão Administrativa",
        hierarchy: "Corregedoria da PMAC · protocolo · ouvidoria · procedimentos · estatística · atividade cartorária",
        orgCategory: "Órgãos de Direção Geral · estrutura da Corregedoria descrita na Seção II",
        role: "A divisão administrativa realiza atividades de protocolo, ouvidoria, registro e controle de procedimentos, estatística, avaliação e atividade cartorária.",
      },
      {
        unitType: "Operacional",
        unitName: "Corregedoria Geral · Divisão Operacional",
        hierarchy: "Seções de Investigação de Crimes Militares · Justiça e Disciplina · Inteligência",
        orgCategory: "Órgãos de Direção Geral · atividade correicional em âmbito estadual",
        role: "Executa, controla e analisa atividade de polícia judiciária militar e correição disciplinar, conforme a estrutura da IN.",
      },
    ],
  },
  {
    domain: "Logística e patrimônio",
    high: ["Gestão, administração, economia, contabilidade, logística e áreas afins", "Ciências exatas, engenharias e tecnologia"],
    moderate: ["Saúde"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Diretoria de Logística e Patrimônio (DLP)",
        hierarchy: "Divisão de Logística (DL) · Divisão Financeira (DF) · Divisão de Patrimônio (DP) · Divisão de Manutenções Veiculares (DMV)",
        orgCategory: administrativeDirectoratePath,
        role: "Inclui licitações, contratos, convênios, almoxarifado, atividades financeiras e orçamentárias, bens móveis e imóveis, material controlado e manutenção veicular.",
      },
      {
        unitType: "Operacional",
        unitName: "Seções de Logística e Patrimônio das unidades",
        hierarchy: "Seções internas previstas em batalhões e unidades especializadas",
        orgCategory: `${operationalExecutionPath} · apoio administrativo da unidade`,
        role: "A estrutura de diversos batalhões prevê Seção de Logística e Patrimônio; a existência e o escopo devem ser confirmados por unidade.",
      },
    ],
  },
  {
    domain: "Planejamento institucional e projetos",
    high: ["Gestão, administração, economia, contabilidade, logística e áreas afins"],
    moderate: ["Ciências exatas, engenharias e tecnologia", "Jurídica"],
    placements: [{
      unitType: "Administrativa",
      unitName: "Diretoria de Planejamento (DPLAN)",
      hierarchy: "Divisão de Tecnologia da Informação e Comunicação (DTIC) · Divisão de Planejamento e Estudos (DPE) · Divisão de Convênios e Projetos (DCP) · Divisão de Planejamento Orçamentário (DPO)",
      orgCategory: administrativeDirectoratePath,
      role: "Atua no planejamento institucional, estudos, projetos, captação de recursos, convênios e planejamento orçamentário.",
    }],
  },
  {
    domain: "Comunicação institucional",
    high: ["Humanidades e comunicação"],
    moderate: ["Gestão, administração, economia, contabilidade, logística e áreas afins", "Ciências exatas, engenharias e tecnologia"],
    placements: [
      {
        unitType: "Administrativa",
        unitName: "Assessoria de Comunicação Social",
        hierarchy: "Seções de Imprensa e Propaganda Institucional · Relações Institucionais",
        orgCategory: sectoralPath,
        role: "Promove a interação institucional com públicos internos e externos, marketing institucional, endomarketing e relações públicas.",
      },
      {
        unitType: "Operacional",
        unitName: "Seções de Comunicação Social das unidades",
        hierarchy: "Seções previstas na estrutura administrativa de diversos batalhões",
        orgCategory: `${operationalExecutionPath} · estrutura interna da unidade`,
        role: "O organograma inclui Seções de Comunicação Social em estruturas de batalhão; a presença pode variar entre unidades.",
      },
    ],
  },
  {
    domain: "Assessoria jurídica",
    high: ["Jurídica"],
    moderate: ["Gestão, administração, economia, contabilidade, logística e áreas afins", "Humanidades e comunicação"],
    placements: [{
      unitType: "Administrativa",
      unitName: "Assessoria Jurídica",
      hierarchy: "Seção de Assuntos Administrativos · Seção de Assuntos Judiciais",
      orgCategory: sectoralPath,
      role: "Presta assessoramento técnico-jurídico ao Comandante-Geral nos assuntos administrativos e de legalidade, ressalvadas as atribuições legais da PGE.",
    }],
  },
  {
    domain: "Tecnologia da informação e comunicação",
    high: ["Ciências exatas, engenharias e tecnologia"],
    moderate: ["Gestão, administração, economia, contabilidade, logística e áreas afins"],
    placements: [{
      unitType: "Administrativa",
      unitName: "Divisão de Tecnologia da Informação e Comunicação (DTIC)",
      hierarchy: "DPLAN · Sistemas e Modernização · Redes e Manutenção · Rádio Comunicação",
      orgCategory: `${administrativeDirectoratePath} · estrutura interna do DPLAN`,
      role: "Planeja e supervisiona sistemas, redes, infraestrutura computacional, serviços de informática, rádio comunicação e segurança cibernética.",
    }],
  },
];

function normalize(value: string) {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toUpperCase()
    .replace(/&/g, " E ")
    .replace(/[^A-Z0-9/;,-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const nonComparable = new Set(["", "SEM DADOS", "ENSINO MEDIO", "MEDIO", "NAO INFORMADO", "NAO SE APLICA"]);

export function getCandidates(input: string, unitType: FilterType): MatchResult {
  const normalized = normalize(input);
  if (nonComparable.has(normalized)) {
    return { foundDomains: [], candidates: [], reviewMessage: "Esta entrada não representa uma área de formação comparável. Revise a informação e encaminhe o caso para análise humana." };
  }

  const found = academicDomains
    .filter((item) => item.keywords.some((keyword) => normalized.includes(keyword)))
    .map((item) => item.name);

  if (!found.length) {
    return {
      foundDomains: [],
      candidates: [],
      reviewMessage: "A formação não foi reconhecida pelas regras atuais. Encaminhe o caso para revisão humana e, se necessário, atualize a matriz após validação institucional.",
    };
  }

  const candidates: Candidate[] = [];
  functionalDomains.forEach((item) => {
    const placements = item.placements.filter((placement) => unitType === "Todos" || placement.unitType === unitType);
    if (!placements.length) return;

    const hasHighMatch = item.high.some((domain) => found.includes(domain));
    const hasModerateMatch = item.moderate.some((domain) => found.includes(domain));
    // Regra definida no estudo: a melhor correspondência prevalece por domínio funcional.
    if (hasHighMatch) {
      candidates.push({ domain: item.domain, placements, priority: "Alta" });
    } else if (hasModerateMatch) {
      candidates.push({ domain: item.domain, placements, priority: "Moderada" });
    }
  });

  candidates.sort((a, b) => (a.priority === b.priority ? a.domain.localeCompare(b.domain, "pt-BR") : a.priority === "Alta" ? -1 : 1));
  return { foundDomains: found, candidates };
}
