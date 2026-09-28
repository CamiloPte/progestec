$message = @{
  systemMessage = 'ProGesTec agent context: production-bound monorepo. Read .github/copilot-instructions.md and docs/PROJECT_STATUS.md before editing. Local CORS is intentional; do not change it in unrelated tasks.'
} | ConvertTo-Json -Compress
Write-Output $message
