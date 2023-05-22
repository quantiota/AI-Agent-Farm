#!/bin/bash

# Set the source and destination directories
microserver_backup_dir="/path/to/microserver/backup"
gpu_server_backup_dir="/path/to/gpu/server/backup"

# Set the Microserver and GPU server details
microserver_address="microserver-ip"
microserver_username="microserver-username"
microserver_password="microserver-password"
gpu_server_username="gpu-server-username"
gpu_server_password="gpu-server-password"

# Function to perform the remote backup
perform_backup() {
  echo "Starting backup process..."

  # Use rsync to transfer Microserver backups to the GPU server
  rsync -avz -e "sshpass -p $microserver_password ssh -o StrictHostKeyChecking=no" \
  $microserver_username@$microserver_address:$microserver_backup_dir/ $gpu_server_username@$gpu_server_address:$gpu_server_backup_dir/

  # Check the rsync exit status
  if [ $? -eq 0 ]; then
    echo "Backup process completed successfully."
  else
    echo "Backup process encountered an error."
  fi
}

# Run the backup process
perform_backup
