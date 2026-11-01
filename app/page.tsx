"use client";

import Image from "next/image";
import { FormEvent, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  Info,
  LockKeyhole,
  RotateCcw,
  Search,
  X,
} from "lucide-react";
import {
  Candidate,
  FilterType,
  getCandidates,
  organizationalLevels,
  organizationReference,
  Placement,
} from "@/components/allocation-engine";

const filters: FilterType[] = ["Todos", "Operacional", "Administrativa"];
const examples = ["Direito", "Enfermagem", "Sistemas de Informação"];
const horizontalLogo = "/pmac-assinatura-horizontal.webp";
const coatOfArms = "/pmac-brasao.webp";

function PlacementDetails({ placement }: { placement: Placement }) {
  return (
    <div className="placement-detail">
      <div className="placement-title-row">
        <span className={`placement-type placement-type--${placement.unitType.toLowerCase()}`}>
          Grupo {placement.unitType.toLowerCase()}
        </span>
        <b>{placement.unitName}</b>
      </div>
      <p className="placement-hierarchy">{placement.hierarchy}</p>
      <p className="placement-category">{placement.orgCategory}</p>
      <p className="placement-role">{placement.role}</p>
    </div>
  );
}

function CandidateCard({ candidate }: { candidate: Candidate }) {
  const isHigh = candidate.priority === "Alta";
  const placementTypes = Array.from(new Set(candidate.placements.map((placement) => placement.unitType)));

  return (
    <article className="candidate-row">
      <div className="candidate-row__main">
        <div className="candidate-summary">
          <h4>{candidate.domain}</h4>
          <div className="candidate-types" aria-label="Grupos funcionais">
            {placementTypes.map((type) => (
              <span className={`type-tag type-tag--${type.toLowerCase()}`} key={type}>
                {type}
              </span>
            ))}
          </div>
        </div>
        <span className={`priority-pill ${isHigh ? "priority-pill--high" : "priority-pill--moderate"}`}>
          {candidate.priority}
        </span>
      </div>
      <details className="candidate-detail">
        <summary>
          Ver destinos no organograma <ChevronDown size={15} aria-hidden="true" />
        </summary>
        <div className="placement-list">
          {candidate.placements.map((placement) => (
            <PlacementDetails
              placement={placement}
              key={`${placement.unitType}-${placement.unitName}`}
            />
          ))}
        </div>
      </details>
    </article>
  );
}

