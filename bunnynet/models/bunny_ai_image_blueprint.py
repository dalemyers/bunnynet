import deserialize


@deserialize.auto_snake()
class BunnyAiImageBlueprint:
    name: str
    properties: dict
