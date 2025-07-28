# Hypha Apps CLI Demo

This repository demonstrates how to use the Hypha Apps CLI to manage applications on a Hypha server. It includes a simple "Hello World" app and comprehensive examples of all CLI commands.

## Overview

The Hypha Apps CLI (`hypha_apps_cli`) is a command-line tool that allows you to:
- Install apps to a Hypha server
- Start and stop running apps
- List installed and running apps
- Manage app lifecycles
- View available services

The exact CLI implementation can be found in the [hypha-rpc repo](https://github.com/oeway/hypha-rpc/blob/main/python/hypha_rpc/utils/hypha_apps_cli.py).

This CLI is for managing hypha apps and its artifact, for general artifact access, see [hypha-artifact](https://github.com/aicell-lab/hypha-artifact).

## Understanding App IDs vs Session IDs

It's important to understand the distinction between **App IDs** and **Session IDs**:

- **App ID**: Think of this as a "class" - it's the identifier for an installed app definition. When you install an app, you give it an `app_id`. This represents the app template/blueprint stored on the server.

- **Session ID**: Think of this as an "instance" - it's the identifier for a running instance of an app. When you start an app using its `app_id`, the server creates a new session and returns a unique `session_id` for that running instance.

**Example workflow:**
1. Install app with `--app-id="my-calculator"` → App definition stored on server
2. Start app using `--app-id="my-calculator"` → Returns `session id: "ws-user-user1/_rapp_abc123def456"`  
3. Multiple sessions can run from the same app → Each gets a different session ID
4. Stop specific session using `--session-id="ws-user-user1/_rapp_abc123def456"` → Stops that specific instance
5. Use `stop-all` to stop all running sessions at once

This allows you to have one app definition but multiple running instances of it.

## Prerequisites

Before using the CLI, ensure you have:

1. **Python 3.10+** installed
2. **hypha-rpc >= 0.20.73** installed:
   ```bash
   pip install "hypha-rpc>=0.20.73"
   ```
3. Access to a **Hypha server** (e.g., https://hypha.aicell.io or your self-hosted instance)
4. A valid **authentication token** from your Hypha server

## Environment Setup

### 1. Create a `.env` file

Create a `.env` file in your project root with the following configuration:

```bash
# Hypha Server Configuration
HYPHA_SERVER_URL=https://hypha.aicell.io # or your own server URL
# HYPHA_TOKEN=your_token_here
HYPHA_WORKSPACE=your_workspace_name
HYPHA_CLIENT_ID=my-hypha-app-client
# Optional: Control SSL behavior
HYPHA_DISABLE_SSL=false   # Set to true/1/yes/on to disable SSL (use plain HTTP)
```


Note that the token will typically valid for 1 day.

### 2. Set Your Workspace

Your workspace name should match the workspace you want to deploy apps to on your Hypha server.

## Token Caching Feature (Recommended)

The Hypha Apps CLI supports local token caching to improve user experience and reduce the need for repeated logins. **We recommend using the dedicated `login` command to enable token caching.**

### How Token Caching Works

1. **Pre-Login (Recommended)**: Run `python -m hypha_apps_cli login` to authenticate and cache your token
2. **Token Storage**: Your token is saved to `.hypha_token` in your current directory with secure permissions
3. **Automatic Reuse**: Subsequent CLI commands automatically use the cached token
4. **Expiration Handling**: The CLI automatically detects expired tokens and removes them
5. **Fallback**: If no cached token exists or it's expired, the CLI will prompt for interactive login

Alternatively, you can get your authentication token:

1. Visit your Hypha server dashboard (e.g., https://hypha.aicell.io/public/apps/hypha-login/)
2. Log in to your account
3. Expand "Get Access Token" and copy the existing token, DO NOT click "Generate New Token" (otherwise the generated token won't have admin permission)
6. Add the token to your `.env` file as `HYPHA_TOKEN`



## CLI Commands Reference

All commands use the format:
```bash
python -m hypha_apps_cli [COMMAND] [OPTIONS]
```

(Make sure you have the `hypha_apps_cli` module under your current working directory).

### Global Options

- `--disable-ssl`: Disable SSL (use plain HTTP). Equivalent to setting `HYPHA_DISABLE_SSL=true` in your environment. When set, the CLI will connect to the server without SSL (`ssl=False`).

> **Note:** CLI flags take precedence over environment variables. This option has to be added before the subcommands.

### Example usage

```bash
python -m hypha_apps_cli --disable-ssl install --app-id hello --manifest=manifest.yaml --source=main.py
```

or using environment variables:

```bash
export HYPHA_DISABLE_SSL=true
python -m hypha_apps_cli install --app-id hello --manifest=manifest.yaml --source=main.py
```

### SSL Behavior

- By default, SSL is **enabled** (`ssl=None`), and the CLI will connect using HTTPS.
- If you pass `--disable-ssl` or set `HYPHA_DISABLE_SSL=true`, SSL is **disabled** (`ssl=False`), and the CLI will connect using plain HTTP.

### Authentication Behavior

The CLI uses a simple two-step authentication approach:

1. **Environment Variable**: If `HYPHA_TOKEN` is set in your environment, it will be used
2. **Cached Token**: If no environment token exists, the CLI will try to load a cached token from `.hypha_token` file
3. **Error**: If neither exists, the CLI will display an error message instructing you to use the `login` command

**No automatic login prompts** - you must explicitly authenticate using the `login` command.

### Login and Cache Token (Recommended First Step)

Authenticate and cache your token for subsequent commands:

```bash
# Interactive login and token caching
python -m hypha_apps_cli login
```

**Benefits:**
- **One-time setup**: Login once, use multiple commands without re-authentication
- **Secure caching**: Token stored with proper file permissions (600)
- **Automatic expiration**: Expired tokens are automatically detected and removed
- **Offline-friendly**: No need for interactive login on every command

**Note:** This is the recommended first step before using other CLI commands. The cached token will be automatically used by all subsequent commands unless you have `HYPHA_TOKEN` set in your environment.

### Install an App

Install an app to the Hypha server:

```bash
# Basic installation
python -m hypha_apps_cli install \
  --app-id hello \
  --manifest=manifest.yaml \
  --source=main.py

# Installation with additional files
python -m hypha_apps_cli install \
  --app-id my-complex-app \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=./static

# Installation with overwrite (replace existing app)
python -m hypha_apps_cli install \
  --app-id hello \
  --manifest=manifest.yaml \
  --source=main.py \
  --overwrite
```

**Options:**
- `--app-id`: Unique identifier for your app (required)
- `--source`: Path to your main Python file (required)
- `--manifest`: Path to your manifest.yaml file (required)
- `--files`: Path to directory containing additional files (optional)
- `--overwrite`: Replace existing app if it exists (optional)

### Start an App

Start a previously installed app (creates a new running session):

```bash
python -m hypha_apps_cli start --app-id hello
```

**Note:** You can start multiple sessions from the same `app_id`. Each will get a unique `session_id`.

### Stop an App Session

Stop a specific running app session using its session ID:

```bash
python -m hypha_apps_cli stop --session-id "ws-user-auth0|sdf229udfj234sf/_rapp_cactus-tugboat-90335059__rlb"
```

**Note:** You need the `session_id` (not `app_id`) to stop a specific running instance. Get the session ID from `list-running` command.

### Stop All Apps

Stop all currently running apps (stops all sessions regardless of session ID):

```bash
python -m hypha_apps_cli stop-all
```

**Note:** This is a convenience command that stops all running sessions without needing individual session IDs.

### Uninstall an App

Remove an app from the server:

```bash
python -m hypha_apps_cli uninstall --app-id hello
```

### List Apps

List all installed apps (shows app IDs):

```bash
python -m hypha_apps_cli list-installed
```

List all currently running apps (shows session IDs and their corresponding app IDs):

```bash
python -m hypha_apps_cli list-running
```

**Output examples:**
- `list-installed` shows: `Hello World (app_id: hello-demo): A simple hello world app`
- `list-running` shows: `Hello World (session id: ws-user-hello-demo/fs3abc123, app_id: hello-demo): A simple hello world app`

### List Services

List all available services on the server:

```bash
python -m hypha_apps_cli list-services
```

## Working with Additional Files

The `--files` option allows you to include additional files (static assets, templates, configuration files, etc.) with your Hypha app installation. This is particularly useful for web apps that need CSS, HTML templates, images, or configuration data.

### How File Upload Works

When you specify `--files=./directory`, the CLI will:

1. **Recursively scan** the directory for all files
2. **Automatically detect** file types using MIME types
3. **Process files** based on their type:
   - **JSON files** (`.json`): Parsed as JSON objects
   - **Text files** (`.txt`, `.html`, `.css`, `.js`, `.py`, etc.): Read as text strings
   - **Binary files** (`.png`, `.jpg`, `.pdf`, etc.): Base64 encoded
4. **Upload files** with relative paths preserved


### File Size and Limitations

**Small files only**: In the CLI, however, since we serialize all the data in one rpc call, it is not recommended to upload large files. The typical use of this is to upload source code files along with some assets.
**For uploading large files**: You should use [hypha-artifact](https://github.com/aicell-lab/hypha-artifact).

### Tips and Best Practices

1. **Organize files logically** in subdirectories (static/, templates/, data/, etc.)
2. **Use JSON files** for configuration that your app needs to parse
3. **Keep binary files small** or consider external hosting for large assets
4. **Test file uploads** with small examples before deploying large file sets
5. **Use relative paths** in your HTML/CSS since the directory structure is preserved

## Testing the Demo App

This repository includes a simple "Hello World" app that you can use to test the CLI.

### Automated Test Workflow

For a quick end-to-end test, use the provided test script:

```bash
python test_workflow.py
```

This script will automatically:
1. Install the demo app
2. Start the app
3. List running apps
4. Stop the app
5. Uninstall the app

### Manual Testing Steps

You can also test manually step by step:

#### 1. Install the demo app (creates app definition with app_id):

Basic installation:
```bash
python -m hypha_apps_cli install \
  --app-id hello-demo \
  --manifest=manifest.yaml \
  --source=main.py
```

Or with example files:
```bash
python -m hypha_apps_cli install \
  --app-id hello-demo \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=example-files
```

#### 2. Start the app (creates running instance with session_id):
```bash
python -m hypha_apps_cli start --app-id hello-demo
```
This will show you the session ID of the running instance.

#### 3. List running apps to verify (shows both session IDs and app IDs):
```bash
python -m hypha_apps_cli list-running
```

#### 4. Stop the app session when done (using the session ID from step 3):
```bash
# First get the session ID from list-running, then use it to stop
python -m hypha_apps_cli stop --session-id ws-user-user1/_rapp_abc123def456__rlbabc123def456
```

#### 5. Uninstall the app (removes the app definition):
```bash
python -m hypha_apps_cli uninstall --app-id hello-demo
```

## Example Output

When you install and start an app, you'll see output like:

```
📦 Installing app 'hello-demo' from main.py with manifest manifest.yaml...
✅ App installation completed
📦 App info: {
  "id": "hello-demo",
  "name": "Hello World",
  "version": "1.0.0",
  "status": "installed"
}
✅ App 'hello-demo' successfully installed

🚀 Starting app 'hello-demo'...
✅ Available services:
  - setup (): No description
🚀 Started app 'hello-demo' with session ID: `ws-user-user1/_rapp_abc123def456__rlbabc123def456`
```

Notice how:
- The **app ID** is `hello-demo` (the installed app definition)
- The **session ID** is `ws-user-user1/_rapp_abc123def456__rlbabc123def456` (the running instance)

## Project Structure

```
my-hypha-app/
├── main.py                     # Demo app source code
├── manifest.yaml               # App configuration
├── requirements.txt            # Python dependencies
├── test_workflow.py            # Automated test script
├── README.md                  # This file
├── ref-hypha_apps_cli.py      # Reference CLI implementation
└── example-files/             # Example files for --files option
    ├── static/
    │   ├── style.css          # Example CSS file
    │   └── icon.png           # Example image (binary)
    ├── templates/
    │   └── index.html         # Example HTML template
    └── data/
        └── config.json        # Example JSON configuration
```

## Files Explained

### `main.py`
Simple Hypha app that exports a `setup` function:
```python
from hypha_rpc import api

async def setup():
    print("hello")

api.export({
    "config": {
        "visibility": "public",
    },
    "setup": setup
})
```

Note 1: You can add other functions to the export, but `setup` is required which will be called automatically by hypha.
You can register or run other function inside `setup`.
Note 2: The exported function can be sync/async python function `def func` or `async def`.

### `manifest.yaml`
App configuration file:
```yaml
type: "web-python"
name: "Hello World"
version: "1.0.0"
requirements:
  - "hypha-rpc"
  - "pandas"
```

## About Hypha Token

### Token Precedence Order

The CLI attempts to get authentication tokens in this order:
1. **Environment Variable**: `HYPHA_TOKEN` from your `.env` file or environment
2. **Cached Token**: Valid token from `.hypha_token` file (created by `login` command)
3. **Interactive Login**: Prompts for login if no valid token is found

### Recommended Usage Pattern

**Step 1: Pre-authenticate (recommended)**
```bash
# Run this once to login and cache your token
python -m hypha_apps_cli login
```

**Step 2: Use any CLI commands**
```bash
# These will automatically use your cached token
python -m hypha_apps_cli list-installed
python -m hypha_apps_cli start --app-id my-app
python -m hypha_apps_cli stop --session-id "session_123"
```

### Security Features

- **Secure Permissions**: Token files are created with `600` permissions (readable only by owner)
- **Automatic Cleanup**: Expired tokens are automatically detected and removed
- **No Version Control**: `.hypha_token` is automatically ignored by git (added to `.gitignore`)
- **JWT Validation**: Tokens are validated by parsing the JWT payload and checking expiration time

### Token Caching Behavior

- **Only the `login` command saves tokens** - other commands will prompt for login but won't cache the token
- **Environment tokens take precedence** - if `HYPHA_TOKEN` is set, cached tokens are ignored
- **Automatic expiration** - expired cached tokens are automatically removed

### Fresh Login

To get a fresh token (updating your cached token), simply run the login command again:

```bash
# Get a fresh token and update cache
python -m hypha_apps_cli login
```

### Managing Token Files

```bash
# Pre-login and cache token (recommended)
python -m hypha_apps_cli login

# View current token file location
ls -la .hypha_token

# Manually remove cached token (forces re-login)
rm .hypha_token

# Check token file permissions
ls -l .hypha_token
# Should show: -rw------- (600 permissions)
```

### Troubleshooting Token Issues

**No cached token:**
```bash
# Run the login command to create one
python -m hypha_apps_cli login
```

**Token Permission Errors:**
```bash
# Fix permissions if needed
chmod 600 .hypha_token
```

**Corrupted Token File:**
```bash
# Remove corrupted token file and re-login
rm .hypha_token
python -m hypha_apps_cli login
```

## Troubleshooting

### Common Issues

1. **Missing environment variables:**
   ```
   ❌ Missing environment variables. Set HYPHA_SERVER_URL, HYPHA_TOKEN, HYPHA_WORKSPACE
   ```
   **Solution:** Ensure your `.env` file contains all required variables.

2. **Connection errors:**
   - Check your `HYPHA_SERVER_URL` is correct
   - Verify your token is valid and not expired
   - Ensure your workspace name exists

3. **Permission errors:**
   - Verify your token has the necessary permissions
   - Check that you're using the correct workspace

4. **App installation fails:**
   - Ensure your `manifest.yaml` is valid YAML or JSON
   - Check that your source file exists and is readable
   - Try using `--overwrite` if the app already exists

5. **Cannot stop a specific app session:**
   - The `stop` command requires a `session_id`, not an `app_id`
   - Get the session ID by running: `python -m hypha_apps_cli list-running`
   - Use the full session ID (e.g., `ws-user-github|sf3a262/_rapp_cactus-tugboat-90335059__rlb`) with `--session-id` and you need to quote it.
   - To stop all sessions, use `stop-all` instead

6. **Token caching issues:**
   - **No cached token**: Run `python -m hypha_apps_cli login` to authenticate and cache your token
   - **Expired cached token**: The CLI automatically detects and removes expired tokens, but if you encounter issues, manually remove: `rm .hypha_token`
   - **Permission errors on token file**: Fix with: `chmod 600 .hypha_token`
   - **Need fresh token**: Run `python -m hypha_apps_cli login` to get a new token

### Getting Help

For detailed help on any command:
```bash
python -m hypha_apps_cli [COMMAND] --help
```

For general CLI help:
```bash
python -m hypha_apps_cli --help
```

## Advanced Usage

### Custom Client ID

You can set a custom client ID in your `.env` file:
```bash
HYPHA_CLIENT_ID=my-custom-client-id
```

### Working with Files

When using `--files`, you can include additional static files or resources. See the [Working with Additional Files](#working-with-additional-files) section above for comprehensive details.

Quick example:
```bash
python -m hypha_apps_cli install \
  --app-id my-app \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=./assets
```

This will recursively include all files in the `./assets` directory, automatically detecting and processing different file types (text, JSON, binary).

## License

This demo is provided as-is for educational purposes.
