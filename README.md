# qbr.
A rubik's cube solver written in python 3 using OpenCV.

NOTE: qbr uses color detection and color detection is insanely hard to fix for
every possible situation, because certain light influences the color detector qbr uses.

# Table of Contents
- [Introduction](#introduction)
- [Usage](#usage)
    - [Paramaters](#paramaters)
- [License](#license)


# Introduction
The idea to create this came personally to mind when I started solving rubik's cubes.
I solve on average a 3x3x3 rubik's cube in 14 seconds when warmed up. My personal record
is 7.90 seconds, but there were already so many professional programmers around the world
who created robots that solve a rubik's cube in an ETA of 5 seconds and since 2016 in 1 second
([link](https://www.youtube.com/watch?v=ixTddQQ2Hs4)).
That inspired me to create my own. I started using images only and eventually switched to webcam.

One of the main things that killed me during developing this was color detection. It works for my
room, but I bet it doesn't work for you, or you must have the same lighting.

# Usage
![demo](demo.png)

Start off by cloning:
```
$ git clone https://github.com/muts/qbr.git
$ cd qbr/qbr/
```

Run qbr:

```
$ ./qbr.py
```

This opens a webcam interface where you see basically the above photo.
You have 3 things: 1) The 9 center squares. These are used for scanning in
your cube colors. 2) the 9 stickers in the upper left corner. These will update
immediately how the computer sees the colors. 3) when pressing `space` a 3rd
cube template appears below the one in the upper left corner. This is the state
that is saved, so you know how qbr saved it.

Two keybindings are available: `space` for saving the current view and `esc` for
quit. Qbr checks if you have filled in all 6 sides when pressing `esc`. If so, it'll
solve it if you've scanned it in correctly.

You should now see a solution (or an error if you did it wrong).

# paramaters

You can use `-n` or `--normalize` to also output the solution in a "human-readable" format.

For example:
`R` will be: `Turn the right side a quarter turn away from you.`

You can also specify a language by passing in `-l` or `--language`. Default language
is set to `en`. The only language other then english that is available is dutch which
is specified with `nl`.


#### Example run:

```
$ ./qbr.py
-- SOLUTION --
Starting position:
    front: green
    top: white

U2 R D2 L2 F2 L U2 L F' U L U R2 B2 U' F2 D2 R2 D2 R2 (20 moves)
```


# License

qbr is licensed under the MIT License.

Copyright (c) muts.
