# TODO: Reliability, Documentation, and Future Features

This list is ordered by priority. Each item should be implemented as a focused change with tests and documentation where applicable. Do not run destructive cleanup against personal data without first testing it on disposable fixtures.

## P0 — Data safety and recovery correctness

- [ ] **Make duplicate cleanup preserve a safe copy** ([#8](https://github.com/maisunmonowar/bitrot/issues/8))
  - Review the `--deleteDuplicate` flow in `bitRotChecker.py`.
  - Build and display an explicit deletion plan before deleting anything.
  - Never delete every copy of a checksum group; retain at least one copy and abort if the tool cannot determine a safe choice.
  - Restrict deletion to files inside the requested scan directory, including nested directories.
  - Default to dry-run or confirmation with the exact paths to be deleted.
  - Add tests proving that root-level and nested duplicates are handled safely and that at least one copy remains.

- [ ] **Define whether the garbage list identifies paths or file contents** ([#9](https://github.com/maisunmonowar/bitrot/issues/9))
  - Reconcile the README promise that `--add` marks only one file with `garbageFileCollector.py`, which currently matches by filename, size, and checksum and can therefore match identical files elsewhere.
  - Adopt path-specific marking as the default, or document and expose content-based matching as a separate explicit mode.
  - Ensure cleanup cannot silently expand a single-file request into deletion of other files.
  - Add tests for same-name identical files in different directories, renamed files, and folder-based marking.

- [ ] **Make Reed–Solomon recovery failures explicit** ([#10](https://github.com/maisunmonowar/bitrot/issues/10))
  - Fix the uncorrectable-failure counter in `rsbep-backup/src/rsbep.c`; ensure it increments the counter value rather than advancing the counter pointer.
  - Review decoder behavior for uncorrectable and truncated input so it does not report success or produce a success-shaped recovered file.
  - Propagate errors and exit statuses through the `melt.sh` pipeline.
  - Add tests for an uncorrupted round trip, correctable corruption, uncorrectable corruption, and truncated input.
  - Document what recovery can and cannot guarantee.

## P1 — Correctness and operational reliability

- [x] **Specify and test the duplicate-count policy**
  - Reconcile the duplicate rules in `README.md`, `bitRotChecker.py`, and its `find_duplicate_files()` docstring.
  - In particular, decide whether the policy flags more than three total copies, exactly three copies across drives, or a different condition.
  - Write examples for the allowed and disallowed cases, then implement tests for those cases.
  - Ensure the duplicate report and deletion workflow use the same policy.

- [ ] **Identify storage volumes consistently**
  - Replace `get_physical_drive()` behavior that currently treats a file’s parent directory as its drive.
  - Decide whether the policy is based on mounted volumes or physical devices; document platform-specific limitations.
  - Add tests showing that different folders on the same volume are treated consistently and that separate volumes are distinguished where supported.
  - Do not automatically delete files based on uncertain device identification.

- [ ] **Detect bit changes even when file size changes**
  - Review `isItRotten()` and its size-based filtering in `bitRotChecker.py`.
  - Report a changed file when its current checksum differs from the recorded checksum, even if its size has changed.
  - Distinguish missing baseline, changed file, and file not yet indexed in the output.
  - Add tests for same-size changes, size changes, unchanged files, missing baselines, and new files.

- [ ] **Stabilize scanner initialization and registry cleanup**
  - Initialize scanner configuration fields in `FileScanner.__init__` so the scanner can be used safely without first calling `read_json()`.
  - Change `cleanup_json()` so it does not remove list elements while iterating over that same list.
  - Preserve existing registry data and remove all stale entries deterministically.
  - Add tests for direct scanner use, empty registries, and multiple missing entries in one checksum group.

- [ ] **Scan valid filenames without interactive prompts**
  - Remove arbitrary filename restrictions such as skipping multiple dots, files without extensions, or extensions longer than four characters.
  - Replace extension prompts with explicit include/exclude options or a documented noninteractive default.
  - Ensure automation and Docker runs never wait for `input()`.
  - Add tests for names such as `archive.tar.gz`, `version.1.data`, `README`, and long extensions.

- [ ] **Stream file hashes and report I/O failures**
  - Update `garbageFileCollector.py` to hash files in chunks rather than reading each file fully into memory.
  - Avoid hashing every file during cleanup when filename and size do not match any garbage-list entry.
  - Report unreadable, missing, or changing files explicitly and continue scanning other files where safe.
  - Add tests for large files and simulated file-access errors.

- [ ] **Add an automated test suite for the command-line tools**
  - Set up pytest tests using temporary directories and disposable sample files.
  - Cover scanner results, JSON registry updates, bit-rot reporting, garbage-list behavior, and duplicate cleanup.
  - Assert exact output files and registry contents, not only successful process exit.
  - Add recovery integration tests when the Reed–Solomon executable is available; skip them with a clear reason when it is not.
  - Document the command for running the tests.

- [ ] **Validate registry data and make updates resilient**
  - Validate the expected JSON shape when loading `filelist.json`, `extlist.json`, and the garbage list.
  - Report malformed or unreadable files with their paths; do not silently replace invalid data with an empty registry.
  - Write updated JSON safely so an interrupted write does not leave a truncated registry.
  - Document how stored paths behave when drives are moved, files are renamed, or the registry is used from another machine.

## P1 — Python interface for Reed–Solomon recovery

- [ ] **Design and implement a Python API/CLI for freeze and melt**
  - Inspect the current `rsb.py`, `scripts/freeze.py`, `scripts/checkBitRot.py`, `scripts/writeHash.py`, Dockerfile, and `rsbep-backup` scripts.
  - Compare the supported execution options: Docker, a locally installed `rsbep` executable, or building/packaging the bundled C code. Choose an approach that is maintainable and document its platform requirements.
  - Provide Python functions and a command-line interface for freezing and melting files; keep command construction argument-based rather than using shell-interpolated command strings.
  - Ensure the required binaries and scripts are found reliably, errors and exit codes reach Python, and failures are not saved as valid `.frozen` or recovered files.
  - Define safe output behavior, including whether existing output files may be overwritten.
  - Add round-trip tests for files with spaces and unusual characters in their names, plus tests for missing dependencies and failed recovery.
  - Document setup, exact commands, dependencies, and recovery limitations.

## P1 — Documentation and build integration

- [ ] **Rewrite the README command guide to match the actual tools**
  - Document the current entry points, exact flags, prerequisites, expected working directory, and where JSON registries and generated files are stored.
  - Clearly distinguish the root-level SHA-256 registry scanner from the legacy MD5 sidecar scripts under `scripts/`.
  - Document separate workflows for scanning, checking bit rot, managing the garbage list, reviewing duplicates, freezing files, and recovering files.
  - Add safe examples with sample output and clear warnings before destructive operations.
  - Verify each documented command against the program’s `--help` output and a disposable test directory.

- [ ] **Fix and verify the bundled Reed–Solomon build configuration**
  - Compare `rsbep-backup/src/Makefile.am` with the generated `Makefile.in`.
  - Correct the Automake source declaration so regenerating the build files produces a working build.
  - Verify configure, build, install, freeze, and melt from a clean checkout or disposable copy.
  - Record the tested build commands and supported platforms.

- [ ] **Make the Docker wrapper safe and predictable**
  - Replace `os.system()` calls in `rsb.py` with argument-based subprocess calls and check every return code.
  - Handle spaces and special characters in host paths safely; document platform-specific Docker mount requirements.
  - Verify that container paths point to the installed freeze/melt scripts and binaries.
  - Define whether directory operations recurse and how output-name collisions are handled.
  - Add tests or a documented manual integration check for file and directory operations.

## P2 — Usability and future features

- [ ] **Benchmark hashing before changing algorithms**
  - Measure scan throughput and resource use on representative files and supported platforms.
  - Determine whether the current Python `hashlib` implementation benefits from the platform’s crypto library and hardware acceleration.
  - Compare candidate algorithms only after measuring real workloads.
  - Document compatibility implications before changing the registry’s checksum format; do not silently invalidate existing registries.

- [ ] **Add optional descriptions to the file catalog**
  - Define a backward-compatible metadata format that associates an optional user-provided description with a file record.
  - Support adding, editing, and searching descriptions without requiring an AI service.
  - Keep existing registries readable and avoid changing file checksums or identity when descriptions change.
  - Add tests for old registries, missing descriptions, and duplicate filenames.

- [ ] **Prototype review-only photo grouping**
  - Create a separate tool or command that proposes photo groups without moving or renaming files.
  - Start with transparent signals such as timestamps and directory location; show the reason for each proposed group.
  - Require explicit user approval before any file operation.
  - Test behavior with missing or inconsistent photo metadata.

- [ ] **Evaluate an optional local-model integration**
  - Treat this as a separate proposal from basic catalog descriptions and photo grouping.
  - Support a configurable local API endpoint, disabled by default.
  - Do not send file contents or metadata anywhere unless the user explicitly enables and configures the integration.
  - Define timeouts, error reporting, and behavior when the local model is unavailable.
  - Document privacy and data-handling behavior and add tests using a mock local endpoint.

- [ ] **Evaluate installable Python packaging and `uv`**
  - After CLI behavior and tests are stable, define package metadata and supported Python versions.
  - Add installable command entry points for the supported tools.
  - Verify documented `uv run` commands in a clean environment.
  - Keep any legacy scripts that remain supported documented during the transition.

- [ ] **Improve module and CLI documentation**
  - Add concise module and public-function docstrings where they clarify behavior or usage.
  - Ensure each CLI has useful `--help` text, examples, and clear error messages.
  - Avoid adding boilerplate docstrings that merely repeat a function or argument name.