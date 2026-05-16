#!/usr/bin/env python3
"""
scale_corridors.py
Amplía los pasillos de un mundo Gazebo (.world / SDF) reescalando las
coordenadas X e Y de los muros por un factor dado, sin alterar grosor,
altura ni rotaciones.

Uso
---
    python3 scale_corridors.py <entrada.world> <salida.world> [factor]

    factor  — multiplicador de distancia (por defecto 1.5)
              Ejemplo: 1.5 → pasillos 50 % más anchos.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

DEFAULT_SCALE = 1.5

# Patrón que captura las 6 componentes de <pose>x y z r p yaw</pose>
_POSE_PATTERN = re.compile(
    r'<pose>\s*'
    r'([-\d.eE+]+)\s+'   # x
    r'([-\d.eE+]+)\s+'   # y
    r'([-\d.eE+]+)\s+'   # z
    r'([-\d.eE+]+)\s+'   # roll
    r'([-\d.eE+]+)\s+'   # pitch
    r'([-\d.eE+]+)'      # yaw
    r'\s*</pose>'
)

# Marcador que delimita el inicio del modelo del laberinto
_MAZE_MARKER = "<model name='mapcorreg'"
_FALLBACK_MARKER = '<state'


# ---------------------------------------------------------------------------
# Lógica principal
# ---------------------------------------------------------------------------

def _scale_xy(match: re.Match, factor: float) -> str:
    """Reemplaza x e y escalados, dejando el resto intacto."""
    vals = [float(match.group(i)) for i in range(1, 7)]
    vals[0] *= factor   # x
    vals[1] *= factor   # y
    formatted = ' '.join(f'{v:g}' for v in vals)
    return f'<pose>{formatted}</pose>'


def scale_world(source: str, factor: float) -> str:
    """
    Aplica el escalado solo a la sección del laberinto dentro del SDF.

    Parámetros
    ----------
    source  : contenido completo del archivo .world
    factor  : multiplicador para las coordenadas XY

    Retorna
    -------
    Cadena con el contenido modificado.
    """
    # Localizar el inicio del modelo del laberinto
    cut = source.find(_MAZE_MARKER)
    if cut == -1:
        cut = source.find(_FALLBACK_MARKER)
    if cut == -1:
        print('[AVISO] No se encontró el modelo del laberinto; se escala todo el archivo.')
        cut = 0

    header  = source[:cut]
    payload = source[cut:]

    scaled_payload = _POSE_PATTERN.sub(
        lambda m: _scale_xy(m, factor),
        payload,
    )
    return header + scaled_payload


# ---------------------------------------------------------------------------
# Entrada de línea de comandos
# ---------------------------------------------------------------------------

def _parse_args() -> tuple[Path, Path, float]:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    src  = Path(sys.argv[1])
    dst  = Path(sys.argv[2])
    fac  = float(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_SCALE
    return src, dst, fac


def main() -> None:
    src, dst, factor = _parse_args()

    content = src.read_text(encoding='utf-8')
    result  = scale_world(content, factor)
    dst.write_text(result, encoding='utf-8')

    pct = (factor - 1) * 100
    print(f'Listo: {src} → {dst}')
    print(f'Factor aplicado: {factor}  ({pct:+.0f} % en anchura de pasillos)')


if __name__ == '__main__':
    main()