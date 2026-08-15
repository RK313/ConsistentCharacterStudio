import time
import uuid

from pathlib import Path

import requests


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

        url = (
            paths["config"]["comfyui"]["url"]
            + f"/history/{prompt_id}"
        )

        response = requests.get(
            url,
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

            if images:

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

    url = (
        paths["config"]["comfyui"]["url"]
        + f"/history/{prompt_id}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    history = response.json()

    if prompt_id not in history:
        return None

    outputs = history[prompt_id].get(
        "outputs",
        {}
    )

    for node in outputs.values():

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
    
    