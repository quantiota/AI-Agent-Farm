# Remote backup of the Microserver  
## Requirements  
- Ensure that you have SSH access and the necessary privileges to perform the backup on both the Microserver and the GPU server.  
- You may need to install sshpass on the GPU server if it's not already available (for Ubuntu-based systems) :    
```
sudo apt-get install sshpass
```  
## Step 1  
Before using this script, please make sure to replace the placeholders **(/path/to/microserver/backup, /path/to/gpu/server/backup, microserver-ip, microserver-username, microserver-password, gpu-server-username, and gpu-server-password)** with the actual directory paths and server details relevant to your setup.  
## Step 2  
Save the script to a file, make it executable:  
```
chmod +x remote_microserver_backup.sh
```  
and then run it periodically using a scheduler like cron to automate the backup process.
# Cron  
Here is an example schedule for the cron that offsets the remote backup process by half an hour from local time:  
```
# Exemple de planification pour le cron

# Minute (0-59)
# Décalage de 30 minutes par rapport à l'heure locale
minute=$((($(date +\%M) + 30) % 60))

# Heure (0-23)
heure=$(date +\%H)

# Jour du mois (1-31)
jour=$(date +\%d)

# Mois (1-12)
mois=$(date +\%m)

# Jour de la semaine (0-6, 0 représente le dimanche)
jour_semaine=$(date +\%u)

# Commande de sauvegarde à distance
commande_sauvegarde="bash /chemin/vers/votre/remote_microserver_backup.sh"

# Planification dans le cron
(crontab -l ; echo "$minute $heure $jour $mois $jour_semaine $commande_sauvegarde") | crontab -
```  
the remote backup script to run (/path/to/your/remote_microserver_backup.sh).   
It retrieves the current local time and adds 30 minutes to the minute to get the offset schedule minute for the remote backup. The other values (hour, day of the month, month, day of the week) are directly retrieved from the current date.  
### Note:   
Be sure to replace **/path/to/your/remote_microserver_backup.sh**
with the actual path to your remote backup script.  
Then run this script to update the schedule in the cron. The remote backup will be triggered whenever the specified minute is reached, half an hour off from the current local time. 
