#/bin/bash
echo Installing as Service
if [[ "$(whoami)" != root ]]; then
  echo "Run this script as root!"
  exit 1
fi
if [! -f "$CONFIG"]; then
    exit 1
fi
mv ./woodboard.service /etc/systemd/system
systemctl daemon-reload
systemctl start woodboard.service