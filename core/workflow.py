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

    destination = (
        comfy_input /
        paths["master"].name
    )

    shutil.copy2(
        paths["master"],
        destination
    )

    return destination.name


def prepare_asset_image(paths, asset_path):

    if asset_path is None:
        return None

    comfy_input = Path(
        paths["config"]["comfyui"]["input"]
    )

    comfy_input.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = (
        comfy_input /
        asset_path.name
    )

    shutil.copy2(
        asset_path,
        destination
    )

    return destination.name


def set_asset_image(
    workflow,
    paths,
    asset_image_name
):

    asset_node = paths["config"]["nodes"]["asset_image"]
    stitch_node = paths["config"]["nodes"]["image_stitch"]

    if asset_image_name is None:

        workflow[stitch_node]["inputs"].pop(
            "image2",
            None
        )

        return

    workflow[asset_node]["inputs"]["image"] = (
        asset_image_name
    )

    workflow[stitch_node]["inputs"]["image2"] = [
        asset_node,
        0
    ]