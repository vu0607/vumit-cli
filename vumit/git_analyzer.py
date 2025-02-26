import os
from git import Repo
from git.exc import InvalidGitRepositoryError

class GitAnalyzer:
    def __init__(self):
        try:
            self.repo = Repo(os.getcwd(), search_parent_directories=True)
        except InvalidGitRepositoryError:
            raise Exception("Not a git repository")

    def get_branch_commits(self, target_branch="dev"):
        """Get all commits that are in the current branch but not in the target branch"""
        try:
            current_branch = self.repo.active_branch
            print(f"Current branch: {current_branch.name}")  # Debug log

            # If we're on the target branch, there's nothing to compare
            if current_branch.name == target_branch:
                print(f"Currently on target branch {target_branch}, no commits to analyze")
                return []

            # Try to find the target branch in local and remote refs
            target = None
            potential_refs = [
                target_branch,                    # Local branch
                f"origin/{target_branch}",        # Remote branch
                f"refs/remotes/origin/{target_branch}"  # Full remote ref
            ]

            print(f"Looking for target branch: {target_branch}")  # Debug log
            for ref_name in potential_refs:
                try:
                    target = self.repo.refs[ref_name]
                    print(f"Found target branch: {ref_name}")  # Debug log
                    break
                except (IndexError, KeyError):
                    print(f"Target branch not found at: {ref_name}")  # Debug log
                    continue

            if not target:
                # If target branch not found, try fallbacks
                fallbacks = ['main', 'master', 'dev']  # Changed order to prioritize main
                print("Trying fallback branches...")  # Debug log
                for name in fallbacks:
                    if name == target_branch:
                        continue  # Skip if it's the same as target_branch
                    try:
                        target = self.repo.refs[name]
                        print(f"Found fallback branch: {name}")  # Debug log
                        break
                    except (IndexError, KeyError):
                        try:
                            target = self.repo.refs[f"origin/{name}"]
                            print(f"Found fallback branch: origin/{name}")  # Debug log
                            break
                        except (IndexError, KeyError):
                            print(f"Fallback branch not found: {name}")  # Debug log
                            continue

            if not target:
                print("No target branch found, using all commits in current branch")  # Debug log
                commits_iter = self.repo.iter_commits(current_branch.name)
            else:
                try:
                    # Use symmetric difference to get commits unique to current branch
                    commits_iter = self.repo.iter_commits(f"{target.commit.hexsha}...{current_branch.commit.hexsha}")
                    print(f"Comparing commits between {target.name} and {current_branch.name}")  # Debug log
                except Exception as e:
                    print(f"Error comparing branches: {e}")  # Debug log
                    # Fallback: get recent commits from current branch
                    commits_iter = self.repo.iter_commits(current_branch.name, max_count=10)

            # Get commits that are in current branch but not in target branch
            commits = []
            for commit in commits_iter:
                # Skip commits that are in the target branch
                if target and commit in self.repo.iter_commits(target.name):
                    print(f"Skipping commit {commit.hexsha[:7]} - present in target branch")  # Debug log
                    continue

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
                print(f"Found commit: {commit.hexsha[:7]} - {commit.message.strip()}")  # Debug log

            print(f"Total commits found: {len(commits)}")  # Debug log
            return commits

        except Exception as e:
            raise Exception(f"Failed to get branch commits: {str(e)}")

    def get_repository_context(self):
        """Get relevant context about the repository"""
        try:
            current_branch = self.repo.active_branch.name
            remote_url = next(self.repo.remotes.origin.urls) if self.repo.remotes else None

            # Get the target branch (main/master)
            target_branch = None
            for ref in self.repo.refs:
                if ref.name in ['origin/main', 'main', 'origin/master', 'master', 'origin/dev', 'dev']:
                    target_branch = ref.name
                    break

            return {
                "current_branch": current_branch,
                "target_branch": target_branch or "main",  # Default to main if no target found
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