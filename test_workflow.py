#!/usr/bin/env python3
"""
Test workflow script for Hypha Apps CLI Demo

This script demonstrates a complete workflow:
1. Install the demo app
2. Start the app
3. List running apps
4. Stop the app
5. Uninstall the app

Usage:
    python test_workflow.py

Make sure your .env file is configured before running this script.
"""

import os
import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a CLI command and print results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out!")
        return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False
    
    return True

def main():
    print("🚀 Starting Hypha Apps CLI Test Workflow")
    print("Make sure your .env file is configured!")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n❌ No .env file found!")
        print("Please create a .env file with your Hypha server configuration.")
        print("See the README.md for instructions.")
        sys.exit(1)
    
    app_id = "hello-demo-test"
    
    commands = [
        (f"python -m hypha_rpc.utils.hypha_apps_cli install --app-id {app_id} --manifest=manifest.yaml --source=main.py --overwrite", 
         "Installing demo app"),
        (f"python -m hypha_rpc.utils.hypha_apps_cli start --app-id {app_id}", 
         "Starting the app"),
        ("python -m hypha_rpc.utils.hypha_apps_cli list-running", 
         "Listing running apps"),
        (f"python -m hypha_rpc.utils.hypha_apps_cli stop --app-id {app_id}", 
         "Stopping the app"),
        (f"python -m hypha_rpc.utils.hypha_apps_cli uninstall --app-id {app_id}", 
         "Uninstalling the app"),
    ]
    
    success_count = 0
    
    for cmd, description in commands:
        if run_command(cmd, description):
            success_count += 1
            # Small delay between commands
            time.sleep(1)
        else:
            print(f"\n⚠️  Stopping workflow due to failed command: {description}")
            break
    
    print(f"\n{'='*60}")
    print(f"🏁 Workflow Complete!")
    print(f"✅ {success_count}/{len(commands)} commands succeeded")
    
    if success_count == len(commands):
        print("🎉 All tests passed! Your Hypha Apps CLI setup is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your configuration and try again.")
        print("Make sure your .env file contains valid credentials.")

if __name__ == "__main__":
    main() 