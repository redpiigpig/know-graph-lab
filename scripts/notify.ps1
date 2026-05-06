# Show a Windows toast notification.
# Usage:  powershell.exe -ExecutionPolicy Bypass -File scripts\notify.ps1 -Title "..." -Body "..."
#
# Used by run_ocr_daily.bat to surface daily-run start + Gemini quota events
# while the bat itself runs invisibly under Task Scheduler.
param(
    [Parameter(Mandatory=$true)] [string]$Title,
    [Parameter(Mandatory=$true)] [string]$Body
)

$ErrorActionPreference = 'SilentlyContinue'

# Prefer BurntToast if installed (cleaner), fall back to native Windows.UI.Notifications.
if (Get-Module -ListAvailable -Name BurntToast) {
    Import-Module BurntToast
    New-BurntToastNotification -Text $Title, $Body -AppLogo $null
    return
}

# Native: works on Windows 10/11 without any module install.
[void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
[void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]

$xmlString = @"
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>$([System.Security.SecurityElement]::Escape($Title))</text>
      <text>$([System.Security.SecurityElement]::Escape($Body))</text>
    </binding>
  </visual>
</toast>
"@

$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml($xmlString)
$toast = [Windows.UI.Notifications.ToastNotification]::new($doc)
# AppId must match a registered Start Menu shortcut to avoid "PowerShell" as the source.
# Using PowerShell's own AppId is fine — Windows accepts it without a custom registration.
$appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
