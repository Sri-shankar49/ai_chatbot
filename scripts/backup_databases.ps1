
$ErrorActionPreference = "Stop"

# Project and database paths
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$backupBase = Join-Path $projectRoot "backups"

$sqliteSource = Join-Path $backendDir "chat_history.db"
$chromaSource = Join-Path $backendDir "chroma_data"

# Validate source data before starting
if (-not (Test-Path $sqliteSource -PathType Leaf)) {
    throw "SQLite database not found: $sqliteSource"
}

if (-not (Test-Path $chromaSource -PathType Container)) {
    throw "ChromaDB folder not found: $chromaSource"
}

# Create a unique timestamped backup folder
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $backupBase $timestamp

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host "Creating backup at: $backupDir"

# Copy SQLite database and ChromaDB files
Copy-Item -LiteralPath $sqliteSource `
    -Destination (Join-Path $backupDir "chat_history.db")

Copy-Item -LiteralPath $chromaSource `
    -Destination (Join-Path $backupDir "chroma_data") `
    -Recurse

# Confirm expected backup files exist
if (-not (Test-Path (Join-Path $backupDir "chat_history.db"))) {
    throw "SQLite backup verification failed."
}

if (-not (Test-Path (Join-Path $backupDir "chroma_data") -PathType Container)) {
    throw "ChromaDB backup verification failed."
}

Write-Host ""
Write-Host "Backup copies created successfully." -ForegroundColor Green
Write-Host "SQLite: $backupDir\chat_history.db"
Write-Host "ChromaDB: $backupDir\chroma_data"
Write-Host ""
Write-Host "Keep the original databases unchanged until you verify the backup."
