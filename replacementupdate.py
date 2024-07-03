#only filling in the white notes not dashed cuz they haven't been replaced

# split eveyrthing into two seperste parts above and below



#number one add something to main.py where if anything in the loop range has a big line through it then we say this is not a black note
#after we make the simple one difference or none up aand get to a certain specific height (we can test in here that height relative to difference between lines make it a lil under) and it has to get there before halfway
#then halfway thru we make it go down
#do this top and bottom
#there is no way in hell our program isn't accurate


#fuck this make chatgpt do this stuff
#i will start working on black note in main.py
#can do that when we land in the terminal

from PIL import Image, ImageDraw
from pathlib import Path
import fitz  # PyMuPDF
import bisect

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

#for testing purposes only
def draw_example_rectangle(image_path, rect):
    # Validate rectangle coordinates
    if not all(isinstance(coord, (int, float)) for coord in rect):
        print(f"Invalid rectangle coordinates: {rect}")
        return

    # Load the image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    # Draw each rectangle
    try:
        draw.rectangle(rect, fill=None, outline="black", width=1)
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
    width = img_array.shape[1]

    height = img_array.shape[0]

    # This will hold the lines found in the image
    lines = []

    # Variable to track the start of a line
    start_line = -1

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

    #just copy and paste in certain parts don't need only this there were other variables in main.py
    difference_between_lines = lines[1][1] - lines[0][3]

    #replace the part we took out
    hits = 0
    spotting_for_white = False
    white_space = 0
    hits2 = 0
    for row in lines:
        upper_line_y = row[1] - 1
        bottom_line_y = row[3] 
        for x_index in range(width):
            got_hit = False
            if img_array[upper_line_y, x_index] != 255 and img_array[bottom_line_y, x_index] != 255:
                for y in range(upper_line_y + 1, bottom_line_y):
                    img_array[y, x_index] = 0
                got_hit = True
                    

            if got_hit:
                hits += 1
                if spotting_for_white:
                    hits2 += 1
            else:
                if spotting_for_white:
                    white_space += 1
                    if white_space >= difference_between_lines:
                        hits2 = 0
                        hits = 0
                        white_space = 0
                        spotting_for_white = False
                    else:
                        if hits2 <= round(difference_between_lines / 3):
                            if white_space >= difference_between_lines / 3 and hits2 != 0:
                                print('got to here will do replacing')
                                img_array[round((upper_line_y + bottom_line_y) / 2), x_index - round(white_space / 2)] = 50
                        else:
                            hits = 0
                            hits2 = 0
                            white_space = 0
                            spotting_for_white = False
                if hits <= round(difference_between_lines / 3) and hits != 0:
                    spotting_for_white = True

                hits = 0

    
    
    img = Image.fromarray(img_array)
    img.save(image_path)

    lines.append(image_path)
    all_rows.append(lines)
    
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
        image_path2 = os.path.join(input_folder, f"temp_page_{page_num + 1}.png")
        img.save(image_path)
        img.save(image_path2)
    
    # Close the document
    doc.close()

# Example usage
pdf_path = "input.pdf"
input_folder = "input"

open_pdf_into_input(pdf_path, input_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(input_folder, filename)
        #extract_highlighted_lines_and_columns_from_image(image_path)

        try:
            extract_highlighted_lines_and_columns_from_image(image_path)
        except IndexError as e:
            print(e) 

#don't remove the new stuff we're gonna need it at the end to add all the notes we find
            