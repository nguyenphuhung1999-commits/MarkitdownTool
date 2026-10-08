# Changelog

Notable changes to MarkitdownTool are listed here by release.

## [2.1.2] - 2026-10-08

### Changed

- Updated the PDFium binding `pypdfium2` from 5.13.0 to 5.14.0.

## [2.1.1] - 2026-10-08

### Changed

- Streamlined the main window by removing the separate OCR language manager shortcut. Language package management remains available in Settings and OCR configuration.

## [2.1.0] - 2026-10-08

### Added

- Added a persistent GUI with OCR-only, Markdown-only, and OCR-then-Markdown processing modes.
- Added English and Vietnamese UI localization, Settings groups, release checking, and AI connection scaffolding for future MCP, CLI, and agent integrations.
- Added OCR language package search, installation from the official Tesseract `tessdata_fast` repository, and removal of app-managed packages.
- Added structured per-file results, background processing, cooperative cancellation between files, and processing logs.
- Added per-user install and data paths, legacy data migration, a versioned installer, and selectable uninstaller components.
- Added third-party license, privacy, and disclaimer documentation.

### Changed

- Replaced PyMuPDF in PDF text-layer detection with PDFium through `pypdfium2`; Microsoft MarkItDown continues to use its PDF conversion dependencies.
- Moved configuration, output, logs, and downloaded OCR language data to the user data directory by default.
