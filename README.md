# Qbr

A rubik's cube solver written in python 3 using OpenCV via your webcam.

# Table of Contents

- [Qbr](#qbr)
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
    + [The first 9-stickers in the upper left corner](#the-first-9-stickers-in-the-upper-left-corner)
    + [The second 9-sticker display below the one in the upper left corner](#the-second-9-sticker-display-below-the-one-in-the-upper-left-corner)
    + [Amount of sides scanned](#amount-of-sides-scanned)
- [Getting the solution](#getting-the-solution)
    + [Keybindings](#keybindings)
- [Paramaters](#paramaters)
- [Example runs](#example-runs)
- [Inspirational sources](#inspirational-sources)
- [License](#license)

# Introduction

![demo](demo.jpg)

The idea to create this came personally to mind when I started solving rubik's
cubes.  My personal record is 7.90 seconds, but there were already so many
professional programmers around the world who created robots that solve a
rubik's cube in an ETA of 5 seconds and since 2016 in 1 second
([link](https://www.youtube.com/watch?v=ixTddQQ2Hs4)).
That inspired me to create my own. I started using images only and eventually switched to webcam.

Color detection might be a problem if you:
- Have colors that are not easy to distinguish
- Do not have the follow color scheme: white, yellow, red, orange, blue, green.

# Installation

```
$ git clone https://github.com/kkoomen/qbr.git
$ cd qbr
$ python3 -m venv env
$ source ./env/bin/activate
$ pip3 install -r requirements.txt
```

# Usage

Run Qbr:

```
$ ./src/qbr.py
```

This opens a webcam interface where you see basically the above photo.

There have 3 things:

### The first 9-stickers in the upper left corner

These will update immediately and display how the program has detected the colors.

### The second 9-sticker display below the one in the upper left corner

When pressing `SPACE` it will update this state in order to show you what state
it has saved. You can press space as many times as you'd like if it has been
detected wrong.

### Amount of sides scanned

In the bottom left corner is shown the amount of sides scanned. This is so you
know if you've scanned in all sides before pressing `ESC`.

# Getting the solution

Qbr checks if you have filled in all 6 sides when pressing `ESC`. If so, it'll
solve it if you've scanned it in correctly.

You should now see a solution (or an error if you did it wrong).

### Keybindings

- `SPACE` for saving the current state

- `ESC` to quit

# Paramaters

You can use `-n` or `--normalize` to also output the solution in a "human-readable" format.

For example:

* `R` will be: `Turn the right side a quarter turn away from you.`
* `F2` will be: `Turn the front face 180 degrees.`

You can also specify a language by passing in `-l` or `--language`. Default language
is set to `en`.

Available languages are:

| language | key  |
| ---      | ---  |
| English  | `en` |
| Dutch    | `nl` |

# Example runs

```
$ ./qbr.py
Starting position:
front: green
top: white

Moves: 20
Solution: U2 R D2 L2 F2 L U2 L F' U L U R2 B2 U' F2 D2 R2 D2 R2
```

```
$ ./qbr.py -n
Starting position:
front: green
top: white

Moves: 20
Solution: B2 U2 F' R U D' L' B' U L F U F2 R2 F2 D' F2 D R2 D2

1. Turn the back side 180 degrees.
2. Turn the top layer 180 degrees.
3. Turn the front side a quarter turn to the left.
4. Turn the right side a quarter turn away from you.
5. Turn the top layer a quarter turn to the left.
6. Turn the bottom layer a quarter turn to the left.
7. Turn the left side a quarter turn away from you.
8. Turn the back side a quarter turn to the right.
9. Turn the top layer a quarter turn to the left.
10. Turn the left side a quarter turn towards you.
11. Turn the front side a quarter turn to the right.
12. Turn the top layer a quarter turn to the left.
13. Turn the front side 180 degrees.
14. Turn the right side 180 degrees.
15. Turn the front side 180 degrees.
16. Turn the bottom layer a quarter turn to the left.
17. Turn the front side 180 degrees.
18. Turn the bottom layer a quarter turn to the right.
19. Turn the right side 180 degrees.
20. Turn the bottom layer 180 degrees.
```

# Inspirational sources

Special thanks to [HaginCodes](https://github.com/HaginCodes) for the main
inspiration on how to improve my color detection.

https://github.com/HaginCodes/3x3x3-Rubiks-Cube-Solver

http://programmablebrick.blogspot.com/2017/02/rubiks-cube-tracker-using-opencv.html

https://gist.github.com/flyboy74/2cc3097f784c8c236a1a85278f08cddd

https://github.com/dwalton76/rubiks-color-resolver

# License

Qbr is licensed under the MIT License.

Copyright (c) Kim Koomen.
