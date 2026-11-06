from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis_runtime import EXPECTED_OUTPUTS, run_notebook


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", dtype_backend="numpy_nullable")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara a execução desktop com saídas de referência do notebook.")
    parser.add_argument("--input", required=True, help="Base usada para produzir os CSVs de referência")
    parser.add_argument("--expected-dir", required=True, help="Diretório com os três CSVs originais de referência")
    parser.add_argument("--output-dir", help="Diretório para a nova execução; se omitido, usa pasta temporária")
    parser.add_argument("--skip-embeddings", action="store_true")
    args = parser.parse_args()
    expected_dir = Path(args.expected_dir).resolve()
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        run_notebook(args.input, output_dir, True, not args.skip_embeddings)
        ephemeral = False
    else:
        temporary = tempfile.TemporaryDirectory(prefix="pmac-parity-")
        output_dir = Path(temporary.name)
        run_notebook(args.input, output_dir, True, not args.skip_embeddings)
        ephemeral = True

    failures: list[str] = []
    for name in EXPECTED_OUTPUTS:
        actual_path = output_dir / name
        expected_path = expected_dir / name
        if not actual_path.is_file() or not expected_path.is_file():
            failures.append(f"{name}: arquivo ausente (atual={actual_path.exists()}, referência={expected_path.exists()})")
            continue
        actual = read_csv(actual_path)
        expected = read_csv(expected_path)
        try:
            assert_frame_equal(actual, expected, check_dtype=False, check_exact=False, rtol=0, atol=1e-4)
            print(f"OK  {name}: {len(actual)} linhas, {len(actual.columns)} colunas, valores equivalentes")
        except AssertionError as exc:
            failures.append(f"{name}: diferença encontrada\n{exc}")

    if failures:
        print("\nFALHA DE PARIDADE\n" + "\n\n".join(failures))
        raise SystemExit(1)
    print("\nPARIDADE CONFIRMADA para os três arquivos.")
    if ephemeral:
        temporary.cleanup()


if __name__ == "__main__":
    main()
