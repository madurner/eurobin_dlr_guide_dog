import os
import pdb
from datetime import datetime, timedelta
import time
import subprocess
import requests
from git import Repo
import argparse
from pathlib import Path


class GuideDogListener:
    def __init__(self, local_repo_path, token, dir_name):
        self.LOCAL_REPO_PATH = local_repo_path
        self.DIR_NAME = dir_name
        self.REPO_URL = 'https://github.com/madurner/eurobin_dlr_guide_dog.git'
        # Configure the repository details
        self.LOCAL_REPO_PATH = local_repo_path  # Path to the local repo
        self.BRANCH_NAME = 'main'  # Or the relevant branch name
        self.GITHUB_API_URL_CT = 'https://api.github.com/repos/madurner/eurobin_dlr_guide_dog/contents/' + str(
            dir_name) + '?sort=created'
        self.GITHUB_API_URL_CM = 'https://api.github.com/repos/madurner/eurobin_dlr_guide_dog/commits?sort=created'
        self.GITHUB_TOKEN = token  # Personal access token
        self.ignored_repo_files = ["vision2eurobin_names.yaml", "guide_dog.png", "pull.txt", "test_pose.txt"]

    # Check for new files added in the repository
    def check_for_new_files(self):
        headers = {'Authorization': f'token {self.GITHUB_TOKEN}'}
        response = requests.get(self.GITHUB_API_URL_CM, headers=headers)
        commits = response.json()
        latest_cm = commits[0]['commit']['committer']['date']
        latest_remote_cm_date = datetime.fromisoformat(latest_cm.replace('Z', '+01:00')) + timedelta(hours=1)

        # Get the latest local commit
        repo = Repo(self.LOCAL_REPO_PATH)
        latest_commit = repo.head.commit

        commit_date = latest_commit.committed_datetime
        latest_local_cm_date = datetime.fromisoformat(str(commit_date))
        latest_local_cm_date = latest_local_cm_date

        # Check the most recent commit for new files
        if latest_remote_cm_date.replace(second=0, microsecond=0) != latest_local_cm_date.replace(second=0,
                                                                                                  microsecond=0) and max(
                latest_remote_cm_date.replace(second=0, microsecond=0),
                latest_local_cm_date.replace(second=0, microsecond=0)) == latest_remote_cm_date.replace(second=0,
                                                                                                        microsecond=0):
            print("Noticed changes")
            response = requests.get(self.GITHUB_API_URL_CT, headers=headers)
            folder_contents = response.json()

            files_in_remote = []
            for content in folder_contents:
                files_in_remote.append(content.get('name'))

            path_to_local_dir = os.path.join(self.LOCAL_REPO_PATH, self.DIR_NAME)
            print(f"Searching for files on local machine in {path_to_local_dir}")
            files_in_local = os.listdir(str(path_to_local_dir))

            files_to_process = []
            for file_in_remote in files_in_remote:
                if file_in_remote not in files_in_local and file_in_remote.endswith("png"):
                    files_to_process.append(file_in_remote)
                    print(f"Found new png file {file_in_remote}")
            if files_to_process is None:
                return True, []
            if len(files_to_process) == 0:
                return True, []
            print(f"return files to process {files_to_process}")
            return False, files_to_process
        return True, []

    # Pull changes from the repository
    def pull_changes(self):
        repo = Repo(self.LOCAL_REPO_PATH)
        origin = repo.remotes.origin
        origin.pull(self.BRANCH_NAME)

    # Commit and push any new files
    def commit_and_push(self, commit_file):
        repo = Repo(self.LOCAL_REPO_PATH)
        repo.git.add(commit_file)
        repo.index.commit('Auto commit new files')
        origin = repo.remotes.origin
        origin.push(self.BRANCH_NAME)

    # Main function to run the polling loop
    def listen_for_changes(self, block=True):
        
        new_commits = True
        new_files_pull = []
        while new_commits:
            print("Woof woof! Guide dog waiting for new files...")
            new_commits, new_files_pull = self.check_for_new_files()
            time.sleep(2)# Wait for 1 minute before checking again
            if not block:
                return True, []

        print(f"Observed {new_files_pull} being pushed")
        print("Trying to pull...")
        self.pull_changes()

        return False, new_files_pull


# Run the listener
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-repo-path", type=str, help="path to local git repo")
    args = parser.parse_args()

    # listener
    listener = GuideDogListener(args.local_repo_path, )

    # check repo until new inference file is push to remote
    no_commits, new_files = listener.listen_for_changes()

    # run inference
    obj = new_files[0].split('/')[-1].split('.')[0]
    print(f"Run inference for {obj}")

    # return new_file
    # new_file = 

    # push pose to remote
    print(f"Woof woof trying to push {new_files}")
    listener.commit_and_push(new_file)
