import os
import sys
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

def add_image(image_path):
    my_canvas = canvas.Canvas('PDF/svg_on_canvas.pdf')
    drawing = svg2rlg(image_path)
    renderPDF.draw(drawing, my_canvas, 0, 40)
    my_canvas.drawString(50, 30, 'My SVG Image')
    my_canvas.save()

if __name__ == '__main__':
    if sys.platform[0] == 'l':
        path = '/home/jan/git/Racen'
    if sys.platform[0] == 'w':
        path = "C:/Users/janbo/OneDrive/Documents/GitHub/Racen"
    os.chdir(path)
    image_path = 'SVG/F1.svg'
    add_image(image_path)
    key = input("Wait")
