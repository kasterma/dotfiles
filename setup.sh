#!/usr/bin/env bash

cd /Users/kasterma

git clone git@github.com:kasterma/dotfiles.git dotfiles-gh  # needs ssh keys setup

ln -s dotfiles-gh/dotbash_profile .bash_profile
ln -s dotfiles-gh/dotbashrc .bashrc
ln -s dotfiles/dotgitconfig .gitconfig
ln -s dotfiles/dotgitignore_global .gitignore_global
ln -s dotfiles-gh/dottmux.conf .tmux.conf
ln -s dotfiles-gh/dotemacs .emacs

brew install pyenv bash-completions age
