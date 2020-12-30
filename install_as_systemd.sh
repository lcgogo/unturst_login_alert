#!/bin/sh

SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
PROCESS=untrust_login_alert
DESCRIPTION="send alert when untrust user login"

if [ ! -f "${SHELL_FOLDER}/${PROCESS}.py" ];then
  echo Not found "${SHELL_FOLDER}/${PROCESS}.py Exit Now."
  exit 1
else
  chmod +x "${SHELL_FOLDER}/${PROCESS}.py"
fi

echo "==== Run ${DESCRIPTION} in systemd ===="
cat > /tmp/${PROCESS}.service << EOF
[Service]
User=${USER}
Group=${USER}
ExecStart=${SHELL_FOLDER}/${PROCESS}.py
Restart=always
StandardOutput=syslog
StandardError=inherit

[Install]
WantedBy=multi-user.target

[Unit]
Description=${DESCRIPTION}
After=network.target
EOF
sudo mv /tmp/${PROCESS}.service /lib/systemd/system/${PROCESS}.service
oldpid=`ps -ef | grep "${PROCESS}" | grep -v grep | awk '{print $2}'`
if [ ! -z "${oldpid}" ];then
  echo Old ${PROCESS} is running. Stop it now.
  sudo systemctl stop ${PROCESS}.service
fi
sudo systemctl daemon-reload
sudo systemctl start ${PROCESS}.service
sudo systemctl enable ${PROCESS}.service
sleep 2
sudo systemctl status ${PROCESS}.service
