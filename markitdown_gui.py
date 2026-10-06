import os
import sys
import json
import hashlib
import shutil
import logging
import subprocess
import pymupdf

from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

import tkinter as tk

from tkinter import (
    Tk,
    Toplevel,
    filedialog,
    messagebox,
    Listbox,
    Button,
    Label,
    MULTIPLE,
    END
)

from tkinter import ttk


# =========================================================
# PROJECT PATHS
# =========================================================

# =========================================================
# PROJECT PATHS (PyInstaller compatible)
# =========================================================

if getattr(sys, "frozen", False):

    PROJECT_DIR = Path(
        sys.executable
    ).parent

else:

    PROJECT_DIR = Path(
        __file__
    ).parent

INPUT_DIR = PROJECT_DIR / "input"

OUTPUT_DIR = PROJECT_DIR / "output"

MARKDOWN_DIR = OUTPUT_DIR / "markdown"

OCRPDF_DIR = OUTPUT_DIR / "ocrpdf"

LOG_DIR = OUTPUT_DIR / "logs"

TEMP_DIR = PROJECT_DIR / "temp"

CONFIG_FILE = PROJECT_DIR / "config.json"

for folder in [
    INPUT_DIR,
    OUTPUT_DIR,
    MARKDOWN_DIR,
    OCRPDF_DIR,
    LOG_DIR,
    TEMP_DIR
]:
    folder.mkdir(
        parents=True,
        exist_ok=True
    )


# =========================================================
# LOGGING
# =========================================================

LOG_FILE = (
    LOG_DIR /
    f"process_{datetime.now():%Y%m%d_%H%M%S}.log"
)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


# =========================================================
# VENV
# =========================================================

def is_running_in_venv():

    return sys.prefix != sys.base_prefix


def get_venv_python():

    if os.name == "nt":

        return (
            PROJECT_DIR
            / ".venv"
            / "Scripts"
            / "python.exe"
        )

    return (
        PROJECT_DIR
        / ".venv"
        / "bin"
        / "python"
    )


def relaunch_in_venv():

    python_exe = get_venv_python()

    if not python_exe.exists():

        raise FileNotFoundError(
            f"Không tìm thấy venv:\n{python_exe}"
        )

    subprocess.run(
        [
            str(python_exe),
            str(__file__)
        ],
        check=True
    )

    sys.exit()


# =========================================================
# TESSERACT
# =========================================================

def find_tesseract():

    bundled_exe = PROJECT_DIR / "tesseract" / "tesseract.exe"

    if bundled_exe.exists():
        return str(bundled_exe)

    exe = shutil.which(
        "tesseract"
    )

    if exe:
        return exe

    common_paths = [

        r"C:\Program Files\Tesseract-OCR\tesseract.exe",

        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]

    for path in common_paths:

        if Path(path).exists():
            return path

    return None


