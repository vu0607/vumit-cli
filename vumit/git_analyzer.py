import os
from git import Repo
from git.exc import InvalidGitRepositoryError


class GitAnalyzer:
    def __init__(self):
        try:
            self.repo = Repo(os.getcwd(), search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise Exception("Not a git repository")

    def get_branch_commits(self):
        """Get all commits in the current feature branch"""
        try:
            current_branch = self.repo.active_branch
            commits = []

            # Get commits from the current branch
            for commit in self.repo.iter_commits(current_branch.name):
                # Get the diff for this commit
                diff_content = []
                if commit.parents:
                    diffs = commit.parents[0].diff(commit)
                else:
                    # For first commit with no parent
                    diffs = commit.diff(None)

                for diff in diffs:
                    try:
                        # Handle both string and bytes diff content
                        if hasattr(diff, 'diff'):
                            diff_data = diff.diff
                            if isinstance(diff_data, bytes):
                                try:
                                    diff_text = diff_data.decode('utf-8')
                                except UnicodeDecodeError:
                                    diff_text = "(binary file)"
                            else:
                                diff_text = str(diff_data)
                        else:
                            diff_text = "(no diff available)"

                        diff_content.append({
                            "file": diff.a_path or diff.b_path,  # Handle renamed files
                            "change_type": diff.change_type,
                            "diff": diff_text
                        })
                    except Exception as e:
                        # If anything goes wrong with this diff, skip it
                        continue

                commits.append({
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": str(commit.committed_datetime),
                    "changes": diff_content
                })

            return commits

        except Exception as e:
            raise Exception(f"Failed to get branch commits: {str(e)}")

    def get_repository_context(self):
        """Get relevant context about the repository"""
        try:
            current_branch = self.repo.active_branch.name
            remote_url = next(
                self.repo.remotes.origin.urls) if self.repo.remotes else None

            # Get the target branch (main/master)
            target_branch = None
            for ref in self.repo.refs:
                if ref.name in ['origin/main', 'origin/master', 'main', 'master']:
                    target_branch = ref.name
                    break

            return {
                "current_branch": current_branch,
                "target_branch": target_branch or "master",
                # Default to master if no target found
                "remote_url": remote_url
            }
        except Exception as e:
            raise Exception(f"Failed to get repository context: {str(e)}")

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

    def _get_diff_content(self, diff):
        """Extract the content from a diff object"""
        try:
            if hasattr(diff, 'diff'):
                diff_data = diff.diff
                if isinstance(diff_data, bytes):
                    return diff_data.decode('utf-8', errors='replace')
                return str(diff_data)
            return "(no diff available)"
        except:
            return "(binary file)"