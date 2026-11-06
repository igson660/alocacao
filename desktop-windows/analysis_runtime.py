from __future__ import annotations

import contextlib
import importlib
import json
import math
import os
import re
import sys
import traceback
import warnings
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

MODEL_ID = "paraphrase-multilingual-MiniLM-L12-v2"
MODEL_REPOSITORY = f"sentence-transformers/{MODEL_ID}"
MODEL_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
EXPECTED_OUTPUTS = (
    "resultado_analise_pmac_completo.csv",
    "resultado_analise_pmac_aplicavel.csv",
    "auditoria_classificacao_unidades.csv",
)
STAGE_LABELS = {
    "cafda1f0": "Preparando bibliotecas e parâmetros",
    "ff137962": "Lendo o arquivo e identificando as colunas",
    "abd30771": "Normalizando dados e removendo identificadores diretos",
    "508403a2": "Calculando estatísticas descritivas e gráficos",
    "2a566cc3": "Classificando áreas de formação",
    "fa94fc97": "Classificando unidades e preparando auditoria",
    "43af4438": "Validando a matriz de correspondência",
    "e458ebf1": "Aplicando a matriz e calculando aderência",
    "5365ed6f": "Executando TF-IDF e regressão logística",
    "475d1643": "Executando embeddings e análise semântica",
    "e06bfc3a": "Comparando os modelos",
    "5836ad52": "Exportando os arquivos de resultado",
}

_EVENT_SINK: Callable[[dict[str, Any]], None] | None = None
_CANCEL_EVENT: Any = None


class RunCancelled(BaseException):
    """Cancelamento cooperativo entre células ou lotes de embeddings."""


def application_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def model_path() -> Path:
    return application_root() / "models" / MODEL_ID


def emit_event(event: str, **data: Any) -> None:
    payload = {"event": event, **data}
    if _EVENT_SINK is not None:
        _EVENT_SINK(payload)
        return
    stream = getattr(sys, "__stdout__", None) or getattr(sys, "stdout", None)
    if stream is not None:
        stream.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
        stream.flush()


def _cancel_if_requested() -> None:
    if _CANCEL_EVENT is not None and _CANCEL_EVENT.is_set():
        raise RunCancelled()


class NotebookLogWriter:
    encoding = "utf-8"

    def __init__(self, channel: str = "log") -> None:
        self.channel = channel
        self.buffer = ""

    def write(self, text: str) -> int:
        if not text:
            return 0
        self.buffer += str(text)
        while "\n" in self.buffer or "\r" in self.buffer:
            match = re.search(r"[\n\r]", self.buffer)
            assert match is not None
            line, self.buffer = self.buffer[: match.start()], self.buffer[match.end() :]
            cleaned = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
            if cleaned:
                emit_event(self.channel, message=cleaned[:1800])
        return len(text)

    def flush(self) -> None:
        if self.buffer.strip():
            cleaned = re.sub(r"\x1b\[[0-9;]*m", "", self.buffer).strip()
            emit_event(self.channel, message=cleaned[:1800])
        self.buffer = ""

    def isatty(self) -> bool:
        return False


class DesktopColabFiles:
    """Adaptador do diálogo de arquivo para o files.upload usado no notebook."""

    def __init__(self, input_path: Path) -> None:
        self.input_path = input_path

    def upload(self) -> dict[str, bytes]:
        emit_event("log", message=f"Arquivo selecionado: {self.input_path.name}")
        return {self.input_path.name: self.input_path.read_bytes()}

    @staticmethod
    def download(_path: str) -> None:
        return None


def _safe_cell(value: Any) -> Any:
    if value is None:
        return None
    try:
        if hasattr(value, "item"):
            value = value.item()
    except Exception:
        pass
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
    except Exception:
        pass
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _install_colab_adapter(input_path: Path) -> None:
    google_pkg = ModuleType("google")
    google_pkg.__path__ = []  # type: ignore[attr-defined]
    colab_pkg = ModuleType("google.colab")
    colab_pkg.__path__ = []  # type: ignore[attr-defined]
    colab_pkg.files = DesktopColabFiles(input_path)  # type: ignore[attr-defined]
    google_pkg.colab = colab_pkg  # type: ignore[attr-defined]
    sys.modules["google"] = google_pkg
    sys.modules["google.colab"] = colab_pkg


