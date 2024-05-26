


#NEXT STEP:

#+intlineheight/2 logic checkup
#everytime we find a note we will have an int in that section such as black_note

#we will create a dictionary where the number integer of that thing such as 0 for the first and 1 for second 

#if there is greater than 1 we access the x, y values in the dictionary and delete the second one below, however if there is only one we keep whatever was put there whether it be one or two

#ONCE THIS IS REMOVED WE WILL CONTINUE WORKING ON THE DASH THRU WHITES


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

#going to process this of a current loop y and the new_y


def process_line(input_y, img_array, width, difference_between_lines_for_line_drawing, difference_between_lines, line_height):
    black_notes = []
    white_notes = []
    dashed_whites = []
    
    last_row_notes = []

    #WE JUST NEED IT TO COMPARE TWO ARRAYS DON'T NEED TO KNOW WHICH NOTES THEY ARE WE CAN COMPARE IT AGAINST EACH OTHER


    #ya it's gonna have to do something for both
    temp_notes = []        
    black_count = 0
    difference_between_blacks = -1



    #white notes
    for x_index in range(width):
        pixel = img_array[input_y, x_index]
        #if it's black
        if pixel != 255 and x_index != width - 1:
            black_count += 1
            if difference_between_blacks >= difference_between_lines_for_line_drawing * 0.4 and difference_between_blacks < difference_between_lines_for_line_drawing:
                counter = 0
                white_note = True
                above = False
                below = False
                #quick up and down check
                while True:
                    temp_pixel_above = img_array[input_y - counter, x_index - int(difference_between_blacks / 2)]
                    temp_pixel_below = img_array[input_y + counter, x_index - int(difference_between_blacks / 2)]
                    if counter > difference_between_lines_for_line_drawing / 3:
                        white_note = False
                        break
                    if temp_pixel_above != 255:
                        above = True
                    if temp_pixel_below != 255:
                        below = True
                    if above and below and counter < difference_between_lines_for_line_drawing / 3:
                        break
                    counter += 1
                #this is a quick check to make sure this isn't dashed
                for i in range (0, line_height):
                    temp_pixel_below = img_array[input_y + i, x_index - int(difference_between_lines / 2)] 
                    if temp_pixel_below != 255:
                        white_note = False
                #this is going across and then up and down 
                if white_note:
                    for new_x_index in range(x_index - difference_between_lines, x_index + 1):
                        temp_y_above = input_y
                        temp_y_below = input_y
                        above_flag = False
                        below_flag = False
                        while temp_y_above > input_y - round(difference_between_lines_for_line_drawing / 2):
                            temp_pixel_above = img_array[temp_y_above, new_x_index]                                        
                            if temp_pixel_above != 255:
                                above_flag = True
                                break
                            temp_y_above -= 1
                        if above_flag == False:
                            white_note = False
                        if white_note:
                            while temp_y_below < input_y + round(difference_between_lines_for_line_drawing / 2):
                                temp_pixel_below = img_array[temp_y_below, new_x_index]                                            
                                if temp_pixel_below != 255:
                                    below_flag = True
                                    break
                                temp_y_below += 1
                            if below_flag == False:
                                white_note = False
                    #this will do the top right thing after determining everything else works 
                    if white_note:
                        up = 0
                        up_right = 0
                        counter = 1
                        while True:
                            temp_pixel_0 = input_y - up
                            temp_pixel_1 = x_index - difference_between_blacks - 1 + up_right
                            temp_pixel = img_array[temp_pixel_0, temp_pixel_1]
                            if temp_pixel_0 <= input_y - difference_between_lines / 2 or temp_pixel_1 > x_index - (difference_between_blacks / 2) - 1:
                                break
                            if temp_pixel == 255:
                                white_note = False
                                break
                            right_addend = 0
                            while True:
                                if temp_pixel_1 + right_addend >= width:
                                    white_note = False
                                    break
                                new_pixel = img_array[temp_pixel_0 - 1, temp_pixel_1 + right_addend]                                    
                                if new_pixel == 255:
                                    break
                                right_addend += 1
                            up += 1
                            up_right += right_addend - 1
                            counter += 1
                    #always have the option to do bottom left later if that is neccesary!
                    if white_note:
                        top_left = [x_index - int(difference_between_blacks / 2) - 10, input_y - 10]
                        bottom_right = [x_index - int(difference_between_blacks / 2) + 10, input_y + 10]   
                        white_notes.append([top_left, bottom_right])
            difference_between_blacks = 0
        else:
            #if it's white
            if difference_between_blacks != -1:
                difference_between_blacks += 1
    
    #black notes
                
    black_count = 0
    
    #black and dashed white
    for x_index in range(width):
        pixel = img_array[input_y, x_index]
        if pixel != 255 and x_index != width - 1:
            black_count += 1
        elif black_count >= difference_between_lines_for_line_drawing * 1.15 and black_count < difference_between_lines_for_line_drawing * 5:
            #apply my logic to see if it is a black note
            middle_x = x_index - round(black_count / 2)
            black_note = True
            for add in range(1, round(difference_between_lines_for_line_drawing / 2) - 1 - round(line_height / 2)):
                above_pixel = img_array[input_y - add, middle_x]
                below_pixel = img_array[input_y + add, middle_x]
                if above_pixel == 255 or below_pixel == 255:
                    black_note = False
            if black_note:
                #black notes
                top_left = [x_index - black_count, input_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                bottom_right = [x_index, input_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
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


                #dashed white notes

                starting_above_white = input_y 
                starting_below_white = input_y 
                temp_pixel_above = img_array[starting_above_white, x_index - int(black_count / 2)]
                temp_pixel_below = img_array[starting_below_white, x_index - int(black_count / 2)]    
                while temp_pixel_below != 255:
                    starting_below_white += 1
                    temp_pixel_below = img_array[starting_below_white, x_index - int(black_count / 2)]
                while temp_pixel_above != 255:
                    starting_above_white -= 1
                    temp_pixel_above = img_array[starting_above_white, x_index - int(black_count / 2)]
                #point 1
                counter = 0
                above = False
                below = False
                white_note = True
                while True:
                    temp_pixel_above = img_array[starting_above_white - counter, x_index - int(black_count / 2)]
                    temp_pixel_below = img_array[starting_below_white + counter, x_index - int(black_count / 2)]
                    if counter > int(difference_between_lines_for_line_drawing / 3.5):
                        white_note = False
                        break
                    if temp_pixel_above != 255:
                        above = True
                    if temp_pixel_below != 255:
                        below = True
                    if above and below:
                        break
                    counter += 1
                #point 2                           
                if white_note:
                    #remove this eventually
                    top_left = [x_index - int(black_count / 2) - 10, input_y - 10]
                    bottom_right = [x_index - int(black_count / 2) + 10, input_y + 10]   
                    dashed_whites.append([top_left, bottom_right])

            black_count = 0       
        else:
            black_count = 0
    last_row_notes = temp_notes

    return dashed_whites, black_notes, white_notes


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

    black_notes = []

    white_notes = []

    dashed_whites = []

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

    #difference between lines

    difference_between_lines = lines[1][1] - lines[0][3]

    #line height

    line_height = lines[0][3] - lines[0][1]

    #For note heights

    staff_white_range = (lines[len(lines) - 5][1] - lines[len(lines) - 6][1]) / 2 
    
    group = []

    temp_difference = -1

    for row_index in range(len(lines)):
        row = lines[row_index]
        current_y = row[1]
        if (row_index + 1) % 5 == 0:
            if row_index == len(lines) - 1:
                stopping_point = row[1]
                while stopping_point < height and stopping_point <= row[1] + staff_white_range:
                    stopping_point += round(temp_difference / 2)
                stopping_point -= round(temp_difference / 2)
            else:
                stopping_point = (row[1] + lines[row_index + 1][1]) / 2
            while current_y <= stopping_point:
                group.extend([[current_y, current_y + round(line_height / 2)]])
                current_y += round(temp_difference / 2)
            invisible_lines.append(group)
            group = []
        #this is on the first line of a staff and goes up 
        elif row_index % 5 == 0:
            #Going to work on the removal of the every other line HERE!!!!
            temp_difference = lines[row_index + 1][1] - current_y
            if row_index == 0:
                stopping_point = row[1] 
                while stopping_point > 0 and stopping_point >= row[1] - staff_white_range:
                    stopping_point -= round(temp_difference / 2)
                stopping_point += round(temp_difference / 2)
            else:
                stopping_point = (row[1] + lines[row_index - 1][1]) / 2
            while current_y >= stopping_point:
                group.extend([[current_y, current_y + round(line_height / 2)]])
                current_y -= round(temp_difference / 2)
            for add_row_index in range(4): 
                future_line = lines[row_index + add_row_index + 1][1] 
                group.extend([[int((future_line + lines[row_index + add_row_index][1]) / 2), int((future_line + lines[row_index + add_row_index][1]) / 2) + round(line_height / 2)]])
                if add_row_index != 3:
                    group.extend([[future_line, future_line + round(line_height / 2)]])

    print(difference_between_lines)
    for group in invisible_lines:
        for [current_loop_y, new_y] in group:
            # Process the lines and get the notes
            current_dashed_whites, current_black_notes, current_white_notes = process_line(
                current_loop_y, img_array.copy(), width, difference_between_lines_for_line_drawing, 
                difference_between_lines, line_height
            )
            new_dashed_whites, new_black_notes, new_white_notes = process_line(
                new_y, img_array.copy(), width, difference_between_lines_for_line_drawing, 
                difference_between_lines, line_height
            )

            #this is where the comparison proessing will go down!!!

            all_blacks_in_line = sorted(current_black_notes + new_black_notes, key=lambda note: note[0][0])

            #then we are going to go thru this!
            #print('hi') -> this proves it's working 

            index = 0

            #i'm worried what happens to that last note once index overlaps and there is nothing left lets go from here keep that in mind see if we get an index out of bounds error
            #once this is working then we can do this to the other notes not just black notes
            #then we adjust the logic to use the same as the normal for the dashed thru whites
            #then we work on sharp and flat and natural
            #we add back in columns
            #we determine and know what to circle
            #we're done and i make a website for this
            while index < len(all_blacks_in_line):
                black_note = all_blacks_in_line[index]
                next_note = all_blacks_in_line[index + 1]
                #the one closer to bottom will have been the 'second one' and not the one closer to current loop y
                if next_note[0][0] - black_note[0][0] < int(difference_between_lines / 3):
                    #compare which ones y is greater it doesn't matter the x
                    if next_note[0][1] < black_note[0][1]:
                        black_notes += black_note
                    else:
                        black_notes += next_note

                    #so we can skip past the second note
                    #maybe we say index += 1 again
                    index += 1
                    #have to add an index thing here
                else:
                    black_notes += black_note
                index += 1
            
            black_notes += (current_black_notes + new_black_notes)
            white_notes += (current_white_notes + new_white_notes)
            dashed_whites += (current_dashed_whites + new_dashed_whites)

    for black_note in black_notes:
        top_left = black_note[0]
        bottom_right = black_note[1]
        #right side
        img_array[top_left[1] - 5: bottom_right[1] + 5, bottom_right[0] + 5] = 0
        #left side
        img_array[top_left[1] - 5: bottom_right[1] + 5, top_left[0] - 5] = 0
        #top side
        img_array[top_left[1] - 5, top_left[0] - 5:bottom_right[0] + 5] = 0
        #bottom side
        img_array[bottom_right[1] + 5, top_left[0] - 5:bottom_right[0] + 5] = 0  

    for white_note in white_notes:
        top_left = white_note[0]
        bottom_right = white_note[1]
        #right side
        img_array[top_left[1] - 5: bottom_right[1] + 5, bottom_right[0] + 5] = 0
        #left side
        img_array[top_left[1] - 5: bottom_right[1] + 5, top_left[0] - 5] = 0
        #top side
        img_array[top_left[1] - 5, top_left[0] - 5:bottom_right[0] + 5] = 0
        #bottom side
        img_array[bottom_right[1] + 5, top_left[0] - 5:bottom_right[0] + 5] = 0      
    
    for dashed_white in dashed_whites:
        top_left = dashed_white[0]
        bottom_right = dashed_white[1]
        #right side
        img_array[top_left[1] - 5: bottom_right[1] + 5, bottom_right[0] + 5] = 0
        #left side
        img_array[top_left[1] - 5: bottom_right[1] + 5, top_left[0] - 5] = 0
        #top side
        img_array[top_left[1] - 5, top_left[0] - 5:bottom_right[0] + 5] = 0
        #bottom side
        img_array[bottom_right[1] + 5, top_left[0] - 5:bottom_right[0] + 5] = 0      

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
        #extract_highlighted_lines_and_columns_from_image(image_path)

        try:
            extract_highlighted_lines_and_columns_from_image(image_path)
        except IndexError as e:
            print(e) 
        