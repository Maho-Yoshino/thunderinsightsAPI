#!/usr/bin/env python3
"""Convert JSON to binary BLK, optionally compressed with lz4hc or bzip2.

Reads JSON from stdin, converts to .blkx text, runs through binBlk to produce
binary .blk, and optionally compresses the output in the game's wire format.

Usage:
    python json_to_blk.py [--compress lz4hc|bzip2] [--binblk PATH]
    echo '{"key": "value"}' | python json_to_blk.py --compress lz4hc > out.compr.blk
"""

import argparse, json, struct, sys
from pathlib import Path
from subprocess import run as run_process, PIPE


def print_err(message: str) -> None:
    print(message, file=sys.stderr)


def json_to_blkx(data: dict) -> str:
    """Convert a JSON-compatible dict to BLKX text format lines."""
    lines = []

    for key, value in data.items():
        if value is None:
            continue

        if isinstance(value, bool):
            lines.append(f'{key}:b = {str(value).lower()}')
        elif isinstance(value, int):
            lines.append(f'{key}:i = {value}')
        elif isinstance(value, float):
            # Format float to avoid scientific notation for whole numbers
            if value == int(value) and abs(value) < 1e15:
                lines.append(f'{key}:i = {int(value)}')
            else:
                lines.append(f'{key}:r = {value}')
        elif isinstance(value, str):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'{key}:t = "{escaped}"')
        elif isinstance(value, list):
            # Serialize list as comma-separated string in quotes
            items = []
            for item in value:
                if isinstance(item, str):
                    items.append(item.replace('\\', '\\\\').replace('"', '\\"'))
                else:
                    items.append(str(item))
            joined = ', '.join(items)
            lines.append(f'{key}:t = "{joined}"')
        else:
            print_err(f'[!] Warning: skipping key "{key}" with unsupported type {type(value).__name__}')

    return '\n'.join(lines) + '\n'


def blkx_to_blk(blkx_text: bytes, binblk_path: Path) -> bytes:
    """Convert BLKX text to binary BLK using binBlk."""
    result = run_process(
        [str(binblk_path), '-', '-', '-b'],
        input=blkx_text,
        capture_output=True,
    )
    if result.returncode != 0:
        stderr_msg = result.stderr.decode('utf-8', errors='replace').strip()
        print_err(f'[-] binBlk failed: {stderr_msg}')
        sys.exit(1)
    return result.stdout


def compress_lz4hc(data: bytes) -> bytes:
    """Compress data in the game's wire format: 4-byte BE size + raw lz4hc block."""
    import lz4.block
    compressed = lz4.block.compress(data, mode='high_compression', store_size=False)
    return struct.pack('>I', len(data)) + compressed


def compress_bzip2(data: bytes) -> bytes:
    """Compress data with bzip2."""
    import bz2
    return bz2.compress(data)


def find_binblk(explicit_path: str | None = None) -> Path:
    """Locate the binBlk executable."""
    if explicit_path:
        p = Path(explicit_path)
        if p.is_file():
            return p
        print_err(f'[-] binBlk not found at: {explicit_path}')
        sys.exit(1)

    # Check tools/ directory next to this script
    script_dir = Path(__file__).resolve().parent
    local = script_dir / 'binBlk'
    if local.is_file():
        return local

    # Check PATH
    from shutil import which
    system_bin = which('binBlk') or which('binblk') or which('blkConvert')
    if system_bin:
        return Path(system_bin)

    print_err(
        '[-] Missing binBlk. Place it in the tools/ directory or install it system-wide.\n'
        '    Source: https://github.com/Warthunder-Open-Source-Foundation/wt_ext_cli/releases'
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Convert JSON to binary BLK, optionally compressed.'
    )
    parser.add_argument(
        '--compress',
        choices=('lz4hc', 'bzip2'),
        default=None,
        help='Compression to apply after converting to binary BLK.',
    )
    parser.add_argument(
        '--binblk',
        default=None,
        help='Path to binBlk executable. Auto-detected if not provided.',
    )
    args = parser.parse_args()

    # Read JSON from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print_err(f'[-] Invalid JSON input: {e}')
        sys.exit(1)

    if not isinstance(input_data, dict):
        print_err('[-] JSON input must be an object (dictionary).')
        sys.exit(1)

    # Convert JSON → BLKX text
    blkx_text = json_to_blkx(input_data)
    blkx_bytes = blkx_text.encode('utf-8')

    # Convert BLKX text → binary BLK
    binblk_path = find_binblk(args.binblk)
    blk_binary = blkx_to_blk(blkx_bytes, binblk_path)

    # Optional compression
    if args.compress == 'lz4hc':
        output = compress_lz4hc(blk_binary)
        print_err(f'[*] Compressed {len(blk_binary)} → {len(output)} bytes (lz4hc)')
    elif args.compress == 'bzip2':
        output = compress_bzip2(blk_binary)
        print_err(f'[*] Compressed {len(blk_binary)} → {len(output)} bytes (bzip2)')
    else:
        output = blk_binary
        print_err(f'[*] Binary BLK: {len(output)} bytes (uncompressed)')

    sys.stdout.buffer.write(output)


if __name__ == '__main__':
    main()
