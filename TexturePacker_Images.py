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
        basecolor = basecolorpath

for roughnesspath in input_images:
    if roughness_str in roughnesspath:
        roughness = roughnesspath

for heightpath in input_images:
    if height_str in heightpath:
        height = heightpath

for ambientocclusionpath in input_images:
    if ambientocclusion_str in ambientocclusionpath:
        ambientocclusion = ambientocclusionpath

for normalpath in input_images:
    if normal_str in normalpath:
        normal = normalpath

print("Basecolor path is: " + basecolor)
print("Roughness path is: " + roughness)
print("Height path is: " + height)
print("Ambientocclusion path is: " + ambientocclusion)
print("Normal path is: " + normal)



