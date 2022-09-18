#!/usr/bin/env bash

cd /Users/kasterma

# ssh-keygen -t ecdsa -b 521
# git clone git@github.com:kasterma/dotfiles.git dotfiles-gh  # needs ssh keys setup
# git clone git@github.com:kasterma/notes.git
# git clone git@bitbucket.org:kasterma/dotfiles.git

ln -s dotfiles-gh/dotbash_profile .bash_profile
ln -s dotfiles-gh/dotbashrc .bashrc
ln -s dotfiles/dotgitconfig .gitconfig
ln -s dotfiles/dotgitignore_global .gitignore_global
ln -s dotfiles-gh/dottmux.conf .tmux.conf
ln -s dotfiles-gh/dotemacs .emacs

# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew analytics off
brew install pyenv bash-completion emacs tmux coreutils findutils gnu-tar gnu-sed gawk gnutls gnu-indent gnu-getopt
brew install tree parallel git
brew install --cask keepassxc

# https://www.virtualbox.org/
# https://www.vagrantup.com/downloads.html
