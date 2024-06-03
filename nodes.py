import json
import os
from tkinter import Image
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths
from nodes import LoadImage
from .apis import FILENAME_FORMAT_INIT_PREFIX_DEFAULT, \
    FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT, \
    FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT

class ProjectorzInitInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0}),
                "name_prefix": ("STRING", {"default": FILENAME_FORMAT_INIT_PREFIX_DEFAULT}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, index, name_prefix):
        loadImage = LoadImage()
        image_name = name_prefix + str(index) + ".png"
        (output_image, output_mask) = loadImage.load_image(image_name)
        image_mask_name = name_prefix + str(index) + "_mask.png"
        (output_image_mask, output_mask_mask) = loadImage.load_image(image_mask_name)
        return (output_image, output_mask_mask)
    
class ProjectorzControlnetInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0}),
                "name_prefix": ("STRING", {"default": FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, index, name_prefix):
        loadImage = LoadImage()
        image_name = name_prefix + str(index) + ".png"
        (output_image, output_mask) = loadImage.load_image(image_name)
        image_mask_name = name_prefix + str(index) + "_mask.png"
        (output_image_mask, output_mask_mask) = loadImage.load_image(image_mask_name)
        return (output_image, output_mask_mask)
    
class ProjectorzOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "name_prefix": ("STRING", {"default": FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "Projectorz"
    OUTPUT_NODE = True

    def run(self, images, name_prefix, prompt=None, extra_pnginfo=None):
        output_dir = folder_paths.get_output_directory()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                    
            output_filename = f"{name_prefix}{batch_number}.png"
            img.save(os.path.join(output_dir, output_filename), pnginfo=metadata)
        return (None,)

NODE_CLASS_MAPPINGS = {
    "ProjectorzInitInput": ProjectorzInitInput,
    "ProjectorzControlnetInput": ProjectorzControlnetInput,
    "ProjectorzOutput": ProjectorzOutput,
}

NODE_DISPLAY_NAME_MAPPINGS = { 
    "ProjectorzInitInput": "Projectorz Init Input",
    "ProjectorzControlnetInput": "Projectorz Controlnet Input",
    "ProjectorzOutput": "Projectorz Output",
}