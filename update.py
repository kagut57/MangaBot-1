import os
import subprocess
import logging
from config import env_vars

LOGGER = logging.getLogger(__name__)

def gitpull():
    UPSTREAM_BRANCH = env_vars["UPSTREAM_BRANCH"]
    UPSTREAM_REPO = env_vars["UPSTREAM_REPO"]
    try:
        if len(UPSTREAM_REPO) == 0:
            raise TypeError("UPSTREAM_REPO is empty")
    except TypeError:
        UPSTREAM_REPO = None

    try:
        if len(UPSTREAM_BRANCH) == 0:
            raise TypeError("UPSTREAM_BRANCH is empty")
    except TypeError:
        UPSTREAM_BRANCH = 'master'

    if UPSTREAM_REPO is not None:
        try:
            if os.path.exists('.git'):
                subprocess.run(["rm", "-rf", ".git"])
            
            update = subprocess.run([
                f"git init -q "
                f"&& git config --global user.email kagutsuchi57@outlook.com"
                f"&& git config --global user.name kagut57"
                f"&& git add . "
                f"&& git commit -sm update -q "
                f"&& git remote add origin {UPSTREAM_REPO} "
                f"&& git fetch origin -q "
                f"&& git reset --hard origin/{UPSTREAM_BRANCH} -q"
            ], shell=True, capture_output=True, text=True)
            
            if update.returncode == 0:
                LOGGER.info('Successfully updated with latest commit from UPSTREAM_REPO')
            else:
                LOGGER.warning(f'Update failed. Error: {update.stderr}')
        
        except Exception as e:
            LOGGER.error(f'An error occurred during update: {e}')

gitpull()
