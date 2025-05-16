#!/usr/bin/env python3
"""
Easy run script for the Pocket AI e-commerce agent.
This script provides a colorful interactive interface to set up and run the application.
"""

import os
import sys
import subprocess
import time
import platform
import shutil

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color, bold=False):
    """Print text with color and optional bold formatting."""
    bold_code = Colors.BOLD if bold else ''
    print(f"{bold_code}{color}{text}{Colors.END}")

def print_header():
    """Print a stylish header for the script."""
    print("\n" + "=" * 70)
    print_colored("                Pocket AI E-COMMERCE AGENT", Colors.PURPLE, bold=True)
    print_colored("              Python Implementation - Startup", Colors.PURPLE, bold=True)
    print("=" * 70 + "\n")

def check_python_version():
    """Check if Python version is adequate."""
    print_colored("→ Checking Python version...", Colors.BLUE)
    
    major, minor, _ = platform.python_version_tuple()
    
    if int(major) < 3 or (int(major) == 3 and int(minor) < 8):
        print_colored("✘ Python 3.8 or higher is required!", Colors.RED)
        print_colored(f"  You are using Python {platform.python_version()}", Colors.RED)
        print_colored("  Please upgrade your Python installation.", Colors.RED)
        return False
    
    print_colored(f"✓ Using Python {platform.python_version()}", Colors.GREEN)
    return True

def check_pip():
    """Check if pip is installed."""
    print_colored("→ Checking pip installation...", Colors.BLUE)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print_colored("✓ pip is installed", Colors.GREEN)
        return True
    except subprocess.CalledProcessError:
        print_colored("✘ pip is not installed or not working correctly", Colors.RED)
        print_colored("  Please install pip to continue.", Colors.RED)
        return False

def install_dependencies():
    """Install required Python packages."""
    print_colored("→ Checking and installing dependencies...", Colors.BLUE)
    
    try:
        # Check if we need to install requirements
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        installed_packages = result.stdout.splitlines()
        
        # Read requirements file
        with open("requirements.txt", "r") as file:
            requirements = [line.strip() for line in file.readlines() if line.strip()]
        
        # Extract package names without versions to check if they're installed
        installed_package_names = [pkg.split("==")[0].lower() for pkg in installed_packages]
        required_package_names = [req.split(">=")[0].lower() for req in requirements]
        
        # Check if all required packages are installed
        missing_packages = [req for req_name, req in zip(required_package_names, requirements) 
                           if req_name not in installed_package_names]
        
        if missing_packages:
            print_colored(f"  Installing {len(missing_packages)} missing packages...", Colors.YELLOW)
            
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print_colored("✓ All dependencies installed successfully", Colors.GREEN)
        else:
            print_colored("✓ All dependencies are already installed", Colors.GREEN)
        
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"✘ Failed to install dependencies", Colors.RED)
        print_colored(f"  Error: {e}", Colors.RED)
        return False
    except Exception as e:
        print_colored(f"✘ An unexpected error occurred: {e}", Colors.RED)
        return False

def check_ollama():
    """Check if Ollama is installed."""
    print_colored("→ Checking Ollama installation...", Colors.BLUE)
    
    ollama_path = shutil.which("ollama")
    if ollama_path:
        print_colored(f"✓ Ollama is installed at: {ollama_path}", Colors.GREEN)
        return True
    else:
        print_colored("✘ Ollama is not installed", Colors.RED)
        print_colored("  Please install Ollama: https://ollama.ai/download", Colors.RED)
        print_colored("  After installing, restart this script.", Colors.RED)
        return False

def run_application():
    """Run the application using the start.py script."""
    print_colored("\n→ Starting Pocket AI E-commerce Agent...", Colors.BLUE, bold=True)
    
    try:
        subprocess.run(
            [sys.executable, "start.py"],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"✘ Failed to start the application", Colors.RED)
        print_colored(f"  Error code: {e.returncode}", Colors.RED)
        return False
    except KeyboardInterrupt:
        print_colored("\n→ Application stopped by user", Colors.YELLOW)
        return True
    except Exception as e:
        print_colored(f"✘ An unexpected error occurred: {e}", Colors.RED)
        return False

def main():
    """Main entry point for the script."""
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_pip():
        return 1
    
    if not install_dependencies():
        return 1
    
    if not check_ollama():
        return 1
    
    # Run the application
    if not run_application():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 