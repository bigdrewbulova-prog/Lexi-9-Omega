#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8080}"
ENDPOINT="http://127.0.0.1:${PORT}/v1/chat/completions"
SYSTEM_PROMPT="You are BigDaddyDrew, a concise and practical local assistant running on this Mac. The user's name is BigDaddyDrew."

if ! curl -fsS "$ENDPOINT" >/dev/null 2>&1; then
  echo "Legacy server is not running on port $PORT. Start run_legacy_server.command first."
  exit 1
fi

echo "BigDaddyDrew legacy chat. Type 'exit' to quit."
while true; do
  printf "You> "
  IFS= read -r prompt || break
  [ "$prompt" = "exit" ] && break

  payload=$(cat <<JSON
{
  "model": "lexi-local",
  "messages": [
    {"role": "system", "content": "$SYSTEM_PROMPT"},
    {"role": "user", "content": "$prompt"}
  ],
  "stream": false
}
JSON
)

  response=$(curl -fsS "$ENDPOINT" -H "Content-Type: application/json" -d "$payload" || true)
  echo "$response" | sed -n 's/.*"content":"\([^"]*\)".*/BigDaddyDrew> \1/p' | sed 's/\\n/\
/g; s/\\"/"/g; s/\\\\/\\/g'
  echo
  if ! echo "$response" | grep -q '"content"'; then
    echo "BigDaddyDrew> [raw response below]"
    echo "$response"
    echo
  fi
done
