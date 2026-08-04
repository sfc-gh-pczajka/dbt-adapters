"""Patch pyproject.toml and hatch.toml to use the Snowflake universal driver.

Usage:
    python scripts/patch_universal_driver.py <git-ref> [owner/repo]

Removes snowflake-connector-python from pyproject.toml and injects
a pip install of the universal driver into hatch.toml pre-install-commands.
"""

import sys

DEFAULT_UD_REPO = "snowflakedb/universal-driver"


def patch_pyproject(path="pyproject.toml"):
    with open(path) as f:
        lines = f.readlines()
    with open(path, "w") as f:
        for line in lines:
            if "snowflake-connector-python" not in line:
                f.write(line)


def patch_hatch(path="hatch.toml", *, ud_ref: str, ud_repo: str = DEFAULT_UD_REPO):
    ud_pip = f"pip install 'git+https://github.com/{ud_repo}@{ud_ref}#subdirectory=python'"
    with open(path) as f:
        content = f.read()
    content = content.replace(
        "pre-install-commands = [",
        f'pre-install-commands = [\n    "{ud_pip}",',
        1,
    )
    with open(path, "w") as f:
        f.write(content)


def show_results():
    print("=== pyproject.toml dependencies ===")
    with open("pyproject.toml") as f:
        in_deps = False
        for line in f:
            if "dependencies" in line and "[" in line:
                in_deps = True
            if in_deps:
                print(line, end="")
            if in_deps and "]" in line:
                break

    print("\n=== hatch.toml pre-install-commands ===")
    with open("hatch.toml") as f:
        in_pre = False
        for line in f:
            if "pre-install-commands" in line:
                in_pre = True
            if in_pre:
                print(line, end="")
            if in_pre and "]" in line:
                break


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(f"Usage: {sys.argv[0]} <universal-driver-git-ref> [owner/repo]", file=sys.stderr)
        sys.exit(1)

    ref = sys.argv[1]
    repo = sys.argv[2] if len(sys.argv) == 3 else DEFAULT_UD_REPO
    patch_pyproject()
    patch_hatch(ud_ref=ref, ud_repo=repo)
    show_results()
