$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$works = [IO.Path]::GetFullPath((Join-Path $workspace 'public\content\works'))
if (Get-Process WINWORD -ErrorAction SilentlyContinue) {
  throw 'Word is still running; refusing to remove lock files.'
}
$prefix = '~' + [char]36
$locks = @(Get-ChildItem -LiteralPath $works -Force -File | Where-Object {
  $_.Name.StartsWith($prefix) -and $_.Name.EndsWith('.docx')
})
foreach ($lock in $locks) {
  $resolved = [IO.Path]::GetFullPath($lock.FullName)
  if (-not $resolved.StartsWith($works + [IO.Path]::DirectorySeparatorChar,
      [StringComparison]::OrdinalIgnoreCase)) {
    throw "Lock path escaped works directory: $resolved"
  }
  if ($lock.Length -gt 4096) {
    throw "Refusing to remove unexpectedly large lock file: $resolved"
  }
  [IO.File]::Delete($resolved)
  Write-Output "Removed stale Word lock: $($lock.Name)"
}
if ($locks.Count -eq 0) {
  Write-Output 'No stale Word locks found.'
}
