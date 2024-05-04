#!/bin/bash

cd "$(dirname "$0")"

# Base Path Setting
export PATH=/bin
export PATH=/usr/bin:$PATH
export PATH=/usr/local/bin:$PATH
export PATH=/sbin:$PATH
export PATH=/usr/sbin:$PATH
export PATH=/opt/homebrew/bin:$PATH
export PATH=/opt/homebrew/sbin:$PATH

# Python Path Setting
MINICONDA_DIR="$(pwd)/tools/miniconda3"
PYTHONHOME="$MINICONDA_DIR/bin"
export PATH="$(pwd):$PATH"
export PATH="$PYTHONHOME:$PATH"
export PYTHONPATH=$PATH

# Checking whether Miniconda has been installed
if [ -d "$MINICONDA_DIR" ]; then
    echo "Miniconda is already installed in $MINICONDA_DIR"
else
    # Installing Miniconda
    echo "Miniconda is not installed. Installing Miniconda..."
    MINICONDA_INSTALLER_SCRIPT=Miniconda3-py312_24.3.0-0-MacOSX-x86_64.sh
    curl -o $MINICONDA_INSTALLER_SCRIPT https://repo.anaconda.com/miniconda/$MINICONDA_INSTALLER_SCRIPT
    bash $MINICONDA_INSTALLER_SCRIPT -b -p $MINICONDA_DIR
    rm $MINICONDA_INSTALLER_SCRIPT
    echo "Miniconda has been installed to $MINICONDA_DIR"

    # Installing Python library
    echo "Installing Python library..."
    pip install -r requirements.txt
    echo "Setup completed."
fi
# Check Python version
python -V

# Run GUI tool
python jhdsfinder/gui/main.py

