# Hand drawn animation of SVG files with HTML

This python package converts an SVG file into an HTML page containing
animations of each SVG element, such that the drawing looks as if it were
being hand-drawn.

## Using the script

There is a video showing the whole process
[here](https://www.youtube.com/watch?v=MjYMQuLoW8M), but I recommend reading the
section below first.

1. Organize your SVG file accordingly (see [The SVG layout](#the-svg-layout)).
  1. This can be done with your favorite SVG editor.
2. From the top level directory, run:

```sh
PYTHONPATH=. python3 examples/example.py <svg_file> <output.html>
```

Open `<output.html>` with a browser.

This has yet to be published as a proper python package.

## The SVG layout

The SVG format can be thought of as a graph:

* Objects (*paths*, *rectangles*, etc) are nodes (leaves).
* *Groups* of objects are nodes (not necessarily leaves).
* There is an edge between a group `G` and an object `O` if `O` is a direct
member of `G`.

For example, we might have this structure:

```
  rectangle1
  group1
    path1
    path2
  par_group2
    group21
      path3
      path4
    group22
      path5
      path6
```

In this case, these are all the edges in the graph:

* `group1` to `path1, path2`
* `par_group2` to `group21, group22`
* `group21` to `path3, path4`
* `group22` to `path5, path6`

The edges flowing out of a group are stored in an *ordered* container, i.e. the
order in which they appear in the `.svg` file.

## Converting the SVG graph to an animation

By organizing an SVG file as a graph, we impose an order between nodes of the
graph. This order is then going to be exploited to create an animation by
visiting nodes and applying some rules to them:

* The graph is visited with a depth-first search.
* If a path is encountered, a hand-writing animation is generated.
* If a rectangle is encountered, a camera-movement animation is generated.
* If a group whose name starts with `par_` is encountered, its children
will be animated in parallel.
* If a group with any other name is encountered, its children will be
animated sequentially with respects to each other.

This is implemented in [SvgVisitors.py](https://github.com/felipepiovezan/svg_html_animation/blob/main/svganimator/SvgVisitors.py).

Additionally, we add a pause (click/tap to continue) between any two top level nodes.

In this example, we would have:

```
  rectangle1
  group1
    path1
    path2
  par_group2
    group21
      path3
      path4
    group22
      path5
      path6
  rectangle2
```

* Camera is set to `rectangle1`.
* Upon click, `path1` is drawn, then `path2` is drawn (no pause between them).
* Upon click, everything in `group21` and `group22` will be drawn at the same time.
  * Note: `path3` and `path4` are drawn sequentially.
  * Note: `path5` and `path6` are drawn sequentially.
* Upon click, camera is set to `rectangle2`.

This can be seen rendered [here](https://felipepiovezan.github.io/animator_example).
Animations were slowed down for visualization purposes.
The SVG source file is [here](https://github.com/felipepiovezan/svg_html_animation/blob/main/examples/example.svg).


# Implementation

TBD.
