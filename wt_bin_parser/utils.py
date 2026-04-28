import os
import sys
from argparse import ArgumentParser

SUPPORTED_FILE_TYPES = ".bin|.blk"
DEFAULT_OUTPUT_PATH = "./output.json"


def get_byte_gen(bytes_data):
    index = 0
    while index < len(bytes_data):
        yield bytes_data[index]
        index += 1


def read_7bit_encoded_int(gen):
    result = 0
    shift = 0
    while True:
        byte_value = next(gen)
        result |= (byte_value & 0x7F) << shift
        shift += 7

        if not byte_value & 0x80:
            break

    return result


def read_c_string(gen):
    result = bytearray()
    while True:
        byte_value = next(gen)
        if not byte_value or byte_value == b"\0":
            break
        result.append(byte_value)
    return result.decode("utf-8")


def read_bytes(length, gen):
    result = bytearray()
    for _ in range(0, length):
        result.append(next(gen))
    return result


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        dest="input_file_name",
        help=f"Input ({SUPPORTED_FILE_TYPES}) file path.",
        metavar="FILE",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file_name",
        help=f"Output file path.",
        metavar="FILE",
        required=False,
        default=DEFAULT_OUTPUT_PATH,
    )

    return parser.parse_args()


def read_input_file(input_file_path):

    if not os.path.exists(input_file_path):
        print(f"Input file {input_file_path} not found!")
        quit()

    _, file_extension = os.path.splitext(input_file_path)

    if not file_extension in SUPPORTED_FILE_TYPES.split("|"):
        print(f"Unsupported file type {file_extension}!")
        quit()

    with open(input_file_path, "rb") as file:
        return file.read()
