"""
Backup software made by __Hubble

Uses SFTP to backups servers (was created to backup docker containers)

Warning: This software does not include any type of spam protection, the requests are mades as fast as possible, use it at your own risks

"""

#import libs
import backup
import time
import json
import logging
import os

#define variables
with open("./conf.json", "r") as f:
    config = json.load(f)
    timing = int(config["time"])*60
    folder = config["starting folder"]

last_save = 0

if not os.path.exists("./last_save.json"):
    with open("./last_save.json", 'x') as f:
        f.close()
    
else:
    with open("./last_save.json", 'r') as f:
        data = json.load(f)
        last_save=data["0"]
        

#automatically gets credit in the .env    
backuper = backup.Backup(conf=config)

#Make the logger
logger = logging.Logger("Main")
stream = logging.StreamHandler()

formatter =  logging.Formatter("[%(asctime)s - %(levelname)s] %(name)s: %(message)s")
stream.setFormatter(formatter)

logger.addHandler(stream)
logger.setLevel(logging.INFO)

print(">>> Welcome to SFTP backup software ! 🌐")
print("-By __Hubble\n")


#Main loop
if __name__ == "__main__":
    logger.info("Starting main loop !")
    print("done")
    while True:
        time.sleep(0.5)
        
        #compare last backup time to now:
        dif = time.time() - last_save
        if dif >= timing:
            logger.info("Starting Backup !")
            last_save = time.time()
            
            with open("./last_save.json", "+w") as f:
                json.dump({"0":last_save}, f)
                
            try:
                backuper.create_backup(folder)
                logger.info("Backup finished !")
                logger.info(f"Took: {round((time.time()-last_save)/60)}min")
            except Exception as e:
                logger.error(f"err in the backup: {e}")
                print("")
                logger.info("Retrying in 5min !")
                last_save = (time.time()-timing)+5*60
            
            
        