def get_available_languages():

    tesseract = find_tesseract()

    if not tesseract:

        raise RuntimeError(
            "Không tìm thấy Tesseract OCR."
        )

    result = subprocess.run(
        [
            tesseract,
            "--list-langs"
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )

    langs = []

    for line in result.stdout.splitlines():

        line = line.strip()

        if (
            line
            and
            "List of available languages" not in line
        ):
            langs.append(line)

    return sorted(langs)


# =========================================================
# CONFIG
# =========================================================

def load_config():

    if CONFIG_FILE.exists():

        try:

            return json.loads(
                CONFIG_FILE.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            pass

    return {
        "ocr_languages": [
            "vie",
            "eng"
        ]
    }


def save_config(languages):

    CONFIG_FILE.write_text(
        json.dumps(
            {
                "ocr_languages": languages
            },
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )


# =========================================================
# OCR LANGUAGE DIALOG
# =========================================================

def select_ocr_languages():

    supported = get_available_languages()

    config = load_config()

    preselected = config.get(
        "ocr_languages",
        []
    )

    dialog = Toplevel()

    dialog.title(
        "Chọn ngôn ngữ OCR"
    )

    dialog.geometry(
        "350x450"
    )

    Label(
        dialog,
        text="Chọn một hoặc nhiều ngôn ngữ OCR"
    ).pack(
        pady=10
    )

    listbox = Listbox(
        dialog,
        selectmode=MULTIPLE,
        width=30,
        height=15
    )

    listbox.pack(
        padx=10,
        pady=10
    )

    for idx, lang in enumerate(supported):

        listbox.insert(
            END,
            lang
        )

        if lang in preselected:

            listbox.selection_set(idx)

    result = []

    def confirm():

        selected = listbox.curselection()

        for idx in selected:

            result.append(
                supported[idx]
            )

        dialog.destroy()

    Button(
        dialog,
        text="Xác nhận",
        command=confirm
    ).pack(
        pady=10
    )

    dialog.grab_set()
    dialog.wait_window()

    if not result:

        raise RuntimeError(
            "Bạn chưa chọn ngôn ngữ OCR."
        )

    save_config(result)

    return result


# =========================================================
# PDF TEXT CHECK
# =========================================================

def pdf_needs_ocr(pdf_path):

    try:

        doc = pymupdf.open(pdf_path)

        try:

            return any(
                not page.get_text().strip()
                for page in doc
            )

        finally:

            doc.close()

    except Exception:

        return True


def output_path_for(source, output_dir, extension):

    source = Path(source)

    identity = os.path.normcase(
        str(source.resolve())
    )

    digest = hashlib.sha256(
        identity.encode("utf-8")
    ).hexdigest()[:10]

    return output_dir / f"{source.stem}_{digest}{extension}"


# =========================================================
# OCR
# =========================================================

@contextmanager
def hide_ocr_console_windows():

    if os.name != "nt":
        yield
        return

    from ocrmypdf.subprocess import _run as ocrmypdf_subprocess

    original_run = ocrmypdf_subprocess.subprocess_run
    original_popen = ocrmypdf_subprocess.Popen
    creation_flag = subprocess.CREATE_NO_WINDOW

    def run_without_console(*args, **kwargs):
        kwargs["creationflags"] = (
            kwargs.get("creationflags", 0)
            | creation_flag
        )
        return original_run(*args, **kwargs)

    def popen_without_console(*args, **kwargs):
        kwargs["creationflags"] = (
            kwargs.get("creationflags", 0)
            | creation_flag
        )
        return original_popen(*args, **kwargs)

    ocrmypdf_subprocess.subprocess_run = run_without_console
    ocrmypdf_subprocess.Popen = popen_without_console

    try:
        yield
    finally:
        ocrmypdf_subprocess.subprocess_run = original_run
        ocrmypdf_subprocess.Popen = original_popen

def run_ocr(
    pdf_file,
    languages
):

    source = Path(pdf_file)

    output_pdf = output_path_for(
        source,
        OCRPDF_DIR,
        ".pdf"
    )

    logging.info(
        f"OCR started: {source.name}"
    )

    import ocrmypdf

    with hide_ocr_console_windows():
        exit_code = ocrmypdf.ocr(
            str(source),
            str(output_pdf),
            language=languages,
            deskew=True,
            rotate_pages=True,
            skip_text=True,
            progress_bar=False,
            use_threads=os.name == "nt"
        )

    if exit_code != ocrmypdf.ExitCode.ok:
        raise RuntimeError(
            f"OCRmyPDF failed with exit code {exit_code}."
        )

    logging.info(
        f"OCR completed: {output_pdf.name}"
    )

    return output_pdf


# =========================================================
# MARKITDOWN
# =========================================================

def convert_markdown(file_path, output_source=None):

    from markitdown import MarkItDown

    md = MarkItDown()

    source = Path(file_path)

    logging.info(
        f"Markdown started: {source.name}"
    )

    result = md.convert(
        str(source)
    )

    output_md = output_path_for(
        output_source or source,
        MARKDOWN_DIR,
        ".md"
    )

    output_md.write_text(
        result.text_content,
        encoding="utf-8"
    )

    logging.info(
        f"Markdown completed: {output_md.name}"
    )

    return output_md


# =========================================================
# PROCESS FILE
# =========================================================

def process_file(
    file_path,
    languages
):

    source = Path(file_path)

    logging.info(
        f"Processing: {source.name}"
    )

    if source.suffix.lower() == ".pdf":

        if not pdf_needs_ocr(source):

            logging.info(
                "PDF text layer detected."
            )

            return convert_markdown(
                source
            )

        logging.info(
            "PDF scan detected."
        )

        ocr_pdf = run_ocr(
            source,
            languages
        )

        return convert_markdown(
            ocr_pdf,
            output_source=source
        )

    return convert_markdown(
        source
    )


# =========================================================
# MAIN GUI
# =========================================================

def show_result_dialog(root, success, failed):

    dialog = root
    dialog.title("Kết quả xử lý")
    dialog.geometry("560x280")
    dialog.minsize(440, 220)
    dialog.attributes("-topmost", True)

    Label(
        dialog,
        text=f"Thành công: {len(success)}\nLỗi: {len(failed)}",
        justify="left",
        anchor="w"
    ).pack(
        fill="x",
        padx=16,
        pady=(16, 8)
    )

    if failed:
        details_frame = tk.Frame(dialog)
        details_frame.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 8)
        )

        details = tk.Text(
            details_frame,
            height=7,
            wrap="word"
        )
        scrollbar = ttk.Scrollbar(
            details_frame,
            orient="vertical",
            command=details.yview
        )
        details.configure(
            yscrollcommand=scrollbar.set
        )
        details.insert("1.0", "\n".join(failed))
        details.configure(state="disabled")
        details.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def open_location(path):

        try:
            dialog.attributes("-topmost", False)
            os.startfile(str(path))
        except Exception as ex:
            dialog.attributes("-topmost", True)
            messagebox.showerror(
                "Không thể mở",
                str(ex),
                parent=dialog
            )

    def close_session():

        dialog.destroy()

    buttons = tk.Frame(dialog)
    buttons.pack(
        fill="x",
        padx=16,
        pady=(0, 16)
    )

    Button(
        buttons,
        text="Open Log",
        command=lambda: open_location(LOG_FILE)
    ).pack(side="left", padx=(0, 8))

    Button(
        buttons,
        text="Open file",
        command=lambda: open_location(MARKDOWN_DIR)
    ).pack(side="left", padx=(0, 8))

    Button(
        buttons,
        text="Close",
        command=close_session
    ).pack(side="right")

    dialog.protocol("WM_DELETE_WINDOW", close_session)
    dialog.deiconify()
    dialog.update_idletasks()
    dialog.grab_set()
    dialog.lift()
    dialog.focus_force()
    dialog.wait_window()


def main():

    root = Tk()

    root.withdraw()

    if not find_tesseract():

        messagebox.showerror(
            "Tesseract OCR",
            "Không tìm thấy Tesseract OCR.",
            parent=root
        )
        root.destroy()
        return

    languages = select_ocr_languages()

    files = filedialog.askopenfilenames(
        title="Chọn tài liệu",
        filetypes=[
            (
                "Supported Documents",
                "*.pdf *.docx *.pptx *.xlsx"
            )
        ]
    )

    if not files:
        root.destroy()
        return

    progress_window = Toplevel(root)

    progress_window.title(
        "Đang xử lý"
    )

    progress_window.geometry(
        "500x150"
    )

    status_label = Label(
        progress_window,
        text="Khởi tạo..."
    )

    status_label.pack(
        pady=10
    )

    progress = ttk.Progressbar(
        progress_window,
        orient="horizontal",
        length=400,
        mode="determinate"
    )

    progress.pack(
        pady=20
    )

    total = len(files)

    success = []
    failed = []

    for idx, file_path in enumerate(files):

        try:

            status_label.config(
                text=f"{idx+1}/{total}: "
                     f"{Path(file_path).name}"
            )

            progress["value"] = (
                (idx + 1)
                / total
                * 100
            )

            progress_window.update()

            md_file = process_file(
                file_path,
                languages
            )

            success.append(
                md_file.name
            )

        except Exception as ex:

            logging.exception(ex)

            failed.append(
                f"{Path(file_path).name}: {ex}"
            )

    progress_window.destroy()

    show_result_dialog(
        root,
        success,
        failed
    )


# =========================================================
# ENTRY
# =========================================================

if __name__ == "__main__":

    if not getattr(sys, "frozen", False) and not is_running_in_venv():

        relaunch_in_venv()

    main()