export default function Home() {
  const [area, setArea] = useState("");
  const [filter, setFilter] = useState<FilterType>("Todos");
  const [submitted, setSubmitted] = useState(false);

  const result = useMemo(
    () => (submitted ? getCandidates(area, filter) : null),
    [area, filter, submitted],
  );
  const highCandidates = result?.candidates.filter((item) => item.priority === "Alta") ?? [];
  const moderateCandidates = result?.candidates.filter((item) => item.priority === "Moderada") ?? [];

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (area.trim()) setSubmitted(true);
  }

  function reset() {
    setArea("");
    setFilter("Todos");
    setSubmitted(false);
  }

  function updateFilter(value: FilterType) {
    setFilter(value);
    setSubmitted(false);
  }

  return (
    <main className="site-shell" id="inicio">
      <header className="topbar">
        <a className="brand" href="#inicio" aria-label="Polícia Militar do Estado do Acre — início">
          <Image
            src={horizontalLogo}
            alt="Polícia Militar do Estado do Acre"
            width={800}
            height={250}
            priority
            unoptimized
            className="brand-signature"
          />
        </a>
        <div className="header-label">
          <span className="header-label__mark" aria-hidden="true" />
          <span>Consulta funcional</span>
        </div>
      </header>

      <section className="intro" aria-labelledby="page-title">
        <div className="intro-copy">
          <p className="eyebrow"><span aria-hidden="true" /> Gestão de pessoas <i /> Estudo aplicado</p>
          <h1 id="page-title">Formação e atuação<br /><em>na PMAC</em></h1>
          <p className="intro-lead">Consulte possíveis correspondências funcionais e destinos previstos no organograma.</p>
        </div>
        <div className="intro-mark" aria-hidden="true">
          <Image src={coatOfArms} alt="" width={480} height={629} unoptimized />
        </div>
      </section>

      <section className="workspace shadow-panel" aria-label="Consulta de correspondências funcionais">
        <form className="input-panel" onSubmit={onSubmit}>
          <div className="panel-kicker"><Search size={14} aria-hidden="true" /> Consulta</div>
          <label className="field-label" htmlFor="area">Área de formação</label>
          <div className="input-wrap">
            <BookOpen size={18} aria-hidden="true" />
            <input
              id="area"
              name="area"
              type="text"
              value={area}
              onChange={(event) => {
                setArea(event.target.value);
                setSubmitted(false);
              }}
              placeholder="Ex.: Direito, Enfermagem, Sistemas de Informação"
              maxLength={180}
              autoComplete="off"
              aria-describedby="privacy-note"
            />
            {area && (
              <button
                type="button"
                className="clear-field"
                onClick={() => {
                  setArea("");
                  setSubmitted(false);
                }}
                aria-label="Limpar área de formação"
              >
                <X size={16} aria-hidden="true" />
              </button>
            )}
          </div>

          <div className="example-row" aria-label="Exemplos de formação">
            <span>Exemplos</span>
            {examples.map((example) => (
              <button
                type="button"
                key={example}
                onClick={() => {
                  setArea(example);
                  setSubmitted(false);
                }}
              >
                {example}
              </button>
            ))}
          </div>

          <fieldset className="filter-block">
            <legend className="filter-label">Mostrar resultados</legend>
            <div className="filter-tabs" role="group" aria-label="Filtrar por grupo funcional">
              {filters.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => updateFilter(item)}
                  className={filter === item ? "is-active" : ""}
                  aria-pressed={filter === item}
                >
                  {item === "Todos" ? "Todas" : item === "Operacional" ? "Operacionais" : "Administrativas"}
                </button>
              ))}
            </div>
            <p className="filter-help">O grupo é analítico; os detalhes apresentam a hierarquia institucional.</p>
          </fieldset>

          <div className="actions-row">
            <button type="submit" className="primary-button" disabled={!area.trim()}>
              Consultar correspondências <ArrowRight size={16} aria-hidden="true" />
            </button>
            {submitted && (
              <button type="button" className="reset-button" onClick={reset} aria-label="Limpar consulta">
                <RotateCcw size={16} aria-hidden="true" />
              </button>
            )}
          </div>

          <p className="privacy-note" id="privacy-note">
            <LockKeyhole size={14} aria-hidden="true" />
            Não informe dados pessoais. O cálculo ocorre neste navegador.
          </p>
        </form>

        <section
          className="output-panel"
          aria-live="polite"
          aria-labelledby="results-title"
        >
          <div className="results-heading">
            <div>
              <p className="eyebrow">Resultado</p>
              <h2 id="results-title">Correspondências</h2>
            </div>
            {result?.candidates.length ? (
              <span className="result-count" role="status">
                {result.candidates.length} {result.candidates.length === 1 ? "domínio" : "domínios"}
              </span>
            ) : null}
          </div>

          {!result && (
            <div className="empty-state">
              <div className="empty-icon"><BookOpen size={23} aria-hidden="true" /></div>
              <p>Informe uma área para consultar possíveis correspondências.</p>
            </div>
          )}

          {result?.reviewMessage && (
            <div className="review-message" role="status">
              <Info size={18} aria-hidden="true" />
              <p>{result.reviewMessage}</p>
            </div>
          )}

          {result && result.candidates.length > 0 && (
            <div className="result-content">
              <div className="recognized-domains">
                <span>Formação reconhecida como</span>
                <div>{result.foundDomains.map((domain) => <b key={domain}>{domain}</b>)}</div>
              </div>

              {highCandidates.length > 0 && (
                <div className="candidate-group">
                  <div className="group-title">
                    <h3>Alta correspondência</h3>
                    <span>{highCandidates.length}</span>
                  </div>
                  {highCandidates.map((candidate) => <CandidateCard candidate={candidate} key={candidate.domain} />)}
                </div>
              )}

              {moderateCandidates.length > 0 && (
                <div className="candidate-group">
                  <div className="group-title">
                    <h3>Moderada correspondência</h3>
                    <span>{moderateCandidates.length}</span>
                  </div>
                  {moderateCandidates.map((candidate) => <CandidateCard candidate={candidate} key={candidate.domain} />)}
                </div>
              )}

              <p className="review-footnote">
                <CheckCircle2 size={15} aria-hidden="true" />
                Indicador exploratório. Não recomenda lotação.
              </p>
            </div>
          )}

          {result && !result.reviewMessage && result.candidates.length === 0 && (
            <div className="empty-state empty-state--small">
              <p>Não há resultados para este grupo.</p>
              <span>Experimente selecionar “Todas”.</span>
            </div>
          )}
        </section>
      </section>

      <details className="org-source">
        <summary>Base organizacional <ChevronDown size={15} aria-hidden="true" /></summary>
        <div>
          <p><b>{organizationReference.title}</b> · {organizationReference.publication}.</p>
          <p>{organizationReference.note}</p>
          <p>{organizationReference.methodologyNote}</p>
          <div className="org-levels">
            {organizationalLevels.map((item) => (
              <section key={item.level}>
                <b>{item.level}</b>
                <p>{item.organs}</p>
              </section>
            ))}
          </div>
        </div>
      </details>

      <footer className="footer-note">
        <span>Ferramenta acadêmica de apoio à consulta.</span>
        <span>Não oficializa movimentações nem substitui decisão institucional.</span>
      </footer>
    </main>
  );
}
