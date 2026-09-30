def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Organizes panel images, structured story text, and outlines into a single layout dictionary list.
    """
    # Split story by Panel markers
    story_panels = full_story.split("**Panel")
    story_panels = [f"**Panel{panel}" for panel in story_panels if panel.strip()]

    layout = []
    for idx, (image, panel_info) in enumerate(zip(image_paths, outline), start=1):
        # Match story text panel segment if available
        text_segment = ""
        if idx <= len(story_panels):
            raw_text = story_panels[idx - 1]
            lines = raw_text.strip().splitlines()
            text_segment = "\n".join(lines[1:]).strip() if len(lines) > 1 else raw_text

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image,
            "text": text_segment,
            "scene_description": panel_info.get("scene_description", ""),
            "image_prompt": panel_info.get("image_prompt", "")
        })

    return layout