#WE COULD MAYBE MAKE A MORE EFFICIENT VERSION WHERE IT CHECKS THE OUTSIDE AND THEN WORKS ITS WAY IN on all of the things like newyindex newxindex
#do it w any of the loops
""" 
while True:
                            
    if temp_y_above <= input_y - round(difference_between_lines_for_line_drawing):
        black_note = False
        break

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
    if temp_pixel_above == 255 or temp_y_above <= input_y - (difference_between_lines / 2):
        break

    temp_y_above -= 1

check old white note logic and incorporate that flag shit later """