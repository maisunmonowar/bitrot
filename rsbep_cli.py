"""Portable file wrapper for the legacy rsbep command-line encoder."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from typing import BinaryIO, Callable, List, Optional


MAGIC = b"MAGIC_TTSIOD_RS"
DATA_SIZE = 223
CODE_SIZE = 255
BEP_SIZE = 4080
ENCODED_GROUP_SIZE = CODE_SIZE * BEP_SIZE
DECODED_GROUP_SIZE = DATA_SIZE * BEP_SIZE


class RecoveryError(ValueError):
    """Raised when the legacy encoder cannot safely recover a stream."""


def find_rsbep(executable: Optional[str] = None) -> str:
    if executable:
        return executable

    program_name = "rsbep.exe" if os.name == "nt" else "rsbep"
    packaged_executable = os.path.join(os.path.dirname(__file__), "bin", program_name)
    if os.path.isfile(packaged_executable):
        return packaged_executable

    path_executable = shutil.which("rsbep")
    if path_executable:
        return path_executable
    raise FileNotFoundError(
        "rsbep executable not found; build it from rsbep-backup or pass --rsbep"
    )


def _write_atomically(destination_path: str, writer: Callable[[BinaryIO], None]) -> None:
    destination_path = os.path.abspath(destination_path)
    output_dir = os.path.dirname(destination_path)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=output_dir, delete=False) as output:
            temporary_path = output.name
            writer(output)
        os.replace(temporary_path, destination_path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


def _copy_exact(source: BinaryIO, destination: BinaryIO, size: int) -> None:
    remaining = size
    while remaining:
        chunk = source.read(min(1024 * 1024, remaining))
        if not chunk:
            raise OSError("input file changed or ended unexpectedly")
        destination.write(chunk)
        remaining -= len(chunk)
    if source.read(1):
        raise OSError("input file grew while it was being processed")


def _copy_payload(source: BinaryIO, destination: BinaryIO, size: int) -> None:
    remaining = size
    while remaining:
        chunk = source.read(min(1024 * 1024, remaining))
        if not chunk:
            raise RecoveryError("decoded payload ended unexpectedly")
        destination.write(chunk)
        remaining -= len(chunk)


def _run_rsbep(
    executable: str,
    arguments: List[str],
    source: BinaryIO,
    destination: BinaryIO,
) -> None:
    result = subprocess.run(
        [executable, *arguments],
        stdin=source,
        stdout=destination,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RecoveryError(
            message or f"rsbep exited with status {result.returncode}"
        )


def freeze_file(
    source_path: str,
    destination_path: str,
    executable: Optional[str] = None,
) -> None:
    if os.path.normcase(os.path.abspath(source_path)) == os.path.normcase(
        os.path.abspath(destination_path)
    ):
        raise ValueError("source and destination must be different files")

    source_size = os.path.getsize(source_path)
    rsbep = find_rsbep(executable)

    def encode(destination: BinaryIO) -> None:
        with tempfile.TemporaryFile(mode="w+b") as encoded_input:
            encoded_input.write(MAGIC + b"\n" + str(source_size).encode("ascii") + b"\n")
            with open(source_path, "rb") as source:
                _copy_exact(source, encoded_input, source_size)
            encoded_input.seek(0)
            _run_rsbep(
                rsbep,
                ["-B", str(CODE_SIZE), "-D", str(DATA_SIZE), "-R", str(BEP_SIZE)],
                encoded_input,
                destination,
            )

    _write_atomically(destination_path, encode)


def _copy_recovered_payload(decoded: BinaryIO, destination: BinaryIO) -> None:
    decoded.seek(0)
    magic_line = decoded.readline(len(MAGIC) + 2)
    if not magic_line.endswith(b"\n"):
        raise RecoveryError("recovered stream has a truncated signature")
    signature = magic_line[:-2] if magic_line.endswith(b"\r\n") else magic_line[:-1]
    if signature != MAGIC:
        raise RecoveryError("recovered stream has an invalid or missing signature")

    size_line = decoded.readline(32)
    if not size_line.endswith(b"\n"):
        raise RecoveryError("recovered stream has a truncated size header")
    size_text = size_line[:-1].rstrip(b"\r")
    if not size_text or not size_text.isdigit():
        raise RecoveryError("recovered stream contains an invalid size header")

    payload_size = int(size_text)
    payload_offset = decoded.tell()
    decoded_size = os.fstat(decoded.fileno()).st_size
    if payload_size > decoded_size - payload_offset:
        raise RecoveryError("encoded input is truncated before the full payload")

    decoded.seek(payload_offset + payload_size)
    while True:
        trailing = decoded.read(1024 * 1024)
        if not trailing:
            break
        if any(trailing):
            raise RecoveryError("recovered stream contains invalid nonzero padding")

    decoded.seek(payload_offset)
    _copy_payload(decoded, destination, payload_size)


def melt_file(
    source_path: str,
    destination_path: str,
    executable: Optional[str] = None,
) -> None:
    if os.path.normcase(os.path.abspath(source_path)) == os.path.normcase(
        os.path.abspath(destination_path)
    ):
        raise ValueError("source and destination must be different files")

    source_size = os.path.getsize(source_path)
    if source_size == 0 or source_size % ENCODED_GROUP_SIZE:
        raise RecoveryError(
            f"encoded input must contain complete {ENCODED_GROUP_SIZE}-byte groups"
        )
    rsbep = find_rsbep(executable)

    def decode(destination: BinaryIO) -> None:
        with tempfile.TemporaryFile(mode="w+b") as decoded:
            with open(source_path, "rb") as source:
                _run_rsbep(
                    rsbep,
                    ["-d", "-B", str(CODE_SIZE), "-D", str(DATA_SIZE), "-R", str(BEP_SIZE)],
                    source,
                    decoded,
                )
            _copy_recovered_payload(decoded, destination)

    _write_atomically(destination_path, decode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Encode or recover files with the platform's rsbep executable."
    )
    parser.add_argument("--rsbep", help="path to the rsbep executable")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("freeze", "encode a file"),
        ("melt", "recover a file"),
    ):
        command_parser = subparsers.add_parser(command, help=help_text)
        command_parser.add_argument("source", help="input file")
        command_parser.add_argument("destination", help="output file")

    args = parser.parse_args()
    try:
        if args.command == "freeze":
            freeze_file(args.source, args.destination, args.rsbep)
        else:
            melt_file(args.source, args.destination, args.rsbep)
    except (OSError, RecoveryError, ValueError) as error:
        print(f"rsbep: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
