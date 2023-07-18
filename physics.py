from cmu_112_graphics import *
import math

# Player and Object classes and physics calculations

# class for player
class Player:
    def __init__(self,pos,size):
        self.x, self.y = pos[0], pos[1] # coords of the bottom left corner of the box
        self.vx, self.vy = 0,0
        self.ax, self.ay = 0,0

        self.terminalVelocity = 20
        self.gravity = 1/10

        # fractions representing what percent of velocity is remaining after collisions
        self.collisionElasticity = 1/5
        self.friction = 1/10

        self.size = size
    
    def drawPlayer(self, canvas, scroll = 0, image = None):
        if image:
            canvas.create_image(self.x + self.size/2 - scroll, self.y - self.size/2, image=ImageTk.PhotoImage(image))
        else: canvas.create_rectangle(self.x, self.y, 
                self.x + self.size, self.y - self.size, fill = "cyan")

    def getPosition(self):
        return self.x, self.y
    
    def getSize(self):
        return self.size

    def getVelocity(self):
        return self.vx, self.vys

    def setPosition(self,pos):
        self.x, self.y = pos[0], pos[1]
    
    def setVelocity(self,pos):
        self.vx, self.vy = pos[0], pos[1]
    
    def getScore(self):
        if self.x < 0: 
            return 0
        else:
            return int(self.x * math.log(self.x)) - 460
    
    def updatePosition(self,app):
        # runs every game tick - updates player position, velocity, etc.

        self.ay = self.gravity

        self.vx += self.ax
        self.vy += self.ay

        if self.vy > self.terminalVelocity or self.vy < -self.terminalVelocity:
            self.ay = 0

        self.x += self.vx
        self.y += self.vy

        self.objectCollisionUpdate(app)
        
    def objectCollisionUpdate(self,app):
        # checks for collisions with game objects and updates player data

        # I wrote most of this code myself, but used this guide to fix some bugs and logical errors
        # https://2dengine.com/?p=collisions

        selfLeftWall = self.x
        selfRightWall = self.x + self.size

        selfBottomWall = self.y 
        selfTopWall = self.y - self.size

        cx,cy = self.x + self.size/2, self.y - self.size/2

        for object in app.objects:
            x,y = object.getPosition()
            size = object.getSize()

            objectLeftWall = x
            objectRightWall = x + size

            objectBottomWall = y
            objectTopWall = y - size

            objcx,objcy = x + size/2, y - size/2
            
            if (selfRightWall >= objectLeftWall and selfLeftWall <= objectRightWall
                 and selfTopWall <= objectBottomWall and selfBottomWall >= objectTopWall):

                # distance vector
                distancex = cx - objcx
                distancey = cy - objcy

                # seperation vector
                if abs(distancex) > abs(distancey):
                    seperationx, seperationy = self.size/2 + size/2 - abs(distancex), 0
                else:
                    seperationx, seperationy = 0, self.size/2 + size/2 - abs(distancey)

                if distancex < 0:
                    seperationx *= -1
                if distancey < 0:
                    seperationy *= -1
                
                # normal vector
                dist = math.sqrt(seperationx**2 + seperationy**2) + 0.001 #don't divide by 0
                normalx = seperationx/dist
                normaly = seperationy/dist

                # speed parallel and tangent to the collision
                collisionspeed = self.vx*normalx + self.vy*normaly

                collisionx = normalx*collisionspeed
                collisiony = normaly*collisionspeed

                tangentx = self.vx - collisionx
                tangenty = self.vy - collisiony

                # move the player
                self.x += seperationx
                self.y += seperationy

                self.vx = self.vx - collisionx*(1+self.collisionElasticity) - tangentx*self.friction
                self.vy = self.vy - collisiony*(1+self.collisionElasticity) - tangenty*self.friction
                
    def collisionUpdate(self,app):
        # checks for collisions with borders and updates player data (OLD, NO LONGER USED)

        leftWall = self.x
        rightWall = self.x + self.size

        bottomWall = self.y 
        topWall = self.y - self.size 

        if leftWall <= app.margin:
            self.x = app.margin
            self.vx = -(self.vx * self.collisionElasticity) 
            self.vy = (self.vy * self.friction/3)
        elif rightWall >= app.width - app.margin:
            self.x = app.width - app.margin - self.size
            self.vx = -(self.vx * self.collisionElasticity) 
            self.vy = (self.vy * self.friction/3)

        if topWall <= app.margin:
            self.y = app.margin + self.size
            self.vy = -(self.vy * self.collisionElasticity) 
            self.vx = (self.vx * self.friction/3)
        elif bottomWall >= app.height - app.margin:
            self.y = app.height - app.margin
            self.vy = -(self.vy * self.collisionElasticity) 
            self.vx = (self.vx * self.friction/3)

    def updateVelocity(self, app):
        # updates velocity after user launches the player 
        x1,y1,x2,y2 = app.vector
        self.vx += (x1-x2) / 50
        self.vy += (y1-y2) / 30
        app.vector = None

