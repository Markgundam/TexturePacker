import tkinter
from tkinter import filedialog
from PIL import Image

input_images = filedialog.askopenfilenames(title = "Select Image Files")

basecolor_str = "basecolor"
roughness_str = "roughness"
height_str = "height"
ambientocclusion_str = "ambientOcclusion"
normal_str = "normal"

for basecolorpath in input_images:
    if basecolor_str in basecolorpath:
        basecolor = Image.open(basecolorpath)

for normalpath in input_images:
    if normal_str in normalpath:
        normal = Image.open(normalpath)

for roughnesspath in input_images:
    if roughness_str in roughnesspath:
        roughness = Image.open(roughnesspath)
        roughness = roughness.convert('L')

for heightpath in input_images:
    if height_str in heightpath:
        height = Image.open(heightpath)
        height = height.convert('L')

for ambientocclusionpath in input_images:
    if ambientocclusion_str in ambientocclusionpath:
        ambientocclusion = Image.open(ambientocclusionpath)
        ambientocclusion = ambientocclusion.convert('L')

image_merged = Image.merge("RGBA", (basecolor.getchannel("R"), basecolor.getchannel("G"), basecolor.getchannel("B"), roughness))
image_merged.save("RGBA.png")

