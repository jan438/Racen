import random

class rand():
    def __str__(self):
        return str(random.randint(0, 100))

class rgbset():
    def __str__(self):
        return str(random.randint(0, 255))

ran = rand()
rgb = rgbset()

svg1 = '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 1400 400">\n<rect width="1400" height="400"/>\n<defs>\n'
svg2 = '<linearGradient id="a" x1="'+str(ran)+'%" y1="'+str(ran)+'%" x2="'+str(ran)+'%" y2="'+str(ran)+'%">\n'
svg3 = '<stop offset="0%" style="stop-color:rgb('+str(rgb)+','+str(rgb)+','+str(rgb)+');stop-opacity:1" />\n'
svg4 = '<stop offset="100%" style="stop-color:rgb('+str(rgb)+','+str(rgb)+','+str(rgb)+');stop-opacity:1" />\n'
svg5 = '</linearGradient>\n</defs>\n<rect fill="url(#a)" width="1400" height="400"/>\n</svg>'

# write to file
file = open("SVG/grad.svg", "w")
file.writelines("%s%s%s%s%s" % (svg1,svg2,svg3,svg4,svg5))
file.close()

key = input("Wait")
