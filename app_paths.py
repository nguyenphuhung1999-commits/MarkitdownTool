import os
import shutil
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "MarkitdownTool"


@dataclass(frozen=True)
class AppPaths:
    install_dir: Path
    settings_dir: Path
    data_dir: Path

    @property
    def config_file(self) -> Path:
        return self.settings_dir / "config.json"

    @property
    def output_dir(self) -> Path:
        return self.data_dir / "output"

    @property
    def markdown_dir(self) -> Path:
        return self.output_dir / "markdown"

    @property
    def ocr_pdf_dir(self) -> Path:
        return self.output_dir / "ocrpdf"

    @property
    def log_dir(self) -> Path:
        return self.output_dir / "logs"

    @property
    def tessdata_dir(self) -> Path:
        return self.data_dir / "tesseract" / "tessdata"


def local_app_data(env: dict[str, str] | None = None) -> Path:
    environment = os.environ if env is None else env
    configured = environment.get("LOCALAPPDATA")
    if configured:
        return Path(configured)
    return Path.home() / "AppData" / "Local"


def build_app_paths(
    install_dir: Path,
    local_data_root: Path,
    configured_data_dir: str | Path | None = None,
) -> AppPaths:
    settings_dir = local_data_root / APP_NAME
    data_dir = Path(configured_data_dir).expanduser() if configured_data_dir else settings_dir
    return AppPaths(
        install_dir=Path(install_dir),
        settings_dir=settings_dir,
        data_dir=data_dir,
    )


def migrate_legacy_config(legacy_config: Path, new_config: Path) -> bool:
    if new_config.exists() or not legacy_config.is_file():
        return False
    new_config.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(legacy_config, new_config)
    return True


def find_application_resource(
    filename: str,
    install_dir: Path,
    bundle_dir: Path | None = None,
    source_dir: Path | None = None,
) -> Path | None:
    relative_path = Path(filename)
    if relative_path.is_absolute() or len(relative_path.parts) != 1:
        raise ValueError("Application resource names must be plain filenames.")

    candidates = [Path(install_dir) / relative_path]
    if bundle_dir:
        candidates.append(Path(bundle_dir) / relative_path)
    if source_dir:
        candidates.append(Path(source_dir) / relative_path)
    return next((candidate for candidate in candidates if candidate.is_file()), None)


def copy_data_preserving_existing(source: Path, destination: Path) -> None:
    source = Path(source)
    destination = Path(destination)
    if not source.is_dir():
        return
    source_resolved = source.resolve()
    destination_resolved = destination.resolve()
    if source_resolved == destination_resolved or source_resolved in destination_resolved.parents:
        raise ValueError("Destination data folder cannot be inside the current data folder.")

    for source_path in source.rglob("*"):
        relative_path = source_path.relative_to(source)
        destination_path = destination / relative_path
        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
        elif source_path.is_file() and not destination_path.exists():
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)