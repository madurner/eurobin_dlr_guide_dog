import os
import pdb
from datetime import datetime
import time
import subprocess
import requests
from git import Repo
import argparse


class GuideDogListener:
    def __init__(self, local_repo_path, token):
        self.LOCAL_REPO_PATH = local_repo_path
        self.REPO_URL = 'https://github.com/madurner/eurobin_dlr_guide_dog.git'
        # Configure the repository details
        self.LOCAL_REPO_PATH = local_repo_path  # Path to the local repo
        self.BRANCH_NAME = 'main'  # Or the relevant branch name
        self.GITHUB_API_URL_CT = 'https://api.github.com/repos/madurner/eurobin_dlr_guide_dog/contents'
        self.GITHUB_API_URL_CM = 'https://api.github.com/repos/madurner/eurobin_dlr_guide_dog/commits'
        self.GITHUB_TOKEN = token  # Personal access token
        self.ignored_repo_files = [ "vision2eurobin_names.yaml", "guide_dog.png", "pull.txt", "test_pose.txt"]
        
    # Check for new files added in the repository
    def check_for_new_files(self):
        headers = {'Authorization': f'token {self.GITHUB_TOKEN}'}
        response = requests.get(self.GITHUB_API_URL_CM, headers=headers)
        commits = response.json()
        latest_cm = commits[0]['commit']['committer']['date'] 
        latest_remote_cm_date = datetime.fromisoformat(latest_cm.replace('Z', '+00:00'))
        print(latest_remote_cm_date)
        
        # Get the latest local commit
        repo = Repo(self.LOCAL_REPO_PATH)
        latest_commit = repo.head.commit

        commit_date = latest_commit.committed_datetime
        latest_local_cm_date = datetime.fromisoformat(str(commit_date))
        print(latest_local_cm_date)

        # Check the most recent commit for new files
        if max(latest_remote_cm_date, latest_local_cm_date) == latest_remote_cm_date:

            response = requests.get(self.GITHUB_API_URL_CT, headers=headers)
            commits = response.json()
            new_files = [commits[-1].get('name')][0]
            print(f"new files {new_files}")
            if all([new_file in self.ignored_repo_files for new_file in new_files]):
                return True, []
            return False, new_files
        return True, []

    # Pull changes from the repository
    def pull_changes(self):
        repo = Repo(self.LOCAL_REPO_PATH)
        import pdb
        pdb.set_trace()
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
    def listen_for_changes(self):
        
        new_commits = True
        while new_commits:
            print("Woof woof! Guide dog waiting for new files...")
            new_commits, new_files = self.check_for_new_files()
            time.sleep(2)# Wait for 1 minute before checking again
        
        print(f"Observed {new_files} being pushed")
        print("Trying to pull...")
        self.pull_changes()
        
        return False, new_files


# Run the listener
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-repo-path", type=str, help="path to local git repo")
    args = parser.parse_args()
    
    # listener
    listener = GuideDogListener(args.local_repo_path)

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
