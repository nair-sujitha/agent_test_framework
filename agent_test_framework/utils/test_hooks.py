import subprocess

def run_hook(hook_data, stage=""):
    if not hook_data:
        return

    if isinstance(hook_data, dict):
        if hook_data.get("log"):
            print(f"[{stage}] {hook_data['log']}")
        if hook_data.get("script"):
            run_script(hook_data["script"])

def run_script(path: str):
    print(f"[Script] Running: {path}")
    try:
        if path.endswith(".py"):
            subprocess.run(["python", path], check=True)
        elif path.endswith(".sh"):
            subprocess.run(["bash", path], check=True)
        else:
            print(f"[Script] Unsupported script type: {path}")
    except subprocess.CalledProcessError as e:
        print(f"[Script Error] {e}")