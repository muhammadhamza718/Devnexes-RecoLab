"""Path validation utilities to prevent path traversal attacks.

This module provides safe path resolution functions for scripts that need
to determine the project root directory.
"""

from pathlib import Path


def get_validated_project_root(script_path: Path | None = None) -> Path:
    """Get and validate project root path to prevent path traversal attacks.
    
    Args:
        script_path: Path to the script file. If None, uses __file__ from caller.
        
    Returns:
        Validated project root Path.
        
    Raises:
        ValueError: If project root validation fails.
    """
    if script_path is None:
        # Get the caller's file path
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back:
            script_path = Path(frame.f_back.f_globals.get('__file__', '')).resolve()
        else:
            raise ValueError("Cannot determine script path automatically")
    
    # Get the script's directory and navigate to project root
    script_dir = script_path.resolve().parent
    
    # Try different parent levels to find the project root
    for level in range(1, 5):  # Try up to 4 levels up
        project_root = script_dir.parents[level - 1]
        
        # Validate that project root exists and has expected structure
        # Be flexible: check for either Devnexes-RecoLab structure or parent structure
        expected_dirs_options = [
            ["src", "data", "scripts", "ui"],  # Devnexes-RecoLab structure
            ["Devnexes-RecoLab"],  # Parent directory
        ]
        
        for expected_dirs in expected_dirs_options:
            found_count = sum(1 for expected_dir in expected_dirs if (project_root / expected_dir).exists())
            if found_count >= len(expected_dirs) * 0.5:  # At least 50% of expected dirs found
                return project_root
    
    # If we get here, try to find Devnexes-RecoLab specifically
    for level in range(1, 5):
        project_root = script_dir.parents[level - 1]
        if (project_root / "Devnexes-RecoLab").exists():
            return project_root / "Devnexes-RecoLab"
    
    raise ValueError(
        f"Invalid project root. Script may be running from unexpected location. "
        f"Script dir: {script_dir}"
    )


def validate_path_within_project(path: Path, project_root: Path) -> bool:
    """Validate that a path is within the project directory.
    
    Args:
        path: Path to validate.
        project_root: Project root directory.
        
    Returns:
        True if path is within project root, False otherwise.
    """
    try:
        resolved_path = path.resolve()
        resolved_root = project_root.resolve()
        return resolved_path.is_relative_to(resolved_root)
    except (ValueError, OSError):
        return False
