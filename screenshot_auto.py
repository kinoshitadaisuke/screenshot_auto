#!/usr/pkg/bin/python3.9

#
# Time-stamp: <2022/02/27 20:35:49 (CST) daisuke>
#

#
# History
#
#    prototype on 26/Feb/2022
#

# importing argparse module
import argparse

# importing sys module
import sys

# importing time module
import time

# importing subprocess module
import subprocess

# importing pathlib module
import pathlib

# importing regular expression module
import re

# constructing a parser object
desc   = 'taking screenshots and moving to next page automatically'
parser = argparse.ArgumentParser (description=desc)

# adding arguments
choices_format = ['bmp', 'eps', 'gif', 'jpg', 'png', \
                  'pdf', 'ppm', 'ps', 'tiff', 'wmf']
choices_direction = ['vertical', 'horizontal']
parser.add_argument ('-b', '--book', default='book', \
                     help='book name (default: book)')
parser.add_argument ('-f', '--format', choices=choices_format, default='png', \
                     help='image format (default: PNG)')
parser.add_argument ('-i', '--initial', type=int, default=10, \
                     help='initial sleep time before screenshots (default: 10)')
parser.add_argument ('-n', '--number', type=int, default=100, \
                     help='number of pages (default: 100)')
parser.add_argument ('-s', '--sleep', type=int, default=2, \
                     help='sleep time between screenshots (default: 2 sec)')
parser.add_argument ('-c', '--convert', default='/usr/pkg/bin/convert', \
                     help='location of convert (default: /usr/pkg/bin/convert)')
parser.add_argument ('-t', '--xdotool', default='/usr/pkg/bin/xdotool', \
                     help='location of xdotool (default: /usr/pkg/bin/xdotool)')
parser.add_argument ('-p', '--xdpyinfo', default='/usr/X11R7/bin/xdpyinfo', \
                     help='location of xdpyinfo (default: /usr/X11R7/bin/xdpyinfo)')
parser.add_argument ('-w', '--xwd', default='/usr/X11R7/bin/xwd', \
                     help='location of xwd (default: /usr/X11R7/bin/xwd)')
parser.add_argument ('-x', '--offsetx', type=int, default=100, \
                     help='location of the mouse from edge (default: 100)')
parser.add_argument ('-y', '--offsety', type=int, default=100, \
                     help='location of the mouse from bottom (default: 100)')
parser.add_argument ('-d', '--direction', choices=choices_direction, \
                     default='vertical', \
                     help='writing direction (default: vertical)')

# parsing argument
args = parser.parse_args ()

# parameters
book_name         = args.book
image_format      = args.format
number_pages      = args.number
sleep_initial     = args.initial
sleep_interval    = args.sleep
command_convert   = args.convert
command_xdotool   = args.xdotool
command_xdpyinfo  = args.xdpyinfo
command_xwd       = args.xwd
offset_x          = args.offsetx
offset_y          = args.offsety
writing_direction = args.direction

# check of existence of commands
list_command = [command_convert, command_xdotool, command_xdpyinfo, command_xwd]
for command in list_command:
    path_command = pathlib.Path (command)
    if not (path_command.exists ()):
        print ("The command \"%s\" does not exists!")
        print ("Install the command \"%s\"!")
        print ("Exiting...")
        sys.exit ()

# size of the screen
output_xdpyinfo = subprocess.run (command_xdpyinfo, shell=True, \
                                  capture_output=True)
output_xdpyinfo_str = output_xdpyinfo.stdout.decode ('utf8')
pattern_dimensions = re.compile ('dimensions:\s+(\d+)x(\d+)\s+pixels')
match_dimensions = re.search (pattern_dimensions, output_xdpyinfo_str)
if (match_dimensions):
    x_size = int (match_dimensions.group (1))
    y_size = int (match_dimensions.group (2))
else:
    print ("Something is wrong with the command \"%s\"!" % command_xdpyinfo)
    sys.exit ()

# mouse cursor position
if (writing_direction == 'vertical'):
    mousepos_x = offset_x
    mousepos_y = y_size - offset_y
elif (writing_direction == 'horizontal'):
    mousepos_x = x_size - offset_x
    mousepos_y = y_size - offset_y
    
# printing status
print ("Taking screenshots")
print ("  Waiting %d sec before taking screenshots..." % sleep_initial)

# initial sleep before starting screenshots
time.sleep (sleep_initial)

# printing status
print ("  Now, starting to take screenshots!")

for i in range (number_pages):
    # file names
    file_base   = "%s_%06d" % (book_name, i)
    file_xwd    = "%s.%s" % (file_base, 'xwd')
    file_output = "%s.%s" % (file_base, image_format)

    # printing status
    print ("  Taking page %d..." % (i + 1) )
    print ("    now, taking a screenshot...")
    
    # taking a screenshot using 'xwd' command
    command_screenshot = "%s -root -out %s" % (command_xwd, file_xwd)
    subprocess.run (command_screenshot, shell=True)

    # printing status
    print ("    file \"%s\" is created!" % file_xwd)
    print ("    converting image to %s format..." % image_format)
    
    # converting file format
    command_conversion = "%s %s %s" % (command_convert, file_xwd, file_output)
    subprocess.run (command_conversion, shell=True)

    # printing status
    print ("    file \"%s\" is created!" % file_output)
    print ("    deleting the file \"%s\"..." % file_xwd)

    # removing xwd file
    path_xwd = pathlib.Path (file_xwd)
    path_xwd.unlink (missing_ok=True)

    # printing status
    print ("    finished deleting the file \"%s\"!" % file_xwd)
    print ("    simulating a mouse click...")

    # simulating a mouse move
    command_mousemove = "%s mousemove %d %d" \
        % (command_xdotool, mousepos_x, mousepos_y)
    subprocess.run (command_mousemove, shell=True)
    
    # simulating a mouse click to move to next page
    command_mouseclick = "%s click 1" % command_xdotool
    subprocess.run (command_mouseclick, shell=True)

    # printing status
    print ("    finished simulating a mouse click!")
    print ("    sleeping for %s sec..." % sleep_interval)
    
    # sleeping between screenshots
    time.sleep (sleep_interval)
        
    # printing status
    print ("    finished sleeping for %s sec!" % sleep_interval)
    print ("  Finished taking page %06d!" % (i + 1) )

print ("Finished taking screenshots for all the pages!")
