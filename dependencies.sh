#!/bin/bash

# Define the list of Python dependencies to install.
DEPENDENCIES=(
    "plotly"
    "scipy"
    "numpy"
    "pandas"
    "dash"
    "dash_mantine_components"
)

# Function to install Python packages
install_dependencies() {
    echo "Installing Python dependencies..."
    for package in "${DEPENDENCIES[@]}"; do
        echo "Installing ${package}..."
        pip install "${package}"
    done
    echo "All dependencies have been installed."
}

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found, attempting to install it."
    # Attempt to install pip. Adjust this command if you're using a specific version of Python.
    # For Python 3.x, you might need to use `python3` and `pip3`.
    if command -v python &> /dev/null; then
        python -m ensurepip --upgrade
    elif command -v python3 &> /dev/null; then
        python3 -m ensurepip --upgrade
    else
        echo "Python is not installed. Please install Python before continuing."
        exit 1
    fi
fi

# Upgrade pip to its latest version
python -m pip install --upgrade pip

# Call the function to install dependencies
install_dependencies
