from pathlib import Path
import json

BASE_DIR = Path(__file__).parent.parent

def load_character(character):

    character_file = (
        BASE_DIR /
        "characters" /
        character /
        "character.json"
    )

    with open(character_file, "r", encoding="utf-8") as f:

        return json.load(f)

def get_character_paths(character):

    config = load_character(character)

    char_dir = BASE_DIR / "characters" / character

    return {

        "config": config,

        "character": character,

        "root": char_dir,

        "workflow":
            char_dir /
            config["workflow"],

        "prompts":
            char_dir /
            "prompts.json",

        "master":
            char_dir /
            config["master_image"],

        "output":
            char_dir /
            "output"

    }