def _install_display_adapter(output_dir: Path, chart_files: list[Path]):
    display_module = ModuleType("IPython.display")
    ipython_pkg = ModuleType("IPython")
    ipython_pkg.__path__ = []  # type: ignore[attr-defined]
    ipython_pkg.version_info = (9, 0, 0)  # type: ignore[attr-defined]
    ipython_pkg.get_ipython = lambda: None  # type: ignore[attr-defined]
    captured_figures: set[int] = set()

    def desktop_display(*objects: Any, **_kwargs: Any) -> None:
        for obj in objects:
            if hasattr(obj, "to_dict") and hasattr(obj, "columns"):
                try:
                    records = obj.head(24).to_dict(orient="records")
                    rows = [{str(k): _safe_cell(v) for k, v in row.items()} for row in records]
                    emit_event(
                        "table",
                        title=f"Tabela exibida — {len(obj):,} registros".replace(",", "."),
                        columns=[str(c) for c in obj.columns],
                        rows=rows,
                        row_count=int(len(obj)),
                        preview_count=len(rows),
                    )
                except Exception as exc:
                    emit_event("log", message=f"Resultado tabular calculado; prévia indisponível: {exc}")
            elif hasattr(obj, "to_frame") and hasattr(obj, "index"):
                try:
                    frame = obj.to_frame().head(24)
                    rows = [{str(k): _safe_cell(v) for k, v in row.items()} for row in frame.to_dict(orient="records")]
                    emit_event(
                        "table",
                        title=f"Tabela exibida — {len(obj):,} registros".replace(",", "."),
                        columns=[str(c) for c in frame.columns],
                        rows=rows,
                        row_count=int(len(obj)),
                        preview_count=len(rows),
                    )
                except Exception:
                    emit_event("log", message=f"Resultado tabular calculado ({type(obj).__name__}).")
            else:
                emit_event("log", message=f"Resultado exibido ({type(obj).__name__}).")

    def capture_plots() -> None:
        import matplotlib.pyplot as plt

        charts_dir = output_dir / "graficos"
        charts_dir.mkdir(parents=True, exist_ok=True)
        for figure_num in plt.get_fignums():
            if figure_num in captured_figures:
                continue
            fig = plt.figure(figure_num)
            idx = len(chart_files) + 1
            path = charts_dir / f"grafico_{idx:02d}.png"
            fig.savefig(path, dpi=170, bbox_inches="tight", facecolor="white")
            captured_figures.add(figure_num)
            chart_files.append(path)
            emit_event("chart", path=str(path), title=f"Gráfico {idx:02d}")

    import matplotlib.pyplot as plt

    def desktop_show(*_args: Any, **_kwargs: Any) -> None:
        capture_plots()

    # No desktop, a exibição do gráfico é transferida à aba Gráficos; salvar
    # aqui evita depender de uma janela ou backend gráfico dentro do worker.
    plt.show = desktop_show
    display_module.display = desktop_display  # type: ignore[attr-defined]
    sys.modules["IPython"] = ipython_pkg
    sys.modules["IPython.display"] = display_module
    return capture_plots


def _install_headless_chart_backend() -> None:
    os.environ["MPLBACKEND"] = "Agg"


def _patch_embedding_progress() -> None:
    """Mantém a barra por lotes do encode e envia também o progresso à interface."""
    try:
        model_module = importlib.import_module("sentence_transformers.sentence_transformer.model")
        original_trange = model_module.trange
        if getattr(original_trange, "_pmac_progress_patch", False):
            return

        def reporting_trange(*args: Any, **kwargs: Any):
            numbers = [int(x) for x in args[:3]]
            if len(numbers) == 1:
                start, stop, step = 0, numbers[0], 1
            elif len(numbers) == 2:
                start, stop, step = numbers[0], numbers[1], 1
            else:
                start, stop, step = numbers[0], numbers[1], numbers[2]
            total = max(0, math.ceil((stop - start) / step)) if step else 0
            description = str(kwargs.get("desc") or "Lotes de embeddings")
            native_kwargs = dict(kwargs)
            native_kwargs["disable"] = True
            for completed, item in enumerate(original_trange(*args, **native_kwargs), start=1):
                _cancel_if_requested()
                yield item
                emit_event("subprogress", message=description, completed=completed, total=total)

        setattr(reporting_trange, "_pmac_progress_patch", True)
        model_module.trange = reporting_trange
    except Exception as exc:
        emit_event("warning", message=f"Não foi possível conectar a barra interna de lotes: {exc}")


