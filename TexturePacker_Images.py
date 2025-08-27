from enum import Enum
from logging import exception
from random import choice
from tkinter import filedialog
from PIL import Image

input_images = filedialog.askopenfilenames(title="Select Image Files")
input_options = {}

for path in input_images:
    if "basecolor" in path:
        color = Image.open(path)
        input_options["basecolor"] = 1
        continue

    if "normal" in path:
        normal = Image.open(path)
        input_options["normal"] = 2
        continue

    if "roughness" in path:
        roughness = Image.open(path)
        input_options["roughness"] = 3
        continue

    if "height" in path:
        height = Image.open(path)
        input_options["height"] = 4
        continue

    if "ambientOcclusion" in path:
        ambient_occlusion = Image.open(path)
        input_options["ambient_occlusion"] = 5
        continue

    raise Exception

def input_texture():

    for key, options in input_options.items():
        print(options, key)

    input_1 = int(input("Select input image: "))

    if input_1 == 1:
        print("Color selected")
        input_1 = color

    elif input_1 == 2:
        print("Normal selected")
        input_1 = normal

    elif input_1 == 3:
        print("Roughness selected")
        input_1 = roughness

    elif input_1 == 4:
        print("Height selected")
        input_1 = height

    elif input_1 == 5:
        print("AO selected")
        input_1 = ambient_occlusion

    elif input_1 != [1, 2, 3, 4, 5]:
        print("Invalid input")

number_of_inputs = int(input("Number of input images: "))

for inputs in range(number_of_inputs):
            input_texture()


#image_merged = Image.merge("RGBA", (normal.getchannel("R"), normal.getchannel("G"), ambient_occlusion.getchannel("R"), height.getchannel("R")))
#image_merged.save("RGBA.png")
