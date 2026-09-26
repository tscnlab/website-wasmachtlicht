"""Recreate website assets from the supplied originals; no image generation.

Run with the bundled Python (Pillow) or another Python with Pillow installed:
  python3 scripts/prepare-brand-assets.py /path/to/roadshow-project

Requires Ghostscript (`gs`) for EPS rasterisation. Quarto builds use the
already prepared assets and do not require this script or the originals.
"""
import argparse
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

parser = argparse.ArgumentParser()
parser.add_argument("source_project", type=Path)
parser.add_argument("--font", type=Path, default=Path.home() / "Library/Fonts/Roboto-VariableFont_wdth,wght.ttf")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
material = args.source_project / "21 Freigabe Layout/3405_Max-Planck_Roadshow/01_Material"
logos = root / "assets/logos"
logos.mkdir(parents=True, exist_ok=True)


def source(name):
    matches = list(material.rglob(name))
    if len(matches) != 1:
        raise ValueError(f"Expected one source for {name}, found {len(matches)}")
    return matches[0]


for output, original in {
    "mpf-de.png": "MPF_Logo_de_cmyk.eps",
    "mpf-en.png": "MPF_Logo_en_cmyk.eps",
    "mpi-de.png": "MPI_Logo_DE_1-zeilig_breit_CMYK_Kybernetik_mpg_green.eps",
    "mpi-en.png": "MPI_Logo_EN_one-line_wide_CMYK_Cybernetics_mpg_green.eps",
}.items():
    subprocess.run([
        "gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dEPSCrop",
        "-sDEVICE=pngalpha", "-r288", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
        f"-sOutputFile={logos / output}", str(source(original)),
    ], check=True)

# Keep the supplied RGB logo unchanged, including its internal clear space.
shutil.copyfile(source("MPG_Logo_RGB_mpg-green.png"), logos / "mps.png")

photograph = args.source_project / "32 Fotos Verena/Fuer Nextcloud/Nachtmensch_oder_Frühaufsteher_40.jpg"
with Image.open(photograph) as original:
    image = ImageOps.exif_transpose(original)
    image.thumbnail((2400, 2400))
    image.save(root / "assets/roadshow-verena-mueller.webp", quality=90)

fonts = root / "assets/fonts"
fonts.mkdir(parents=True, exist_ok=True)
shutil.copyfile(args.font, fonts / "Roboto-Variable.ttf")
print("Prepared four language-specific logos, the supplied MPS logo, the roadshow photograph and Roboto.")
