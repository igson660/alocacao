from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QTimer, QUrl, Qt, QSize
from PySide6.QtGui import QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from analysis_runtime import EXPECTED_OUTPUTS, application_root, run_worker_from_cli

PALETTE = {
    "navy": "#143f79",
    "blue": "#2055a5",
    "green": "#078744",
    "red": "#e52b3c",
    "yellow": "#ffd91c",
    "ink": "#17263c",
    "muted": "#68788d",
    "paper": "#f5f7fa",
    "white": "#ffffff",
    "line": "#e4eaf0",
    "soft_blue": "#edf4fc",
    "soft_green": "#eaf7f0",
    "soft_yellow": "#fff9dc",
}

APP_QSS = f"""
QMainWindow, QWidget {{ background: {PALETTE['paper']}; color: {PALETTE['ink']}; font-family: 'Segoe UI'; font-size: 10pt; }}
QFrame#Header {{ background: {PALETTE['white']}; border: 1px solid {PALETTE['line']}; border-radius: 18px; }}
QFrame#Panel {{ background: {PALETTE['white']}; border: 1px solid {PALETTE['line']}; border-radius: 16px; }}
QLabel#Title {{ color: {PALETTE['ink']}; font-size: 21pt; font-weight: 700; }}
QLabel#Subtitle {{ color: {PALETTE['muted']}; font-size: 10pt; }}
QLabel#SectionTitle {{ color: {PALETTE['ink']}; font-size: 12pt; font-weight: 700; }}
QLabel#Muted {{ color: {PALETTE['muted']}; }}
QLabel#Status {{ color: {PALETTE['blue']}; font-weight: 600; }}
QLabel#Warning {{ color: #6a5712; background: {PALETTE['soft_yellow']}; border: 1px solid #f0df80; border-radius: 11px; padding: 10px 12px; }}
QPushButton {{ border: 1px solid {PALETTE['line']}; border-radius: 9px; padding: 9px 14px; background: {PALETTE['white']}; color: {PALETTE['ink']}; font-weight: 600; }}
QPushButton:hover {{ background: {PALETTE['soft_blue']}; border-color: #bed0e8; }}
QPushButton:disabled {{ color: #9aa7b5; background: #f1f3f6; }}
QPushButton#Primary {{ background: {PALETTE['blue']}; color: white; border: 0; padding: 11px 19px; }}
QPushButton#Primary:hover {{ background: {PALETTE['navy']}; }}
QPushButton#Danger {{ color: #a51926; border-color: #f1c6ca; background: #fffafa; }}
QLineEdit {{ border: 1px solid {PALETTE['line']}; border-radius: 8px; background: white; padding: 9px 10px; }}
QCheckBox {{ spacing: 8px; color: {PALETTE['ink']}; }}
QTabWidget::pane {{ border: 0; }}
QTabBar::tab {{ background: transparent; color: {PALETTE['muted']}; padding: 10px 15px; margin-right: 5px; border-radius: 9px; font-weight: 600; }}
QTabBar::tab:selected {{ background: {PALETTE['soft_blue']}; color: {PALETTE['blue']}; }}
QProgressBar {{ border: 0; border-radius: 6px; height: 11px; background: #e8edf3; text-align: center; }}
QProgressBar::chunk {{ border-radius: 6px; background: {PALETTE['green']}; }}
QListWidget {{ background: transparent; border: 0; outline: 0; }}
QListWidget::item {{ padding: 9px 8px; border-radius: 8px; }}
QTextEdit {{ background: #fbfcfe; border: 1px solid {PALETTE['line']}; border-radius: 10px; padding: 10px; color: #33445b; font-family: Consolas, 'Cascadia Mono', monospace; font-size: 9pt; }}
QTableWidget {{ background: white; alternate-background-color: #f8fafc; border: 1px solid {PALETTE['line']}; border-radius: 10px; gridline-color: {PALETTE['line']}; }}
QHeaderView::section {{ background: {PALETTE['soft_blue']}; color: {PALETTE['navy']}; padding: 7px; border: 0; font-weight: 700; }}
QScrollArea {{ border: 0; background: transparent; }}
"""

