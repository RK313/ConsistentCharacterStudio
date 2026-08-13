import shutil

from pathlib import Path

from core.utils import load_json

# ==========================================================
# Helpers
# ==========================================================

def load_workflow(paths):

    return load_json(paths["workflow"])


# ==========================================================
# Image Preparation
# ==========================================================

def prepare_master_image(paths):

    comfy_input = Path(
        paths["config"]["comfyui"]["input"]
    )

    comfy_input.mkdir(
        parents=True,
        exist_ok=True
    )
    destination = comfy_input / paths["master"].name

    shutil.copy2(
        paths["master"],
        destination
    )

    return destination.name
