#some stuff is screwed up with replacement
#it just has to do when it is replaced
#don't need output segments but need columns
#the draw_example rectangles explains a lot of issues when it's inside the black note logic this is wherei should be working from!

from PIL import Image, ImageDraw
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

all_black_notes = []

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

    # This will hold the lines found in the image
    lines = []

    # Variable to track the start of a line
    start_line = -1

    black_notes = []

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

    #replace the part we took out
    for row in lines:
        upper_line_y = row[1] - 1
        bottom_line_y = row[3] 
        for x_index in range(width):
            if img_array[upper_line_y, x_index] != 255 and img_array[bottom_line_y, x_index] != 255:
                for y in range(upper_line_y + 1, bottom_line_y):
                    img_array[y, x_index] = 0
    
    invisible_lines = []

    #Space it in middle for line identification

    difference_between_lines_for_line_drawing = lines[1][1] - lines[0][1] 

    #line height

    line_height = lines[0][3] - lines[0][1]

    #For note heights

    staff_white_range = (lines[len(lines) - 5][1] - lines[len(lines) - 6][1]) / 2 
    
    group = []

    for row_index in range(len(lines)):
        row = lines[row_index]
        current_y = row[1]
        #this is when it is on the last line of a staff and ends up going down
        if (row_index + 1) % 5 == 0:
            #Going to work on the removal of the every other line HERE!!!!
            if row_index == len(lines) - 1:
                stopping_point = row[1] + staff_white_range
            else:
                stopping_point = (row[1] + lines[row_index + 1][1]) / 2
            while current_y <= stopping_point:
                group.append(current_y)
                current_y += round(difference_between_lines_for_line_drawing / 2)
            invisible_lines.append(group)
            group = []
        #this is on the first line of a staff and goes up 
        elif row_index % 5 == 0:
            #Going to work on the removal of the every other line HERE!!!!
            if row_index == 0:
                stopping_point = row[1] - staff_white_range
            else:
                stopping_point = (row[1] + lines[row_index - 1][1]) / 2
            while current_y >= stopping_point:
                group.append(current_y)
                current_y -= round(difference_between_lines_for_line_drawing / 2)
            for add_row_index in range(4):
                future_line = lines[row_index + add_row_index + 1][1] 
                group.append(int((future_line + lines[row_index + add_row_index][1]) / 2))
                if add_row_index != 3:
                    group.append(future_line)

    for group in invisible_lines:
        #It might have to do with this
        last_row_notes = []
        for current_loop_y in group:
            temp_notes = []
            half_height = round(difference_between_lines_for_line_drawing / 2)
            top = max(0, current_loop_y - half_height)
            bottom = min(img_array.shape[0], current_loop_y + half_height)
            
            # Assuming you want to crop the entire width of the image
            left = 0
            right = img_array.shape[1]

            black_count = 0



            #this here is our white note logic I'm thinking of doing a diagonal slash and going from there
            difference_between_blacks = -1

            for x_index in range(width):
                pixel = img_array[current_loop_y, x_index]
                #if it's black
                if pixel != 255 and x_index != width - 1:
                    black_count += 1
                    if difference_between_blacks >= difference_between_lines_for_line_drawing * 0.4 and difference_between_blacks < difference_between_lines_for_line_drawing:
                        counter = 0
                        white_note = True


                        #will eventually take out try except
                        try:
                            while True:
                                temp_pixel_above = img_array[x_index - int(difference_between_blacks / 2), current_loop_y - counter]
                                temp_pixel_below = img_array[x_index - int(difference_between_blacks / 2), current_loop_y + counter]

                                #figure out issues here
                                if counter > difference_between_lines_for_line_drawing / 3 or current_loop_y + counter > width - 2:
                                    white_note = False
                                    break
                                if temp_pixel_above != 255 and temp_pixel_below != 255 and counter < difference_between_lines_for_line_drawing / 3:
                                    break
                                counter += 1
                        except Exception as e:
                            print(e)
                            print(current_loop_y)
                            #how is current loop y so high!
                            print(counter)



                        #going to do the up and down thing
                        #then going to calculate the left right
                        #then going to calculate if there is a line above or not
                        #can calculate it right off of the top part
                        #if so ignore the top and if not heck for the top left and bottom right being black
                        #we can calculate the top and bottom max when there is no line
                        #we will calculate line by going across and seeing if all is 100% black the average line height amount of times 
                        #maybe ceil / 2 idk
                        if white_note:
                            draw_example_rectangle(image_path, (x_index - int(difference_between_blacks / 2) - 10, current_loop_y - 10, x_index - int(difference_between_blacks / 2) + 10, current_loop_y + 10))
                    difference_between_blacks = 0
                else:
                    #if it's white
                    if difference_between_blacks != -1:
                        difference_between_blacks += 1

            #will do dash through middle whites here
            black_count = 0
            
            for x_index in range(width):
                pixel = img_array[current_loop_y, x_index]
                if pixel != 255 and x_index != width - 1:
                    black_count += 1
                elif black_count >= difference_between_lines_for_line_drawing * 1.15 and black_count < difference_between_lines_for_line_drawing * 5:
                    #apply my logic to see if it is a black note
                    middle_x = x_index - round(black_count / 2)
                    #-1 to discount the current one
                    black_note = True
                    for add in range(1, round(difference_between_lines_for_line_drawing / 2) - 1 - round(line_height / 2)):
                        above_pixel = img_array[current_loop_y - add, middle_x]
                        below_pixel = img_array[current_loop_y + add, middle_x]
                        if above_pixel == 255 or below_pixel == 255:
                            black_note = False
                            black_count = 0
                    if black_note:
                        #has to be x, y tuple
                        top_left = [x_index - black_count, current_loop_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        bottom_right = [x_index, current_loop_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        roi = img_array[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                        total_pixels = roi.size
                        non_white_pixels = np.sum(roi < 255)
                        non_white_percentage = (non_white_pixels / total_pixels) * 100
                        if non_white_percentage > 70:
                            if black_count >= difference_between_lines_for_line_drawing * 1.5:
                                if last_row_notes == []:
                                    black_notes.append([top_left, bottom_right])
                                else:
                                    none_above = True 
                                    for note in last_row_notes:
                                        #have to get middle here they won't align perfectly
                                        #or we can account for the -10!!!!! by saying - 10
                                        if note[0][0] - 10 >= top_left[0] - 5 and note[0][0] - 10 <= top_left[0] + 5:
                                            none_above = False
                                    if none_above:
                                        black_notes.append([top_left, bottom_right])
                            else:
                                temp_notes.append([top_left, bottom_right])
                                black_notes.append([top_left, bottom_right])
                        elif black_count >= difference_between_lines_for_line_drawing * 1.5:
                            little_increment = int(difference_between_lines_for_line_drawing / (7/3))          
                            new_roi = img_array[top_left[1]:bottom_right[1], top_left[0] + little_increment:bottom_right[0] - little_increment]
                            new_total_pixels = new_roi.size
                            new_non_white_pixels = np.sum(new_roi < 255)
                            new_non_white_percentage = (new_non_white_pixels / new_total_pixels) * 100
                            if new_non_white_percentage > 80:
                                if last_row_notes == []:
                                    black_notes.append([top_left, bottom_right])
                                else:
                                    none_above = True 
                                    for note in last_row_notes:
                                        #or we can account for the -10!!!!! by saying - 10
                                        if note[0][0] - 10 >= top_left[0] - 5 and note[0][0] - 10 <= top_left[0] + 5:
                                            none_above = False
                                    if none_above:
                                        black_notes.append([top_left, bottom_right])
                        black_count = 0
                else:
                    black_count = 0
            last_row_notes = temp_notes


    #put this back once white note logic is solid
    """ #drawing the black_notes
    for black_note in black_notes:
        top_left = black_note[0]
        bottom_right = black_note[1]
        draw_example_rectangle(image_path, (top_left[0] - 10, top_left[1] - 10, bottom_right[0] + 10, bottom_right[1] + 10))
 """
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
        img.save(image_path)
    
    # Close the document
    doc.close()

# Example usage
pdf_path = "oldinput.pdf"
input_folder = "input"

open_pdf_into_input(pdf_path, input_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(input_folder, filename)
        try:
            extract_highlighted_lines_and_columns_from_image(image_path)
        except Exception as e:
            print(e)