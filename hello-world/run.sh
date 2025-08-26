#!/usr/bin/env bash
set -euo pipefail

echo "---------------------------------------"
echo " Hello from Home Assistant add-on! 👋"
echo " Time: $(date -Iseconds)"
echo "---------------------------------------"

# Hold containeren kjørende så du kan se loggen i Add-on UI
# (HA stopper add-onen hvis prosessen avslutter)
tail -f /dev/null
