import importlib
import inspect
import os
import sys
from pathlib import Path

def find_project_root(start_path: Path = None) -> Path:
    """
    Walks upward from the given path (or caller file) to find the project root,
    defined as a directory containing either 'config', '.git', or 'test_specs'.
    """
    if not start_path:
        frame = inspect.stack()[2]
        start_path = Path(frame.filename).resolve()

    root = start_path.parent

    while root != root.parent:
        if (root / "config").is_dir() or (root / ".git").is_dir() or (root / "test_specs").is_dir():
            return root
        root = root.parent

    return start_path.parent  # fallback

def ensure_caller_project_on_sys_path():
    """
    Ensures the root of the importing project is on sys.path.
    This allows dynamic imports like 'model.X' or 'controller.Y' to work from the test project.
    """
    root = find_project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

def resolve(dotted_path: str):
    """
    Dynamically import and return an object from a dotted path.
    Example: 'model.delivery.Delivery' => returns the Delivery class.
    """
    ensure_caller_project_on_sys_path()

    try:
        mod_name, attr = dotted_path.rsplit(".", 1)
        module = importlib.import_module(mod_name)
        return getattr(module, attr)
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not resolve '{dotted_path}': {e}") from e
