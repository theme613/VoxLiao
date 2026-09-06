[Setup]
AppName=VoxLiao
AppVersion=1.0.0
AppPublisher=Theme613
AppPublisherURL=PASTE_YOUR_OPTIONAL_CREATOR_PAGE_URL_HERE
AppSupportURL=PASTE_YOUR_OPTIONAL_SUPPORT_PAGE_URL_HERE
AppUpdatesURL=PASTE_YOUR_OPTIONAL_UPDATE_PAGE_URL_HERE
DefaultDirName={autopf}\VoxLiao
DefaultGroupName=VoxLiao
OutputBaseFilename=VoxLiao-Setup
UninstallDisplayName=VoxLiao
SetupIconFile=dist\VoxLiao.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE.txt
OutputDir=release

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\VoxLiao.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VoxLiao"; Filename: "{app}\VoxLiao.exe"
Name: "{group}\{cm:UninstallProgram,VoxLiao}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\VoxLiao"; Filename: "{app}\VoxLiao.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\VoxLiao.exe"; Description: "{cm:LaunchProgram,VoxLiao}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\*"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Remove my VoxLiao profiles, imported sounds, and settings?', mbConfirmation, MB_YESNO) = idYes then
    begin
      AppDataPath := ExpandConstant('{userappdata}\VoxLiao');
      DelTree(AppDataPath, True, True, True);
    end;
  end;
end;
