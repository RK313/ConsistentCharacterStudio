import shutil


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


def copy_output(image_path, paths, pose):

    if image_path is None:

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
        image_path,
        destination
    )

    print("\nImage copied to folder:\n")
    print(destination)