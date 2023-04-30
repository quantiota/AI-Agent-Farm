#sudo bash -x recovery-microserver.sh

#!/bin/bash

rm -rf /home /opt
cp -pr /backup/rsnapshot/daily.1/localhost/home /
cp -pr /backup/rsnapshot/daily.1/localhost/opt /
