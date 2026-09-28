$message = @{
  systemMessage = 'Contexto del agente ProGesTec: monorepo orientado a produccion. Lee .github/copilot-instructions.md y docs/PROJECT_STATUS.md antes de editar. El CORS local es intencional; no lo cambies en tareas no relacionadas.'
} | ConvertTo-Json -Compress
Write-Output $message
