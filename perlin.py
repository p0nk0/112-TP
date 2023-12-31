# here lies Perlin

# resources used: 
#   https://adrianb.io/2014/08/09/perlinnoise.html
#   https://gpfault.net/posts/perlin-noise.txt.html
#   https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf

#   All code, unless stated otherwise, was written myself without looking at pseudocode

# used when generating gradients
import random
import math
from cmu_112_graphics import *

# DISCLAIMER: for this entire program, (0,0) is defined as the top left of the screen

# generates a grid of pseudorandom gradient (unit) vectors
def generateGrid(rows,cols):

    # generates empty grid of gradients (unit vectors)
    gradients = [[(0,0)]*cols for _ in range(rows)]

    # generages list of 8 random normalized unit vectors
    # idea modified from the 3D version in Ken Perlin's "Improving Noise" paper
    sqrt2 = math.sqrt(2)
    unitVectorList = [(0,1),(0,-1),(1,0),(-1,0), 
            (sqrt2/2,sqrt2/2), (sqrt2/2, -sqrt2/2), 
            (-sqrt2/2, sqrt2/2), (-sqrt2/2,-sqrt2/2)]
    
    # populates array with gradient vectors (random unit vectors)
    # TODO: make these pseudorandom, generated by a seed
    for row in range(rows):
        for col in range(cols):
            gradients[row][col] = random.choice(unitVectorList)
    
    return gradients

def findLatticePoints(x,y):
    # finds closet lattice points to an (x,y) pair
    # assumes x and y are floats
    x0,y0 = int(x), int(y) 
    x1,y1 = x0 + 1, y0 + 1

    # finds the (x,y) coordinates inside of the lattice point grid
    # ex: x = 2.5 -> x0 = 2, xc = 0.5
    xc, yc = round(x%1, 2), round(y%1, 2)

    return x0,y0,x1,y1,xc,yc

def findGradient(x,y,gradients):
    # finds the gradient vector at an (x,y) lattice point
    # assumes x and y are integers
    if x < 0 or x >= len(gradients) or y < 0 or y >= len(gradients):
        print("ERROR: gradient out of bounds")
        print(f"x,y = {x,y}")
        return None
    else: return gradients[y][x]
    


def findDistanceVectors(xc,yc):
    # given (xc,yc) coordinates (values from [0,1] in the center of a cell)
    # returns the distance vectors {d1 - d4} from the 4 corners to that point:
    
    #   d1         d2
    #
    #     (xc,yc)
    #
    #   d3         d3

    dx = round(1 - xc,2)
    dy = round(1 - yc,2)

    d1 = (xc,yc)
    d2 = (dx,yc)
    d3 = (xc,dy)
    d4 = (dx,dy)
    
    return d1,d2,d3,d4

def dot(vec1, vec2):
    # finds dot product of 2 2d vectors (each in (x, y) format)
    xv1, yv1 = vec1[0],vec1[1]
    xv2, yv2 = vec2[0],vec2[1]

    # rounding because floating points
    return round(xv1*xv2 + yv1*yv2,4)

def fade(x):
    # the fade function as defined by Ken Perlin in his "Improving Perlin Noise" paper
    return 6*(x**5) - 15*(x**4) + 10*(x**3)

