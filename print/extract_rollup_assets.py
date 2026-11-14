#!/usr/bin/env python3
"""Recover campaign fonts and the original vector MPI mark from supplied artwork.

The SVG embeds Liberation Sans; the A5 PDF preserves the MPI mark as paths.
Source reads time out after eight seconds to avoid hanging on cloud placeholders.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

from pypdf import PdfReader, PdfWriter, PageObject
from pypdf.generic import ContentStream, DecodedStreamObject, NameObject

ROOT = Path(__file__).resolve().parents[1]
ROLLUP = Path('/Users/mspitschan/Library/CloudStorage/OneDrive-TUM/Projects/Light therapy in the community/06 Promotional - Codex/rollup')
MM = 72 / 25.4


def bounded_read(path: Path) -> bytes:
    return subprocess.run(['/bin/cat', str(path)], capture_output=True,
                          timeout=8, check=True).stdout


def font_names(data: bytes) -> dict[int, str]:
    count = struct.unpack_from('>H', data, 4)[0]
    names = {}
    for i in range(count):
        tag, _, offset, _ = struct.unpack_from('>4sIII', data, 12 + 16 * i)
        if tag != b'name':
            continue
        _, n, storage = struct.unpack_from('>HHH', data, offset)
        for j in range(n):
            platform, _, _, name_id, length, at = struct.unpack_from(
                '>HHHHHH', data, offset + 6 + 12 * j)
            if name_id in (0, 1, 2, 8, 9, 13, 14) and (platform == 3 or name_id not in names):
                raw = data[offset + storage + at:offset + storage + at + length]
                names[name_id] = raw.decode('utf-16-be' if platform in (0, 3)
                                           else 'mac_roman', errors='replace')
    return names


def extract_fonts(source: Path, out: Path, license_source: Path) -> dict:
    svg = bounded_read(source).decode('utf-8')
    matches = re.findall(
        r'@font-face\{font-family:Campaign;font-weight:(400|700);src:url\(data:font/ttf;base64,([A-Za-z0-9+/=]+)\)', svg)
    assert len(matches) == 2 and {weight for weight, _ in matches} == {'400', '700'}
    info = {}
    license_lines = ['Liberation Sans - embedded font provenance and license metadata',
                     'Source: ' + str(source),
                     'Font bytes extracted without alteration from inline @font-face declarations.', '']
    for weight, encoded in matches:
        data = base64.b64decode(encoded, validate=True)
        names = font_names(data)
        style = 'Regular' if weight == '400' else 'Bold'
        assert names[1] == 'Liberation Sans' and names[2] == style
        filename = f'LiberationSans-{style}.ttf'
        (out / filename).write_bytes(data)
        info[filename] = {'sha256': hashlib.sha256(data).hexdigest(),
                          'bytes': len(data), 'embedded_name_records': names}
        license_lines += [filename]
        license_lines += [f'{key}: {names[key]}' for key in (0, 1, 2, 8, 9, 13, 14) if key in names]
        license_lines += ['']
    source_license = bounded_read(license_source).decode('utf-8')
    start = source_license.index('\n# SIL Open Font\n')
    end = source_license.index('\n# ', start + 2)
    ofl = source_license[start:end].strip()
    assert 'License Version 1.1' in ofl
    license_lines += ['Full license reproduced from: ' + str(license_source), '', ofl]
    (out / 'FONT-LICENSE.txt').write_text('\n'.join(license_lines) + '\n')
    return info


def extract_logo(source: Path, out: Path) -> dict:
    reader = PdfReader(source)
    source_page = reader.pages[0]
    content = ContentStream(source_page.get_contents(), reader)
    operations = content.operations
    start = next(i for i, (_, op) in enumerate(operations) if op == b'q')
    matrix, op = operations[start + 1]
    assert op == b'cm' and abs(float(matrix[0]) - .326667) < 1e-8
    assert [float(matrix[4]), float(matrix[5])] == [445.0, 939.1486]
    depth = 0
    for end in range(start, len(operations)):
        op = operations[end][1]
        depth += (op == b'q') - (op == b'Q')
        if depth == 0:
            break
    else:
        raise ValueError('Unbalanced logo graphics state')
    selected = operations[start:end + 1]
    assert not any(op in (b'Do', b'BI', b'INLINE IMAGE', b'Tj', b'TJ') for _, op in selected)
    group = ContentStream(None, reader)
    group.operations = selected

    # The A5 artwork uses a 0.566929-point design unit (0.2 mm).
    # Clip before translation so the output is an exact 49 x 16.97028 mm asset.
    x, y, width, height = 89 * MM, 187.82972 * MM, 49 * MM, 16.97028 * MM
    prefix = (f'q\n0 0 {width:.12f} {height:.12f} re W n\n'
              f'1 0 0 1 {-x:.12f} {-y:.12f} cm\n'
              '0.566929 0 0 0.566929 0 0 cm\n').encode('ascii')
    stream = DecodedStreamObject()
    stream.set_data(prefix + group.get_data() + b'\nQ\n')
    page = PageObject.create_blank_page(width=width, height=height)
    page[NameObject('/Contents')] = stream
    page[NameObject('/Resources')] = source_page['/Resources']
    writer = PdfWriter()
    writer.add_page(page)
    writer.add_metadata({'/Title': 'Max-Planck-Institut für biologische Kybernetik - vector logo',
                         '/Subject': 'Original vector paths isolated from supplied A5 campaign flyer; transparent background.'})
    target = out / 'mpi-logo.pdf'
    with target.open('wb') as output:
        writer.write(output)
    check = PdfReader(target).pages[0]
    assert not list(check.images)
    return {'source': str(source), 'source_operation_range_inclusive': [start, end],
            'size_mm': [49, 16.97028], 'transparent_background': True,
            'vector_paths_only': True, 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rollup-svg', type=Path, default=ROLLUP / 'output/v9/editable/lichtcafe-rollup-gelb-80x200-ENTWURF.svg')
    parser.add_argument('--a5-pdf', type=Path, default=ROOT / 'print/assets/source-lichtmobil-projekt-a5.pdf')
    parser.add_argument('--font-license', type=Path, default=ROLLUP / 'assets/fonts/LibreOffice-LICENSE.txt')
    parser.add_argument('--output', type=Path, default=ROOT / 'print/assets')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    fonts = extract_fonts(args.rollup_svg, args.output, args.font_license)
    logo = extract_logo(args.a5_pdf, args.output)
    provenance = {'fonts': {'source': str(args.rollup_svg), 'license_source': str(args.font_license), 'files': fonts}, 'mpi-logo.pdf': logo}
    (args.output / 'asset-provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'files': list(fonts) + ['mpi-logo.pdf', 'FONT-LICENSE.txt', 'asset-provenance.json'],
                      'logo_size_mm': logo['size_mm']}, indent=2))


if __name__ == '__main__':
    main()
