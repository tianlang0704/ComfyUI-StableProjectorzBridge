import json
import os
from tkinter import Image
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import torch
import folder_paths
from nodes import LoadImage
from . import apis

DEFAUL_VALUE_TEXT = "!!!Autofill when executed!!!";

def get_empty_image():
    r = torch.full([1, 512, 512, 1], ((0xFF >> 16) & 0xFF) / 0xFF)
    g = torch.full([1, 512, 512, 1], ((0xFF >> 8) & 0xFF) / 0xFF)
    b = torch.full([1, 512, 512, 1], ((0xFF) & 0xFF) / 0xFF)
    return torch.cat((r, g, b), dim=-1)

loadImage = LoadImage()
def load_image(image_name):
    try:
        (output_image, output_mask) = loadImage.load_image(image_name)
    except:
        output_image = get_empty_image()
        output_mask = torch.full([512, 512], 0)
    return (output_image, output_mask)

class ProjectorzInitInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0}),
                "name_prefix": ("STRING", {"default": apis.FILENAME_FORMAT_INIT_PREFIX_DEFAULT}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, index, name_prefix):
        image_name = name_prefix + str(index) + ".png"
        (output_image, output_mask) = load_image(image_name)
        image_mask_name = name_prefix + str(index) + "_mask.png"
        (output_image_mask, output_mask_mask) = load_image(image_mask_name)
        return (output_image, output_mask_mask)
    
class ProjectorzControlnetInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0}),
                "name_prefix": ("STRING", {"default": apis.FILENAME_FORMAT_CONTROLNET_PREFIX_DEFAULT}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, index, name_prefix):
        image_name = name_prefix + str(index) + ".png"
        (output_image, output_mask) = load_image(image_name)
        image_mask_name = name_prefix + str(index) + "_mask.png"
        (output_image_mask, output_mask_mask) = load_image(image_mask_name)
        return (output_image, output_mask_mask)
    
class ProjectorzOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "name_prefix": ("STRING", {"default": apis.FILENAME_FORMAT_OUTPUT_PREFIX_DEFAULT}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "run"
    CATEGORY = "Projectorz"
    OUTPUT_NODE = True

    def run(self, images, name_prefix, prompt=None, extra_pnginfo=None):
        output_dir = folder_paths.get_output_directory()
        dup_count = 0
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))
            output_filename = f"{name_prefix}_{batch_number}_{dup_count}.png"
            while os.path.exists(os.path.join(output_dir, output_filename)):
                dup_count += 1
                output_filename = f"{name_prefix}_{batch_number}_{dup_count}.png"
            img.save(os.path.join(output_dir, output_filename), pnginfo=metadata)
        return (None,)
    
PROJECTORZ_PARAMETERS = [
    'prompt',
    'negative_prompt',
    'sampler_name',
    'batch_size',
    'n_iter',
    'steps',
    'cfg_scale',
    'width',
    'height',
    'seed',
    'refiner_checkpoint',
    'refiner_switch_at',
    'tiling',
    'enable_hr',
    'hr_upscaler',
    'hr_sampler_name',
    'hr_scale',
    'denoising_strength',
    'hr_second_pass_steps',
]
class ProjectorzParameter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "name": (PROJECTORZ_PARAMETERS, {"default": PROJECTORZ_PARAMETERS[0]}),
                "value": ("STRING", {"default": DEFAUL_VALUE_TEXT}),
            }
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, name, value):
        return (str(value),)

PROJECTORZ_CONTROLNET_PARAMETERS = [
    'enabled',
    'resize_mode',
    'module',
    'model',
    'weight',
    'low_vram',
    'processor_res',
    'threshold_a',
    'threshold_b',
    'guidance_start',
    'guidance_end',
    'control_mode',
    'pixel_perfect',
]
class ProjectorzControlnetParameter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0}),
                "name": (PROJECTORZ_CONTROLNET_PARAMETERS, {"default": PROJECTORZ_CONTROLNET_PARAMETERS[0]}),
                "value": ("STRING", {"default": DEFAUL_VALUE_TEXT}),
            }
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, index, name, value):
        return (str(value),)

class ProjectorzStringToInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("INT", )
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, string):
        return (int(string),)

class ProjectorzStringToFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("FLOAT", )
    FUNCTION = "run"
    CATEGORY = "Projectorz"

    def run(self, string):
        return (float(string),)

NODE_CLASS_MAPPINGS = {
    "ProjectorzInitInput": ProjectorzInitInput,
    "ProjectorzControlnetInput": ProjectorzControlnetInput,
    "ProjectorzOutput": ProjectorzOutput,
    "ProjectorzParameter": ProjectorzParameter,
    "ProjectorzControlnetParameter": ProjectorzControlnetParameter,
    "ProjectorzStringToInt": ProjectorzStringToInt,
    "ProjectorzStringToFloat": ProjectorzStringToFloat,
}

NODE_DISPLAY_NAME_MAPPINGS = { 
    "ProjectorzInitInput": "Projectorz Init Input",
    "ProjectorzControlnetInput": "Projectorz Controlnet Input",
    "ProjectorzOutput": "Projectorz Output",
    "ProjectorzParameter": "Projectorz Parameter",
    "ProjectorzControlnetParameter": "Projectorz Controlnet Parameter",
    "ProjectorzStringToInt": "Projectorz String To Int",
    "ProjectorzStringToFloat": "Projectorz String To Float",
}