STEPS_FOR_UI = [
    "Preparando bibliotecas e parâmetros",
    "Lendo o arquivo e identificando as colunas",
    "Normalizando dados e removendo identificadores diretos",
    "Calculando estatísticas descritivas e gráficos",
    "Classificando áreas de formação",
    "Classificando unidades e preparando auditoria",
    "Validando a matriz de correspondência",
    "Aplicando a matriz e calculando aderência",
    "Executando TF-IDF e regressão logística",
    "Executando embeddings e análise semântica",
    "Comparando os modelos",
    "Exportando os arquivos de resultado",
]


class Panel(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Panel")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PMAC | Análise de Formação e Unidade")
        self.setMinimumSize(1100, 740)
        self.resize(1420, 920)
        self.setWindowIcon(QIcon(str(application_root() / "assets" / "pmac-icon.png")))
        self.input_path: Path | None = None
        self.output_dir: Path | None = None
        self.outputs: list[Path] = []
        self.chart_paths: list[Path] = []
        self.stage_index = 0
        self.stage_total = len(STEPS_FOR_UI)
        self.last_error = ""
        self.event_file: Path | None = None
        self.cancel_file: Path | None = None
        self.event_line_count = 0
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._process_finished)
        self.process.errorOccurred.connect(self._process_error)
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(240)
        self.animation_timer.timeout.connect(self._animate_status)
        self.animation_frame = 0
        self.event_timer = QTimer(self)
        self.event_timer.setInterval(120)
        self.event_timer.timeout.connect(self._poll_event_file)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(26, 20, 26, 22)
        outer.setSpacing(16)

        header = QFrame()
        header.setObjectName("Header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 10, 22, 10)
        logo = QLabel()
        logo.setFixedSize(255, 80)
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_path = application_root() / "assets" / "pmac-assinatura-horizontal.png"
        pix = QPixmap(str(logo_path))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(250, 74, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("POLÍCIA MILITAR\nDO ESTADO DO ACRE")
        hl.addWidget(logo)
        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setStyleSheet(f"color:{PALETTE['line']};")
        hl.addWidget(vline)
        brand_text = QVBoxLayout()
        title = QLabel("Análise de formação e unidade")
        title.setObjectName("Title")
        subtitle = QLabel("Execução local do fluxo analítico do notebook PMAC")
        subtitle.setObjectName("Subtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        hl.addLayout(brand_text)
        hl.addStretch(1)
        self.model_badge = QLabel()
        self.model_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_badge.setMinimumWidth(164)
        self._refresh_model_badge()
        hl.addWidget(self.model_badge)
        outer.addWidget(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        outer.addLayout(grid, 1)

        setup = Panel()
        setup.setMinimumWidth(415)
        setup_layout = QVBoxLayout(setup)
        setup_layout.setContentsMargins(20, 20, 20, 20)
        setup_layout.setSpacing(13)

        section = QLabel("1. Selecione a análise")
        section.setObjectName("SectionTitle")
        setup_layout.addWidget(section)
        setup_layout.addWidget(self._muted("Escolha uma única base CSV ou Excel para analisar."))

        self.input_label = QLabel("Nenhum arquivo selecionado")
        self.input_label.setWordWrap(True)
        self.input_label.setMinimumHeight(42)
        self.input_label.setStyleSheet(f"background:{PALETTE['soft_blue']};border-radius:9px;padding:9px;color:{PALETTE['navy']};")
        setup_layout.addWidget(self.input_label)
        browse_row = QHBoxLayout()
        browse_row.addWidget(self._primary_button("Selecionar arquivo", self._choose_input))
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self._clear_input)
        browse_row.addWidget(self.clear_button)
        browse_row.addStretch(1)
        setup_layout.addLayout(browse_row)

        setup_layout.addSpacing(2)
        output_title = QLabel("Pasta dos resultados")
        output_title.setObjectName("SectionTitle")
        setup_layout.addWidget(output_title)
        output_row = QHBoxLayout()
        self.output_label = QLabel("Escolha uma pasta de saída")
        self.output_label.setWordWrap(True)
        self.output_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        output_row.addWidget(self.output_label, 1)
        output_row.addWidget(self._button("Selecionar pasta", self._choose_output))
        setup_layout.addLayout(output_row)

        setup_layout.addSpacing(3)
        options_title = QLabel("Experimentos do notebook")
        options_title.setObjectName("SectionTitle")
        setup_layout.addWidget(options_title)
        self.tfidf_check = QCheckBox("Executar TF-IDF + regressão logística")
        self.tfidf_check.setChecked(True)
        self.embedding_check = QCheckBox("Executar embeddings semânticos")
        self.embedding_check.setChecked(True)
        setup_layout.addWidget(self.tfidf_check)
        setup_layout.addWidget(self.embedding_check)
        setup_layout.addWidget(self._muted("O padrão preserva as duas etapas habilitadas no notebook."))

        privacy = QLabel("Os cálculos são feitos no computador. O arquivo e o texto não são enviados pela aplicação.")
        privacy.setObjectName("Warning")
        privacy.setWordWrap(True)
        setup_layout.addWidget(privacy)

        self.run_button = self._primary_button("Executar análise", self._start_run)
        self.run_button.setMinimumHeight(43)
        setup_layout.addWidget(self.run_button)
        self.cancel_button = QPushButton("Cancelar execução")
        self.cancel_button.setObjectName("Danger")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_run)
        setup_layout.addWidget(self.cancel_button)
        setup_layout.addStretch(1)

        footer = QLabel("Saídas: 3 CSVs com os mesmos nomes e colunas do notebook; gráficos são salvos em PNG.")
        footer.setWordWrap(True)
        footer.setObjectName("Muted")
        setup_layout.addWidget(footer)
        grid.addWidget(setup, 0, 0, 1, 1)

        progress_panel = Panel()
        progress_layout = QVBoxLayout(progress_panel)
        progress_layout.setContentsMargins(20, 18, 20, 18)
        progress_layout.setSpacing(8)
        title_row = QHBoxLayout()
        t = QLabel("2. Acompanhe o processamento")
        t.setObjectName("SectionTitle")
        title_row.addWidget(t)
        title_row.addStretch(1)
        self.progress_percent = QLabel("0%")
        self.progress_percent.setStyleSheet(f"font-size:17pt;font-weight:700;color:{PALETTE['green']};")
        title_row.addWidget(self.progress_percent)
        progress_layout.addLayout(title_row)
        self.main_progress = QProgressBar()
        self.main_progress.setRange(0, 100)
        self.main_progress.setValue(0)
        self.main_progress.setTextVisible(False)
        progress_layout.addWidget(self.main_progress)
        self.status_label = QLabel("Aguardando a seleção do arquivo.")
        self.status_label.setObjectName("Status")
        progress_layout.addWidget(self.status_label)
        self.subprogress = QProgressBar()
        self.subprogress.setRange(0, 100)
        self.subprogress.setValue(0)
        self.subprogress.setTextVisible(False)
        self.subprogress.hide()
        self.subprogress_label = QLabel("")
        self.subprogress_label.setObjectName("Muted")
        self.subprogress_label.hide()
        progress_layout.addWidget(self.subprogress_label)
        progress_layout.addWidget(self.subprogress)

        self.step_list = QListWidget()
        self.step_list.setMinimumHeight(315)
        self.step_list.setMaximumHeight(420)
        for step in STEPS_FOR_UI:
            item = QListWidgetItem("○   " + step)
            item.setData(Qt.ItemDataRole.UserRole, step)
            self.step_list.addItem(item)
        progress_layout.addWidget(self.step_list, 1)
        grid.addWidget(progress_panel, 0, 1, 1, 1)
        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 6)

        bottom = Panel()
        bottom_layout = QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(14, 10, 14, 10)
        self.tabs = QTabWidget()
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setPlaceholderText("As mensagens da análise aparecerão aqui.")
        self.chart_scroll = QScrollArea()
        self.chart_scroll.setWidgetResizable(True)
        self.chart_container = QWidget()
        self.chart_grid = QGridLayout(self.chart_container)
        self.chart_grid.setContentsMargins(6, 6, 6, 6)
        self.chart_grid.setSpacing(12)
        self.chart_scroll.setWidget(self.chart_container)
        self.output_list = QListWidget()
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.tabs.addTab(self._wrap_tab(self.log_view), "Registro das etapas")
        self.tabs.addTab(self.chart_scroll, "Gráficos")
        self.tabs.addTab(self._wrap_tab(self.output_list), "Arquivos gerados")
        self.tabs.addTab(self._wrap_tab(self.preview_table), "Prévia tabular")
        bottom_layout.addWidget(self.tabs)
        bottom.setMinimumHeight(220)
        grid.addWidget(bottom, 1, 0, 1, 2)
        grid.setRowStretch(0, 4)
        grid.setRowStretch(1, 2)

        note = QLabel("Caráter exploratório: a classificação não é avaliação de competência nem decisão de lotação.")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        note.setObjectName("Muted")
        outer.addWidget(note)
        self.setStyleSheet(APP_QSS)
        self._update_steps()

    def _muted(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("Muted")
        label.setWordWrap(True)
        return label

    def _primary_button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("Primary")
        button.clicked.connect(callback)
        return button

    def _button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.clicked.connect(callback)
        return button

    def _wrap_tab(self, widget: QWidget) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(widget)
        return wrapper

    def _refresh_model_badge(self) -> None:
        model_dir = application_root() / "models" / "paraphrase-multilingual-MiniLM-L12-v2"
        ready = model_dir.is_dir() and any(model_dir.glob("*.safetensors"))
        color = PALETTE["green"] if ready else "#8b6b18"
        background = PALETTE["soft_green"] if ready else PALETTE["soft_yellow"]
        text = "MODELO LOCAL DISPONÍVEL" if ready else "MODELO LOCAL AUSENTE"
        self.model_badge.setText(text)
        self.model_badge.setStyleSheet(f"color:{color};background:{background};border-radius:12px;padding:10px;font-size:8pt;font-weight:700;")

    def _choose_input(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione uma base CSV ou Excel",
            str(self.input_path.parent if self.input_path else Path.home()),
            "Arquivos de dados (*.csv *.xlsx *.xls)",
        )
        if path:
            self.input_path = Path(path)
            size_mb = self.input_path.stat().st_size / (1024 * 1024)
            self.input_label.setText(f"{self.input_path.name}\n{size_mb:.1f} MB")
            if self.output_dir is None:
                self.output_dir = self.input_path.parent / "resultados_pmac"
                self.output_label.setText(str(self.output_dir))

    def _clear_input(self) -> None:
        self.input_path = None
        self.input_label.setText("Nenhum arquivo selecionado")

    def _choose_output(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta para os resultados",
            str(self.output_dir or Path.home()),
        )
        if path:
            self.output_dir = Path(path)
            self.output_label.setText(str(self.output_dir))

    def _start_run(self) -> None:
        if self.input_path is None or not self.input_path.is_file():
            QMessageBox.information(self, "Arquivo necessário", "Selecione um único arquivo CSV ou Excel antes de executar.")
            return
        if self.output_dir is None:
            QMessageBox.information(self, "Pasta necessária", "Selecione uma pasta para salvar os resultados.")
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        existing = [self.output_dir / name for name in EXPECTED_OUTPUTS if (self.output_dir / name).exists()]
        if existing:
            names = "\n".join(p.name for p in existing)
            answer = QMessageBox.question(
                self,
                "Arquivos existentes",
                "Os arquivos abaixo serão substituídos nesta pasta:\n\n" + names + "\n\nDeseja continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        self._reset_run_ui()
        assert self.output_dir is not None and self.input_path is not None
        self.event_file = self.output_dir / ".pmac_run_events.jsonl"
        self.cancel_file = self.output_dir / ".pmac_cancel_request"
        self.event_file.write_text("", encoding="utf-8")
        self.cancel_file.unlink(missing_ok=True)
        self.event_line_count = 0
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.animation_timer.start()
        self.status_label.setText("Preparando o processamento…")
        self._append_log("Iniciando execução local do fluxo do notebook.")
        self.tabs.setCurrentIndex(0)

        executable = sys.executable
        if getattr(sys, "frozen", False):
            args = ["--worker", str(self.input_path), str(self.output_dir)]
        else:
            args = [str(Path(__file__).resolve()), "--worker", str(self.input_path), str(self.output_dir)]
        args.extend(["--event-file", str(self.event_file), "--cancel-file", str(self.cancel_file)])
        if not self.tfidf_check.isChecked():
            args.append("--no-tfidf")
        if not self.embedding_check.isChecked():
            args.append("--no-embeddings")
        self.process.setWorkingDirectory(str(application_root()))
        self.process.setProgram(executable)
        self.process.setArguments(args)
        self.process.start()
        self.event_timer.start()
        if not self.process.waitForStarted(5000):
            self.animation_timer.stop()
            self.run_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            QMessageBox.critical(self, "Falha ao iniciar", self.process.errorString())

    def _reset_run_ui(self) -> None:
        self.outputs.clear()
        self.chart_paths.clear()
        self.last_error = ""
        self.main_progress.setValue(0)
        self.progress_percent.setText("0%")
        self.subprogress.hide()
        self.subprogress_label.hide()
        self.preview_table.clear()
        self.preview_table.setRowCount(0)
        self.preview_table.setColumnCount(0)
        self.output_list.clear()
        self.log_view.clear()
        while self.chart_grid.count():
            item = self.chart_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.stage_total = len(STEPS_FOR_UI)
        self.stage_index = 0
        self._update_steps()

    def _read_stdout(self) -> None:
        data = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        for line in data.splitlines():
            try:
                event = json.loads(line)
                self._handle_event(event)
            except json.JSONDecodeError:
                self._append_log(line)

    def _read_stderr(self) -> None:
        data = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")
        for line in data.splitlines():
            if line.strip():
                self._append_log("Aviso técnico: " + line[:1200])

    def _poll_event_file(self) -> None:
        if self.event_file is None or not self.event_file.is_file():
            return
        try:
            text = self.event_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        lines = text.splitlines()
        if text and not text.endswith("\n"):
            lines = lines[:-1]
        new_lines = lines[self.event_line_count :]
        self.event_line_count = len(lines)
        for line in new_lines:
            try:
                self._handle_event(json.loads(line))
            except json.JSONDecodeError:
                self._append_log("Mensagem de progresso inválida recebida do processo de análise.")

    def _handle_event(self, event: dict) -> None:
        kind = event.get("event")
        if kind == "run_started":
            self.stage_total = int(event.get("total_steps", len(STEPS_FOR_UI)))
            self.status_label.setText(f"Analisando {event.get('input_name', 'arquivo')}…")
            self._append_log(f"Fluxo iniciado com {self.stage_total} etapas de notebook.")
        elif kind == "stage_started":
            self.stage_index = int(event.get("index", 0))
            label = str(event.get("label", "Processando"))
            self.status_label.setText(label + "…")
            self._set_step(label, "active")
            self._append_log("Início: " + label)
            if "embeddings" in label.casefold():
                self.subprogress_label.setText("Lotes do modelo semântico")
                self.subprogress_label.show()
                self.subprogress.setValue(0)
                self.subprogress.show()
            else:
                self.subprogress.hide()
                self.subprogress_label.hide()
        elif kind == "stage_completed":
            index = int(event.get("index", self.stage_index))
            label = str(event.get("label", "Etapa"))
            self._set_step(label, "done")
            pct = int(index * 100 / max(1, int(event.get("total", self.stage_total))))
            self.main_progress.setValue(pct)
            self.progress_percent.setText(f"{pct}%")
            self._append_log("Concluído: " + label)
            if "embeddings" in label.casefold():
                self.subprogress.hide()
                self.subprogress_label.hide()
        elif kind == "subprogress":
            done = int(event.get("completed", 0))
            total = max(1, int(event.get("total", 1)))
            pct = int(done * 100 / total)
            self.subprogress.setValue(pct)
            self.subprogress_label.setText(f"Lotes do modelo: {done} de {total} ({pct}%)")
        elif kind == "log":
            self._append_log(str(event.get("message", "")))
        elif kind == "table":
            self._show_table(event)
        elif kind == "chart":
            self.chart_paths.append(Path(event["path"]))
            self._add_chart(Path(event["path"]), str(event.get("title", "Gráfico")))
            self._append_log("Gráfico calculado e salvo: " + Path(event["path"]).name)
        elif kind == "warning":
            message = str(event.get("message", ""))
            self._append_log("ATENÇÃO: " + message)
            self.status_label.setText("Uma etapa opcional sinalizou aviso; consulte o registro.")
        elif kind == "fatal_error":
            self.last_error = str(event.get("traceback", ""))
            self._append_log("ERRO na etapa " + str(event.get("stage", "")))
            self._append_log(self.last_error[-5000:])
            self.status_label.setText("A execução parou; veja o erro no registro.")
        elif kind == "run_completed":
            self.outputs = [Path(p) for p in event.get("outputs", [])]
            self.main_progress.setValue(100)
            self.progress_percent.setText("100%")
            self.status_label.setText("Análise concluída; arquivos salvos.")
            self._append_log("Execução concluída. Os CSVs e gráficos estão na pasta selecionada.")
            self._refresh_outputs()
            self.tabs.setCurrentIndex(1 if self.chart_paths else 2)
        elif kind == "worker_error":
            self.last_error = str(event.get("traceback", event.get("message", "")))
            self._append_log("Falha: " + str(event.get("message", "Erro sem detalhe")))
            if self.last_error:
                self._append_log(self.last_error[-5000:])
            self.status_label.setText("Não foi possível concluir a execução.")
        elif kind == "run_cancelled":
            self.status_label.setText("Execução cancelada pelo usuário.")
            self._append_log("A análise foi interrompida em um ponto seguro entre etapas ou lotes.")

    def _set_step(self, label: str, state: str) -> None:
        for row in range(self.step_list.count()):
            item = self.step_list.item(row)
            name = str(item.data(Qt.ItemDataRole.UserRole))
            if name == label:
                icon = "✓" if state == "done" else "●"
                item.setText(f"{icon}   {name}")
                item.setForeground(Qt.GlobalColor.darkGreen if state == "done" else Qt.GlobalColor.blue)
                if state == "active":
                    self.step_list.setCurrentItem(item)
                return

    def _update_steps(self) -> None:
        for row in range(self.step_list.count()):
            item = self.step_list.item(row)
            name = str(item.data(Qt.ItemDataRole.UserRole))
            if row >= self.stage_index:
                item.setText("○   " + name)
                item.setForeground(Qt.GlobalColor.gray)

    def _animate_status(self) -> None:
        self.animation_frame = (self.animation_frame + 1) % 4
        dots = "." * self.animation_frame
        base = self.status_label.text().rstrip(".")
        if base and not base.startswith("Análise concluída") and not base.startswith("A execução parou"):
            self.status_label.setText(base + dots)

    def _append_log(self, message: str) -> None:
        if message:
            self.log_view.append(message.replace("\x00", ""))

    def _show_table(self, event: dict) -> None:
        columns = [str(c) for c in event.get("columns", [])]
        rows = event.get("rows", [])
        if not columns:
            return
        self.preview_table.clear()
        self.preview_table.setColumnCount(len(columns))
        self.preview_table.setHorizontalHeaderLabels(columns)
        self.preview_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, col in enumerate(columns):
                value = row.get(col)
                cell = QTableWidgetItem("" if value is None else str(value))
                self.preview_table.setItem(r, c, cell)
        count = int(event.get("row_count", len(rows)))
        self.preview_table.setToolTip(f"Exibindo uma prévia de {len(rows)} de {count} linhas")
        self.tabs.setTabText(3, f"Prévia ({count})")

    def _add_chart(self, path: Path, title: str) -> None:
        if not path.is_file():
            return
        card = QFrame()
        card.setObjectName("Panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel(title)
        label.setStyleSheet(f"font-weight:700;color:{PALETTE['navy']};")
        image = QLabel()
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(str(path))
        image.setPixmap(pix.scaled(QSize(520, 300), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(label)
        layout.addWidget(image)
        row = self.chart_grid.count() // 2
        col = self.chart_grid.count() % 2
        self.chart_grid.addWidget(card, row, col)
        self.tabs.setCurrentIndex(1)

    def _refresh_outputs(self) -> None:
        self.output_list.clear()
        for path in self.outputs:
            item = QListWidgetItem(f"✓   {path.name}  —  {path.stat().st_size / 1024:.0f} KB")
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            self.output_list.addItem(item)
        if self.output_dir:
            charts = self.output_dir / "graficos"
            if charts.is_dir():
                for path in sorted(charts.glob("*.png")):
                    item = QListWidgetItem(f"▧   {path.name}  —  PNG")
                    item.setData(Qt.ItemDataRole.UserRole, str(path))
                    self.output_list.addItem(item)
        self.output_list.itemDoubleClicked.connect(self._open_output_item)

    def _open_output_item(self, item: QListWidgetItem) -> None:
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _cancel_run(self) -> None:
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return
        answer = QMessageBox.question(
            self,
            "Cancelar execução",
            "Deseja interromper a análise? Os arquivos exportados podem ficar incompletos se a interrupção ocorrer durante a gravação.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.status_label.setText("Interrompendo a análise…")
            if self.cancel_file is not None:
                self.cancel_file.write_text("cancel", encoding="utf-8")
            self.cancel_button.setEnabled(False)

    def _process_error(self, _error) -> None:
        self._append_log("Erro ao iniciar o processo: " + self.process.errorString())
        self.status_label.setText("Falha ao iniciar o processamento.")
        self._finish_ui()

    def _process_finished(self, exit_code: int, _exit_status) -> None:
        self._poll_event_file()
        self._read_stdout()
        self._read_stderr()
        self.animation_timer.stop()
        self.event_timer.stop()
        if exit_code == 0 and self.outputs:
            self.status_label.setText("Análise concluída; arquivos salvos.")
            QMessageBox.information(self, "Concluído", "A análise terminou. Os três CSVs e os gráficos estão na pasta selecionada.")
        elif not self.status_label.text().startswith(("A execução parou", "Execução cancelada")):
            self.status_label.setText("Execução encerrada sem concluir; veja o registro.")
        self._finish_ui()

    def _finish_ui(self) -> None:
        self.animation_timer.stop()
        self.event_timer.stop()
        if self.process.state() == QProcess.ProcessState.NotRunning:
            if self.event_file is not None:
                self.event_file.unlink(missing_ok=True)
            if self.cancel_file is not None:
                self.cancel_file.unlink(missing_ok=True)
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._refresh_model_badge()

    def closeEvent(self, event) -> None:
        if self.process.state() != QProcess.ProcessState.NotRunning:
            answer = QMessageBox.question(
                self,
                "Execução em andamento",
                "A análise ainda está rodando. Fechar o aplicativo interromperá o processo. Deseja sair mesmo assim?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.process.kill()
            self.process.waitForFinished(2000)
        event.accept()


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        return run_worker_from_cli(sys.argv)
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication(sys.argv)
    app.setApplicationName("PMAC | Análise de Formação e Unidade")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_QSS)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
