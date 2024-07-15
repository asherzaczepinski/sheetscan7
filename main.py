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

def process_line(input_y, img_array, width, difference_between_lines_for_line_drawing, difference_between_lines, line_height):
    black_notes = []
    white_notes = []
    dashed_whites = []
    black_count = 0
    difference_between_blacks = -1
    #white notes
    for x_index in range(width):
        pixel = img_array[input_y, x_index]
        if pixel != 255 and x_index != width - 1:
            black_count += 1
            if difference_between_blacks >= difference_between_lines_for_line_drawing * 0.4 and difference_between_blacks < difference_between_lines_for_line_drawing:
                counter = 0
                white_note = True
                above = False
                below = False
                max_above = -1
                max_below = -1
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
                #this is going across and then up and down 
                if white_note:
                    first = -1
                    middle = -1
                    start = x_index - difference_between_blacks
                    end = x_index + 1
                    for new_x_index in range(start, end):
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
                    left = -1
                    right = -1
                    left_x = x_index - difference_between_blacks - 1
                    while left_x > x_index - difference_between_blacks - 1 - difference_between_blacks:
                        temp_pixel = img_array[input_y, left_x]
                        if temp_pixel == 255:
                            left = left_x + 1
                            break
                        left_x -= 1
                    if left == -1:
                        white_note = False
                    if white_note:
                        for right_x in range (x_index + 1, x_index + difference_between_blacks):
                            temp_pixel = img_array[input_y, right_x]
                            if temp_pixel == 255:
                                right = right_x - 1
                                break
                        if right == -1:
                            white_note = False
                    if white_note:
                        past_temp_y_above = -1
                        past_temp_y_below = -1
                        #testing where it is here
                        start = x_index - difference_between_blacks + 1
                        end = x_index - 1

                        for new_x_index in range(start, end):
                            temp_pixel = img_array[input_y, new_x_index]
                            if temp_pixel != 255:
                                continue
                            temp_y_above = input_y
                            temp_y_below = input_y
                            while True:
                                continued = True
                                for new_x_index2 in range(left - int(difference_between_lines / 4), right + int(difference_between_lines / 4)):
                                    if img_array[temp_y_above, new_x_index2] == 255:
                                        continued = False
                                        break
                                if continued:
                                    break
                                if temp_y_above <= input_y - round(difference_between_lines_for_line_drawing * 3 / 4):
                                    white_note = False
                                    break
                                temp_pixel_above = img_array[temp_y_above, new_x_index]       
                                if temp_pixel_above != 255:
                                    break
                                temp_y_above -= 1   
                             

                            if white_note and past_temp_y_above != -1:
                                if past_temp_y_above - temp_y_above < 0:
                                    white_note = False
                            #the reason for the step on some is bc of both input_y on the two things
                            if white_note:
                                if temp_y_above <= max_above or max_above == -1:
                                    max_above = temp_y_above
                                while True:
                                    continued = True
                                    for new_x_index2 in range(left - int(difference_between_lines / 4), right + int(difference_between_lines / 4)):
                                        if img_array[temp_y_below, new_x_index2] == 255:
                                            continued = False
                                            break
                                    if continued:
                                        break
                                    if temp_y_below >= input_y + round(difference_between_lines_for_line_drawing * 3 / 4):
                                        white_note = False
                                        break
                                    temp_pixel_below = img_array[temp_y_below, new_x_index]      
                                    if temp_pixel_below != 255:
                                        break
                                    temp_y_below += 1  

                            if white_note and past_temp_y_below != -1:
                                if past_temp_y_below - temp_y_below < 0:
                                    white_note = False         

                            if white_note:
                                if temp_y_below >= max_below:
                                    max_below = temp_y_below
                                if new_x_index == start:
                                    first = round((temp_y_above + temp_y_below) / 2)
                                elif new_x_index == round((start + end) / 2):
                                    middle = round((temp_y_above + temp_y_below) / 2)
                                    if first - middle < int(difference_between_lines / 10):
                                        white_note = False
                                        break
                                elif new_x_index == end - 1:
                                    ending = round((temp_y_above + temp_y_below) / 2)
                                    if middle - ending < int(difference_between_lines / 10):
                                        white_note = False
                                        break        
                                if abs((past_temp_y_above - temp_y_above) - (temp_y_below - past_temp_y_below)) < difference_between_lines / 10 and past_temp_y_above - temp_y_above >= 0 and temp_y_below - past_temp_y_below >= 0:
                                    past_temp_y_above = temp_y_above
                                    past_temp_y_below = temp_y_below
                                elif past_temp_y_above == -1 or (abs(past_temp_y_above - temp_y_above) <= round(difference_between_lines / 5) and abs(past_temp_y_below - temp_y_below) <= round(difference_between_lines / 5)):
                                    past_temp_y_above = temp_y_above
                                    past_temp_y_below = temp_y_below
                                else:
                                    white_note = False
                                    break
                        if white_note:
                            #little /5 cuz it is not all the way
                            if max_above > input_y - round(difference_between_lines / 5):
                                white_note = False
                            if white_note:
                                if max_below < input_y + round(difference_between_lines / 5):
                                    white_note = False
                            #overall height check
                            if white_note:
                                if max_below - max_above > difference_between_lines + line_height:
                                    white_note = False
                        if white_note:
                            top_left = [left - 5, input_y - 10]
                            bottom_right = [right + 5, input_y + 10]   
                            white_notes.append([top_left, bottom_right])
            difference_between_blacks = 0
        else:
            #if it's white
            if difference_between_blacks != -1:
                difference_between_blacks += 1
    
    
    black_count = 0
    #black and dashed white

    for x_index in range(width):
        pixel = img_array[input_y, x_index]
        if pixel != 255 and x_index != width - 1:
            black_count += 1
        elif black_count >= difference_between_lines_for_line_drawing * 1.15 and black_count < difference_between_lines_for_line_drawing * 5:
            
            changed_direction_above = 0
            changed_direction_below = 0

            #apply my logic to see if it is a black note
            middle_x = x_index - round(black_count / 2)
            black_note = True
            for add in range(1, round(difference_between_lines_for_line_drawing / 2) - 1 - round(line_height / 2)):
                above_pixel = img_array[input_y - add, middle_x]
                below_pixel = img_array[input_y + add, middle_x]
                if above_pixel == 255 or below_pixel == 255:
                    black_note = False
            max_above = -1
            max_below = -1

            if black_note:
                if black_count < difference_between_lines_for_line_drawing * 1.5:
                    past_temp_y_above = -1
                    past_temp_y_below = -1
                    for new_x_index in range(x_index - black_count + 1, x_index - 1):
                        temp_pixel = img_array[input_y, new_x_index]      
                        continued = True
                        for new_y_index in range (input_y - difference_between_lines, input_y):
                            if img_array[new_y_index, new_x_index] == 255:
                                continued = False
                                break
                        if not continued:
                            for new_y_index in range (input_y, input_y + difference_between_lines):
                                if img_array[new_y_index, new_x_index] == 255:
                                    continued = False
                                    break
                                else:
                                    continued = True
                        if continued:
                            continue 
                        temp_y_above = input_y
                        temp_y_below = input_y                  
                        while True:
                            continued = True
                            for new_x_index2 in range(x_index - black_count + 1 - int(difference_between_lines / 4), x_index - 1 + int(difference_between_lines / 4)):
                                if img_array[temp_y_above, new_x_index2] == 255:
                                    continued = False
                                    break
                            if continued:
                                break
                            if temp_y_above <= input_y - round(difference_between_lines_for_line_drawing * 3 / 4):
                                black_note = False
                                break
                            temp_pixel_above = img_array[temp_y_above, new_x_index]       
                            if temp_pixel_above == 255:
                                break
                            temp_y_above -= 1

                        #the black notes pass the test

                        if black_note and past_temp_y_above != -1:
                            if changed_direction_above == 0: 
                                #going up has to start in this way
                                if past_temp_y_above - temp_y_above > 0:
                                    changed_direction_above = 1
                                elif past_temp_y_above - temp_y_above != 0:
                                    black_note = False
                            elif changed_direction_above == 1:
                                #if it's going up make sure it starts going down
                                if temp_y_above - past_temp_y_above > 0:
                                    changed_direction_above = 2
                            else:
                                if past_temp_y_above - temp_y_above > 0:
                                    black_note = False

                        if black_note:
                            if temp_y_above <= max_above or max_above == -1:
                                max_above = temp_y_above
                            while True:
                                continued = True
                                for new_x_index2 in range(x_index - black_count + 1 - int(difference_between_lines / 4), x_index - 1 + int(difference_between_lines / 4)):
                                    if img_array[temp_y_below, new_x_index2] == 255:
                                        continued = False
                                        break
                                if continued:
                                    break
                                if temp_y_below >= input_y + round(difference_between_lines_for_line_drawing * 3 / 4):
                                    black_note =  False
                                    break                                
                                temp_pixel_below = img_array[temp_y_below, new_x_index]      
                                if temp_pixel_below == 255:
                                    break
                                temp_y_below += 1   

                        if black_note and past_temp_y_below != -1:
                            if changed_direction_below == 0: 
                                #<= bc of the below it can start straight too not only down
                                if past_temp_y_below - temp_y_below <= 0:
                                    changed_direction_below = 1
                                else:
                                    black_note = False
                            elif changed_direction_below == 1:
                                #if it's going down or straight make sure it starts going up
                                if temp_y_below - past_temp_y_below < 0:
                                    changed_direction_below = 2
                            else:
                                if past_temp_y_below - temp_y_below < 0:
                                    black_note = False

                        if black_note: 
                            if temp_y_below >= max_below:
                                max_below = temp_y_below                                   
                            left_zone = False
                            if not left_zone and new_x_index >= x_index - black_count + 1:
                                if new_x_index >= x_index - round(black_count / 2):
                                    left_zone = True
                                #gives exception of if it increases proportiately
                                elif abs((past_temp_y_above - temp_y_above) - (temp_y_below - past_temp_y_below)) < difference_between_lines / 10 and past_temp_y_above - temp_y_above >= 0 and temp_y_below - past_temp_y_below >= 0:
                                    past_temp_y_above = temp_y_above
                                    past_temp_y_below = temp_y_below
                                #have no past
                                elif past_temp_y_above == -1:
                                    past_temp_y_above = temp_y_above
                                    past_temp_y_below = temp_y_below
                                #slowly increasing
                                elif past_temp_y_above - temp_y_above <= round(difference_between_lines / 5) and past_temp_y_above - temp_y_above >= 0:
                                    if temp_y_below - past_temp_y_below <= round(difference_between_lines / 5) and temp_y_below - past_temp_y_below >= 0:
                                        past_temp_y_above = temp_y_above
                                        past_temp_y_below = temp_y_below
                                #not the correct note
                                else:
                                    black_note = False
                                    break
                            elif new_x_index <= x_index - 1:
                                if abs((temp_y_above - past_temp_y_above) - (past_temp_y_below - temp_y_below)) < difference_between_lines / 10 and temp_y_above - past_temp_y_above >= 0 and past_temp_y_below - temp_y_below >= 0:
                                    past_temp_y_above = temp_y_above
                                    past_temp_y_below = temp_y_below
                                elif temp_y_above - past_temp_y_above <= round(difference_between_lines / 5) and temp_y_above - past_temp_y_above >= 0:
                                    if past_temp_y_below - temp_y_below <= round(difference_between_lines / 5) and past_temp_y_below - temp_y_below >= 0:
                                        past_temp_y_above = temp_y_above
                                        past_temp_y_below = temp_y_below
                                else:
                                    black_note = False
                                    break
                    black_note = False
                    if changed_direction_above == 2 or changed_direction_below == 2:
                        black_note = True
                    if black_note:
                        if max_above > input_y - round(difference_between_lines_for_line_drawing / 2) + (line_height * 2):
                            black_note = False
                        if black_note:
                            if max_below < input_y + round(difference_between_lines_for_line_drawing / 2) - (line_height * 2):
                                black_note = False
                        if black_note:
                            if max_below - max_above > difference_between_lines_for_line_drawing + (line_height * 3):
                                black_note = False
                    if black_note:
                        top_left = [x_index - black_count, input_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        bottom_right = [x_index, input_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        black_notes.append([top_left, bottom_right])

                else:
                    #dashed black
                    changed_direction_above = 0
                    changed_direction_below = 0
                    starting_above_black = input_y 
                    starting_below_black = input_y 
                    past_temp_y_above = -1
                    past_temp_y_below = -1
                    temp_pixel_above = img_array[starting_above_black, x_index - black_count + 1]
                    temp_pixel_below = img_array[starting_below_black, x_index - black_count + 1]    
                    while temp_pixel_below != 255:
                        starting_below_black += 1
                        temp_pixel_below = img_array[starting_below_black, x_index - black_count + 1]
                    while temp_pixel_above != 255:
                        starting_above_black -= 1
                        temp_pixel_above = img_array[starting_above_black, x_index - black_count + 1]
                    start_up = -1
                    end_up = -1
                    if black_note:
                        found_black = False


                        #this change of check wouldn't be game changing tho that is the thing! it would jus make sure the start up shit was more accurate
                        for new_x_index in range(x_index - black_count + 1, x_index):
                            new_pixel = img_array[starting_above_black, new_x_index]
                            if new_pixel == 0 and not found_black:



                                #have to run a check here ot make sure it is not a column type shit

                                found_black = True
                                start_up = new_x_index
                            elif found_black:


                                
                                #also run a check here

                                #white and a black has been found
                                end_up = new_x_index - 1
                        if end_up - start_up < difference_between_lines / 5:
                            black_note = False
                    start_down = -1
                    end_down = -1
                    if black_note:
                        found_black = False
                        for new_x_index in range(x_index - black_count + 1, x_index):
                            new_pixel = img_array[starting_below_black, new_x_index]
                            if new_pixel == 0 and not found_black:


                                #same run a check here
                                found_black = True
                                start_down = new_x_index
                            elif found_black:


                                #same run a check here
                                end_down = new_x_index - 1
                        if end_down - start_down < difference_between_lines / 5:
                            black_note = False
                    max_above = -1
                    max_below = -1

                    start = max(start_up, start_down)
                    end = min(end_up, end_down)
                    
                    #testing distance!!!
                    if abs(start_up - start_down) > difference_between_lines / 4 or abs(end_up - end_down) > difference_between_lines / 4:
                        black_note = False
                    if max(end_up, end_down) - min(start_up, start_down) > difference_between_lines * 2.5:
                        black_note = False
                    if end - start <= difference_between_lines * 1.15:
                        black_note = False
                    if black_note:
                        #it meets it on edges
                        past_temp_y_above = -1
                        past_temp_y_below = -1
                        for new_x_index in range(start, end):
                            #both have to have at least one white    
                            continued = True
                            for new_y_index in range (starting_above_black - difference_between_lines, starting_above_black):
                                if img_array[new_y_index, new_x_index] == 255:
                                    continued = False
                                    break
                            if not continued:
                                for new_y_index in range (starting_below_black, starting_below_black + difference_between_lines):
                                    if img_array[new_y_index, new_x_index] == 255:
                                        continued = False
                                        break
                                    else:
                                        continued = True
                            if continued:
                                continue 
                            temp_y_above = starting_above_black
                            temp_y_below = starting_below_black   
                            while True:
                                continued = True
                                for new_x_index2 in range(x_index - black_count + 1 - int(difference_between_lines / 4), x_index - 1 + int(difference_between_lines / 4)):
                                    if img_array[temp_y_above, new_x_index2] == 255:
                                        continued = False
                                        break
                                if continued:
                                    break
                                if temp_y_above <= input_y - (round(difference_between_lines_for_line_drawing) * 3 / 4) :
                                    black_note = False
                                    break

                                #there should be a number where temp_y_above is only there for this check or another variable if it hits where a line was
                                #i think this is the issue bc it is scared of the line it cuts off once it gets a max above
                                continued = True
                                most_left = -1
                                flag = False
                                while True:
                                    if most_left == -1:
                                        most_left = x_index - black_count + 1
                                    temp_pixel = img_array[temp_y_above, most_left]
                                    if temp_pixel == 255:
                                        most_left += 1
                                        break
                                    if x_index - most_left >= round(difference_between_lines * 2):
                                        flag = True
                                        break
                                    most_left -= 1
                                if not flag:
                                    for new_x_index2 in range (most_left, most_left + round(difference_between_lines * 2)):
                                        if img_array[temp_y_above, new_x_index2] == 255:
                                            continued = False
                                            break
                                temp_pixel_above = img_array[temp_y_above, new_x_index]       
                                if temp_pixel_above == 255:
                                    break
                                temp_y_above -= 1   

                            #this would all be working if temp_y_above worked better
                            if black_note and past_temp_y_above != -1:
                                if changed_direction_above == 0: 
                                    if past_temp_y_above - temp_y_above > 0:
                                        changed_direction_above = 1
                                    elif past_temp_y_above - temp_y_above != 0:                                        
                                        black_note = False
                                elif changed_direction_above == 1:
                                    #if it's going up make sure it starts going down
                                    if temp_y_above - past_temp_y_above > 0:
                                        changed_direction_above = 2
                                else:
                                    if past_temp_y_above - temp_y_above > 0:
                                        black_note = False  

                            if black_note:
                                if temp_y_above <= max_above or max_above == -1:
                                    max_above = temp_y_above
                                while True:
                                    continued = True
                                    for new_x_index2 in range(x_index - black_count + 1 - int(difference_between_lines / 4), x_index - 1 + int(difference_between_lines / 4)):
                                        if img_array[temp_y_below, new_x_index2] == 255:
                                            continued = False
                                            break
                                    if continued:
                                        break
                                    if temp_y_below >= input_y + (round(difference_between_lines_for_line_drawing) * 3 / 4):

                                        black_note = False
                                        break
                                    continued = True
                                    most_left = -1
                                    flag = False
                                    while True:
                                        if most_left == -1:
                                            most_left = x_index - black_count + 1
                                        temp_pixel = img_array[temp_y_below, most_left]
                                        if temp_pixel == 255:
                                            most_left += 1
                                            break
                                        if x_index - most_left >= round(difference_between_lines * 2):
                                            flag = True
                                            break
                                        most_left -= 1
                                    if not flag:
                                        for new_x_index2 in range (most_left, most_left + round(difference_between_lines * 2)):
                                            if img_array[temp_y_below, new_x_index2] == 255:
                                                continued = False
                                                break
                                    temp_pixel_below = img_array[temp_y_below, new_x_index]      
                                    if temp_pixel_below == 255:
                                        break
                                    temp_y_below += 1  

                                if black_note and past_temp_y_below != -1:
                                    if changed_direction_below == 0: 
                                        #<= bc of the below it can start straight too not only down
                                        if past_temp_y_below - temp_y_below <= 0:
                                            changed_direction_below = 1
                                        else:

                                            black_note = False
                                    elif changed_direction_below == 1:
                                        #if it's going down or straight make sure it starts going up
                                        if temp_y_below - past_temp_y_below < 0:
                                            changed_direction_below = 2
                                    else:
                                        if past_temp_y_below - temp_y_below < 0:
                                            black_note = False   
                                if black_note:
                                    if temp_y_below >= max_below:
                                        max_below = temp_y_below
                                    left_zone = False
                                    if not left_zone and new_x_index >= x_index - black_count + 1:
                                        if new_x_index >= x_index - round(black_count / 2):
                                            #note here
                                            left_zone = True
                                        #gives exception of if it increases proportiately
                                        elif abs((past_temp_y_above - temp_y_above) - (temp_y_below - past_temp_y_below)) < difference_between_lines / 10 and past_temp_y_above - temp_y_above >= 0 and temp_y_below - past_temp_y_below >= 0:
                                            past_temp_y_above = temp_y_above
                                            past_temp_y_below = temp_y_below
                                        #have no past
                                        elif past_temp_y_above == -1:                                            
                                            past_temp_y_above = temp_y_above
                                            past_temp_y_below = temp_y_below
                                        #slowly increasing
                                        elif past_temp_y_above - temp_y_above <= round(difference_between_lines / 5) and past_temp_y_above - temp_y_above >= 0:
                                            if temp_y_below - past_temp_y_below <= round(difference_between_lines / 5) and temp_y_below - past_temp_y_below >= 0:
                                                past_temp_y_above = temp_y_above
                                                past_temp_y_below = temp_y_below
                                        #not the correct note
                                        else:
                                            black_note = False
                                            break
                                    elif new_x_index <= x_index - 1:
                                        if abs((temp_y_above - past_temp_y_above) - (past_temp_y_below - temp_y_below)) < difference_between_lines / 10 and temp_y_above - past_temp_y_above >= 0 and past_temp_y_below - temp_y_below >= 0:
                                            past_temp_y_above = temp_y_above
                                            past_temp_y_below = temp_y_below
                                        elif temp_y_above - past_temp_y_above <= round(difference_between_lines / 5) and temp_y_above - past_temp_y_above >= 0:
                                            if past_temp_y_below - temp_y_below <= round(difference_between_lines / 5) and past_temp_y_below - temp_y_below >= 0:
                                                past_temp_y_above = temp_y_above
                                                past_temp_y_below = temp_y_below
                                        else:
                                            black_note = False
                                            break
                    
                    black_note = False
                    if changed_direction_above == 2 or changed_direction_below == 2:
                        black_note = True
                    if black_note:
                        if max_above > input_y - round(difference_between_lines_for_line_drawing / 2) + (line_height * 2):
                            black_note = False
                        if black_note:
                            if max_below < input_y + round(difference_between_lines_for_line_drawing / 2) - (line_height * 2):
                                black_note = False   
                        if black_note:
                            if max_below - max_above > difference_between_lines_for_line_drawing + (line_height * 3):
                                black_note = False

                    if black_note:
                        top_left = [x_index - black_count, input_y - (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        bottom_right = [x_index, input_y + (round(difference_between_lines_for_line_drawing / 2) - 1)]
                        black_notes.append([top_left, bottom_right])
                    black_count = 0

            else:
                #dashed white notes
                max_above = -1
                max_below = -1
                white_note = True
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

                if white_note:    
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

                starting_of_space_above_outside = -1
                ending_of_space_above_outside = -1
                starting_of_space_above_inside = -1
                ending_of_space_above_inside = -1
                
                #starting
                temporary_x = x_index - round(black_count / 2)
                #getting starting inside
                if white_note:
                    while True:
                        if temporary_x < 0: 
                            white_note = False
                            break
                        temp_pixel = img_array[starting_above_white, temporary_x]
                        if temp_pixel != 255:
                            starting_of_space_above_inside = temporary_x + 1
                            break
                        temporary_x -= 1
                if white_note:
                    while True:
                        if temporary_x < 0:
                            white_note = False
                            break
                        #think this is the right area
                        temp_pixel = img_array[starting_above_white, temporary_x]
                        if temp_pixel == 255:
                            starting_of_space_above_outside = temporary_x + 1
                            break
                        temporary_x -= 1
                #ending
                temporary_x = x_index - round(black_count / 2)
                if white_note:
                    while True:
                        if temporary_x >= width - 1: 
                            white_note = False
                            break
                        temp_pixel = img_array[starting_above_white, temporary_x]
                        if temp_pixel != 255:
                            ending_of_space_above_inside = temporary_x - 1
                            break
                        temporary_x += 1
                if white_note:
                    while True:
                        if temporary_x >= width - 1:
                            white_note = False
                            break
                        #think this is the right area
                        temp_pixel = img_array[starting_above_white, temporary_x]
                        if temp_pixel == 255:
                            ending_of_space_above_outside = temporary_x - 1
                            break
                        temporary_x += 1
               
                distance_above = ending_of_space_above_inside - starting_of_space_above_inside + 1

                if white_note:
                    if distance_above < (difference_between_lines / 3) or distance_above > (difference_between_lines):
                        white_note = False
                                
                starting_of_space_below_outside = -1
                ending_of_space_below_outside = -1
                starting_of_space_below_inside = -1
                ending_of_space_below_inside = -1
                if white_note:
                    #starting
                    temporary_x = x_index - round(black_count / 2)
                    #getting starting inside
                    while True:
                        if temporary_x < 0: 
                            white_note = False
                            break
                        temp_pixel = img_array[starting_below_white, temporary_x]
                        if temp_pixel != 255:
                            starting_of_space_below_inside = temporary_x + 1
                            break
                        temporary_x -= 1
                if white_note:
                    while True:
                        if temporary_x < 0:
                            white_note = False
                            break
                        temp_pixel = img_array[starting_below_white, temporary_x]
                        if temp_pixel == 255:
                            starting_of_space_below_outside = temporary_x + 1
                            break
                        temporary_x -= 1
                #ending
                if white_note:
                    temporary_x = x_index - round(black_count / 2)
                    while True:
                        if temporary_x >= width - 1: 
                            white_note = False
                            break
                        temp_pixel = img_array[starting_below_white, temporary_x]
                        if temp_pixel != 255:
                            ending_of_space_below_inside = temporary_x - 1
                            break
                        temporary_x += 1
                if white_note:
                    while True:
                        if temporary_x >= width - 1:
                            white_note = False
                            break
                        temp_pixel = img_array[starting_below_white, temporary_x]
                        if temp_pixel == 255:
                            ending_of_space_below_outside = temporary_x - 1
                            break
                        temporary_x += 1

                #+1 bc of how it is the inside white pixels spacing have to compensate
                distance_below = ending_of_space_below_inside - starting_of_space_below_inside + 1

                if distance_below < (difference_between_lines / 3):
                    white_note = False

                start = max(starting_of_space_above_outside, starting_of_space_below_outside)
                end = min(ending_of_space_above_outside, ending_of_space_below_outside)
                
                #testing distance!!!
                if abs(starting_of_space_above_outside - starting_of_space_below_outside) > difference_between_lines / 4 or abs(ending_of_space_above_outside - ending_of_space_below_outside) > difference_between_lines / 4:
                    white_note = False
                if max(ending_of_space_above_outside, ending_of_space_below_outside) - min(starting_of_space_above_outside, starting_of_space_below_outside) > difference_between_lines * 2.5:
                    white_note = False
                if end - start <= difference_between_lines * 1.15:
                    white_note = False

                #top part 
                if white_note:
                    past_temp_y = -1
                    for new_x_index in range(starting_of_space_above_inside, ending_of_space_above_inside):
                        temp_pixel = img_array[starting_above_white, new_x_index]
                        temp_y_above = starting_above_white
                        if white_note:
                            while True:
                                if temp_y_above <= input_y - round(difference_between_lines_for_line_drawing * 3 / 4):
                                    white_note = False
                                    break
                                temp_pixel_above = img_array[temp_y_above, new_x_index]
                                if temp_pixel_above != 255:
                                    break
                                temp_y_above -= 1
                            if temp_y_above <= max_above or max_above == -1:
                                max_above = temp_y_above
                            if past_temp_y == -1 or (abs(past_temp_y - temp_y_above) <= round(difference_between_lines / 5) and abs(past_temp_y - temp_y_above) <= round(difference_between_lines / 5)):
                                past_temp_y = temp_y_above
                            else:
                                white_note = False
                                break      

                #bottom part
                if white_note:
                    past_temp_y = -1
                    for new_x_index in range(starting_of_space_below_inside, ending_of_space_below_inside):
                        temp_pixel = img_array[starting_below_white, new_x_index]
                        temp_y_below = starting_below_white
                                
                        if white_note:
                            while True:
                                if temp_y_below >= input_y + round(difference_between_lines_for_line_drawing * 3 / 4):
                                    white_note = False
                                    break
                                temp_pixel_below = img_array[temp_y_below, new_x_index]
                                if temp_pixel_below != 255:
                                    break
                                temp_y_below += 1
                            if white_note:
                                if temp_y_below >= max_below:
                                    max_below = temp_y_below
                            if past_temp_y == -1 or (abs(past_temp_y - temp_y_below) <= round(difference_between_lines / 5) and abs(past_temp_y - temp_y_below) <= round(difference_between_lines / 5)):
                                past_temp_y = temp_y_below
                            else:
                                white_note = False
                                break
                        
                if white_note:
                    #little /5 cuz it is not all the way
                    if max_above > input_y - round(difference_between_lines / 5):
                        white_note = False
                    if white_note:
                        if max_below < input_y + round(difference_between_lines / 5):
                            white_note = False
                    #overall height check
                    if white_note:
                        if max_below - max_above > difference_between_lines + line_height:
                            white_note = False
                #put it in here
                if white_note:
                    #remove this eventually
                    top_left = [x_index - black_count, input_y - 10]
                    bottom_right = [x_index, input_y + 10]   
                    dashed_whites.append([top_left, bottom_right])

            black_count = 0       
        else:
            black_count = 0



    return dashed_whites, black_notes, white_notes

def sort_pairs(input_array):
    # Initialize an empty list to store the pairs
    pairs = []
    for sublist in input_array:
        pairs.extend(sublist)
    # Sort the pairs list by the first element of each pair
    pairs.sort(key=lambda x: x[0])
    # Calculate the middle value (rounded mean) for each pair and add to middle_values list
    middle_values = [round((pair[0] + pair[1]) / 2) for pair in pairs]
    return middle_values
def sort_notes(notes):
    sorted_notes = []
    for row in notes:
        sorted_row = sorted(row, key=lambda note: note[1][0][0])
        sorted_notes.append(sorted_row)
    return sorted_notes

def y_assigner(y_array, y):
    if not y_array:
        return None
    # Find the closest value using binary search
    pos = bisect.bisect_left(y_array, y)
    if pos == 0:
        return y_array[0]
    if pos == len(y_array):
        return y_array[-1]
    before = y_array[pos - 1]
    after = y_array[pos]
    if after - y < y - before:
        return after
    else:
        return before

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
    notes = []
    for group in invisible_lines:
        for [current_loop_y, new_y] in group:
            row_notes = []
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
                    row_notes.append(['black', black_note])
                    break
                next_note = all_blacks_in_line[index + 1]
                
                if next_note[0][0] - black_note[0][0] < difference_between_lines:
                    #compare which ones y is greater it doesn't matter the x
                    if next_note[0][1] < black_note[0][1]:
                        row_notes.append(['black', black_note])
                    else:
                        row_notes.append(['black', next_note])
                    index += 1
                else:
                    row_notes.append(['black', black_note])
                index += 1
            
            index = 0

            while index < len(all_whites_in_line):
                white_note = all_whites_in_line[index]
                if index == len(all_whites_in_line) - 1:
                    row_notes.append(['white', white_note])
                    break
                next_note = all_whites_in_line[index + 1]
                if next_note[0][0] - white_note[0][0] < difference_between_lines:
                    if next_note[0][1] < white_note[0][1]:
                        row_notes.append(['white', white_note])
                    else:
                        row_notes.append(['white', next_note])
                    index += 1
                else:
                    row_notes.append(['white', white_note])
                index += 1

            index = 0

            while index < len(all_dashed_whites_in_line):
                dashed_white = all_dashed_whites_in_line[index]
                if index == len(all_dashed_whites_in_line) - 1:
                    row_notes.append(['dashed_white', dashed_white])
                    break
                next_note = all_dashed_whites_in_line[index + 1]
                if next_note[0][0] - dashed_white[0][0] < difference_between_lines:
                    if next_note[0][1] < dashed_white[0][1]:
                        row_notes.append(['dashed_white', dashed_white])
                    else:
                        row_notes.append(['dashed_white', next_note])
                    index += 1
                else:
                    row_notes.append(['dashed_white', dashed_white])
                index += 1
            notes.append(row_notes)

    past_notes = []
    
    for index, row in enumerate(notes):
        if index != 0:
            for index2, note in enumerate(row):
                note = note[1]
                for index3, past_note in enumerate(past_notes):
                    past_note = past_note[1]
                    #this is an example of a specific usecase when removing!
                    if abs(past_note[0][0] - note[0][0]) <= difference_between_lines:
                        if past_notes[index3][0] == 'black' and row[index2][0] != 'black':
                            notes[index - 1].pop(index3)
                            break
                        else:
                            notes[index].pop(index2)
                            break
        past_notes = row

    sorted_middles = sort_pairs(invisible_lines)

    notes = sort_notes(notes)
    for row in notes:
        past_note = -1
        for note in row:
            note = note[1]
            #sometimes they like encompass each other thats y abs like it could start before end later
            if past_note != -1 and abs(note[1][0] - past_note) < (difference_between_lines * 2 / 3):
                continue
            top_left = note[0]
            bottom_right = note[1]
            assigned_value = y_assigner(sorted_middles, top_left[1] + (round(difference_between_lines_for_line_drawing / 2) - 1))
            top_left[1] = assigned_value - (round(difference_between_lines_for_line_drawing / 2) - 1)
            bottom_right[1] = assigned_value + (round(difference_between_lines_for_line_drawing / 2) - 1)
            #right side
            img_array[top_left[1] - 5: bottom_right[1] + 5, bottom_right[0] + 5] = 0
            #left side
            img_array[top_left[1] - 5: bottom_right[1] + 5, top_left[0] - 5] = 0
            #top side
            img_array[top_left[1] - 5, top_left[0] - 5:bottom_right[0] + 5] = 0
            #bottom side
            img_array[bottom_right[1] + 5, top_left[0] - 5:bottom_right[0] + 5] = 0  
            past_note = note[1][0]

    img = Image.fromarray(img_array)
    img.save(image_path)

    lines.append(image_path)
    all_rows.append(lines)
    
def open_pdf_into_input(pdf_path, input_folder, new_input):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    
    # Ensure input folder exists
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(new_input, exist_ok=True)

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Render page to a pixmap (an image) at 300 DPI
        pix = page.get_pixmap(dpi=300)
        
        # Convert the pixmap to a PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save the image to a file
        image_path = os.path.join(input_folder, f"page_{page_num + 1}.png")
        image_path2 = os.path.join(new_input, f"page_{page_num + 1}.png")
        img.save(image_path)
        img.save(image_path2)

# Example usage
pdf_path = "input.pdf"
input_folder = "input"
new_input = 'new_input'

open_pdf_into_input(pdf_path, input_folder, new_input)

for filename in os.listdir(input_folder):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        image_path = os.path.join(input_folder, filename)

        try:
            extract_highlighted_lines_and_columns_from_image(image_path)
        except IndexError as e:
            print(e) 

