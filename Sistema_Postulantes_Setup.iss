; Script de Inno Setup para Sistema de Postulantes
; Desarrollado por Guillermo Recalde a.k.a. 's1mple'
; Versión 1.0

#define MyAppName "Sistema QUIRA"
#define MyAppVersion "1.0"
#define MyAppPublisher "Guillermo Recalde a.k.a. 's1mple'"
#define MyAppURL "https://github.com/s1mple"
#define MyAppExeName "Sistema_Postulantes.exe"

[Setup]
; Configuración básica
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=Output
OutputBaseFilename=Sistema_QUIRA_Setup_v{#MyAppVersion}
SetupIconFile=quira_maxima_calidad.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Requisitos del sistema
MinVersion=10.0.17763
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Privilegios
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Configuración de idioma
LanguageDetectionMethod=locale
ShowLanguageDialog=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Archivo ejecutable principal
Source: "dist\Sistema_Postulantes\Sistema_Postulantes.exe"; DestDir: "{app}"; Flags: ignoreversion

; Icono del sistema
Source: "quira_maxima_calidad.ico"; DestDir: "{app}"; Flags: ignoreversion

; Imágenes (están en _internal)
Source: "dist\Sistema_Postulantes\_internal\quira.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Sistema_Postulantes\_internal\quiraXXXL.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Sistema_Postulantes\_internal\quiraXXL.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Sistema_Postulantes\_internal\quira_bigger.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Sistema_Postulantes\_internal\instituto.png"; DestDir: "{app}"; Flags: ignoreversion

; Carpeta _internal completa
Source: "dist\Sistema_Postulantes\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\quira_maxima_calidad.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\quira_maxima_calidad.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\quira_maxima_calidad.ico"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Configuración de registro para integración con Windows
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

[UninstallDelete]
; Limpiar archivos residuales al desinstalar
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: dirifempty; Name: "{app}"
