import os
import torch # type: ignore
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
                "counter_digits": ("INT", {"default": 4, "min": 0, "max": 8, "step": 1, 
                                          "display": "slider", 
                                          "tooltip": "Number of digits for counter. Set to 0 to disable counter."}),
                "counter_position": (["last", "first"], {"default": "last", 
                                                        "tooltip": "Position of counter: last = filename_0001, first = 0001_filename"}),
                "one_counter_per_folder": ("BOOLEAN", {"default": True, 
                                                      "tooltip": "Use one counter per subfolder instead of per filename"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("message",)
    FUNCTION = "save_image"
    CATEGORY = "Custom Nodes"

    def save_image(self, image, file_name, main_folder_path, subfolder_name, file_format="PNG", 
                  counter_digits=4, counter_position="last", one_counter_per_folder=True):
        try:
            full_save_path = os.path.join(main_folder_path, subfolder_name)
            os.makedirs(full_save_path, exist_ok=True)
            np_images = image.cpu().numpy()
            messages = []
            
            # Get the latest counter for this folder/filename
            counter = self._get_latest_counter(full_save_path, file_name, 
                                              counter_digits, counter_position, 
                                              file_format, one_counter_per_folder)

            if np_images.ndim == 4:
                for idx, img in enumerate(np_images):
                    save_path = self._process_and_save_image(img, file_name, full_save_path, file_format, 
                                                           counter, counter_digits, counter_position)
                    messages.append(save_path)
                    counter += 1
                return (f"Batch images saved in: {full_save_path}",)
            elif np_images.ndim == 3:
                save_path = self._process_and_save_image(np_images, file_name, full_save_path, file_format, 
                                                       counter, counter_digits, counter_position)
                return (f"Image successfully saved at: {save_path}",)
        except Exception as e:
            return (f"Error: {str(e)}",)

    def _get_latest_counter(self, folder_path, filename_prefix, counter_digits, counter_position, file_format, one_counter_per_folder):
        """
        Get the next available counter number based on existing files in the folder.
        """
        counter = 1
        if not os.path.exists(folder_path):
            return counter
        
        try:
            # Get all files with the specified extension
            file_ext = f".{file_format.lower()}"
            files = [file for file in os.listdir(folder_path) if file.endswith(file_ext)]
            
            if files and counter_digits > 0:
                # If counter is disabled (digits=0), just return 1
                if counter_position == "last":
                    # For filename_0001.png format
                    counters = []
                    for file in files:
                        # Only check files that match our prefix if not using one counter per folder
                        if one_counter_per_folder or file.startswith(filename_prefix):
                            # Extract the counter part before the extension
                            parts = os.path.splitext(file)[0].split('_')
                            if len(parts) > 1:
                                last_part = parts[-1]
                                if last_part.isdigit() and len(last_part) == counter_digits:
                                    counters.append(int(last_part))
                else:
                    # For 0001_filename.png format
                    counters = []
                    for file in files:
                        # Only check files that match our pattern if not using one counter per folder
                        if one_counter_per_folder or '_' in file and file.split('_', 1)[1].startswith(filename_prefix):
                            # Extract the counter part at the beginning
                            parts = os.path.splitext(file)[0].split('_')
                            if len(parts) > 0:
                                first_part = parts[0]
                                if first_part.isdigit() and len(first_part) == counter_digits:
                                    counters.append(int(first_part))
                
                # Get the next counter value
                if counters:
                    counter = max(counters) + 1
        
        except Exception as e:
            print(f"Error finding latest counter: {e}")
        
        return counter

    def _process_and_save_image(self, np_image, file_name, full_save_path, file_format, 
                               counter, counter_digits, counter_position):
        """
        Process and save a single image with the appropriate counter in the filename.
        """
        try:
            np_image = np_image.squeeze()
            
            # Format the filename with counter
            if counter_digits > 0:
                counter_str = f"{counter:0{counter_digits}d}"
                if counter_position == "last":
                    final_name = f"{file_name}_{counter_str}"
                else:
                    final_name = f"{counter_str}_{file_name}"
            else:
                final_name = file_name
                
            file_path = os.path.join(full_save_path, f"{final_name}.{file_format.lower()}")
            
            # Save the image
            np_image = (np_image * 255).astype(np.uint8)
            pil_image = Image.fromarray(np_image)
            pil_image.save(file_path, format=file_format.upper(), quality=100)
            
            return file_path
        except Exception as e:
            return f"Error in image processing: {str(e)}"

class ExtractLastPathComponent:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_path": ("STRING", {"default": "./outputs"}),
                "filename_text_extension": (["true", "false"], {"default": "true", "tooltip": "Include file extension in output names"})
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("last_component", "folder_paths", "file_names", "subfolder_filenames")
    FUNCTION = "extract_last_component"
    CATEGORY = "Custom Nodes"

    def extract_last_component(self, input_path, filename_text_extension):
        # Extract the last component of the path
        last_component = os.path.basename(input_path)
        
        # Initialize empty lists for paths and file names
        folder_paths = []
        file_names = []
        subfolder_files = []
        
        # Check if the input path is a directory
        if os.path.isdir(input_path):
            # Get all items in the directory
            for item in os.listdir(input_path):
                item_path = os.path.join(input_path, item)
                
                # Only add directories to folder_paths
                if os.path.isdir(item_path):
                    folder_paths.append(item_path)
                    
                    # For each subfolder, get its files
                    for subfile in os.listdir(item_path):
                        if os.path.isfile(os.path.join(item_path, subfile)):
                            if filename_text_extension == "true":
                                subfolder_files.append(subfile)
                            else:
                                subfolder_files.append(os.path.splitext(subfile)[0])
                
                # Process file names according to the extension preference
                else:
                    if filename_text_extension == "true":
                        file_names.append(item)
                    else:
                        # Remove extension
                        file_names.append(os.path.splitext(item)[0])
        
        # Join the file names into a single string with newlines
        file_names_string = "\n".join(file_names)
        subfolder_files_string = "\n".join(subfolder_files)
        
        return (last_component, folder_paths, file_names_string, subfolder_files_string)


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
