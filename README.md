# MarkitdownTool 2.1.1

A Windows desktop tool for processing PDF, DOCX, PPTX, and XLSX files. Scanned PDFs can be OCR-processed with Tesseract and OCRmyPDF.

---

## Author

Nguyễn Phú Hùng

GitHub:
https://github.com/nguyenphuhung1999-commits/MarkitdownTool

---

## License

This project is licensed under the MIT License.

See LICENSE.md for details.

---

## Disclaimer

Please review DISCLAIMER.md before using the software.

---

## Privacy

Please review PRIVACY.md for information regarding local processing and data handling.

---

## Third-Party Components

Please review THIRD_PARTY_NOTICES.md for information regarding third-party dependencies and licenses.

See [CHANGELOG.md](CHANGELOG.md) for versioned release notes.

## Processing modes

- **OCR only** creates searchable PDFs from scanned PDFs.
- **Markdown only** converts eligible documents without running OCR. The app checks the selected files first and asks whether to continue when some files cannot be converted.
- **OCR then Markdown** OCR-processes scanned PDFs and creates Markdown for supported documents.

Processing runs in the background so the window remains responsive. Cancel stops the batch after the current file finishes. Results, skipped files, and errors are reported separately.

## OCR languages

Use **OCR Languages** to review installed language packages. Packages installed by MarkitdownTool are downloaded from the official `tesseract-ocr/tessdata_fast` repository and stored in the application's `tesseract/tessdata` folder. They can be removed from the app there. Languages supplied by a system Tesseract installation are read-only and are not modified by MarkitdownTool.

The installer bundles `eng`, `vie`, and `osd`, so those packages are available offline. Additional packages require an internet connection. Language models are stored in the user data directory and do not modify a system Tesseract installation.

## Run from source

Requirements: Windows 10/11 x64, Python 3.12, and Tesseract OCR with the required language data installed.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python markitdown_gui.py
```

The application opens a persistent work window. Add files, select a processing mode, and start a batch. By default, configuration, output, and logs are stored under `%LOCALAPPDATA%\MarkitdownTool`; the user data directory can be changed in Settings. The executable and bundled OCR runtime are installed under `%LOCALAPPDATA%\Programs\MarkitdownTool`.

## Build the executable

```powershell
python -m PyInstaller --noconfirm .\markitdown_gui.spec
```

The executable is created at `dist\markitdown_gui.exe`.

## Build the installer

Install Tesseract OCR with the `eng`, `vie`, and `osd` language data, and install NSIS 3. Then run:

```powershell
.\installer\Build-Release.ps1
```

The script stages the Tesseract runtime, builds the executable, and creates `dist\MarkitdownTool-Setup.exe`. The installer targets the current Windows user and does not require administrator rights.

## Repository contents

Generated binaries, build intermediates, virtual environments, runtime output, logs, and user configuration are excluded from Git. The installer is distributed as a GitHub Release asset rather than committed to the repository.
