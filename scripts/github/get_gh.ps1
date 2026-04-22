$GhCandidates = @(
  'gh',
  'C:\Program Files\GitHub CLI\gh.exe',
  'C:\Program Files (x86)\GitHub CLI\gh.exe'
)

foreach ($candidate in $GhCandidates) {
  $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
  if ($cmd) {
    $cmd.Source
    exit 0
  }
}

throw 'GitHub CLI not found. Install with: winget install --id GitHub.cli -e'
