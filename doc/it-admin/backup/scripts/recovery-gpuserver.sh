#sudo bash -x recovery-gpuserver.sh

#!/bin/bash

rm -rf /home /opt
cp -pr /backup/rsnapshot/hourly.0/localhost/home /
cp -pr /backup/rsnapshot/hourly.0/localhost/opt /
updatedb