
import sys
from core.character import get_character_paths

from core.scene import (
    load_scene,
    get_scene_request,
    build_scene_instruction,
)

from core.prompt import (
    load_prompts,
    build_prompt,
    get_instruction,
)

from core.workflow import (
    load_workflow,
    prepare_master_image,
    prepare_asset_image,
    set_asset_image,
)

from core.assets import (
    get_reference_asset,
)

from core import output
from core import comfyui


# ==========================================================
# Main
# ==========================================================

def generate_request(
    character,
    paths,
    workflow,
    instruction,
    reference_asset,
    output_name
):

    asset_image_name = prepare_asset_image(
        paths,
        reference_asset
    )

    workflow[
        paths["config"]["nodes"]["image"]
    ]["inputs"]["image"] = prepare_master_image(
        paths
    )

    set_asset_image(
        workflow,
        paths,
        asset_image_name
    )

    workflow[
        paths["config"]["nodes"]["prompt"]
    ]["inputs"]["text"] = build_prompt(
        instruction
    )

    print("\n*****====================================*****")
    print("Character :", character)
    print("Output    :", output_name)
    print("*****====================================*****\n")

    prompt_id = comfyui.submit_prompt(
        workflow,
        paths
    )

    print("Prompt Submitted")
    print("Prompt ID :", prompt_id)

    comfyui.wait_for_completion(
        prompt_id,
        paths
    )

    image_path = comfyui.get_generated_image(
        prompt_id,
        paths
    )

    output.copy_output(
        image_path,
        paths,
        output_name
    )

    print("\nDone.\n")


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

    instruction = get_instruction(
        prompts,
        pose
    )

    if instruction is None:
        print(f"\nUnknown pose/expression/object : {pose}")
        return

    reference_asset = get_reference_asset(
        paths,
        pose
    )

    generate_request(
        character=character,
        paths=paths,
        workflow=workflow,
        instruction=instruction,
        reference_asset=reference_asset,
        output_name=pose
    )


def generate_scene(character, scene_name):

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

    scene = load_scene(
        paths,
        scene_name
    )

    request = get_scene_request(
        scene,
        paths
    )

    workflow = load_workflow(paths)

    scene_instruction = build_scene_instruction(
        request
    )

    generate_request(
        character=character,
        paths=paths,
        workflow=workflow,
        instruction=scene_instruction,
        reference_asset=request["reference_asset"],
        output_name=scene_name
    )

# ==========================================================
# Entry
# ==========================================================

def usage():

    print("\nCharacterStudio\n")
    print("Usage:\n")
    print("python generate.py <Character> <Pose>\n")
    print("python generate.py <Character> --scene <Scene>\n")
    print("Examples\n")
    print("python generate.py Mankua walking")
    print("python generate.py Mankua waving")
    print("python generate.py Mankua running")
    print("python generate.py Mankua banana")
    print("")


if __name__ == "__main__":

    if len(sys.argv) == 4 and sys.argv[2] == "--scene":

        character = sys.argv[1]
        scene_name = sys.argv[3]

        generate_scene(
            character,
            scene_name
        )

    elif len(sys.argv) == 3:

        character = sys.argv[1]
        pose = sys.argv[2]

        generate(
            character,
            pose
        )

    else:

        usage()
        sys.exit(0)
