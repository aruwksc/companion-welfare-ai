#define AppName "Companion Welfare AI"
#define AppVersion "0.1.0"
#define AppPublisher "Companion Welfare AI Project"

[Setup]
AppId={{7F2B61D1-10B8-4F5D-BB3E-0C9D8D67F001}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\Companion Welfare AI
DefaultGroupName={#AppName}
OutputDir=..\..\dist\installer
OutputBaseFilename=CompanionWelfareAI-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\CompanionWelfareAI.exe

[Files]
Source: "..\..\dist\CompanionWelfareAI\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\CompanionWelfareAI.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\CompanionWelfareAI.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\CompanionWelfareAI.exe"; Description: "Launch {#AppName}"; Flags: postinstall nowait skipifsilent
