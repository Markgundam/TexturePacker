from enum import Enum
from logging import exception
from random import choice
from tkinter import filedialog
from PIL import Image

texture_files = filedialog.askopenfilenames(title="Select Image Files")
input_options = {}

#fill in the input_options dictionary based on the images loaded
for path in texture_files:
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

#function that shows all the input options, asks the user the choose which input to work with
def choose_input():

    for key, options in input_options.items():
        print(options, key)

    choice = int(input("Select input image: "))

    if choice == 1:
        print("Color selected")
        choice = color
    elif choice == 2:
        print("Normal selected")
        choice = normal
    elif choice == 3:
        print("Roughness selected")
        choice = roughness
    elif choice == 4:
        print("Height selected")
        choice = height
    elif choice == 5:
        print("AO selected")
        choice = ambient_occlusion
    elif choice != [1, 2, 3, 4, 5]:
        print("Invalid input")
    return choice

#asks the user to choose how many inputs to work with
number_of_inputs = int(input("Number of input images: "))

#loop through all inputs and call the choose_input function
for inputs in range(number_of_inputs):
            choose_input()

#image_merged = Image.merge("RGBA", (normal.getchannel("R"), normal.getchannel("G"), ambient_occlusion.getchannel("R"), height.getchannel("R")))
#image_merged.save("RGBA.png")
