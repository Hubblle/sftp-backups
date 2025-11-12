# import libs
import asyncssh
import os
import time
import asyncio
import shutil
from dotenv import load_dotenv
import stat

load_dotenv()

class Backup():
    def __init__(self, conf:dict):
        #setup config
        self.hostname=os.getenv("HOSTNAME")
        self.port=str(os.getenv("PORT"))
        self.username=os.getenv("SSHUSER")
        self.password=os.getenv("PASSWORD")
        self.conf = conf

        
        
    
    def create_backup(self, dir:str):

        at = time.localtime()
        temp_name = f"./temp/{at.tm_year}-{at.tm_mon}-{at.tm_mday}--{at.tm_hour}h{at.tm_min}m{at.tm_sec}s"
        os.mkdir(temp_name)
        os.chmod(temp_name, 0o777)
        
        self.download(ddir=dir, locald=temp_name)
        
        #compress to the result folder
        shutil.make_archive("./backups"+temp_name.removeprefix("./temp"), 'zip', temp_name)
            
                

        
        
    def download(self, ddir, locald):
        
        """The plan here is to list every directory in the destination make every directory in the temp folder, (asynchronously in the futur)
        after that, start to download every files asynchronously
        """
        
        
        
        async def run_client():
            async with asyncssh.connect(
                self.hostname, username=self.username, password=self.password, port=self.port, known_hosts=None
            ) as conn:
                async with conn.start_sftp_client() as sftp:
                    
                    
                    files = []
                    async def parse(dir):
                        #get every files in the folder
                        try:
                            entries = await sftp.listdir(dir)
                        except Exception as e:
                            raise e
                        for entrie in entries:
                            dpath= os.path.join(dir, entrie)
                            
                            #If the path leads to a directory
                            if await sftp.isdir(dpath):
                                #make the local dir
                                os.makedirs(locald+dpath, 0o777)
                                await parse(dpath)
                                
                                
                            elif not await sftp.islink(dpath):
                                print(dpath)
                                files.append(dpath)
                    
                    await parse(ddir)
                    
                        
                    
                    tasks = (self.download_file(sftp, file, locald) for file in files)
                    await asyncio.gather(*tasks)


        asyncio.run(run_client())
        
        
    async def download_file(self, sftp, file: str, localdir: str):
        print(f"  downloading --> {file}")
        await sftp.get(file, localpath=f"{localdir}/{file}")
            