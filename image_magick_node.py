import torch
from PIL import Image, ImageOps, ImageSequence
import numpy as np
import torch
import torchvision
import torchvision.transforms as T
from PIL import Image
import subprocess
import os
import datetime
import folder_paths

comfy_path = os.path.dirname(folder_paths.__file__)

image_magick_path = f'{comfy_path}/custom_nodes/ComfyUI-ImageMagick'
import uuid
class ImageMagick:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),

                "param1": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "param2": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "param3": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "param4": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "param5": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
                "param6": ("STRING", {
                    "multiline": False,
                    "default": ""
                }),
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "image_path")

    FUNCTION = "execute"

    #OUTPUT_NODE = False

    CATEGORY = "ImageMagick"

    def save_image(self, images):
        img_full_path = None

        for (batch_number, ii) in enumerate(images):
            i = 255. * ii.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            now = datetime.datetime.now()

            timestamp = now.strftime("%Y%m%d_%H%M%S")

            img_file_name = f'ImageMagick_{timestamp}.png'

            tmp_path = f'{image_magick_path}/tmp'

            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)

            img_full_path = f'{tmp_path}/{img_file_name}'

            img_full_path = os.path.normpath(img_full_path)

            if os.path.exists(img_full_path):
                random_suffix = uuid.uuid4().hex
                img_file_name = f'ImageMagick_{timestamp}_{random_suffix}.png'
                img_full_path = os.path.join(tmp_path, img_file_name)

            img.save(img_full_path)

        return img_full_path

    def read_image_from_path(self, image_path):
        img = Image.open(image_path)

        image = None

        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)
            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]

        return image

    def execute(self, image1, param1, param2, param3, param4, param5, param6, image2 = None, image3 = None):
        image1_store_path = self.save_image(image1)

        image2_store_path = None

        if not image2 is None:
            image2_store_path = self.save_image(image2)

        image3_store_path = None

        if not image3 is None:
            image3_store_path = self.save_image(image3)

        now = datetime.datetime.now()

        timestamp = now.strftime("%Y%m%d_%H%M%S")

        img_file_name = f'ImageMagick_{timestamp}.png'

        out_path = f'{image_magick_path}/output'

        if not os.path.exists(out_path):
            os.makedirs(out_path)

        image_out_path = f'{out_path}/{img_file_name}'

        image_out_path = os.path.normpath(image_out_path)

        params = ['magick', image1_store_path, image2_store_path, image3_store_path, param1, param2, param3, param4, param5, param6, image_out_path]

        filtered_params = [param for param in params if param not in ['', None]]

        print(filtered_params)

        result = subprocess.run(filtered_params)

        if result.returncode == 0:
            print("Image processed successfully.")
        else:
            print("Error processing image.")

        return (self.read_image_from_path(image_out_path), image_out_path)

NODE_CLASS_MAPPINGS = {
    "ImageMagick": ImageMagick
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageMagick": "ImageMagick"
}
