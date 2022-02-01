# Check mysql service status
systemctl status mysql.service

# Config Database
sudo nano /etc/mysql/my.cnf

[client]
database = journal
user = opquity
password = opquity
default-character-set = utf8

# Restart mysql
sudo systemctl daemon-reload
sudo systemctl restart mysql

sudo apt install libmysqlclient-dev default-libmysqlclient-dev

