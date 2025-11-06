# STFP Backups
This software was created to make "snaps" backups of docker containers hosted with hosts who don't offers a lot of backup space.
You can host it on a small device, event a raspPI to store backups in local, tho its ofc slower than an classic local backup solution.

## How to start ?
The project use python 3.9+.

First, clone the repo,
next, use the `/conf.json.example` file to make your backup config and add your credentials in the .env using the included `/.env.example`.

Then, install every dependencies listed in `requirements.txt`.

When your done, you can start it with `python3 main.py`, it will start to do backups.

## To do
- Add multiple servers support
- Add auto old backups deletion
- Add incrementials backups?