# given (x,y) coordinates (floats), generates a value from [0.0 - 1.0]
def perlin(x,y,gradients, debug = False):
    # make debug true to enable console output

    if debug: print(f"input coordinates: {x,y}")

    # finds closest lattice points:
    #  (x0,y0)     (x1,y0)
    #
    #       (xc,yc)
    #
    #  (x0,y1)     (x1,y1)

    x0,y0,x1,y1,xc,yc = findLatticePoints(x,y)
    if debug: print(f"coordinates: {x0,y0},{x1,y1},{xc,yc}")

    # finds gradients corresponding to those lattice points
    g1 = findGradient(x0,y0,gradients)
    g2 = findGradient(x1,y0,gradients)
    g3 = findGradient(x0,y1,gradients)
    g4 = findGradient(x1,y1,gradients)
    if debug: print(f"gradient vecs: {g1,g2,g3,g4}")

    # finds the distance vectors from the 4 corners of the cell to (xc,yc)
    d1,d2,d3,d4 = findDistanceVectors(xc,yc)
    if debug: print(f"distance vecs:{d1,d2,d3,d4}")

    # calculates the dot products of the corresponding (gi,di) pairs
    v1 = dot(g1,d1)
    v2 = dot(g2,d2)
    v3 = dot(g3,d3)
    v4 = dot(g4,d4)
    if debug: print(f"dot products:{v1,v2,v3,v4}")

    # bilinear interpolation algorithm from wikipedia: (code is my own, though)
    #   https://en.wikipedia.org/wiki/Bilinear_interpolation#On_the_unit_square

    # (effectively identical to the one from this handout)
    #   https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
    
    # f(x,y) = f(0,0)(1-x)(1-y) + f(1,0)(x)(1-y) + f(0,1)....

    xcf = fade(xc)
    ycf = fade(yc)

    # bilerp = v1*(1-xc)*(1-yc) + v2*(xc)*(1-yc) + v3*(1-xc)*(yc) + v4*(xc)*(yc)
    bilerp = v1*(1-xcf)*(1-ycf) + v2*(xcf)*(1-ycf) + v3*(1-xcf)*(ycf) + v4*(xcf)*(ycf)
    
    if debug:
        # print(f"bilerp = {v1*(1-xcf)*(1-ycf)} + {v2*(xcf)*(1-ycf)} + {v3*(1-xcf)*(ycf)} + {v4*(xcf)*(ycf)}")
        # print(f"bilerp = {v1*(1-xc)*(1-yc)} + {v2*(xc)*(1-yc)} + {v3*(1-xc)*(yc)} + {v4*(xc)*(yc)}")
        print(f"bilerp = {bilerp}")



    return round(bilerp,4)

def generatePerlinArray(xmax,ymax,stepsize,gradients):
    # generates a 2D array filled with perlin noise
    
    xcount = int(xmax/stepsize)
    ycount = int(ymax/stepsize)
    results = [[0]*xcount for _ in range(ycount)]

    row,col = 0,0
    # this horrendous list comprehension is because python can't do a float stepsize in range
    for x in [round(x*stepsize + stepsize,5) for x in range(xcount)]:
        col = 0
        
        for y in [round(y*stepsize + stepsize,5) for y in range(ycount)]:

            value = perlin(x,y,gradients)
            results[row][col] = value

            col += 1
        row += 1
    
    return results


def getCellColorGrayscale(row,col,array):

    # retrieves the color value of a perlin array cell (-1 = black,  1 = white)
    # adds 1 to shift it the range to [0,2]
    value = array[row][col] + 1

    # multiply value by 255 to get a decimal value
    # the ":02x" foces this value to be a hex (requires int)
    # then, since it's a string, multiply it by 3 to make it fill all R, G, and B values

    return "#" + f"{int(value*127.5):02X}"*3

def getCellColorBlue(value):
    # see getCellColorGrayscale for explanation
    return "#00" + f"{int(value*127.5):02X}"*2



# getCellBounds and drawBoard modified from
# https://www.cs.cmu.edu/~112/notes/notes-animations-part3.html

def getCellBounds(app, row, col):

    rows = len(app.perlinArray)
    cols = len(app.perlinArray[0])

    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    x0 = app.margin + gridWidth * col / cols
    x1 = app.margin + gridWidth * (col+1) / cols
    y0 = app.margin + gridHeight * row / rows
    y1 = app.margin + gridHeight * (row+1) / rows
    return (x0, y0, x1, y1)



def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            (x0, y0, x1, y1) = getCellBounds(app, row, col)
            canvas.create_rectangle(x0, y0, x1, y1, width = 0,
            fill = getCellColorGrayscale(row,col,app.perlinArray))

def generate2DPerlinArray(rows,cols,stepSize):
    rows = 10
    cols = 10
    stepSize = 1/10

    gradients = generateGrid(rows+1,cols+1)
    return generatePerlinArray(rows-1,cols-1, stepSize, gradients)

def redrawAll(app,canvas): 
    drawBoard(app,canvas)

def appStarted(app):

    app.perlinArray = generate2DPerlinArray(10,10, 1/10)

    app.margin = 5
    app.rows = len(app.perlinArray)
    app.cols = len(app.perlinArray[0])


def main():
    runApp(width = 600, height = 600)

if __name__ == "__main__":
    main()