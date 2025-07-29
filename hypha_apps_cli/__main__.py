import os
import sys
import json
import base64
import mimetypes
import argparse
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv, find_dotenv
from hypha_rpc import connect_to_server, login
import yaml
import glob


load_dotenv(dotenv_path=find_dotenv(usecwd=True))

def get_bool_env(varname: str, default: bool = False) -> bool:
    val = os.getenv(varname)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")

def get_token_file_path() -> Path:
    """Get the path to the token cache file."""
    return Path.cwd() / ".hypha_token"

def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired by parsing its payload."""
    try:
        # JWT has 3 parts: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return True
        
        # Decode the payload (second part)
        payload_b64 = parts[1]
        # Add padding if needed for base64 decoding
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_bytes = base64.b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Check expiration time
        exp = payload.get('exp')
        if exp is None:
            return True
        
        current_time = int(time.time())
        return current_time >= exp
        
    except Exception:
        # If we can't parse the token, consider it expired
        return True

def save_token_to_file(token: str) -> None:
    """Save token to local cache file."""
    try:
        token_file = get_token_file_path()
        with open(token_file, 'w', encoding='utf-8') as f:
            f.write(token)
        # Set file permissions to be readable only by owner
        token_file.chmod(0o600)
        print(f"💾 Token saved to {token_file}")
    except Exception as e:
        print(f"⚠️ Warning: Could not save token to file: {e}")

def load_token_from_file() -> Optional[str]:
    """Load token from local cache file and validate it."""
    token_file = get_token_file_path()
    
    if not token_file.exists():
        return None
    
    try:
        with open(token_file, 'r', encoding='utf-8') as f:
            token = f.read().strip()
        
        if is_token_expired(token):
            print("🔄 Cached token has expired, removing token file")
            token_file.unlink()
            return None
        
        print(f"✅ Using cached token from file: {token_file}")
        return token
        
    except Exception as e:
        print(f"⚠️ Warning: Could not load token from file: {e}")
        # Try to remove corrupted token file
        try:
            token_file.unlink()
        except:
            pass
        return None

def get_token_expiration_info(token: str) -> Dict[str, Any]:
    """Get expiration information from a JWT token."""
    try:
        # JWT has 3 parts: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return {"valid": False, "error": "Invalid JWT format"}
        
        # Decode the payload (second part)
        payload_b64 = parts[1]
        # Add padding if needed for base64 decoding
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_bytes = base64.b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Check expiration time
        exp = payload.get('exp')
        if exp is None:
            return {"valid": False, "error": "No expiration time in token"}
        
        current_time = int(time.time())
        expires_in_seconds = exp - current_time
        is_expired = expires_in_seconds <= 0
        
        return {
            "valid": True,
            "exp_timestamp": exp,
            "current_timestamp": current_time,
            "expires_in_seconds": expires_in_seconds,
            "is_expired": is_expired,
            "expires_in_human": format_time_remaining(expires_in_seconds)
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

def format_time_remaining(seconds: int) -> str:
    """Format time remaining in a human-readable way."""
    if seconds <= 0:
        return "EXPIRED"
    
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes} minutes"
        else:
            return f"{minutes} minutes {remaining_seconds} seconds"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes == 0:
            return f"{hours} hours"
        else:
            return f"{hours} hours {remaining_minutes} minutes"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours == 0:
            return f"{days} days"
        else:
            return f"{days} days {remaining_hours} hours"

async def connect(disable_ssl: bool = False) -> Any:
    server_url = os.getenv("HYPHA_SERVER_URL")
    workspace = os.getenv("HYPHA_WORKSPACE")
    client_id = os.getenv("HYPHA_CLIENT_ID", "hypha-apps-cli")

    # ssl should be False (to disable SSL) or None (to enable SSL)
    ssl = False if disable_ssl else None

    token = None
    
    # Try to get token from environment variable first
    token = os.getenv("HYPHA_TOKEN")
    
    # If no env token, try to load from cached file
    if not token:
        token = load_token_from_file()
    
    # If still no token, provide clear error message
    if not token:
        print("❌ No authentication token found!", file=sys.stderr)
        print("", file=sys.stderr)
        print("Please authenticate using one of these methods:", file=sys.stderr)
        print("", file=sys.stderr)
        print("🔐 Method 1 (Recommended): Use the login command", file=sys.stderr)
        print("   python -m hypha_apps_cli login", file=sys.stderr)
        print("", file=sys.stderr)
        print("🔧 Method 2: Set environment variable", file=sys.stderr)
        print("   Add HYPHA_TOKEN=your_token_here to your .env file", file=sys.stderr)
        print("   or export HYPHA_TOKEN=your_token_here", file=sys.stderr)
        print("", file=sys.stderr)
        sys.exit(1)

    if not all([server_url, workspace]):
        print("❌ Missing environment variables. Set HYPHA_SERVER_URL, HYPHA_WORKSPACE", file=sys.stderr)
        sys.exit(1)

    return await connect_to_server({
        "client_id": client_id,
        "server_url": server_url,
        "token": token,
        "workspace": workspace,
        "ssl": ssl,
    })

async def debug_token_info():
    """Debug token sources and caching status."""
    print("🔍 Token Debug Information")
    print("=" * 50)
    
    # Check environment variables
    server_url = os.getenv("HYPHA_SERVER_URL")
    workspace = os.getenv("HYPHA_WORKSPACE")
    env_token = os.getenv("HYPHA_TOKEN")
    disable_ssl_env = get_bool_env("HYPHA_DISABLE_SSL", False)
    
    print(f"📊 Environment Configuration:")
    print(f"  HYPHA_SERVER_URL: {server_url}")  
    print(f"  HYPHA_WORKSPACE: {workspace}")
    print(f"  HYPHA_TOKEN: {'SET' if env_token else 'NOT SET'}")
    if env_token:
        env_exp_info = get_token_expiration_info(env_token)
        if env_exp_info["valid"]:
            print(f"    └─ Expires in: {env_exp_info['expires_in_human']}")
        else:
            print(f"    └─ Token error: {env_exp_info['error']}")
    print(f"  HYPHA_DISABLE_SSL: {disable_ssl_env}")
    
    print(f"\n💾 Token File Information:")
    token_file = get_token_file_path()
    print(f"  Token file path: {token_file}")
    print(f"  Token file exists: {token_file.exists()}")
    
    if token_file.exists():
        try:
            file_stat = token_file.stat()
            file_mode = oct(file_stat.st_mode)[-3:]
            print(f"  Token file permissions: {file_mode}")
            print(f"  Token file size: {file_stat.st_size} bytes")
            
            # Check if we can load the token
            cached_token = load_token_from_file()
            print(f"  Cached token loadable: {cached_token is not None}")
            
            if cached_token:
                cached_exp_info = get_token_expiration_info(cached_token)
                if cached_exp_info["valid"]:
                    print(f"    └─ Expires in: {cached_exp_info['expires_in_human']}")
                else:
                    print(f"    └─ Token error: {cached_exp_info['error']}")
            
        except Exception as e:
            print(f"  Error reading token file: {e}")
    
    print(f"\n🔄 Token Resolution Order:")
    print(f"  1. Environment variable (HYPHA_TOKEN): {'✅ FOUND' if env_token else '❌ Not set'}")
    
    if not env_token:
        cached_token = load_token_from_file()
        print(f"  2. Cached token file: {'✅ FOUND' if cached_token else '❌ Not found/expired'}")
        if not cached_token:
            print(f"  3. Interactive login: ⏳ Would be prompted")
    else:
        print(f"  2. Cached token file: ⏭️ SKIPPED (env token takes precedence)")
        
    print(f"\n💡 Recommendations:")
    if env_token:
        print(f"  • Environment token found - cached tokens are bypassed")
        print(f"  • To use cached tokens, remove HYPHA_TOKEN from environment")
    elif not token_file.exists():
        print(f"  • No cached token found - run 'python -m hypha_apps_cli login' to create one")
    else:
        print(f"  • Token caching appears to be working correctly")


def progress_callback(info: Dict[str, Any]):
    emoji = {
        "info": "ℹ️",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "upload": "📤",
        "download": "📥"
    }.get(info.get("type", ""), "🔸")
    print(f"{emoji} {info.get('message', '')}")

def load_manifest(manifest_path: str) -> Dict[str, Any]:
    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return yaml.safe_load(content)

def infer_format_and_content(filepath: Path) -> Dict[str, Any]:
    mime_type, _ = mimetypes.guess_type(filepath)
    if mime_type == "application/json":
        with open(filepath, "r", encoding="utf-8") as f:
            return {
                "name": str(filepath),
                "content": json.load(f),
                "format": "json"
            }
    elif mime_type and mime_type.startswith("text/"):
        with open(filepath, "r", encoding="utf-8") as f:
            return {
                "name": str(filepath),
                "content": f.read(),
                "format": "text"
            }
    else:
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return {
                "name": str(filepath),
                "content": encoded,
                "format": "base64"
            }

def collect_files(path_input: Union[str, Path], source_path: Optional[Union[str, Path]] = None) -> List[Dict[str, Any]]:
    path_input = Path(path_input)
    
    # Resolve source root
    if source_path:
        source_path = Path(source_path).resolve()
        source_root = source_path.parent if source_path.is_file() else source_path
    else:
        source_root = None

    files = []

    # If it's a single file
    if path_input.is_file():
        file_data = infer_format_and_content(path_input)
        rel_path = path_input.relative_to(source_root) if source_root else path_input.name
        file_data["name"] = str(rel_path).replace("\\", "/")
        return [file_data]

    # If it's a glob pattern
    if any(c in path_input.name for c in "*?[]"):
        base_dir = path_input.parent.resolve()
        pattern = path_input.name
        matching_paths = list(base_dir.glob(pattern))
    else:
        base_dir = path_input.resolve()
        matching_paths = list(base_dir.rglob("*"))

    for path in matching_paths:
        if path.is_file():
            file_data = infer_format_and_content(path)
            if source_root:
                rel_path = path.relative_to(source_root)
            else:
                rel_path = path.relative_to(base_dir)
            file_data["name"] = str(rel_path).replace("\\", "/")
            files.append(file_data)

    return files


    return files
async def install_app(app_id: str, source_path: str, manifest_path: str, files_path: str, overwrite: bool = False, disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    controller = await api.get_service("public/server-apps")

    with open(source_path, "r", encoding="utf-8") as f:
        source = f.read()
    manifest = load_manifest(manifest_path)
    files = collect_files(path_input=files_path, source_path=source_path) if files_path else []

    print(f"📦 Installing app '{app_id}' from {source_path} with manifest {manifest_path}...")
    await controller.install(
        app_id=app_id,
        source=source,
        manifest=manifest,
        files=files,
        overwrite=overwrite,
        progress_callback=progress_callback
    )
    
    app_info = await controller.get_app_info(app_id)
    print(f"📦 App info: {json.dumps(app_info, indent=2)}")
    print(f"✅ App '{app_id}' successfully installed")
    await api.disconnect()

async def start_app(app_id: str, disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    controller = await api.get_service("public/server-apps")
    print(f"🚀 Starting app '{app_id}'...")
    started = await controller.start(app_id, timeout=30, progress_callback=progress_callback)
    print("✅ Available services:")
    for service in started.services:
        print(f"  - {service.id.split(':')[1]} ({service.get('name', '')}): {service.get('description', 'No description')}")
    print(f"🚀 Started app '{app_id}' with session ID: {started.id}")
    await api.disconnect()

async def stop_app(session_id: str, disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    controller = await api.get_service("public/server-apps")
    running = await controller.list_running()
    found = next((a for a in running if a.id == session_id), None)
    if not found:
        print(f"⚠️ Session '{session_id}' is not currently running.")
        await api.disconnect()
        return
    await controller.stop(session_id)
    print(f"🛑 Stopped session '{session_id}'.")
    await api.disconnect()

async def stop_all_apps(disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    controller = await api.get_service("public/server-apps")
    running = await controller.list_running()
    if not running:
        print("⚠️ No apps are currently running.")
        await api.disconnect()
        return
    for app in running:
        await controller.stop(app.id)
        print(f"🛑 Stopped app '{app.id}'.")
    await api.disconnect()

async def uninstall_app(app_id: str, disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    controller = await api.get_service("public/server-apps")
    await controller.uninstall(app_id)
    print(f"🗑️ Uninstalled app '{app_id}'")
    await api.disconnect()

async def list_apps(running: bool = False, disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    controller = await api.get_service("public/server-apps")
    if running:
        apps = await controller.list_running()
        print(f"🟢 Running apps ({len(apps)}):")
    else:
        apps = await controller.list_apps()
        print(f"📦 Installed apps ({len(apps)}):")

    for app in apps:
        if running:
            print(f"- {app.get('name')} (session id: `{app.id}`, app_id: `{app.get('app_id', '')}`): {app.get('description', 'No description')}")
        else:
            print(f"- {app.get('name')} (app_id: `{app.id}`): {app.get('description', 'No description')}")
    await api.disconnect()

async def list_services(disable_ssl: bool = False):
    api = await connect(disable_ssl=disable_ssl)
    services = await api.list_services()
    print(f"🔧 Available services ({len(services)}):")
    for svc in services:
        # use an emjoi for the service name
        print(f"🔧 {svc['id']}")
        print(f"  {json.dumps(svc, indent=2)}")
    await api.disconnect()

async def login_command(disable_ssl: bool = False):
    """Perform interactive login and cache token."""
    server_url = os.getenv("HYPHA_SERVER_URL")
    workspace = os.getenv("HYPHA_WORKSPACE")
    client_id = os.getenv("HYPHA_CLIENT_ID", "hypha-apps-cli")

    if not all([server_url, workspace]):
        print("❌ Missing environment variables. Set HYPHA_SERVER_URL, HYPHA_WORKSPACE", file=sys.stderr)
        sys.exit(1)

    # ssl should be False (to disable SSL) or None (to enable SSL)
    ssl = False if disable_ssl else None

    print(f"🔐 Logging in to {server_url} (workspace: {workspace})...")
    
    try:
        user_info = await login({"server_url": server_url, "ssl": ssl, "profile": True})
        token = user_info.get("token")
        
        if not token:
            print("❌ Login failed: No token received", file=sys.stderr)
            sys.exit(1)
        
        print(f"✅ Successfully logged in as user: {user_info.get('user_id', 'Unknown')}")
        
        # Save token to cache file
        save_token_to_file(token)
        
        # Show token caching status
        token_file = get_token_file_path()
        if token_file.exists():
            print(f"🔄 Token will be automatically used for subsequent commands")
            print(f"💡 To get a fresh token in the future, run 'python -m hypha_apps_cli login' again")
        else:
            print("⚠️ Warning: Token could not be saved to cache")
        
        print(f"✨ Ready to use Hypha Apps CLI!")
        
    except Exception as e:
        print(f"❌ Login failed: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Hypha Apps CLI")
    parser.add_argument("--disable-ssl", action="store_true", help="Disable SSL (set ssl=None)")
    subparsers = parser.add_subparsers(dest="command")

    install = subparsers.add_parser("install", help="Install an app")
    install.add_argument("--app-id", required=True)
    install.add_argument("--source", required=True)
    install.add_argument("--manifest", required=True)
    install.add_argument("--files", required=False)
    install.add_argument("--overwrite", action="store_true")

    start = subparsers.add_parser("start", help="Start an app")
    start.add_argument("--app-id", required=True)

    stop = subparsers.add_parser("stop", help="Stop a running app session")
    stop.add_argument("--session-id", required=True, help="Session ID of the running app instance to stop")
    
    stop_all = subparsers.add_parser("stop-all", help="Stop all running apps")
    stop_all.set_defaults(func=stop_all_apps)

    uninstall = subparsers.add_parser("uninstall", help="Uninstall an app")
    uninstall.add_argument("--app-id", required=True)

    subparsers.add_parser("debug-token", help="Debug token sources and caching status")
    subparsers.add_parser("login", help="Perform interactive login and cache token")

    subparsers.add_parser("list-installed", help="List all installed apps")
    subparsers.add_parser("list-running", help="List all currently running apps")
    subparsers.add_parser("list-services", help="List all available services")

    args = parser.parse_args()

    # CLI flags override env vars
    disable_ssl = getattr(args, "disable_ssl", False) or get_bool_env("HYPHA_DISABLE_SSL", False)

    if args.command == "install":
        asyncio.run(install_app(args.app_id, args.source, args.manifest, args.files, args.overwrite, disable_ssl=disable_ssl))
    elif args.command == "start":
        asyncio.run(start_app(args.app_id, disable_ssl=disable_ssl))
    elif args.command == "stop":
        asyncio.run(stop_app(args.session_id, disable_ssl=disable_ssl))
    elif args.command == "stop-all":
        asyncio.run(stop_all_apps(disable_ssl=disable_ssl))
    elif args.command == "uninstall":
        asyncio.run(uninstall_app(args.app_id, disable_ssl=disable_ssl))
    elif args.command == "debug-token":
        asyncio.run(debug_token_info())
    elif args.command == "login":
        asyncio.run(login_command(disable_ssl=disable_ssl))
    elif args.command == "list-installed":
        asyncio.run(list_apps(running=False, disable_ssl=disable_ssl))
    elif args.command == "list-running":
        asyncio.run(list_apps(running=True, disable_ssl=disable_ssl))
    elif args.command == "list-services":
        asyncio.run(list_services(disable_ssl=disable_ssl))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
