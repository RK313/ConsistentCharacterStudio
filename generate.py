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
from core import output
from core import comfyui
# ==========================================================
# Character Paths
# ==========================================================

BASE_DIR = Path(__file__).parent


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

    prompt_id = comfyui.submit_prompt(workflow, paths)

    print("Prompt Submitted")
    print("Prompt ID :", prompt_id)

    comfyui.wait_for_completion(prompt_id, paths)

    image_path = comfyui.get_generated_image(
        prompt_id,
        paths
    )

    output.copy_output(
        image_path,
        paths,
        pose
    )
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