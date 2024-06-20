import os
import re

import folder_paths

class CLIPTextEncodeWithWildcards:

    def __init__(self):
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.wildcards_dir = os.path.join(folder_paths.base_path, "wildcards")

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"multiline": True}),
            "clip": ("CLIP",),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
        }
        }

    RETURN_TYPES = ("CONDITIONING", "INT")
    FUNCTION = "encode"

    CATEGORY = "conditioning"

    def read_wildcard(self, filename, seed):
        y_path = os.path.join(self.wildcards_dir, filename)
        f = open(y_path, "r")
        k = f.readlines()
        f.close()
        modu = k[seed % len(k)].strip()
        return modu

    def process_text(self, text: str, seed):
        files, folders_all = folder_paths.recursive_search(self.wildcards_dir)

        for match in re.finditer("__[a-zA-Z0-9-]*__", text):
            group = match.group(0)
            s = group[2:len(group) - 2]
            z = s + ".txt"
            if z in files:
                wc_text = self.read_wildcard(z, seed)
            else:
                wc_text = "WILDCARD NOT FOUND"
                print(f"Wildcard file not found for {group}")

            text = text.replace(group, wc_text)

        return text

    def encode(self, clip, text, seed):
        text = self.process_text(text, seed)
        tokens = clip.tokenize(text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        return ([[cond, {"pooled_output": pooled}]]), seed


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "CLIPTextEncodeWithWildcards": CLIPTextEncodeWithWildcards
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "CLIPTextEncodeWithWildcards": "CLIP with Wildcards"
}
