#!/usr/bin/env python3

# originally based on powerline-shell.py, but simplified lots.  Only
# in the git repo collection original code remains.
# also detect if in tmux and have text ready to send to tmux status.

import os
import os.path
import pathlib
import re
import subprocess
import sys
from time import strftime, localtime
import click


proc_env = {
    "LANG": "C",
    "HOME": os.getenv("HOME"),
    "PATH": os.getenv("PATH"),
}


class GitRepo:
    def __init__(self, debug=False):
        self.in_git_repo, self.status = self._git_status(debug)
        if not self.in_git_repo:
            return

        self._branch_info = self._parse_git_branch_info(self.status)
        if debug:
            print(self._branch_info)

        if not self._branch_info:
            self.detached_head = self._get_git_detached_branch()
            return
        else:
            self.detached_head = None

        self.local = self._branch_info["local"]
        self.remote = self._branch_info["remote"]
        self.ahead = self._branch_info["ahead"] or 0
        self.behind = self._branch_info["behind"] or 0
        self.untracked = 0
        self.changed = 0
        self.staged = 0
        self.conflicted = 0

        for statusline in self.status[1:]:
            code = statusline[:2]
            if code == "??":
                self.untracked += 1
            elif code in ("DD", "AU", "UD", "UA", "DU", "AA", "UU"):
                self.conflicted += 1
            else:
                if code[1] != " ":
                    self.changed += 1
                if code[0] != " ":
                    self.staged += 1

    @staticmethod
    def _git_status(debug):
        p = subprocess.Popen(
            ["git", "status", "--porcelain", "-b"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=proc_env,
        )

        pdata = p.communicate()
        if debug:
            print(pdata)
        return p.returncode == 0, pdata[0].decode("utf-8").splitlines()

    @staticmethod
    def _parse_git_branch_info(status):
        info = re.search(
            "^## (?P<local>\S+?)"
            "(\.{3}(?P<remote>\S+?)( \[(ahead (?P<ahead>\d+)(, )?)?(behind (?P<behind>\d+))?\])?)?$",
            status[0],
        )
        return info.groupdict() if info else None

    @staticmethod
    def _get_git_detached_branch():
        p = subprocess.Popen(
            ["git", "describe", "--tags", "--always"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=proc_env,
        )
        detached_ref = p.communicate()[0].decode("utf-8").rstrip("\n")
        if p.returncode == 0:
            branch = "{} {}".format("detached", detached_ref)
        else:
            branch = "Big Bang"
        return branch

    def __str__(self):
        if self.in_git_repo:
            if self.detached_head:
                return self.detached_head
            else:
                stat = ",".join(
                    [
                        x
                        for x in [
                            f"ahead {self.ahead}" if self.ahead else "",
                            f"behind {self.behind}" if self.behind else "",
                            f"untracked {self.untracked}" if self.untracked else "",
                            f"conflicted {self.conflicted}" if self.conflicted else "",
                            f"{self.changed}" if self.changed else "",
                        ]
                        if x
                    ]
                )
                return f"{self.local}:{stat}"
        else:
            return ""


def git():
    gd = GitRepo()
    git_str = str(gd)
    if git_str:
        return f"(git {git_str})"


def jobs():
    output_proc = subprocess.Popen(["ps", "-a", "-o", "ppid"], stdout=subprocess.PIPE)
    output = output_proc.communicate()[0].decode("utf-8")
    num_jobs = len(re.findall(str(os.getppid()), output)) - 1

    if num_jobs > 0:
        return f"(jobs {num_jobs})"


def k8s():
    output_proc = subprocess.Popen(
        ["kubectl config get-contexts | grep '\*'"], stdout=subprocess.PIPE, shell=True
    )
    output = output_proc.communicate()[0].decode("utf-8").strip().split()[2::2]
    if output:
        return f"(k8s {', '.join(output)})"


def time(timer):
    if timer > 2:
        return f'(took {timer}s)'
    else:
        return ""


def prompt(last_status):
    if last_status != 0:
        prompt = (
            f"\\[\\e[38;5;15m\\]\\[\\e[48;5;161m\\] :-( {last_status} \\[\\e[0m\\] $ "
        )
    else:
        prompt = "$ "
    return "\n" + prompt


def cwd():
    cwd = re.sub(str(pathlib.Path.home()), "~", str(pathlib.Path.cwd()))

    return f"(cwd {cwd})"


def virtual_env():
    env = (
        os.getenv("VIRTUAL_ENV")
        or os.getenv("CONDA_ENV_PATH")
        or os.getenv("CONDA_DEFAULT_ENV")
    )
    if env is None:
        return

    venv_path = pathlib.Path(env)
    env_name = (
        "/".join(venv_path.parts[-2:])
        if pathlib.Path.cwd() != venv_path.parent
        else pathlib.Path(env).stem
    )
    return f"(venv {env_name})"


@click.command()
@click.option("--last-status", type=int)
@click.option("--timer", type=int)
@click.option("--tmux/--no-tmux", type=bool, default=False)
def cli(last_status, timer, tmux):
    if tmux:
        print(" ".join(filter(lambda x: x and len(x) > 0, ["->", k8s()])))
    else:
        # No idea why PyCharm sets TMUX variable (why it is set in that context)
        if os.getenv("TMUX", None) and not os.getenv("TERMINAL_EMULATOR"):
            fns = [lambda: "  ", cwd, virtual_env, git, jobs, lambda: time(timer), lambda: prompt(last_status)]
        else:
            fns = [lambda: "  ", cwd, virtual_env, git, k8s, jobs, lambda: time(timer), lambda: prompt(last_status)]
        print(
            " ".join(
                filter(lambda x: x and len(x) > 0, [f() for f in fns])
            )
        )

cli()
