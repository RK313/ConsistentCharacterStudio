import json
from core.prompt import load_prompts, get_instruction
from core.assets import get_reference_asset

def load_scene(paths, scene_name):

    scene_file = (
        paths["root"] /
        "scenes" /
        f"{scene_name}.json"
    )

    with open(
        scene_file,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def validate_scene(scene, paths):

    required_fields = [
        "id",
        "character",
        "pose",
        "action",
        "duration",
    ]

    for field in required_fields:

        if field not in scene:
            raise ValueError(
                f"Scene missing required field: {field}"
            )

    if scene["character"] != paths["character"]:
        raise ValueError(
            f"Scene character '{scene['character']}' "
            f"does not match character '{paths['character']}'"
        )

    if not isinstance(scene["duration"], (int, float)):
        raise ValueError(
            "Scene duration must be a number"
        )

    if scene["duration"] <= 0:
        raise ValueError(
            "Scene duration must be greater than zero"
        )

    return True


def resolve_scene(scene, paths):

    prompts = load_prompts(paths)

    pose = scene.get("pose")
    expression = scene.get("expression")
    prop = scene.get("prop")

    instruction = None

    # Prefer explicit expression.
    if expression:
        instruction = get_instruction(
            prompts,
            expression
        )

    # Otherwise use pose.
    if instruction is None and pose:
        instruction = get_instruction(
            prompts,
            pose
        )

    # Finally check prop.
    if instruction is None and prop:
        instruction = get_instruction(
            prompts,
            prop
        )

    if instruction is None:
        raise ValueError(
            "No prompt instruction found for scene"
        )

    reference_asset = None

    for name in [
        expression,
        pose,
        prop,
    ]:

        if not name:
            continue

        reference_asset = get_reference_asset(
            paths,
            name
        )

        if reference_asset is not None:
            break

    return {
        "instruction": instruction,
        "reference_asset": reference_asset
    }


def get_scene_request(scene, paths):

    validate_scene(
        scene,
        paths
    )

    resolved = resolve_scene(
        scene,
        paths
    )

    return {
        "scene_id": scene["id"],
        "character": scene["character"],
        "instruction": resolved["instruction"],
        "reference_asset": resolved["reference_asset"],
        "camera": scene.get("camera"),
        "action": scene["action"],
        "duration": scene["duration"]
    }

def build_scene_instruction(request):

    instruction = request["instruction"]
    action = request.get("action")
    camera = request.get("camera")

    parts = [
        instruction
    ]

    if action:
        parts.append(
            f"Action: {action}"
        )

    if camera:
        shot = camera.get("shot")
        angle = camera.get("angle")

        if shot or angle:
            camera_text = "Camera:"

            if shot:
                camera_text += f" {shot} shot"

            if angle:
                camera_text += f", {angle} angle"

            parts.append(camera_text)

    return "\n\n".join(parts)
