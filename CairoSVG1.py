# importing pycairo
import cairo

# creating a SVG surface
# here geek95 is file name & 700, 700 is dimension
with cairo.SVGSurface("SVG/geek95_1.svg", 700, 700) as surface:

    # creating a cairo context object for SVG surface
    # using Context method
    context = cairo.Context(surface)

    # Creating a liner gradient object.
    lg1 = cairo.LinearGradient(0.0, 0.0, 350.0, 350.0)

    # Creating Loops for adding color stripes
    count = 1
    i = 0.1
    while i < 1.0:
        if count % 2:
            lg1.add_color_stop_rgba(i, 0, 0, 0, 1)
        else:
            lg1.add_color_stop_rgba(i, 1, 0, 0, 1)
        i = i + 0.1
        count = count + 1

    # Creating Shape
    context.rectangle(20, 20, 300, 100)

    #
    context.set_source(lg1)
    # Fill the color inside the rectangle
    context.fill()

    # printing message when file is saved
print("File Saved")

key = input("Wait")
