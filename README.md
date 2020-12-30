# spec_login_alert
send alert to pageduty or email if spec one login from last log

```shell
git clone <this_repo>
cd <this_repo>
cp local_settings.py.example local_settings.py
# add config
vi local_settings.py
pip3 install requests
# Start Option 1 (need sudo permission):
./install_as_systemd.sh
# Start Option 2 (normal user):
python3 spec_login_alert.py 1> spec_login_alert.log 2>&1 & 
```
