import os
from git import Repo
from git.exc import InvalidGitRepositoryError


class GitAnalyzer:
    def __init__(self):
        try:
            self.repo = Repo(os.getcwd(), search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise Exception("Not a git repository")

    def get_uncommitted_changes(self):
        """Get all uncommitted changes in the repository"""
        changes = []

        # Get staged changes
        staged_files = self.repo.index.diff("HEAD")
        for diff in staged_files:
            changes.append({
                "file": diff.a_path,
                "status": "staged",
                "content": self._get_diff_content(diff)
            })

        # Get unstaged changes
        unstaged_files = self.repo.index.diff(None)
        for diff in unstaged_files:
            changes.append({
                "file": diff.a_path,
                "status": "unstaged",
                "content": self._get_diff_content(diff)
            })

        # Get untracked files
        untracked_files = self.repo.untracked_files
        for file_path in untracked_files:
            with open(os.path.join(self.repo.working_dir, file_path), 'r') as f:
                content = f.read()
            changes.append({
                "file": file_path,
                "status": "untracked",
                "content": content
            })

        return changes

    def get_repository_context(self):
        """Get relevant context about the repository"""
        try:
            current_branch = self.repo.active_branch.name
            remote_url = next(
                self.repo.remotes.origin.urls) if self.repo.remotes else None

            # Get the last few commits for context
            recent_commits = []
            for commit in self.repo.iter_commits(max_count=5):
                recent_commits.append({
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": str(commit.committed_datetime)
                })

            return {
                "branch": current_branch,
                "remote_url": remote_url,
                "recent_commits": recent_commits
            }
        except Exception as e:
            raise Exception(f"Failed to get repository context: {str(e)}")

    def _get_diff_content(self, diff):
        """Extract the content from a diff object"""
        try:
            return diff.diff.decode('utf-8')
        except:
            return "(binary file)"
