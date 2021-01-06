import math
import pygame

class Player():
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.playerRight = pygame.transform.scale(pygame.image.load("assets/right.png"), (80,80)).convert_alpha()
        self.playerRight_1 = pygame.transform.scale(pygame.image.load("assets/rightSit.png"), (80,80)).convert_alpha()
        self.playerLeft = pygame.transform.scale(pygame.image.load("assets/left.png"), (80,80)).convert_alpha()
        self.playerLeft_1 = pygame.transform.scale(pygame.image.load("assets/leftSit.png"), (80,80)).convert_alpha()
        self.x = 300
        self.y = 550
        self.startY = 300
        self.direction = 0
        self.xvel = 0
        self.jump = 0
        self.gravity = 0
        self.ai = True

    
    def move(self, decision):
        if self.jump == 0:        
            self.gravity += 0.5
            self.y += self.gravity
            self.startY -= self.gravity

        elif self.jump > 0:
            self.jump -= 1
            self.y -= self.jump
            
            self.startY += self.jump

        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            if (self.ai):
                self.ai = False

        if (self.ai):
            if (decision == 0):
                if self.xvel < 10:
                    self.xvel += 1
                    self.direction = 0

            elif (decision == 1):
                if self.xvel > -10:
                    self.xvel -= 1
                self.direction = 1
            elif (decision == 2):
                if self.xvel > 0:
                    self.xvel -= 1
                elif self.xvel < 0:
                    self.xvel += 1
        else:
            if key[pygame.K_RIGHT]:
                if self.xvel < 10:
                    self.xvel += 1
                    self.direction = 0

            elif key[pygame.K_LEFT]:
                if self.xvel > -10:
                    self.xvel -= 1
                self.direction = 1
            else:
                if self.xvel > 0:
                    self.xvel -= 1
                elif self.xvel < 0:
                    self.xvel += 1
        
        self.x += self.xvel

        if self.x > 650:
            self.x = -50
        elif self.x < -50:
            self.x = 650

    def think(self, net, platforms):
        coordinatesUp = self.getPlatformAbove(platforms)
        coordinatesDown = self.getClosestBelow(platforms)
        inputs = []
        vision = self.look(platforms)
        

        inputs.append(vision[0])
        inputs.append(vision[1])
        inputs.append(vision[2])
        inputs.append(vision[3])

        inputs.append(coordinatesUp - self.x/600-self.x)
        inputs.append(coordinatesDown - self.x/600 -self.x)
        
        output = net.activate((inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5]))

        index = output.index(max(output))
        return index

    def getPlatformAbove(self,platforms):
        for p in platforms:
            if (self.startY < p.startY):
                if (p.kind != 2):
                    return p.x

    def getPlatformBelow(self,platforms):
        maxX = 0
        for p in platforms:
            if (self.startY > p.startY):
                if (p.kind != 2):
                    maxX = p.x
        return maxX
    
    def getClosetsAbove(self, platforms):
        closest = 9999
        platform = platforms[0]
        for p in platforms:
            if (p.kind != 2 and p.startY > self.startY):
                dist = math.sqrt((self.startY-p.startY)**2 + (self.x-p.x)**2)
                if (dist < closest):
                    closest = dist
                    platform = p
        return platform.x

    def getClosestBelow(self, platforms):
        closest = 9999
        platform = platforms[0]
        for p in platforms:
            if (p.kind != 2 and p.startY < self.startY):
                dist = math.sqrt((self.startY-p.startY)**2 + (self.x-p.x)**2)
                if (dist < closest):
                    closest = dist
                    platform = p
        return platform.x

    def look(self, platforms):
        vision = [0, 0, 0, 0]

        for p in platforms:
            rect = pygame.Rect(p.x , p.y, p.green.get_width(), p.green.get_height())
            
            up = pygame.Rect(self.x+ 50, self.y, 1, 800)
            down = pygame.Rect(self.x + 50, self.y-800, 1, 800)
            left = pygame.Rect(self.x-600, self.y +50, 600, 1)
            right = pygame.Rect(self.x, self.y +50, 600, 1)

            if (rect.colliderect(up) and p.kind != 2):
                vision[0] = 1

            if (rect.colliderect(down) and p.kind != 2):
                vision[1] = 1

            if (rect.colliderect(left) and p.kind != 2):
                vision[2] = 1

            if (rect.colliderect(right) and p.kind != 2):
                vision[3] = 1

        return vision