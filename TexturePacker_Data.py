from tkinter import filedialog
from PIL import Image

file_path = filedialog.askopenfilename()
channel_1_input = input("Enter channel 1: ")
channel_2_input = input("Enter channel 2: ")
channel_3_input = input("Enter channel 3: ")

# load image
image = Image.open(file_path)

# get channels from image and save them in separate vars
img_channel_1 = image.getchannel(channel_1_input)
img_channel_2 = image.getchannel(channel_2_input)
img_channel_3 = image.getchannel(channel_3_input)

# save separate channels as images
img_channel_1.save("R.png")
img_channel_2.save("G.png")
img_channel_3.save("B.png")

# save swizzled image
image_merged = Image.merge("RGB", (img_channel_1, img_channel_2, img_channel_3))
image_merged.save(channel_1_input + channel_2_input + channel_3_input + ".png")