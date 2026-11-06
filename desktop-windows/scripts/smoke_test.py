from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis_runtime import EXPECTED_OUTPUTS, run_notebook


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="pmac-smoke-") as temp:
        base = Path(temp)
        source = base / "amostra_sintetica.csv"
        output = base / "saidas"
        rows = []
        formations_by_class = {
            "ALTA": ["Segurança Pública", "Enfermagem", "Educação Física", "Segurança Pública", "Enfermagem", "Educação Física"],
            "MODERADA": ["Administração", "Direito", "Administração", "Direito", "Administração", "Direito"],
            "BAIXA": ["Agronomia", "Agronomia", "Agronomia", "Agronomia", "Agronomia", "Agronomia"],
        }
        units = [
            ("BATALHAO DE TRANSITO", "OPERACIONAL"),
            ("HOSPITAL DA POLICIA MILITAR", "ADMINISTRATIVA"),
            ("DIRETORIA DE ENSINO", "ADMINISTRATIVA"),
            ("BATALHAO DE TRANSITO", "OPERACIONAL"),
            ("HOSPITAL DA POLICIA MILITAR", "ADMINISTRATIVA"),
            ("DIRETORIA DE ENSINO", "ADMINISTRATIVA"),
        ]
        for category, formations in formations_by_class.items():
            for index, formation in enumerate(formations):
                unit, unit_type = units[index]
                rows.append({
                    "Grau de Escolaridade": "Ensino Superior Completo",
                    "Área de Formação": formation,
                    "Unidade": unit,
                    "Tipo de Unidade": unit_type,
                })
        with source.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        events = []
        run_notebook(source, output, run_tfidf=True, run_embeddings=False, event_callback=events.append)
        missing = [name for name in EXPECTED_OUTPUTS if not (output / name).is_file()]
        if missing:
            raise SystemExit(f"Saídas faltantes: {missing}")
        if not list((output / "graficos").glob("*.png")):
            raise SystemExit("Nenhum gráfico foi gerado.")
        if not any(e.get("event") == "run_completed" for e in events):
            raise SystemExit("O evento de conclusão não foi recebido.")
        print("Smoke test aprovado:")
        for name in EXPECTED_OUTPUTS:
            print(f"  {name}: {(output / name).stat().st_size:,} bytes")
        print(f"  gráficos: {len(list((output / 'graficos').glob('*.png')))}")


if __name__ == "__main__":
    main()
