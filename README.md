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

## Prerequisites

Before using the CLI, ensure you have:

1. **Python 3.7+** installed
2. **hypha-rpc >= 0.20.71** installed:
   ```bash
   pip install "hypha-rpc>=0.20.71"
   ```
3. Access to a **Hypha server** (e.g., https://hypha.aicell.io or your self-hosted instance)
4. A valid **authentication token** from your Hypha server

## Environment Setup

### 1. Create a `.env` file

Create a `.env` file in your project root with the following configuration:

```bash
# Hypha Server Configuration
HYPHA_SERVER_URL=https://hypha.aicell.io # or your own server URL
HYPHA_TOKEN=your_token_here
HYPHA_WORKSPACE=your_workspace_name
HYPHA_CLIENT_ID=my-hypha-app-client
```

### 2. Get Your Authentication Token

To get your authentication token:

1. Visit your Hypha server dashboard (e.g., https://hypha.aicell.io)
2. Log in to your account
3. Go to "My Workspace"
4. Find the "Development" tab
5. Generate a new token
6. Add it to your `.env` file as `HYPHA_TOKEN`

### 3. Set Your Workspace

Your workspace name should match the workspace you want to deploy apps to on your Hypha server.

## CLI Commands Reference

All commands use the format:
```bash
python -m hypha_rpc.utils.hypha_apps_cli [COMMAND] [OPTIONS]
```

### Install an App

Install an app to the Hypha server:

```bash
# Basic installation
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id hello \
  --manifest=manifest.yaml \
  --source=main.py

# Installation with additional files
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id my-complex-app \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=./static

# Installation with overwrite (replace existing app)
python -m hypha_rpc.utils.hypha_apps_cli install \
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

Start a previously installed app:

```bash
python -m hypha_rpc.utils.hypha_apps_cli start --app-id hello
```

### Stop an App

Stop a running app:

```bash
python -m hypha_rpc.utils.hypha_apps_cli stop --app-id hello
```

### Stop All Apps

Stop all currently running apps:

```bash
python -m hypha_rpc.utils.hypha_apps_cli stop-all
```

### Uninstall an App

Remove an app from the server:

```bash
python -m hypha_rpc.utils.hypha_apps_cli uninstall --app-id hello
```

### List Apps

List all installed apps:

```bash
python -m hypha_rpc.utils.hypha_apps_cli list-installed
```

List all currently running apps:

```bash
python -m hypha_rpc.utils.hypha_apps_cli list-running
```

### List Services

List all available services on the server:

```bash
python -m hypha_rpc.utils.hypha_apps_cli list-services
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

### File Processing Examples

Here's how different file types are handled:

#### Text Files (CSS, HTML, JavaScript, etc.)
```css
/* static/style.css - processed as text */
body { font-family: Arial, sans-serif; }
```
→ Stored as: `{"name": "static/style.css", "content": "body { font-family: Arial, sans-serif; }", "format": "text"}`

#### JSON Configuration Files
```json
{
  "app_settings": {
    "version": "1.0.0",
    "debug": false
  }
}
```
→ Stored as: `{"name": "config.json", "content": {...}, "format": "json"}`

#### Binary Files (Images, PDFs, etc.)
```
icon.png (binary image file)
```
→ Stored as: `{"name": "icon.png", "content": "iVBORw0KGgoAAAANS...", "format": "base64"}`

### Directory Structure Example

Create a directory structure like this:

```
my-app-files/
├── static/
│   ├── style.css          # Text file
│   ├── script.js          # Text file
│   └── icon.png           # Binary file (base64 encoded)
├── templates/
│   ├── index.html         # Text file
│   └── error.html         # Text file
├── data/
│   ├── config.json        # JSON file (parsed as object)
│   └── sample-data.csv    # Text file
└── docs/
    └── readme.txt         # Text file
```

### Installation with Files

Install your app with additional files:

```bash
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id my-web-app \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=my-app-files
```

### Accessing Files in Your App

Once uploaded, you can access these files in your Hypha app. The exact method depends on your app type, but files are typically accessible through the app's file system or API.

Example in Python:
```python
from hypha_rpc import api

# Files are available in your app context
def setup():
    # Access uploaded files through the app's file system
    # Implementation depends on your specific app type
    pass

api.export({"setup": setup})
```

### Real-World Use Cases

#### 1. Web Application with Assets
```bash
# Upload web assets (CSS, JS, images)
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id my-dashboard \
  --manifest=manifest.yaml \
  --source=app.py \
  --files=./web-assets
```

#### 2. Data Processing App with Configuration
```bash
# Upload configuration and sample data
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id data-processor \
  --manifest=manifest.yaml \
  --source=processor.py \
  --files=./config-and-data
```

#### 3. Machine Learning Model with Assets
```bash
# Upload model files, templates, and static assets
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id ml-demo \
  --manifest=manifest.yaml \
  --source=model_app.py \
  --files=./model-assets
```

### Testing File Upload

You can test the file upload feature using the provided example files:

```bash
# Install app with example files
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id hello-with-files \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=example-files \
  --overwrite
```

This will upload:
- `static/style.css` (text)
- `static/icon.png` (base64)
- `templates/index.html` (text)
- `data/config.json` (JSON object)

### File Size and Limitations

- **No explicit file size limits** in the CLI, but your Hypha server may have upload limits
- **Large files** are automatically base64 encoded, which increases size by ~33%
- **Consider server storage** when uploading many large files
- **Binary files** like images, videos, or large datasets may be better served from external storage

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

#### 1. Install the demo app:

Basic installation:
```bash
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id hello-demo \
  --manifest=manifest.yaml \
  --source=main.py
```

Or with example files:
```bash
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id hello-demo \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=example-files
```

#### 2. Start the app:
```bash
python -m hypha_rpc.utils.hypha_apps_cli start --app-id hello-demo
```

#### 3. List running apps to verify:
```bash
python -m hypha_rpc.utils.hypha_apps_cli list-running
```

#### 4. Stop the app when done:
```bash
python -m hypha_rpc.utils.hypha_apps_cli stop --app-id hello-demo
```

#### 5. Uninstall the app:
```bash
python -m hypha_rpc.utils.hypha_apps_cli uninstall --app-id hello-demo
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
🚀 Started app with client ID: hello-demo:12345
```

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

def setup():
    print("hello")

api.export({
    "config": {
        "visibility": "public",
    },
    "setup": setup
})
```

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

### Getting Help

For detailed help on any command:
```bash
python -m hypha_rpc.utils.hypha_apps_cli [COMMAND] --help
```

For general CLI help:
```bash
python -m hypha_rpc.utils.hypha_apps_cli --help
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
python -m hypha_rpc.utils.hypha_apps_cli install \
  --app-id my-app \
  --manifest=manifest.yaml \
  --source=main.py \
  --files=./assets
```

This will recursively include all files in the `./assets` directory, automatically detecting and processing different file types (text, JSON, binary).

## Contributing

This is a demonstration repository. The reference implementation is in `ref-hypha_apps_cli.py` for educational purposes.

## License

This demo is provided as-is for educational purposes.