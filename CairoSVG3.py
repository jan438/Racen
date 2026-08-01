# importing pycairo
import cairo

# creating a SVG surface
# here geek95 is file name & 700, 700 is dimension
with cairo.SVGSurface("SVG/geek95_3.svg", 700, 700) as surface:

    # creating a cairo context object for SVG surface
    # using Context method
    context = cairo.Context(surface)

    # Creating a liner gradient object.
    lg3 = cairo.LinearGradient(20.0, 260.0,  20.0, 360.0)

    # adding color stripes
    lg3.add_color_stop_rgba(0.2, 0, 0, 0, 1)
    lg3.add_color_stop_rgba(0.5, 1, 1, 0, 1)
    lg3.add_color_stop_rgba(0.9, 0, 0, 0, 1)

    # Creating Shape
    context.rectangle(20, 260, 300, 100)
    context.set_source(lg3)

    # Fill the color inside the rectangle
    context.fill()

# printing message when file is saved
print("File Saved")

key = input("Wait")
