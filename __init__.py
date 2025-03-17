from .save_image_with_subfolder import SaveImageNode
from .save_image_with_subfolder import ExtractLastPathComponent

NODE_CLASS_MAPPINGS = {
    "SaveImageNode": SaveImageNode,
    "ExtractLastPathComponent": ExtractLastPathComponent
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNode": "Save Image With Subfolder",
    "ExtractLastPathComponent": "Extract Last Path Component"
}
