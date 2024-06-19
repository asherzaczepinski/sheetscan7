#COPY AND PASTE THE NEW WHITE NOTe STATEMENTS INTO OUR MAIN.PY THIS IS OUR FINAL GOAL!!!!!
#THE IMG ARRAYS AND OTHER STUFF HAS BEEN EDITED FOR TESTING ANYWAYS!


#for black notes we could incorporate our same concept we did on the white notes but just w black pixels









#I JUST REALIZE FOR EVERY NOTe WE SHOULD FIGURE OUT WHICH CURRENT LOOP Y IT IS CLOSEST TO AND REASSIGN ITS Y BASED OFF THIS FOR THE CENTER Y THIS IS AN IMPORTANT STEP I CAN IMPLEMENT AFTER THE BLACK NOTe SHIT
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

def process_line(input_y, img_array, width, difference_between_lines_for_line_drawing, difference_between_lines, line_height):
    black_notes = []
    white_notes = []
    dashed_whites = []
    last_row_notes = []
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
                    #making sure there is not too much variation
                    if white_note:
                        past_temp_y_above = -1
                        past_temp_y_below = -1
                        #testing where it is here
                        for new_x_index in range(x_index - difference_between_lines + 1, x_index - 1):
                            temp_pixel = img_array[input_y, new_x_index]
                            if temp_pixel != 255:
                                continue
                            temp_y_above = input_y
                            temp_y_below = input_y
                            
                            while temp_y_above > input_y - round(difference_between_lines_for_line_drawing / 2):
                                temp_pixel_above = img_array[temp_y_above, new_x_index]       
                                if temp_pixel_above == 0:
                                    break
                                temp_y_above -= 1
                            if white_note:
                                while temp_y_below < input_y + round(difference_between_lines_for_line_drawing / 2):
                                    temp_pixel_below = img_array[temp_y_below, new_x_index]      
                                    if temp_pixel_below == 0:
                                        break
                                    temp_y_below += 1
                                if past_temp_y_above == -1 or (abs(past_temp_y_above - temp_y_above) <= round(difference_between_lines / 10) and abs(past_temp_y_below - temp_y_below) <= round(difference_between_lines / 10)):
                                    past_temp_y_above = temp_y_above
                                    past_temp_y_below = temp_y_below
                                else:
                                    white_note = False
                                    break
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




                #put in the last row notes temp notes after this




                #working here!!!!
                if black_count < difference_between_lines_for_line_drawing * 1.5:
                    past_temp_y_above = -1
                    past_temp_y_below = -1
                    #testing where it is here
                    for new_x_index in range(x_index - black_count + 1, x_index - 1):
                        temp_pixel = img_array[input_y, new_x_index]
                        if temp_pixel != 0:
                            continue
                        temp_y_above = input_y
                        temp_y_below = input_y
                        
                        while temp_y_above > input_y - round(difference_between_lines_for_line_drawing / 2):
                            temp_pixel_above = img_array[temp_y_above, new_x_index]       
                            if temp_pixel_above == 255:
                                break
                            temp_y_above -= 1
                        while temp_y_below < input_y + round(difference_between_lines_for_line_drawing / 2):
                            temp_pixel_below = img_array[temp_y_below, new_x_index]      
                            if temp_pixel_below == 255:
                                break
                            temp_y_below += 1
                        if past_temp_y_above == -1 or (abs(past_temp_y_above - temp_y_above) <= round(difference_between_lines / 10) and abs(past_temp_y_below - temp_y_below) <= round(difference_between_lines / 10)):
                            past_temp_y_above = temp_y_above
                            past_temp_y_below = temp_y_below
                        else:
                            black_note = False
                            break
                    if black_note:
                        if last_row_notes == []:
                            top_left = [x_index - black_count, input_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                            bottom_right = [x_index, input_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
                            black_notes.append([top_left, bottom_right])
                        else:
                            none_above = True 
                            for note in last_row_notes:
                                #or we can account for the -10!!!!! by saying - 10
                                if note[0][0] - 10 >= top_left[0] - 5 and note[0][0] - 10 <= top_left[0] + 5:
                                    none_above = False
                            if none_above:
                                #black notes
                                top_left = [x_index - black_count, input_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                                bottom_right = [x_index, input_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
                                black_notes.append([top_left, bottom_right])
                else:
                    print('found a dashed black --- edited it to calculate before on the above below part')
                    starting_above_white = input_y 
                    starting_below_white = input_y 
                    #changing it has to start before
                    temp_pixel_above = img_array[starting_above_white, x_index - black_count + 1]
                    temp_pixel_below = img_array[starting_below_white, x_index - black_count + 1]    
                    while temp_pixel_below != 255:
                        starting_below_white += 1
                        temp_pixel_below = img_array[starting_below_white, x_index - black_count + 1]
                    while temp_pixel_above != 255:
                        starting_above_white -= 1
                        temp_pixel_above = img_array[starting_above_white, x_index - black_count + 1]
                    counter = 0
                    above = False
                    below = False
                    white_note = True
                    print(black_note)
                    while True:
                        temp_pixel_above = img_array[starting_above_white - counter, x_index - black_count + 1]
                        temp_pixel_below = img_array[starting_below_white + counter, x_index - black_count + 1]
                        if counter > int(difference_between_lines_for_line_drawing / 3.5):
                            black_note = False
                            break
                        if temp_pixel_above != 255:
                            above = True
                        if temp_pixel_below != 255:
                            below = True
                        if above and below:
                            break
                        counter += 1
                    #copy and paste the rest in here
                    if black_note:
                        print(img_array[starting_above_white - 0, x_index - black_count + 1])
                    #AFTER WE GET TOP WE FIGURE WHERE THE note STARTS AND ENDS
                    #WE DO THE WHITE note SHIT ON THE BLCK note STUFF
                    #EVENTUALLY MAKE EVERY note Y ASSIGNED TO ITS CLOSEST CURRENT LOOP Y WILL BE A SUPER QUICK THING
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


                #its going across on just above the top line and bottom line
                #its making sure there is not more than one gap while also making sure there is 
                    
                #keepworking here
                #top part
                if white_note:
                    first_switch = False
                    space_counter = 0
                    past_temp_y = -1
                    for new_x_index in range(x_index - round(difference_between_lines * 1.5), x_index - round(difference_between_lines * 0.5)):
                        temp_pixel = img_array[starting_above_white, new_x_index]
                        if temp_pixel != 255:
                            if space_counter > 0:
                                if not first_switch:
                                    first_switch = True
                                    space_counter = 0
                                else:
                                    white_note = False
                                    break
                            continue
                        else:
                            space_counter += 1
                        temp_y_above = starting_above_white

                        if white_note:
                            while temp_y_above > input_y - round(difference_between_lines_for_line_drawing / 2):
                                temp_pixel_above = img_array[temp_y_above, new_x_index]
                                if temp_pixel_above == 0:
                                    break
                                temp_y_above -= 1
                            if past_temp_y == -1 or (abs(past_temp_y - temp_y_above) <= round(difference_between_lines / 10) and abs(past_temp_y - temp_y_above) <= round(difference_between_lines / 10)):
                                past_temp_y = temp_y_above
                            else:
                                white_note = False
                                break
                #bottom part
                if white_note:
                    first_switch = False
                    space_counter = 0
                    past_temp_y = -1
                    for new_x_index in range(x_index - round(difference_between_lines * 2), x_index - difference_between_lines):
                        temp_pixel = img_array[starting_below_white, new_x_index]
                        if temp_pixel != 255:
                            if space_counter > 0:
                                if not first_switch:
                                    first_switch = True
                                    space_counter = 0
                                else:
                                    white_note = False
                                    break
                            continue
                        else:
                            space_counter += 1
                        temp_y_below = starting_below_white

                        if white_note:
                            while temp_y_below < input_y + round(difference_between_lines_for_line_drawing / 2):
                                temp_pixel_below = img_array[temp_y_below, new_x_index]
                                if temp_pixel_below == 0:
                                    break
                                temp_y_below += 1
                            if past_temp_y == -1 or (abs(past_temp_y - temp_y_below) <= round(difference_between_lines / 10) and abs(past_temp_y - temp_y_below) <= round(difference_between_lines / 10)):
                                past_temp_y = temp_y_below
                            else:
                                white_note = False
                                break
                     
                
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

    for group in invisible_lines:
        for [current_loop_y, new_y] in group:
            row_black_notes = []
            # Process the lines and get the notes
            current_dashed_whites, current_black_notes, current_white_notes = process_line(
                current_loop_y, img_array, width, difference_between_lines_for_line_drawing, 
                difference_between_lines, line_height
            )
            new_dashed_whites, new_black_notes, new_white_notes = process_line(
                new_y, img_array, width, difference_between_lines_for_line_drawing, 
                difference_between_lines, line_height
            )

            all_blacks_in_line = sorted(current_black_notes + new_black_notes, key=lambda note: note[0][0])
            all_whites_in_line = sorted(current_white_notes + new_white_notes, key=lambda note: note[0][0])
            all_dashed_whites_in_line = sorted(current_dashed_whites + new_dashed_whites, key=lambda note: note[0][0])

            index = 0

            while index < len(all_blacks_in_line):
                black_note = all_blacks_in_line[index]
                if index == len(all_blacks_in_line) - 1:
                    row_black_notes.append(black_note)
                    break
                next_note = all_blacks_in_line[index + 1]
                
                if next_note[0][0] - black_note[0][0] < difference_between_lines:
                    #compare which ones y is greater it doesn't matter the x
                    if next_note[0][1] < black_note[0][1]:
                        row_black_notes.append(black_note)
                    else:
                        row_black_notes.append(next_note)
                    index += 1
                else:
                    row_black_notes.append(black_note)
                index += 1
            
            index = 0

            while index < len(all_whites_in_line):
                white_note = all_whites_in_line[index]
                if index == len(all_whites_in_line) - 1:
                    white_notes.append(white_note)
                    break
                next_note = all_whites_in_line[index + 1]
                if next_note[0][0] - white_note[0][0] < difference_between_lines:
                    if next_note[0][1] < white_note[0][1]:
                        white_notes.append(white_note)
                    else:
                        white_notes.append(next_note)
                    index += 1
                else:
                    white_notes.append(white_note)
                index += 1

            index = 0

            while index < len(all_dashed_whites_in_line):
                dashed_white = all_dashed_whites_in_line[index]
                if index == len(all_dashed_whites_in_line) - 1:
                    dashed_whites.append(dashed_white)
                    break
                next_note = all_dashed_whites_in_line[index + 1]
                if next_note[0][0] - dashed_white[0][0] < difference_between_lines:
                    if next_note[0][1] < dashed_white[0][1]:
                        dashed_whites.append(dashed_white)
                    else:
                        dashed_whites.append(next_note)
                    index += 1
                else:
                    dashed_whites.append(dashed_white)
                index += 1
            black_notes.append(row_black_notes)

    past_notes = []

    for index, row in enumerate(black_notes):
        if index != 0:
            for index2, black_note in enumerate(row):
                for past_note in past_notes:
                    if abs(past_note[0][0] - black_note[0][0]) <= difference_between_lines:
                        black_notes[index].pop(index2)
                        break
        past_notes = row

    for row in black_notes:
        for black_note in row:
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

        img_array[round((bottom_right[1] + top_left[1]) / 2), bottom_right[0] + 10] = 0

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
        