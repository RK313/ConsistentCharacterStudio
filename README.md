# CharacterStudio

CharacterStudio is a local AI-powered character generation framework built on ComfyUI and Flux Kontext.

## Features

- Fully local generation
- Character-based workflow
- Prompt library
- Asset library
- ComfyUI automation
- Modular Python architecture
- Automatic output versioning
- Cached generation support through ComfyUI

## Architecture

```text
CharacterStudio
│
├── generate.py
│
├── core/
│   ├── character.py
│   ├── prompt.py
│   ├── workflow.py
│   ├── comfyui.py
│   ├── output.py
│   └── utils.py
│
└── characters/
    └── Mankua/
        ├── character.json
        ├── prompts.json
        ├── master.png
        ├── assets/
        └── workflow/
