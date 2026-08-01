# code
import cairo
print("GFG")
# importing pycairo

# creating a SVG surface
# here geek95 is file name & 700, 700 is dimension
with cairo.SVGSurface("SVG/geek95_2.svg", 700, 700) as surface:

    # creating a cairo context object for SVG surface
    # using Context method
    context = cairo.Context(surface)

    # Creating a liner gradient object.
    lg2 = cairo.LinearGradient(0.0, 0.0, 350.0, 0.0)

    count = 1
    i = 0.05
    # Creating Loops for adding color stripes
    while i < 0.95:
        if count % 2:
            lg2.add_color_stop_rgba(i, 0, 0, 0, 1)
        else:
            lg2.add_color_stop_rgba(i, 0, 0, 1, 1)
        i = i + 0.025
        count = count + 1
    # Creating Shape
    context.rectangle(20, 20, 300, 100)
    context.set_source(lg2)
    # Fill the color inside the rectangle
    context.fill()
# printing message when file is saved
print("File Saved")

key = input("Wait")
