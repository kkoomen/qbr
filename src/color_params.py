# Color detection parameters

# The parameters are used by colordetection.py

# Default values for the parameters

# white-filter
sat_W = 60  # hsv-pixels with a saturation s > sat_W are considered not to be a white facelet-pixel
val_W = 150 # hsv-pixels with a value v < sat_W are considered not to be a white facelet-pixel

# These parameters depend on the actually used cube colors and lightning conditions
orange_L = 6    # lowest hue for the color orange
orange_H = 23   # highest allowed hue for the color orange
yellow_H = 50   # highest allowed hue for the color yellow
green_H = 100   # highest allowed hue for the color green
blue_H = 160    # highest allowed hue for the color blue
# hue values > blue_H and < orange_H describe the color red

