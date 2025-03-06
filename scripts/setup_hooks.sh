#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Lefthook
install_lefthook() {
    echo "Installing Lefthook..."
    if command_exists npm; then
        npm install -g @evilmartians/lefthook
    elif command_exists yarn; then
        yarn global add @evilmartians/lefthook
    else
        echo "Error: npm or yarn is required to install Lefthook"
        exit 1
    fi
}

# Function to check if git hooks are already configured
check_git_hooks() {
    if [ -f ".git/hooks/pre-commit" ]; then
        echo "Git hooks are already configured"
        return 0
    else
        return 1
    fi
}

# Main setup process
echo "Setting up Git hooks with Lefthook..."

# Check if Lefthook is installed
if ! command_exists lefthook; then
    echo "Lefthook is not installed. Installing..."
    install_lefthook
fi

# Check if git hooks are already configured
if check_git_hooks; then
    echo "Git hooks are already configured. Skipping..."
else
    echo "Configuring Git hooks..."
    lefthook install
fi

# Verify installation
if command_exists lefthook; then
    echo "Lefthook setup completed successfully!"
    echo "Your pre-commit hooks are now configured to run:"
    echo "- Black formatting check"
    echo "- Flake8 linting"
else
    echo "Error: Lefthook installation failed"
    exit 1
fi 