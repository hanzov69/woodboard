#/bin/bash
echo Installing as Service
if [[ "$(whoami)" != root ]]; then
  echo "Run this script as root!"
  exit 1
fi

cp ./woodboard.service /etc/systemd/system
systemctl daemon-reload
systemctl enable woodboard.service
systemctl start woodboard.service