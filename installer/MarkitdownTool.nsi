!include "MUI2.nsh"

!define ROOT_DIR "${__FILEDIR__}\.."
!define PRODUCT_NAME "MarkitdownTool"
!define PRODUCT_VERSION "1.0.0"
!define UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${ROOT_DIR}\dist\MarkitdownTool-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\${PRODUCT_NAME}"
RequestExecutionLevel user
SetCompressor /SOLID lzma

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "${PRODUCT_NAME}" MainSection
  SectionIn RO
  SetOutPath "$INSTDIR"
  File "${ROOT_DIR}\dist\markitdown_gui.exe"

  SetOutPath "$INSTDIR\tesseract"
  File /r "${ROOT_DIR}\build\installer_payload\tesseract\*"

  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\markitdown_gui.exe" "" "$INSTDIR\markitdown_gui.exe" 0 SW_SHOWNORMAL "" "$INSTDIR"

  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "Publisher" "MarkitdownTool"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\markitdown_gui.exe"
  WriteRegStr HKCU "${UNINSTALL_KEY}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${UNINSTALL_KEY}" "NoRepair" 1
SectionEnd

Section /o "Desktop shortcut" DesktopShortcut
  CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\markitdown_gui.exe" "" "$INSTDIR\markitdown_gui.exe" 0 SW_SHOWNORMAL "" "$INSTDIR"
SectionEnd

Section "Uninstall"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  DeleteRegKey HKCU "${UNINSTALL_KEY}"

  Delete "$INSTDIR\markitdown_gui.exe"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR\tesseract"
  RMDir "$INSTDIR"
SectionEnd
