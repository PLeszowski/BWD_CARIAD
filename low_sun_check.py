"""
Script looks for "low sun", a pink circle in png images and creates a list of those images.
Patryk Leszowski
APTIV
BWD
"""
from PIL import Image
import os
import serializer


def has_pink_circle(image_path, circle_radius):
    # Open the image using PIL
    image = Image.open(image_path)

    # Convert the image to RGB mode
    image = image.convert("RGB")

    # Get the dimensions of the image
    width, height = image.size

    # Loop through each pixel in the image
    for x in range(width):
        for y in range(height):
            # Check if the pixel is pink (R, G, B values are close to 255, 0, 255)
            pixel = image.getpixel((x, y))
            if pixel[0] > 250 and 160 < pixel[1] < 170 and pixel[2] > 250:
                # Check if there is a circle with the specified radius around the pixel
                is_circle = check_circle(image, x, y, circle_radius)
                if is_circle:
                    return True  # Pink circle found

    return False  # No pink circle found

def check_circle(image, x, y, circle_radius):
    # Get the dimensions of the image
    width, height = image.size

    # Check if the circle is fully contained within the image boundaries
    if x - circle_radius < 0 or x + circle_radius >= width or y - circle_radius < 0 or y + circle_radius >= height:
        return False

    # Loop through each pixel in the circular region
    for i in range(x - circle_radius, x + circle_radius + 1):
        for j in range(y - circle_radius, y + circle_radius + 1):
            # Check if the pixel is within the circle using the distance formula
            if ((i - x) ** 2 + (j - y) ** 2) <= (circle_radius ** 2):
                # Check if the pixel is pink (R, G, B values are close to 255, 0, 255)
                pixel = image.getpixel((i, j))
                if pixel[0] > 250 and 160 < pixel[1] < 170 and pixel[2] > 250:
                    return True  # Pink color found

    return False  # No pink color found within the circle

def find_pink_circle_files(folder_path, circle_radius):
    pink_circle_file_list = []

    # Iterate through all the files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is a PNG image
        if os.path.isfile(file_path) and file_path.lower().endswith(".png"):
            print(f'Checking {file_path}')
            if has_pink_circle(file_path, circle_radius):
                pink_circle_file_list.append(file_path)

    return pink_circle_file_list

# Folder path where the PNG files are located
folder = r"f:\BWD\CP60\TR\SOP1_A480\lowsun_fp\screenshots"

# Radius of the pink circle in pixels
radius = 30

# Find PNG files with a pink circle
pink_circle_files = find_pink_circle_files(folder, radius)

# Print the list of files with a pink circle
print("Files with a pink circle:")
for path in pink_circle_files:
    print(path)

serializer.save_json(pink_circle_files, folder, 'lowsun_fp_file_list.json')
