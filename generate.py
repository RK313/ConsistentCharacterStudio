import json
import shutil
import sys
import time
import uuid
from pathlib import Path

import requests

from core.character import (
    load_character,
    get_character_paths,
)

from core.prompt import (
    load_prompts,
    build_prompt,
    get_instruction,
)
from core.utils import load_json

from core.workflow import (
    load_workflow,
    prepare_master_image,
)
# ==========================================================
# Character Paths
# ==========================================================

BASE_DIR = Path(__file__).parent


# ==========================================================
# ComfyUI API
# ==========================================================

def submit_prompt(workflow, paths):

    payload = {
        "prompt": workflow,
        "client_id": str(uuid.uuid4())
    }

    response = requests.post(
        paths["config"]["comfyui"]["url"] + "/prompt",
        json=payload,
        timeout=30
    )

    print("Status :", response.status_code)
    print(response.text)

    response.raise_for_status()

    return response.json()["prompt_id"]

def is_finished(prompt_id, paths):

    try:

        response = requests.get(
            paths["config"]["comfyui"]["url"] + "/history",
            timeout=10
        )

        response.raise_for_status()

        history = response.json()

        if prompt_id not in history:
            return False

        outputs = history[prompt_id].get(
            "outputs",
            {}
        )

        for node in outputs.values():

            images = node.get(
                "images",
                []
            )

            if len(images) > 0:

                filename = images[0].get(
                    "filename"
                )

                if filename:
                    return True

        return False

    except Exception:

        return False

def wait_for_completion(prompt_id, paths):

    print("\nWaiting for ComfyUI...\n")

    start = time.time()

    while True:

        if is_finished(prompt_id, paths):

            elapsed = int(time.time() - start)

            print(
                f"\n\nCompleted in {elapsed} seconds."
            )

            return

        elapsed = int(
            time.time() - start
        )

        print(
            f"\rGenerating... {elapsed:>4}s",
            end="",
            flush=True
        )
        time.sleep(3)


def get_generated_image(prompt_id, paths):

    response = requests.get(
        paths["config"]["comfyui"]["url"] + "/history",
        timeout=30
    )

    response.raise_for_status()

    history = response.json()

    if prompt_id not in history:
        return None

    outputs = history[prompt_id]["outputs"]

    for node in outputs.values():

        if "images" not in node:
            continue

        images = node.get(
            "images",
            []
        )

        if not images:
            continue

        image = images[0]
        comfy_output = Path(
            paths["config"]["comfyui"]["output"]
        )

        return comfy_output / image["filename"]

    return None

# ==========================================================
# Output Management
# ==========================================================

def newest_output_image(paths):

    comfy_output = Path(
        paths["config"]["comfyui"]["output"]
    )

    files = list(
        comfy_output.glob("*.png")
    )

    if not files:
        return None

    files.sort(
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    return files[0]

def next_filename(output_dir, pose):

    pose = pose.capitalize()

    target = output_dir / f"{pose}.png"

    if not target.exists():
        return target

    index = 2

    while True:

        candidate = output_dir / f"{pose}_v{index}.png"

        if not candidate.exists():
            return candidate

        index += 1


def copy_output(prompt_id,paths, pose):

    latest = get_generated_image(
        prompt_id,
        paths
    )
    if latest is None:

        print("No output image found.")

        return

    paths["output"].mkdir(
        parents=True,
        exist_ok=True
    )

    destination = next_filename(
        paths["output"],
        pose
    )

    shutil.copy2(
        latest,
        destination
    )

    print("\nImage copied to folder:\n")
    print(destination)

# ==========================================================
# Main
# ==========================================================

def generate(character, pose):

    paths = get_character_paths(character)

    if not paths["workflow"].exists():
        print(f"\nWorkflow not found:\n{paths['workflow']}")
        return

    if not paths["prompts"].exists():
        print(f"\nPrompts not found:\n{paths['prompts']}")
        return

    if not paths["master"].exists():
        print(f"\nMaster image not found:\n{paths['master']}")
        return

    workflow = load_workflow(paths)

    prompts = load_prompts(paths)

    instruction = get_instruction(prompts, pose)

    if instruction is None:
        print(f"\nUnknown pose/expression/object : {pose}")
        return

    image_name = prepare_master_image(paths)

    workflow[paths["config"]["nodes"]["image"]]["inputs"]["image"] = image_name

    workflow[
        paths["config"]["nodes"]["prompt"]
    ]["inputs"]["text"] = build_prompt(
        instruction
    )

    print("\n*****====================================*****")
    print("Character :", character)
    print("Pose      :", pose)
    print("*****====================================*****\n")

    prompt_id = submit_prompt(workflow, paths)

    print("Prompt Submitted")
    print("Prompt ID :", prompt_id)

    wait_for_completion(prompt_id, paths)

    copy_output(prompt_id, paths, pose)

    print("\nDone.\n")


# ==========================================================
# Entry
# ==========================================================

def usage():

    print("\nCharacterStudio\n")
    print("Usage:\n")
    print("python generate.py <Character> <Pose>\n")
    print("Examples\n")
    print("python generate.py Mankua walking")
    print("python generate.py Mankua waving")
    print("python generate.py Mankua running")
    print("python generate.py Mankua banana")
    print("")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(0)

    character = sys.argv[1]
    pose = sys.argv[2]

    generate(character, pose)