#once we figure out rows i don't know if we need preprocessing







from PIL import Image, ImageDraw
import shutil
from pathlib import Path
import fitz  # PyMuPDF

import numpy as np
import os

import argparse

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("inputfolder", help="Input Folder", nargs='?', default="input")

args = parser.parse_args()

# Threshold for line to be considered as an initial staff line #
threshold = 0.6

all_rows = []
all_columns = []
def draw_example_rectangle(image_path, rect):
    # Validate rectangle coordinates
    if not all(isinstance(coord, (int, float)) for coord in rect):
        print(f"Invalid rectangle coordinates: {rect}")
        return

    # Load the image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Draw each rectangle
    print("Drawing rectangle:", rect)  # Debugging statement
    try:
        draw.rectangle(rect, fill="black", width=1)
    except ValueError as e:
        print(f"Failed to draw rectangle {rect} on {image_path}: {e}")
        return

    # Save the image with rectangles
    img.save(image_path)


def extract_highlighted_lines_and_columns_from_image(image_path, threshold=2/3):
    # Load the image
    img = Image.open(image_path).convert("L")  # Convert to grayscale

    # Convert the PIL Image to a NumPy array
    img_array = np.array(img)

    # Get image width
    width, height = img_array.shape[1], img_array.shape[0]

    # This will hold the lines found in the image
    lines = []
    columns = []

    # Variable to track the start of a line
    start_line = -1

    for x in range(width):
        column_start = -1
        column = []
        for y in range(height):
            if img_array[y, x] < 255:  # Pixel is not white
                if column_start == -1:
                    column_start = y
            else:
                if column_start != -1 and (y - column_start) >= 200:
                    column.append([x, column_start, x + 1, y])
                    #put this back later
                    img_array[column_start:y, x:x + 1] = 255


                    #find this but we rly only need the x that's all 
                    column_start = -1  # Reset column_start for the next potential column
                else:
                    column_start = -1  # Reset column_start if the column height is less than 50
        if len(column) > 0:
            columns.append(column)
    # Iterate through each row of pixels
    for row_index, row in enumerate(img_array):
        # Count non-white (in grayscale, white is 255) pixels in the row
        non_white_pixels = np.sum(row != 255)
        # Highlight the row if the count exceeds the threshold
        if non_white_pixels > (threshold * width):
            img_array[row_index: row_index + 1, 0: width] = 255
            if start_line == -1:
                start_line = row_index
        else:
            # If a line was started previously, add it to the list
            if start_line != -1:
                lines.append([0, start_line, width, row_index])
                start_line = -1  # Reset start_line

    
    # Save the modified image
    Image.fromarray(img_array).save(image_path)


    #this won't work anymore
    """ for vert in columns:
        for column in vert:
            draw_example_rectangle(image_path, column) """
    # Append the lines found in the image to the list
    lines.append(image_path)
    all_rows.append(lines)
    columns.append(image_path)
    all_columns.append(columns)

def open_pdf_into_input(pdf_path, input_folder):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Ensure input folder exists
    os.makedirs(input_folder, exist_ok=True)

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Render page to a pixmap (an image) at 300 DPI
        pix = page.get_pixmap(dpi=300)
        
        # Convert the pixmap to a PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save the image to a file
        image_path = os.path.join(input_folder, f"page_{page_num + 1}.png")
        img.save(image_path)
    
    # Close the document
    doc.close()

def duplicate_folder(src, dst):
    """
    Duplicate a folder from src to dst. If dst exists, it will be removed first.

    :param src: Source folder path
    :param dst: Destination folder path
    """
    # Convert to Path objects for convenience
    src_path = Path(src)
    dst_path = Path(dst)

    # Check if the source directory exists
    if not src_path.is_dir():
        raise ValueError(f"The source directory {src} does not exist.")
    
    # If destination directory exists, remove it first
    if dst_path.exists():
        shutil.rmtree(dst_path)
    
    # Copy the directory tree to the new location
    shutil.copytree(src_path, dst_path)

# Example usage
pdf_path = "input.pdf"
input_folder = "input"

#uncomment enventually

open_pdf_into_input(pdf_path, input_folder)



for filename in os.listdir(input_folder):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(input_folder, filename)
        extract_highlighted_lines_and_columns_from_image(image_path)

source_folder = 'input'
destination_folder = 'new_input'
duplicate_folder(source_folder, destination_folder)

def draw_example_rectangle(image_path, rect):
    # Load the image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    # Draw the rectangle
    print("Drawing rectangle:", rect)  # Debugging statement to show which rectangle is being drawn
    draw.rectangle(rect, fill="black", width=1)
    
    # Save the image with rectangles drawn
    img.save(image_path)
            
new_columns = []
for page in all_columns:
    saved_vert = []
    current_page = []
    past_x = -1
    page_location = f"new_input/{str(page[-1])[5:]}"
    for line_index, line in enumerate(page[:-1]):  # Exclude the last item (image path)
        x = line[0][0]
        if x >= past_x + 1 and x <= past_x + 5 and past_x != -1:
            if line[0][1] >= page[line_index - 1][0][1] - 5 and line[0][1] <= page[line_index - 1][0][1] + 5:
            #we have to make sure right here the past_x + 1 and this crap actually have the same columns
            #we can prob do this by just checking the first one and assuming based off the y
            #will do this
            #let's say they are not the same
            #what we can do is do two different checks
            #we will somehow need to split it
                if saved_vert == []:
                    saved_vert = page[line_index - 1].copy()
            else:
                #how will we split up is the question
                #splitting here and moving on
                #all we want to do is append the first column in it's own right... can use the previous saved_vert
                #then we will start a new saved_vert with the new past_x + 1
                new_vert = saved_vert.copy()
                for column in new_vert:
                    column[2] = page[line_index - 1][0][2]
                current_page.append(new_vert)
                saved_vert = page[line_index].copy()

        elif saved_vert != []:
            new_vert = saved_vert.copy()
            for column in new_vert:
                column[2] = page[line_index - 1][0][2]
            current_page.append(new_vert)
            saved_vert = []
        if line_index == len(page) - 2 and saved_vert != []:
            new_vert = saved_vert.copy()
            # Adjust the end x-coordinate to match the last column in the merged group

            #and for here we have to go through the actual new_vert and compare the columns one by one in two nested for loops
            #this will decide what we keep and don't keep


            for column in new_vert:
                column[2] = page[line_index - 1][0][2]
            current_page.append(new_vert)
        past_x = x
    current_page.append(page[-1])  # Add the image path to the current page's columns
    new_columns.append(current_page)

#going to comment this for testing

for page in new_columns:
    page_location = f"new_input/{str(page[-1])[5:]}"  # Image path is the last element
    for vert_line in page[:-1]:  # Exclude the last item (image path)
        for column in vert_line:
            draw_example_rectangle(page_location, column)
