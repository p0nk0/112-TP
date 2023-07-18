from cmu_112_graphics import *
import perlin
import physics

# modified from perlin.getCellBounds (which was from 112 notes)
def findWaterBounds(app,value,col):

    rows = len(app.perlinArray)
    cols = len(app.perlinArray[0])

    x0 = app.width * col / cols
    x1 = app.width * (col+1) / cols

    # value is currently 0-2, we need it to be 0-rows

    y0 = app.height
    y1 = app.height * value / 2 + (app.height / 3)

    return (x0,y0,x1,y1)

def drawWater(app,canvas):
    for col in range(len(app.perlinArray[app.row])):
        value = app.perlinArray[app.row][col] + 1
        (x0, y0, x1, y1) = findWaterBounds(app,value,col)
        canvas.create_rectangle(x0, y0, x1, y1, width = 0,
        fill = perlin.getCellColorBlue(value))

def drawBackground(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "blue")

def drawUI(app,canvas):
    canvas.create_rectangle(0, 0, 300, 100, fill = "grey")
    canvas.create_text(150, 50, text = f"Score: {app.score}", font = "arial 20 bold")

def gameOverScreen(app,canvas):
    canvas.create_rectangle(0,0,app.width,app.height, fill = "Cyan")
    canvas.create_text(app.width/2,app.height/2, fill = "red",
                text = f"You Died! Total Score: {app.score}", font = "arial 30 bold")
    canvas.create_text(app.width/2,app.height/2 + 100, fill = "grey",
                text = f"Press R to restart", font = "arial 15 ")

def redrawAll(app,canvas):
    if app.gameOver:
        gameOverScreen(app,canvas)
        return
    drawBackground(app,canvas)
    app.player.drawPlayer(canvas,app.scroll,app.egg)
    drawWater(app,canvas)
    physics.drawObjects(app,canvas,app.scroll,app.toast)
    physics.drawVector(app,canvas)
    
    
    drawUI(app,canvas)

# code mostly from https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html
def sideScroll(app):

    x,y = app.player.getPosition()

    if (x < app.scroll + app.width/3):
        app.scroll = x - app.width/3
    if (x > app.scroll + app.width - app.width/3):
        app.scroll = x - app.width + app.width/3

def checkDeath(app):
    x,y = app.player.getPosition()
    if y >= app.height - app.blockSize:
        app.gameOver = True

def timerFired(app):
    if app.gameOver:
        return
    app.frame += 1
    app.player.updatePosition(app)
    sideScroll(app)
    generateNewObjects(app)
    if app.frame % 50 == 0:
        app.row = (app.row + 1) % (app.rows-1)
    app.score = app.player.getScore()
    checkDeath(app)

def mousePressed(app,event):
    physics.startVector(app,event,app.scroll)
    
def mouseDragged(app,event):
    physics.updateVector(app,event, app.scroll)

def mouseReleased(app,event):
    physics.stopVector(app,event, app.scroll)

def keyPressed(app,event):
    if event.key == "r":
        app.player.setPosition(app.startingPosition)
        app.player.setVelocity((0,0))
        app.scroll = 0
        app.farthestObject = 0
        app.objects = []
        generateNewObjects(app)
        app.gameOver = False

def getBlockHeight(app):
    row = app.currentBlockRow
    col = app.currentBlockCol
    return app.height * (app.perlinArray[row][col] + 1)/2 + app.blockSize

def generateNewObjects(app):
    if len(app.objects) == 0:
        # generate starting platform
        x = app.startingPosition[0]
        app.objects.append(physics.Object(x,app.height/2 + app.blockSize,app.blockSize))
    else:
        x,y = app.player.getPosition()
        if x > app.farthestObject - app.blockDistance:
            newX = app.farthestObject + app.blockDistance
            height = getBlockHeight(app)
            app.objects.append(physics.Object(newX,height,app.blockSize))
            app.farthestObject = newX
            app.currentBlockCol = app.currentBlockCol + 1 
            if app.currentBlockCol > app.rows - 1:
                app.currentBlockCol = 0
                app.currentBlockRows = (app.currentBlockRows + 1) % (app.rows - 1)
    
    if len(app.objects) >= 10:
        app.objects = app.objects[1:]


def appStarted(app):
    app.timerDelay = 1
    app.frame = 0
    app.scroll = 0
    app.score = 0
    app.gameOver = False

    app.startingPosition = 100, 200
    app.player = physics.Player(app.startingPosition,50)

    app.vector = None

    app.objects = []
    app.blockSize = 100
    app.farthestObject = 0
    app.blockDistance = 400
    app.currentBlock = 0
    app.currentBlockRow = 0
    app.currentBlockCol = 0
    generateNewObjects(app)

    app.perlinArray = perlin.generate2DPerlinArray(10,10,1/10)

    app.row = 0
    app.rows = len(app.perlinArray)
    app.cols = len(app.perlinArray[0])

    app.egg = app.loadImage('egg.png')
    app.egg = app.scaleImage(app.egg,1/20)

    app.toast = app.loadImage('toast.png')
    app.toast = app.scaleImage(app.toast,1/10)

def main():
    runApp(width = 1000, height = 600)

if __name__ == "__main__":
    main()