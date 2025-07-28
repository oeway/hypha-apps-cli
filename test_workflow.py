#!/usr/bin/env python3
"""
Test workflow script for Hypha Apps CLI Demo

This script demonstrates a complete workflow with app IDs and session IDs:
1. Install demo apps (creates app definitions with app_ids)
2. Start apps (creates running sessions with session_ids)
3. List running apps (shows both session_ids and their corresponding app_ids)
4. Stop specific sessions (using session_ids, not app_ids)
5. Uninstall apps (removes app definitions)

Key concepts tested:
- app_id: The identifier for an installed app definition (like a "class")
- session_id: The identifier for a running instance of an app (like an "object")
- Stop command now requires session_id (specific instance) not app_id (definition)

Usage:
    python test_workflow.py

Make sure your .env file is configured before running this script.
"""

import os
import subprocess
import sys
import time
import re

def run_command(cmd, description, capture_session_id=False):
    """Run a CLI command and print results, optionally capture session ID"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    session_id = None
    
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
                
                # Extract session ID from start command output
                if capture_session_id and "with session ID:" in result.stdout:
                    match = re.search(r"with session ID: ([^\s\n]+)", result.stdout)
                    if match:
                        session_id = match.group(1)
                        print(f"📝 Captured session ID: {session_id}")
        else:
            print("❌ Failed!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
            return False, None
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out!")
        return False, None
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False, None
    
    return True, session_id

def main():
    print("🚀 Starting Hypha Apps CLI Test Workflow")
    print("This test demonstrates app_id (definitions) vs session_id (running instances)")
    print("Make sure your .env file is configured!")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n❌ No .env file found!")
        print("Please create a .env file with your Hypha server configuration.")
        print("See the README.md for instructions.")
        sys.exit(1)
    
    app_id = "hello-demo-test"
    app_id_with_files = f"{app_id}-with-files"
    
    print(f"\n📋 Test Plan:")
    print(f"  • Install 2 app definitions: '{app_id}' and '{app_id_with_files}'")
    print(f"  • Start sessions from each app (capture unique session_ids)")
    print(f"  • List running sessions (see both session_ids and app_ids)")
    print(f"  • Stop specific sessions using session_ids (not app_ids)")
    print(f"  • Uninstall app definitions")
    
    # Track session IDs for stopping
    session_ids = {}
    
    # Step 1: Install basic app
    success, _ = run_command(
        f"python -m hypha_apps_cli install --app-id {app_id} --manifest=manifest.yaml --source=main.py --overwrite",
        f"Installing demo app definition (app_id: {app_id})"
    )
    if not success:
        print("❌ Failed to install basic app")
        return
    
    # Step 2: Start basic app and capture session ID
    success, session_id = run_command(
        f"python -m hypha_apps_cli start --app-id {app_id}",
        f"Starting app session from app_id '{app_id}' (creates session_id)",
        capture_session_id=True
    )
    if not success:
        print("❌ Failed to start basic app")
        return
    if session_id:
        session_ids[app_id] = session_id
    
    # Step 3: Stop basic app using session ID
    if app_id in session_ids:
        success, _ = run_command(
            f"python -m hypha_apps_cli stop --session-id {session_ids[app_id]}",
            f"Stopping session '{session_ids[app_id]}' (specific instance)"
        )
        if not success:
            print("❌ Failed to stop basic app session")
            return
    else:
        print("⚠️ Skipping stop - no session ID captured")
    
    # Step 4: Install app with files
    success, _ = run_command(
        f"python -m hypha_apps_cli install --app-id {app_id_with_files} --manifest=manifest.yaml --source=main.py --files=example-files --overwrite",
        f"Installing demo app with files (app_id: {app_id_with_files})"
    )
    if not success:
        print("❌ Failed to install app with files")
        return
    
    # Step 5: Start app with files and capture session ID
    success, session_id = run_command(
        f"python -m hypha_apps_cli start --app-id {app_id_with_files}",
        f"Starting app session from app_id '{app_id_with_files}' (creates session_id)",
        capture_session_id=True
    )
    if not success:
        print("❌ Failed to start app with files")
        return
    if session_id:
        session_ids[app_id_with_files] = session_id
    
    # Step 6: List running apps to see both session IDs and app IDs
    success, _ = run_command(
        "python -m hypha_apps_cli list-running",
        "Listing running app sessions (shows session_ids and app_ids)"
    )
    if not success:
        print("❌ Failed to list running apps")
        return
    
    # Step 7: Stop app with files using session ID
    if app_id_with_files in session_ids:
        success, _ = run_command(
            f"python -m hypha_apps_cli stop --session-id {session_ids[app_id_with_files]}",
            f"Stopping session '{session_ids[app_id_with_files]}' (specific instance)"
        )
        if not success:
            print("❌ Failed to stop app with files session")
            return
    else:
        print("⚠️ Skipping stop - no session ID captured")
    
    # Steps 8-9: Uninstall apps
    remaining_commands = [
        (f"python -m hypha_apps_cli uninstall --app-id {app_id}", 
         f"Uninstalling app definition (app_id: {app_id})"),
        (f"python -m hypha_apps_cli uninstall --app-id {app_id_with_files}", 
         f"Uninstalling app definition (app_id: {app_id_with_files})"),
    ]
    
    success_count = 7  # We've completed 7 steps successfully so far
    
    for cmd, description in remaining_commands:
        success, _ = run_command(cmd, description)
        if success:
            success_count += 1
            time.sleep(1)
        else:
            print(f"\n⚠️  Stopping workflow due to failed command: {description}")
            break
    
    total_steps = 9  # Total number of workflow steps
    
    print(f"\n{'='*60}")
    print(f"🏁 Workflow Complete!")
    print(f"✅ {success_count}/{total_steps} steps succeeded")
    
    if success_count == total_steps:
        print("🎉 All tests passed! Your Hypha Apps CLI setup is working correctly.")
        print("✨ You've successfully tested both app_id (definitions) and session_id (instances) concepts!")
        print("🔑 Key learning: Stop command now uses session_id (specific instance) not app_id (definition)")
    else:
        print("⚠️  Some tests failed. Check your configuration and try again.")
        print("Make sure your .env file contains valid credentials.")
        print("💡 Remember: app_id = installed definition, session_id = running instance")
        print("🔑 Important: Stop command requires session_id, get it from list-running or start output")

if __name__ == "__main__":
    main() 