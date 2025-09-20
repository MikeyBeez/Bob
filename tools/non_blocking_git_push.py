import asyncio
import sys

async def non_blocking_git_push(repo_path: str, remote: str, branch: str):
    """
    Asynchronously pushes a git branch to a remote repository.

    Args:
        repo_path (str): The path to the git repository.
        remote (str): The name of the remote to push to.
        branch (str): The name of the branch to push.

    Returns:
        bool: True if the push was successful, False otherwise.
    """
    git_command = [
        "git",
        "-C",
        repo_path,
        "push",
        remote,
        branch,
    ]

    print(f"Executing command: {' '.join(git_command)}")

    process = await asyncio.create_subprocess_exec(
        *git_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print("Git push successful.")
        if stdout:
            print(f"[stdout]:\n{stdout.decode()}")
        return True
    else:
        print(f"Git push failed with return code {process.returncode}.")
        if stderr:
            print(f"[stderr]:\n{stderr.decode()}")
        return False

async def main():
    """
    Main function to test the non_blocking_git_push function.
    """
    if len(sys.argv) != 4:
        print("Usage: python non_blocking_git_push.py <repo_path> <remote> <branch>")
        sys.exit(1)

    repo_path = sys.argv[1]
    remote = sys.argv[2]
    branch = sys.argv[3]

    success = await non_blocking_git_push(repo_path, remote, branch)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
