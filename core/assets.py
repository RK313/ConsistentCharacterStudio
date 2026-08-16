import json
import shutil
from pathlib import Path


def load_assets(paths):

    with open(
        paths["assets"],
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_asset(assets, category, name):

    return assets.get(
        category,
        {}
    ).get(name)


def get_approved_asset(assets, category, name):

    asset = get_asset(
        assets,
        category,
        name
    )

    if asset is None:
        return None

    # Single asset
    if asset.get("status") == "approved":
        return asset

    # Variant-based asset
    variants = asset.get(
        "variants",
        []
    )

    approved_variants = [
        variant
        for variant in variants
        if variant.get("status") == "approved"
    ]

    if not approved_variants:
        return None

    default_index = asset.get(
        "default",
        0
    )

    if (
        isinstance(default_index, int)
        and 0 <= default_index < len(approved_variants)
    ):
        return approved_variants[default_index]

    return approved_variants[0]


def resolve_asset_path(paths, asset):

    if asset is None:
        return None

    path = (
        paths["root"] /
        "assets" /
        asset["file"]
    )

    if not path.exists():
        return None

    return path

def get_reference_asset(paths, name):

    assets = load_assets(paths)

    # The prompt system calls these "objects",
    # while the asset system calls them "props".
    categories = [
        "poses",
        "expressions",
        "props",
    ]

    for category in categories:

        asset = get_approved_asset(
            assets,
            category,
            name
        )

        path = resolve_asset_path(
            paths,
            asset
        )

        if path is not None:
            return path

    return None

def promote_asset(
    paths,
    category,
    name,
    source_file,
    asset_file=None,
    set_default=False
):

    source = paths["output"] / source_file

    if not source.exists():
        raise FileNotFoundError(
            f"Source file not found: {source}"
        )

    assets = load_assets(paths)

    category_assets = assets.setdefault(
        category,
        {}
    )

    if asset_file is None:
        asset_file = (
            Path(category) /
            source.name
        )

    asset_file = Path(asset_file)

    destination = (
        paths["root"] /
        "assets" /
        asset_file
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Copy the source image if it is not already
    # present at the destination.
    if not destination.exists():
        shutil.copy2(
            source,
            destination
        )

    relative_file = asset_file.as_posix()

    # Expressions use the variant-based schema.
    if category == "expressions":

        existing = category_assets.get(
            name
        )

        if existing is None:
            existing = {
                "default": 0,
                "variants": []
            }

        variants = existing.setdefault(
            "variants",
            []
        )

        # Check whether this asset is already registered.
        for existing_variant in variants:

            if existing_variant.get(
                "file"
            ) == relative_file:

                # Re-promoting an existing asset is
                # safe and idempotent.
                existing_variant["status"] = "approved"

                if set_default:
                    existing["default"] = (
                        variants.index(existing_variant)
                    )

                category_assets[name] = existing

                with open(
                    paths["assets"],
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        assets,
                        f,
                        indent=2
                    )

                    f.write("\n")

                return destination

        # New expression variant.
        variant = {
            "file": relative_file,
            "status": "approved"
        }

        variants.append(variant)

        if set_default:
            existing["default"] = (
                len(variants) - 1
            )

        category_assets[name] = existing

    # Other categories use the simple asset schema.
    else:

        category_assets[name] = {
            "file": relative_file,
            "status": "approved"
        }

    with open(
        paths["assets"],
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            assets,
            f,
            indent=2
        )

        f.write("\n")

    return destination