def run_notebook(
    input_file: str | Path,
    output_dir: str | Path,
    run_tfidf: bool = True,
    run_embeddings: bool = True,
    event_callback: Callable[[dict[str, Any]], None] | None = None,
    cancel_event: Any = None,
) -> dict[str, Any]:
    """Executa as células analíticas originais com adaptadores desktop.

    O notebook é executado sem alteração. Somente a célula `%pip` não roda, pois
    as bibliotecas estão empacotadas no programa; upload/download são adaptados a
    caminhos locais e o modelo é apontado para a mesma revisão incluída no pacote.
    """
    global _EVENT_SINK, _CANCEL_EVENT
    _EVENT_SINK = event_callback
    _CANCEL_EVENT = cancel_event
    input_path = Path(input_file).resolve()
    out_dir = Path(output_dir).resolve()
    notebook_path = application_root() / "notebook" / "ferramenta_preditiva_pmac.ipynb"
    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo de entrada inexistente: {input_path}")
    if input_path.suffix.casefold() not in {".csv", ".xlsx", ".xls"}:
        raise ValueError("Selecione um arquivo CSV ou Excel (.csv, .xlsx ou .xls).")
    if not notebook_path.is_file():
        raise FileNotFoundError(f"Notebook original ausente: {notebook_path}")
    out_dir.mkdir(parents=True, exist_ok=True)

    _install_colab_adapter(input_path)
    _install_headless_chart_backend()
    charts: list[Path] = []
    capture_plots = _install_display_adapter(out_dir, charts)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells: list[tuple[dict[str, Any], str]] = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        # Esta é a célula exclusiva de instalação no runtime Colab.
        if any(line.lstrip().startswith("%") for line in source.splitlines()):
            continue
        if source.strip():
            code_cells.append((cell, source))
    if not code_cells:
        raise RuntimeError("O notebook não contém células de análise executáveis.")

    total_steps = len(code_cells)
    emit_event("run_started", total_steps=total_steps, input_name=input_path.name)
    writer = NotebookLogWriter()
    namespace: dict[str, Any] = {"__name__": "__pmac_notebook_runtime__"}
    previous_cwd = Path.cwd()
    os.chdir(out_dir)
    old_stdout, old_stderr = sys.stdout, sys.stderr
    completed_steps = 0
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            for index, (cell, source) in enumerate(code_cells, start=1):
                _cancel_if_requested()
                cell_id = str(cell.get("id", f"c{index}"))
                label = STAGE_LABELS.get(cell_id, f"Etapa {index} de {total_steps}")
                emit_event("stage_started", index=index, total=total_steps, cell_id=cell_id, label=label)
                sys.stdout, sys.stderr = writer, writer
                try:
                    if cell_id == "475d1643" and run_embeddings:
                        _patch_embedding_progress()
                    exec(compile(source, f"<notebook-cell-{cell_id}>", "exec"), namespace, namespace)
                    if cell_id == "cafda1f0":
                        namespace["EXECUTAR_TFIDF"] = bool(run_tfidf)
                        namespace["EXECUTAR_EMBEDDINGS"] = bool(run_embeddings)
                        local_model = application_root() / "models" / MODEL_ID
                        if local_model.is_dir():
                            namespace["MODELO_EMBEDDING"] = str(local_model)
                        emit_event(
                            "log",
                            message=(
                                "Opções selecionadas: TF-IDF "
                                + ("ativado" if run_tfidf else "desativado")
                                + "; embeddings "
                                + ("ativados" if run_embeddings else "desativados")
                                + "."
                            ),
                        )
                    if cell_id == "5836ad52":
                        capture_plots()
                    completed_steps = index
                    emit_event("stage_completed", index=index, total=total_steps, cell_id=cell_id, label=label)
                except RunCancelled:
                    raise
                except Exception:
                    detail = traceback.format_exc()
                    emit_event("fatal_error", stage=label, traceback=detail)
                    raise
                finally:
                    writer.flush()
                    sys.stdout, sys.stderr = old_stdout, old_stderr
            for item in caught:
                emit_event("warning", message=str(item.message), category=item.category.__name__)

        outputs = [str(out_dir / name) for name in EXPECTED_OUTPUTS if (out_dir / name).is_file()]
        missing = sorted(set(EXPECTED_OUTPUTS) - {Path(p).name for p in outputs})
        if missing:
            raise RuntimeError("A análise terminou sem criar todos os arquivos previstos: " + ", ".join(missing))
        emit_event("run_completed", completed_steps=completed_steps, total_steps=total_steps, outputs=outputs, charts=[str(p) for p in charts])
        return {"outputs": outputs, "charts": [str(p) for p in charts]}
    except RunCancelled:
        emit_event("run_cancelled", completed_steps=completed_steps, total_steps=total_steps)
        return {"cancelled": True, "outputs": [], "charts": []}
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
        os.chdir(previous_cwd)
        _EVENT_SINK = None
        _CANCEL_EVENT = None


