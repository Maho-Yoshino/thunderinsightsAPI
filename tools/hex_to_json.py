import argparse, struct
from sys import stderr, stdin, stdout, exit as _exit
from lz4.block import decompress as lz4_decompress
from bz2 import decompress as bz2_decompress
from subprocess import run as run_process
from pathlib import Path

def print_err(message):
	print(message, file=stderr)

def read_input_bytes() -> bytes:
	raw_data = stdin.buffer.read()

	stripped = b''.join(raw_data.split())
	try:
		decoded = bytes.fromhex(stripped.decode('ascii'))
	except (ValueError, UnicodeDecodeError):
		return raw_data

	return decoded

def lz4_decompress_try(data) -> None|bytes:
	if len(data) < 4:
		print_err("[-] LZ4 data is too short to contain a size header.")
		return None

	candidates = []

	# Standard lz4 frame with 0x4C marker byte
	if data[:1] == b'\x4c':
		if len(data) < 5:
			return None
		candidates.append(("marker+size", struct.unpack('>I', data[1:5])[0], data[5:]))

	# Game wire format: [4-byte BE uncompressed size][raw lz4hc block]
	if not candidates:
		be_size = struct.unpack('>I', data[:4])[0]
		# Sanity check: decompressed size should be between 100 and 100MB
		if 100 <= be_size <= 100 * 1024 * 1024 and len(data) > 4:
			candidates.append(("be-size prefix", be_size, data[4:]))

	for label, uncompressed_size, compressed_payload in candidates:
		try:
			print_err(f"[*] Trying LZ4 {label}; potential uncompressed size: {uncompressed_size}")
			return lz4_decompress(compressed_payload, uncompressed_size=uncompressed_size)
		except Exception as e:
			print_err(f"[-] LZ4 {label} decompression failed: {e}")

	return None

def bzip_decompress_try(data) -> None|bytes:
	offset = data[:20].find(b'BZh')
	if offset == -1:
		offset = 0

	try:
		return bz2_decompress(data[offset:])
	except Exception as e:
		print_err(f"[-] BZip2 decompression failed: {e}")
		return None

def main(wt_ext_cli_path=None):
	if wt_ext_cli_path is None:
		script_dir = Path(__file__).resolve().parent
		wt_ext_cli = script_dir / 'wt_ext_cli'
	else:
		wt_ext_cli = Path(wt_ext_cli_path)

	if not wt_ext_cli.is_file():
		# Try system-wide fallback
		from shutil import which
		system_cli = which('wt_ext_cli')
		if system_cli:
			wt_ext_cli = Path(system_cli)
		else:
			print_err(
				'Missing dependency: Install wt_ext_cli from '
				'https://github.com/Warthunder-Open-Source-Foundation/wt_ext_cli/releases'
			)
			_exit(1)

	input_data = read_input_bytes()

	decompressed = None
	if b'BZh' in input_data[:20]:
		decompressed = bzip_decompress_try(input_data)
	if decompressed is None:
		decompressed = lz4_decompress_try(input_data)

	payload = decompressed or input_data
	run_process(
		[str(wt_ext_cli), 'unpack_raw_blk', '--stdin', '--stdout', '--format', 'Json'],
		input=payload,
		stdout=stdout,
		stderr=stderr,
	)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Convert hex input to JSON, with decompression for LZ4 and BZip2 formats.'
	)
	parser.add_argument(
		'--wt_ext_cli_path',
		type=str,
		default=None,
		help='Path to wt_ext_cli executable. If not provided, it will look for wt_ext_cli in the "tools" directory.',
		required=False
	)
	args = parser.parse_args()

	main(args.wt_ext_cli_path)
