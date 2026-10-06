# MarkitdownTool

A Windows desktop tool for converting PDF, DOCX, PPTX, and XLSX files to Markdown. Scanned PDFs can be OCR-processed with Tesseract and OCRmyPDF.

## Run from source

Requirements: Windows 10/11 x64, Python 3.12, and Tesseract OCR with the required language data installed.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python markitdown_gui.py
```

The application prompts for files and OCR languages. Output Markdown, OCR PDFs, and logs are written beside the application under `output/`.

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
