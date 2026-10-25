import os
import subprocess
import tempfile
import unittest

import rsbep_cli


def available_rsbep():
    try:
        rsbep_cli.find_rsbep()
        return True
    except FileNotFoundError:
        return False


class RecoveredPayloadTests(unittest.TestCase):
    def test_valid_header_and_payload_are_copied(self):
        with tempfile.TemporaryFile(mode="w+b") as decoded:
            decoded.write(rsbep_cli.MAGIC + b"\n5\nhello" + b"\0" * 20)
            decoded.seek(0)
            with tempfile.TemporaryFile(mode="w+b") as destination:
                rsbep_cli._copy_recovered_payload(decoded, destination)

                destination.seek(0)
                self.assertEqual(destination.read(), b"hello")

    def test_truncated_payload_is_rejected_before_writing(self):
        with tempfile.TemporaryFile(mode="w+b") as decoded:
            decoded.write(rsbep_cli.MAGIC + b"\n10\nshort")
            decoded.seek(0)
            with tempfile.TemporaryFile(mode="w+b") as destination:
                with self.assertRaisesRegex(rsbep_cli.RecoveryError, "truncated"):
                    rsbep_cli._copy_recovered_payload(decoded, destination)

                destination.seek(0)
                self.assertEqual(destination.read(), b"")

    def test_nonzero_padding_is_rejected_before_writing(self):
        with tempfile.TemporaryFile(mode="w+b") as decoded:
            decoded.write(rsbep_cli.MAGIC + b"\n5\nhello\0bad")
            decoded.seek(0)
            with tempfile.TemporaryFile(mode="w+b") as destination:
                with self.assertRaisesRegex(rsbep_cli.RecoveryError, "padding"):
                    rsbep_cli._copy_recovered_payload(decoded, destination)

                destination.seek(0)
                self.assertEqual(destination.read(), b"")

    def test_missing_executable_is_reported_without_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source_path = os.path.join(directory, "source file.bin")
            destination_path = os.path.join(directory, "output file.frozen")
            with open(source_path, "wb") as source:
                source.write(b"payload")

            with self.assertRaises(FileNotFoundError):
                rsbep_cli.freeze_file(
                    source_path,
                    destination_path,
                    os.path.join(directory, "missing-rsbep"),
                )

            self.assertFalse(os.path.exists(destination_path))


@unittest.skipUnless(
    available_rsbep(),
    "native rsbep executable unavailable; skipping recovery integration tests",
)
class NativeRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.executable = rsbep_cli.find_rsbep()
        self.source_path = os.path.join(self.temp_dir.name, "source with spaces ü.bin")
        self.encoded_path = os.path.join(
            self.temp_dir.name, "source with spaces ü.frozen"
        )
        self.destination_path = os.path.join(
            self.temp_dir.name, "recovered with spaces ü.bin"
        )
        with open(self.source_path, "wb") as source:
            source.write(b"interoperable \r\n\x1a\x00 payload\x00" * 20)
        rsbep_cli.freeze_file(self.source_path, self.encoded_path, self.executable)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_uncorrupted_round_trip(self):
        rsbep_cli.melt_file(
            self.encoded_path, self.destination_path, self.executable
        )

        with open(self.destination_path, "rb") as recovered:
            with open(self.source_path, "rb") as original:
                self.assertEqual(recovered.read(), original.read())

    def test_correctable_corruption_round_trip(self):
        with open(self.encoded_path, "r+b") as encoded:
            for column in range(16):
                position = column * rsbep_cli.BEP_SIZE
                encoded.seek(position)
                value = encoded.read(1)
                encoded.seek(position)
                encoded.write(bytes([value[0] ^ (column + 1)]))

        rsbep_cli.melt_file(
            self.encoded_path, self.destination_path, self.executable
        )

        with open(self.destination_path, "rb") as recovered:
            with open(self.source_path, "rb") as original:
                self.assertEqual(recovered.read(), original.read())

    def test_uncorrectable_corruption_fails_without_replacing_destination(self):
        with open(self.encoded_path, "r+b") as encoded:
            for column in range(17):
                position = column * rsbep_cli.BEP_SIZE
                encoded.seek(position)
                value = encoded.read(1)
                encoded.seek(position)
                encoded.write(bytes([value[0] ^ (column + 1)]))
        with open(self.destination_path, "wb") as destination:
            destination.write(b"previous recovered file")

        with self.assertRaises(rsbep_cli.RecoveryError):
            rsbep_cli.melt_file(
                self.encoded_path, self.destination_path, self.executable
            )

        with open(self.destination_path, "rb") as destination:
            self.assertEqual(destination.read(), b"previous recovered file")

    def test_truncated_encoded_input_fails(self):
        with open(self.encoded_path, "r+b") as encoded:
            encoded.truncate(os.path.getsize(self.encoded_path) - 1)

        with self.assertRaisesRegex(rsbep_cli.RecoveryError, "complete"):
            rsbep_cli.melt_file(
                self.encoded_path, self.destination_path, self.executable
            )

    def test_c_decoder_returns_nonzero_for_truncated_group(self):
        with open(self.encoded_path, "rb") as encoded:
            truncated = encoded.read()[:-1]
        result = subprocess.run(
            [
                self.executable,
                "-d",
                "-B",
                str(rsbep_cli.CODE_SIZE),
                "-D",
                str(rsbep_cli.DATA_SIZE),
                "-R",
                str(rsbep_cli.BEP_SIZE),
            ],
            input=truncated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
