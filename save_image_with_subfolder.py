import os
import torch
import numpy as np
from PIL import Image

class SaveImageNode:
    """
    A ComfyUI-compatible Save Image Node that asks for a subfolder name,
    creates the subfolder inside a specified main folder, and saves the images inside.
    Supports any image format without forced conversion, including RGB, RGBA, grayscale, and batch processing.
    Ensures all images are saved correctly while preserving the original format.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),  # Single image tensor or batch of images
                "file_name": ("STRING", {"default": "output"}),  # Base file name
                "main_folder_path": ("STRING", {"default": "./outputs"}),  # Main directory
                "subfolder_name": ("STRING", {"default": "New_Subfolder"}),  # Subfolder name
                "file_format": ("STRING", {"default": "PNG", "options": ["PNG", "JPEG", "BMP"]}),  # File format
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("message",)
    FUNCTION = "save_image"
    CATEGORY = "Custom Nodes"

    def save_image(self, image, file_name, main_folder_path, subfolder_name, file_format="PNG"):
        try:
            full_save_path = os.path.join(main_folder_path, subfolder_name)
            os.makedirs(full_save_path, exist_ok=True)
            np_images = image.cpu().numpy()
            messages = []

            if np_images.ndim == 4:
                for idx, img in enumerate(np_images):
                    save_path = self._process_and_save_image(img, f"{file_name}_{idx + 1}", full_save_path, file_format)
                    messages.append(save_path)
                return (f"Batch images saved in: {full_save_path}",)
            elif np_images.ndim == 3:
                save_path = self._process_and_save_image(np_images, file_name, full_save_path, file_format)
                return (f"Image successfully saved at: {save_path}",)
        except Exception as e:
            return (f"Error: {str(e)}",)

    def _process_and_save_image(self, np_image, file_name, full_save_path, file_format):
        try:
            np_image = np_image.squeeze()
            file_path = os.path.join(full_save_path, f"{file_name}_{len(os.listdir(full_save_path)) + 1}.{file_format.lower()}")
            
            # Save the image as it is, without conversion
            np_image = (np_image * 255).astype(np.uint8)
            pil_image = Image.fromarray(np_image)
            pil_image.save(file_path, format=file_format.upper(), quality=100)
            return file_path
        except Exception as e:
            return "Error in image processing"

class ExtractLastPathComponent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_path": ("STRING", {"default": "C:\\Users\\Devel\\Downloads\\example_folder\\file.png"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_last_component"
    CATEGORY = "Custom Nodes"

    def extract_last_component(self, input_path):
        last_component = os.path.basename(input_path)
        return (last_component,)

NODE_CLASS_MAPPINGS = {
    "SaveImageNode": SaveImageNode,
    "ExtractLastPathComponent": ExtractLastPathComponent
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageNode": "Save Image With Subfolder",
    "ExtractLastPathComponent": "Extract Last Path Component"
}
class ListSubfoldersNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "main_folder_path": ("STRING", {"default": "./outputs"}),
                "path_index": ("INT", {"default": 0, "min": 0, "description": "Index of the path to select (0 for first path)"}),
                "load_capacity": ("INT", {"default": 100, "min": 1}),
                "start_index": ("INT", {"default": 0, "min": 0}),
            }
        }

    RETURN_TYPES = ("STRING", "LIST",)
    RETURN_NAMES = ("selected_path", "all_paths",)
    FUNCTION = "list_subfolders"
    CATEGORY = "Custom Nodes"

    def list_subfolders(self, main_folder_path, path_index, load_capacity, start_index):
        try:
            if not os.path.isdir(main_folder_path):
                return ("No valid directory found", [])

            # Get all subfolders
            all_subfolders = sorted([
                os.path.join(main_folder_path, name)
                for name in os.listdir(main_folder_path)
                if os.path.isdir(os.path.join(main_folder_path, name))
            ])
            
            # Get the paginated subset of subfolders
            selected_subfolders = all_subfolders[start_index:start_index + load_capacity]
            
            # Select the specific path based on user input
            if not all_subfolders:
                return ("No subfolders found", [])
                
            # Ensure path_index is within valid range
            if path_index >= len(all_subfolders):
                selected_path = f"Index {path_index} out of range (max: {len(all_subfolders)-1})"
            else:
                selected_path = all_subfolders[path_index]
            
            return (selected_path, selected_subfolders)
        except Exception as e:
            return (f"Error: {str(e)}", [f"Error: {str(e)}"])
