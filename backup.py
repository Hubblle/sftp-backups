# import libs
import paramiko
import os
import time
import posixpath
import stat
import asyncio
import shutil
from dotenv import load_dotenv

load_dotenv()

class Backup():
    def __init__(self):
        #setup config
        self.hostname=os.getenv("HOSTNAME")
        self.port=int(os.getenv("PORT"))
        self.username=os.getenv("SSHUSER")
        self.password=os.getenv("PASSWORD")

        
        
    
    def connect(self):
        # Establish the SSH client
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add host keys (not secure for production)

        # Connect to the server
        try:
            print("Trying connexion with the ssh server")
            self.ssh.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
        except Exception as e:
            print("Error while connecting to ssh: ",e)
            exit()

        # Establish the SFTP client
        try:
            print("Trying to establish the sftp client")
            self.sftp = self.ssh.open_sftp()
        except Exception as e:
            print("Error while establishing the sftp client:",e)
            exit()
        

    def getListofFiles(self, remoteFilePath):
        try:
            print(f"lists of files {self.sftp.listdir(remoteFilePath)}")
        except Exception:
            print(f"Error while getting the list of files")
    

    def downloadFiles(self, remoteFilePath):
        localFilePath= os.path.join("temp",remoteFilePath)
        print(f"downloading file {remoteFilePath} to remote {localFilePath}")
            
        sftp_client=self.__SSH_Client.open_sftp()
        try:
            sftp_client.get(remoteFilePath, localFilePath)
        except FileNotFoundError as err:
            print(f"File: {remoteFilePath} was not found on the server")
            
    def close(self):
        #close the sftp
        self.sftp.close()
        #close the ssh
        self.ssh.close()
    
    def create_backup(self, dir):
        #open the sftp
        self.connect()
        at = time.localtime()
        path=f"./temp/{at.tm_year}-{at.tm_mon}-{at.tm_mday}--{at.tm_hour}h{at.tm_min}m{at.tm_sec}s"
        os.mkdir(path)
        os.chmod(path, 0o777)
        
        
        
        async def parse(dir):
            try:
                entries = self.sftp.listdir_attr(dir)
            except Exception as e:
                print(f"Could not list directory {dir}: {e}")
                return

            for entry in entries:
                name = entry.filename
                remote_path = posixpath.join(dir, name)
                # build a local path under the backup root
                rel_path = remote_path.lstrip("/")
                local_path = os.path.join(path, rel_path)

                # directory
                if stat.S_ISDIR(entry.st_mode):
                    try:
                        os.makedirs(local_path, exist_ok=True)
                        try:
                            os.chmod(local_path, 0o777)
                        except Exception:
                            pass
                    except Exception as e:
                        print(f"Could not create local directory {local_path}: {e}")
                        continue

                    # recurse into directory
                    await parse(remote_path)
                    
                    # I do in fact know that its not a great use of async (I/O opperations by the ssh lib are async blocking), but i don't wanna think abt fixing it for now x)

                # symlink (treat as file: try to read link target metadata)
                elif stat.S_ISLNK(entry.st_mode):
                    try:
                        # attempt to resolve and download the target if possible, otherwise skip
                        target = self.sftp.readlink(remote_path)
                        print(f"Skipping symlink {remote_path} -> {target}")
                    except Exception:
                        print(f"Skipping broken symlink {remote_path}")

                # regular file (or other types)
                else:
                    try:
                        os.makedirs(os.path.dirname(local_path), exist_ok=True)
                        print(f"Downloading {remote_path} -> {local_path}")
                        self.sftp.get(remote_path, local_path)
                        try:
                            os.chmod(local_path, 0o666)
                        except Exception:
                            pass
                    except Exception as e:
                        print(f"Failed to download {remote_path}: {e}")
                        continue
            
        asyncio.run(parse(dir))
        
        #compress to the result folder
        shutil.make_archive("./backups"+path.removeprefix("./temp"), 'zip', path)
        
                
        
        #close
        self.close()
            