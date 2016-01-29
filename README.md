# qbr.
A rubik's cube solver written in python 3 using OpenCV.

![demo](demo.png)

You can scan in all 6 sides of your rubik's cube. Order doesn't matter. When you
are satisfied with the preview showing in the top left corner you press space bar.
When you have scanned in all your 6 sides, you can press escape and the algorithm
is shown below for example as follows:

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
