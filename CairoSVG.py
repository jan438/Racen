import cairo
with cairo.SVGSurface("SVG/geek95_1.svg", 700, 700) as surface:
    context = cairo.Context(surface)
    lg1 = cairo.LinearGradient(0.0, 0.0, 350.0, 350.0)
    count = 1
    i = 0.1
    while i < 1.0:
        if count % 2:
            lg1.add_color_stop_rgba(i, 0, 0, 0, 1)
        else:
            lg1.add_color_stop_rgba(i, 1, 0, 0, 1)
        i = i + 0.1
        count = count + 1
    context.rectangle(20, 20, 300, 100)
    context.set_source(lg1)
    context.fill()
print("File1 Saved")
with cairo.SVGSurface("SVG/geek95_2.svg", 700, 700) as surface:
    context = cairo.Context(surface)
    lg2 = cairo.LinearGradient(0.0, 0.0, 350.0, 0.0)
    count = 1
    i = 0.05
    while i < 0.95:
        if count % 2:
            lg2.add_color_stop_rgba(i, 0, 0, 0, 1)
        else:
            lg2.add_color_stop_rgba(i, 0, 0, 1, 1)
        i = i + 0.025
        count = count + 1
    context.rectangle(20, 20, 300, 100)
    context.set_source(lg2)
    context.fill()
print("File2 Saved")
with cairo.SVGSurface("SVG/geek95_3.svg", 700, 700) as surface:
    context = cairo.Context(surface)
    lg3 = cairo.LinearGradient(20.0, 260.0,  20.0, 360.0)
    lg3.add_color_stop_rgba(0.2, 0, 0, 0, 1)
    lg3.add_color_stop_rgba(0.5, 1, 1, 0, 1)
    lg3.add_color_stop_rgba(0.9, 0, 0, 0, 1)
    context.rectangle(20, 260, 300, 100)
    context.set_source(lg3)
    context.fill()
print("File3 Saved")
key = input("Wait")