class CancellationMarker:
    def __init__(self, path: str | Path | None) -> None:
        self.path = Path(path) if path else None

    def is_set(self) -> bool:
        return bool(self.path and self.path.exists())


class EventFileSink:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")

    def __call__(self, event: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
            stream.flush()


def run_worker_from_cli(argv: list[str]) -> int:
    import argparse

    event_path = None
    for index, value in enumerate(argv[:-1]):
        if value == "--event-file":
            event_path = argv[index + 1]
            break
        if value.startswith("--event-file="):
            event_path = value.split("=", 1)[1]
            break
    event_sink = EventFileSink(event_path) if event_path else None

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("input_file")
    parser.add_argument("output_dir")
    parser.add_argument("--event-file", required=True)
    parser.add_argument("--cancel-file")
    parser.add_argument("--no-tfidf", action="store_true")
    parser.add_argument("--no-embeddings", action="store_true")
    try:
        options = parser.parse_args(argv[1:])
    except SystemExit as exc:
        if event_sink is not None:
            event_sink({"event": "worker_error", "message": "Argumentos do worker inválidos; verifique o log de execução."})
        return int(exc.code or 0)

    event_sink = event_sink or EventFileSink(options.event_file)

    try:
        run_notebook(
            options.input_file,
            options.output_dir,
            run_tfidf=not options.no_tfidf,
            run_embeddings=not options.no_embeddings,
            event_callback=event_sink,
            cancel_event=CancellationMarker(options.cancel_file),
        )
        return 0
    except RunCancelled:
        return 130
    except Exception as exc:
        event_sink({"event": "worker_error", "message": str(exc), "traceback": traceback.format_exc()})
        return 1


def run_worker_from_config(config_file: str | Path) -> int:
    """Executa o mesmo fluxo worker usando um arquivo de configuração local.

    Esse modo evita depender de argumentos de linha de comando ao iniciar o
    binário GUI empacotado no Windows. O arquivo é apagado assim que lido.
    """
    config_path = Path(config_file)
    config: dict[str, Any] = {}
    event_sink: EventFileSink | None = None
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config_path.unlink(missing_ok=True)
        event_path = config.get("event_file")
        if event_path:
            event_sink = EventFileSink(event_path)
        if event_sink is None:
            raise ValueError("A configuração do worker precisa informar event_file.")
        run_notebook(
            config["input_file"],
            config["output_dir"],
            run_tfidf=bool(config.get("run_tfidf", True)),
            run_embeddings=bool(config.get("run_embeddings", True)),
            event_callback=event_sink,
            cancel_event=CancellationMarker(config.get("cancel_file")),
        )
        return 0
    except RunCancelled:
        return 130
    except Exception as exc:
        if event_sink is None and config.get("event_file"):
            try:
                event_sink = EventFileSink(config["event_file"])
            except Exception:
                event_sink = None
        if event_sink is not None:
            event_sink({"event": "worker_error", "message": str(exc), "traceback": traceback.format_exc()})
        return 1
