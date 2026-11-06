# PyInstaller onedir. Modelo, notebook e identidade ficam como recursos editáveis
# ao lado do executável, para uso offline e atualização/verificação independente.
from PyInstaller.utils.hooks import collect_all

packages = [
    "PySide6",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "openpyxl",
    "xlrd",
    "sklearn",
    "scipy",
    "sentence_transformers",
    "transformers",
    "huggingface_hub",
    "tokenizers",
    "safetensors",
    "torch",
]

datas = []
binaries = []
hiddenimports = ["sentence_transformers.sentence_transformer.model"]
for package in packages:
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["IPython", "jupyter", "notebook", "pytest", "tkinter"],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PMAC-Analise-Formacao",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon="assets/pmac.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PMAC-Analise-Formacao",
)
