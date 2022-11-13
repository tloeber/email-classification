#!/bin/bash

# Settings to adjust:
# ===================
GIT_REPO_URL="https://github.com/tloeber/email-classification.git"


# GitHub
# ======
git config --global user.name tloeber
git config --global user.email thomas.loeber73@gmail.com
cd ~ && \
    git clone $GIT_REPO_URL

git config credential.helper 'cache --timeout=604800'

# Bash aliases
# ============
wget https://raw.githubusercontent.com/tloeber/utils_and_configs/main/dotfiles/bash_aliases \
    -O ~/.bash_aliases
# There are no dotfiles in ~ (i.e., /root/) to modify, so use the ones in /etc
echo "source ~/.bash_aliases" >> /etc/bash.bashrc

# Python packages
# ===============

# Incl. sklearn so version can be updated to work with imblearn 
pip install python-dotenv  scikit-learn imbalanced-learn 
