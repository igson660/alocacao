from __future__ import annotations

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from main import MainWindow


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "tests" / "fixtures" / "mini_pmac.csv"
    if not source.is_file():
        raise SystemExit(f"Fixture ausente: {source}")
    temp = tempfile.TemporaryDirectory(prefix="pmac-ui-smoke-")
    output = Path(temp.name) / "outputs"
    app = QApplication(sys.argv)
    QMessageBox.information = staticmethod(lambda *_args, **_kwargs: QMessageBox.StandardButton.Ok)
    QMessageBox.question = staticmethod(lambda *_args, **_kwargs: QMessageBox.StandardButton.No)
    window = MainWindow()
    window.input_path = source
    window.output_dir = output
    window.input_label.setText(source.name)
    window.output_label.setText(str(output))
    window.tfidf_check.setChecked(True)
    run_embeddings = os.environ.get("PMAC_SMOKE_EMBEDDINGS", "0") == "1"
    window.embedding_check.setChecked(run_embeddings)
    window.show()
    window.process.finished.connect(lambda *_args: QTimer.singleShot(250, app.quit))
    timeout = QTimer()
    timeout.setSingleShot(True)
    timeout.timeout.connect(app.quit)
    timeout.start(120_000)
    QTimer.singleShot(100, window._start_run)
    app.exec()
    if window.process.state().name != "NotRunning":
        window.process.kill()
        window.process.waitForFinished(3000)
        raise SystemExit("Worker da interface não encerrou no tempo esperado.")
    if len(window.outputs) != 3:
        raise SystemExit(f"A interface recebeu {len(window.outputs)} CSVs, esperado: 3.")
    if not window.chart_paths:
        raise SystemExit("A interface não recebeu os gráficos.")
    if window.main_progress.value() != 100:
        raise SystemExit(f"Progresso final incorreto: {window.main_progress.value()}%.")
    if run_embeddings and window.subprogress.value() != 100:
        raise SystemExit(f"Progresso dos embeddings incorreto: {window.subprogress.value()}%.")
    print(f"UI smoke test aprovado: {len(window.outputs)} CSVs, {len(window.chart_paths)} gráficos, progresso {window.main_progress.value()}%.")
    window.close()
    temp.cleanup()


if __name__ == "__main__":
    main()
