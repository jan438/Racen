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
print("File Saved")
key = input("Wait")
