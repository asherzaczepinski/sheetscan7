#make a review page for my amazing product on my website
#work on making the going down logic for notes to be better!
#make sure the lines r being removed
#if we implement the decreasing stuff we might be able to forget the percentage thing





#IF I FIX THE LINE REMOVAL STUFF I CAN NARROW DOWN THE AREA FOR The BLACK NOTES AND NOT IMPLEMENT THE SUPER COMPLICATED
#DECREASING METHOD. THIS WAY I DON'T HAVE TO WORK ON TOO MUCH



#instead of circling black or white notes could also mark it right before based on the mode
#then if there is a note in the vicinity we would then circle beau and jake told me this
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

    #I think it is not removing the whole thing we should get this working
                  
    temp_output_folder = 'test_output_first'
    modified_img = Image.fromarray(img_array)

    # Ensure the output directory exists
    if not os.path.exists(temp_output_folder):
        os.makedirs(temp_output_folder)
    
    # Construct the output image path
    image_filename = os.path.basename(image_path)
    output_image_path = os.path.join(temp_output_folder, image_filename)
    
    # Save the modified image to the output path
    modified_img.save(output_image_path)


    #ooooOOOOOOH IT's NOT REMOVING THE WHITE LINES AFTER
    #I THINK I DELETED THAT PART
    #THIS WOULD FIX A LOT OF STUFF RN
    #BECAUSE ITS LOOKING FOR THE BLACK STUFF IN THE LINES ANYWAYS
    #HAVE GOT TO FIX THISSSSSS!!!!




    #replace the part we took out
    for row in lines:
        upper_line_y = row[1] - 1
        bottom_line_y = row[3] 
        for x_index in range(width):
            if img_array[upper_line_y, x_index] != 255 and img_array[bottom_line_y, x_index] != 255:
                for y in range(upper_line_y + 1, bottom_line_y):
                    img_array[y, x_index] = 0
    
    
    #have to prove img_array is working bc our issue w the  long things shouldn't be happening can also work down there
                    

    temp_output_folder = 'test_output_second'
    modified_img = Image.fromarray(img_array)

    # Ensure the output directory exists
    if not os.path.exists(temp_output_folder):
        os.makedirs(temp_output_folder)
    
    # Construct the output image path
    image_filename = os.path.basename(image_path)
    output_image_path = os.path.join(temp_output_folder, image_filename)
    
    # Save the modified image to the output path
    modified_img.save(output_image_path)


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




    #need to do the take out and replace thing right here!!!!!
    #for the new white lines!
    #this is good for everything especially bc it could rly fuck up the white replace thing
    #i can do the white replacement above and do the black fill in blanks between
    
    for group in invisible_lines:
        #It might have to do with this

        for current_loop_y in group:

            half_height = round(difference_between_lines_for_line_drawing / 2)
            top = max(0, current_loop_y - half_height)
            bottom = min(img_array.shape[0], current_loop_y + half_height)
            
            # Assuming you want to crop the entire width of the image
            left = 0
            right = img_array.shape[1]

            #Black notes

            black_count = 0

            #IF IT ACTUALLY REMOVES THE LINES AND REPLACES THEM OUR A SHOULDN'T BE AN ISSUE
            #WE HAVE TO IMPLEMENT THIS AND WORK FROM THERE CONCISING DOWN OUR CODE!!!!
            for x_index in range(width):
                pixel = img_array[current_loop_y, x_index]
                if pixel != 255 and x_index != width - 1:
                    black_count += 1
                #we basically have to make sure the new blackcount when we adjust the image is less than difference_between_lines_for_line_drawing * 1.5
                #same with when we draw any rectangle
                elif black_count >= difference_between_lines_for_line_drawing * 1.15:
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
                        little_increment = int(difference_between_lines_for_line_drawing / (7/3))
                        top_left = [x_index - black_count, current_loop_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        bottom_right = [x_index, current_loop_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        roi = img_array[top_left[1]:bottom_right[1], top_left[0] + little_increment:bottom_right[0] - little_increment]
                        total_pixels = roi.size
                        non_white_pixels = np.sum(roi < 255)
                        non_white_percentage = (non_white_pixels / total_pixels) * 100

                        if non_white_percentage > 80:
                            draw_example_rectangle(image_path, (top_left[0] - 10, top_left[1] - 10, bottom_right[0] + 10, bottom_right[1] + 10))
            
                    
                        elif black_count >= difference_between_lines_for_line_drawing * 1.5:

                   
                            new_roi = img_array[top_left[1]:bottom_right[1], top_left[0] + little_increment:bottom_right[0] - little_increment]
                            new_total_pixels = new_roi.size
                            new_non_white_pixels = np.sum(new_roi < 255)
                            new_non_white_percentage = (new_non_white_pixels / new_total_pixels) * 100

                            if new_non_white_percentage > 80:





                                #have to do the going down pixel calculation
                                #this way we go through each line
                                draw_example_rectangle(image_path, (top_left[0] - 10, top_left[1] - 10, bottom_right[0] + 10, bottom_right[1] + 10))



                        black_count = 0
                else:
                    black_count = 0
            
            #white notes
            #once we implement the across white secross from black to black should be this much then, we can go up and down from the middle of white_count
            #when we're going up and down if it qualifies we can take the column that went up and down and keep moving left and right
            #we have to make sure the last black point and top black point decreases and increases
            #could loop 5 times or the whole thing for that matter
            #we could also do this for the black notes but it might be excess and could be a feature i add later on!
                    
            # Crop the image
            cropped_img = img.crop((left, top, right, bottom))

            # Output directory for cropped images
            output_dir = "output_segments"
            os.makedirs(output_dir, exist_ok=True)

            # File name for the cropped image
            file_name = f"{Path(image_path).stem}_{current_loop_y}_{left}_{top}_{right}_{bottom}.png"

            # Save the cropped image directly in the 'output_segments' directory
            cropped_img.save(os.path.join(output_dir, file_name))

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
pdf_path = "input.pdf"
input_folder = "input"

open_pdf_into_input(pdf_path, input_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(input_folder, filename)
        extract_highlighted_lines_and_columns_from_image(image_path)
            
