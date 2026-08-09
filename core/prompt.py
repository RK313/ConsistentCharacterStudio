from core.utils import load_json

# ==========================================================
# Prompt Template
# ==========================================================

PROMPT_TEMPLATE = """
Edit only the body pose.

{instruction}

Keep the original face unchanged.

Keep the original gentle closed smile unchanged.

Do not change the eyes, ears, nose, mouth,
hair tuft, fur color, body proportions,
tail, lighting, background or camera angle.

Do not change the character identity.
"""


def load_prompts(paths):

    return load_json(paths["prompts"])


def build_prompt(instruction):

    return PROMPT_TEMPLATE.format(
        instruction=instruction
    )

def get_instruction(prompts, pose):

    pose = pose.lower()

    for section in [
        "poses",
        "objects",
        "expressions"
    ]:

        if section not in prompts:
            continue

        if pose in prompts[section]:

            return prompts[section][pose]["instruction"]

    return None

