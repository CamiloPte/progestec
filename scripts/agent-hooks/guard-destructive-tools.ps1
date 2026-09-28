$inputText = [Console]::In.ReadToEnd()
$dangerous = '(?i)(git\s+(reset\s+--hard|clean\s+-fd|push\s+.*--force)|drop\s+database|drop\s+table|alembic\s+downgrade|docker\s+compose\s+down\s+--volumes|remove-item\s+.*-recurse|rm\s+(-rf|-r))'
if ($inputText -match $dangerous) {
  @{ hookSpecificOutput = @{ hookEventName = 'PreToolUse'; permissionDecision = 'ask'; permissionDecisionReason = 'Potentially destructive command. Confirm scope, target and backup before continuing.' } } | ConvertTo-Json -Compress
}
