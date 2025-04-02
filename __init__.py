from .save_image_with_subfolder import SaveImageNode
from .save_image_with_subfolder import ExtractLastPathComponent
from .save_image_with_subfolder import ListSubfoldersNode  # 👈 new import

NODE_CLASS_MAPPINGS = {
    "SaveImageNode": SaveImageNode,
    "ExtractLastPathComponent": ExtractLastPathComponent,
    "ListSubfoldersNode": ListSubfoldersNode  # 👈 new mapping
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNode": "Save Image With Subfolder",
    "ExtractLastPathComponent": "Extract Last Path Component",
    "ListSubfoldersNode": "List Subfolder Paths"  # 👈 new display name
}
