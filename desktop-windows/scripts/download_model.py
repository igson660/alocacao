from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from huggingface_hub import snapshot_download

MODEL_ID = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara o modelo local para distribuição offline.")
    parser.add_argument("--target", default="models/paraphrase-multilingual-MiniLM-L12-v2")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    snapshot_download(
        repo_id=MODEL_ID,
        revision=REVISION,
        local_dir=str(target),
        allow_patterns=[
            "1_Pooling/**",
            "config.json",
            "config_sentence_transformers.json",
            "model.safetensors",
            "modules.json",
            "sentence_bert_config.json",
            "special_tokens_map.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "README.md",
            "LICENSE*",
        ],
        ignore_patterns=["*.msgpack", "flax_model.*", "tf_model.h5", ".gitattributes"],
    )
    required = [target / "model.safetensors", target / "modules.json", target / "config.json"]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit("Modelo incompleto; arquivos ausentes: " + ", ".join(missing))
    print(f"Modelo instalado em: {target}")
    print(f"Revisão imutável: {REVISION}")
    print(f"Tamanho: {sum(p.stat().st_size for p in target.rglob('*') if p.is_file()) / (1024**2):.1f} MiB")


if __name__ == "__main__":
    main()