class Object:
    def __init__(self,x,y,size):
        self.x,self.y = x,y #bottom left corner
        self.size = size
    
    def getPosition(self):
        return self.x, self.y
    
    def getSize(self):
        return self.size

    def setPosition(self,pos):
        self.x,self.y = pos[0], pos[1]

def timerFired(app): 
    app.player.updatePosition(app)

def appStarted(app):
    app.startingPosition = 50,300
    app.player = Player(app.startingPosition,50)
    app.margin = 10
    app.timerDelay = 10
    app.blockSize = 50 # defualt platform size
    app.vector = None # contains [x1,y1,x2,y2] values of the player-drawn launch vector
    app.objects = [] # list of objects the player can interact with
    createTestPlatforms(app)

# two example levels for debugging
def createWalls(app):
    width = app.width // app.blockSize
    height = app.height // app.blockSize
    for n in range(width):
        app.objects.append(Object(app.blockSize*n,app.height,app.blockSize))
    for n in range(height):
        app.objects.append(Object(app.width - app.blockSize,app.height - app.blockSize*n,app.blockSize))

def createTestPlatforms(app):
    app.objects.append(Object(50,app.height,app.blockSize))
    app.objects.append(Object(150,300,app.blockSize))
    app.objects.append(Object(400,350,app.blockSize))

# functions for clicking and dragging on the block 
#   (seperate functions for the sake of running in other files)

def checkBounds(eventX,eventY,x1,y2,size):
    # checks if eventX, eventY is in the player
    x2 = x1 + size
    y1 = y2 - size
    return x1 < eventX and eventX < x2 and y1 < eventY and eventY < y2

def startVector(app,event,scroll = 0):
    app.isDrawing = True
    x,y = app.player.getPosition()
    x -= scroll
    size = app.player.getSize()

    if (app.vector is None or len(app.vector) == 4):
        if checkBounds(event.x,event.y,x,y,size):
            app.vector = [0,0]
            app.vector[0] = event.x
            app.vector[1] = event.y
        else:
            app.vector = None

def updateVector(app,event, scroll = 0):
    if app.vector is None:
        return
    elif len(app.vector) == 2:
        app.vector.extend([0,0])
    app.vector[2] = event.x
    app.vector[3] = event.y

def stopVector(app,event, scroll = 0):
    app.isDrawing = False
    if app.vector is None:
        return
    elif len(app.vector) == 2:
        app.vector.extend([0,0])
    app.vector[2] = event.x
    app.vector[3] = event.y

    app.player.updateVelocity(app)

def mousePressed(app,event):
    startVector(app,event)
    
def mouseDragged(app,event):
    updateVector(app,event)

def mouseReleased(app,event):
    stopVector(app,event)

def keyPressed(app,event):
    # reset button for testing
    if event.key == "r":
        app.player.setPosition(app.startingPosition)
        app.player.setVelocity((0,0))


# drawing functions
def drawVector(app,canvas):
    # draws green launch vector
    if app.vector is not None and len(app.vector) == 4:
        x1,y1,x2,y2 = app.vector
        canvas.create_line(x1,y1,x2,y2,fill = "green", width = 5)

def drawObjects(app,canvas,scroll = 0, image = None):
    # draws all platforms
    for object in app.objects:
        x,y = object.getPosition()
        x -= scroll
        size = object.getSize()
        if image:
            canvas.create_image(x + size/2, y - size/2, image=ImageTk.PhotoImage(image))
        else:
            canvas.create_rectangle(x, y, x + size, y - size)

def redrawAll(app, canvas):
    drawObjects(app,canvas)
    app.player.drawPlayer(canvas)
    drawVector(app,canvas)
    
def main():
    runApp(width = 600, height = 400)


if __name__ == "__main__":
    main()