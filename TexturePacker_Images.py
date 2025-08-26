from logging import exception
from tkinter import filedialog
from PIL import Image

input_images = filedialog.askopenfilenames(title="Select Image Files")

for path in input_images:
    if "basecolor" in path:
        color = Image.open(path)
        color.save("BaseColor.png")
        continue

    if "normal" in path:
        normal = Image.open(path)
        normal.save("Normal.png")
        continue

    if "roughness" in path:
        roughness = Image.open(path)
        roughness.save("Roughness.png")
        continue

    if "height" in path:
        height = Image.open(path)
        height.save("Height.png")
        continue

    if "ambientOcclusion" in path:
        ambient_occlusion = Image.open(path)
        ambient_occlusion.save("AmbientOcclusion.png")
        continue

    raise Exception

image_merged = Image.merge("RGBA", (normal.getchannel("R"), normal.getchannel("G"), ambient_occlusion.getchannel("R"), height.getchannel("R")))
image_merged.save("RGBA.png")
