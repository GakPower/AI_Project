import pygame
import random
import Platform
import Player
import time as tm
import neat
import os

global screen, score, font, green, blue, red, red_1, spring, spring_1, gravity, camera, platforms, generation, Time, startY

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('AI Project Game')
pygame.font.init()
score = 0
font = pygame.font.SysFont("calibri", 25)                           
green = pygame.transform.scale(pygame.image.load("assets/green.png"), (80,25)).convert_alpha()              # Green Platform
blue = pygame.transform.scale(pygame.image.load("assets/blue.png"), (80,25)).convert_alpha()                # Blue Moving Platform
red = pygame.transform.scale(pygame.image.load("assets/red.png"), (80,25)).convert_alpha()                  # Red Fragile Platform
red_1 = pygame.transform.scale(pygame.image.load("assets/redBroken.png"), (80,40)).convert_alpha()          # Red Broken Platform
spring = pygame.transform.scale(pygame.image.load("assets/spring.png"), (25,25)).convert_alpha()            # Spring
spring_1 = pygame.transform.scale(pygame.image.load("assets/spring_1.png"), (25,25)).convert_alpha()        # Spring activated
gravity = 0
camera = 0
platforms = []
generation = 1
Time = tm.time()
startY = -100
highestScore = 0
cameraTime = Time
lastCameraValue = camera

def playerUpdate(player):
    global camera, cameraTime
    if (player.y - camera <=200):
        camera -= 8
        cameraTime = tm.time()

def drawPlayer(player):
    if (player.direction == 0):
        if (player.jump > 0):
            screen.blit(player.playerRight_1, (player.x, player.y - camera))
        else:
            screen.blit(player.playerRight, (player.x, player.y - camera))
    
    else:
        if (player.jump):
            screen.blit(player.playerLeft_1, (player.x, player.y - camera))
        else:
            screen.blit(player.playerLeft, (player.x, player.y - camera))

def updateplatforms(player):
    for p in platforms:
        rect = pygame.Rect(p.x + 10, p.y, p.green.get_width() - 25, p.green.get_height() - 20)
        playerCollider = pygame.Rect(player.x, player.y, player.playerRight.get_width() - 10, player.playerRight.get_height())
        
        
        if (rect.colliderect(playerCollider) and player.gravity > 0 and player.y < (p.y - camera)):
            if (p.kind != 2):
                player.jump = 20
                player.gravity = 0
            else:
                p.broken = True

def drawplatforms():
    global score
    for p in platforms:
        y = p.y - camera
        if (y > WINDOW_HEIGHT):
            generateplatforms(False)
            platforms.pop(0)
            score += 10
            Time = tm.time()
        if (p.kind == 1):
            p.blueMovement(score)    

        if (p.kind == 0):
            screen.blit(p.green, (p.x, p.y - camera))
        elif (p.kind == 1):
            screen.blit(p.blue, (p.x, p.y - camera))
        elif (p.kind == 2):
            if (p.broken == False):
                screen.blit(p.red, (p.x, p.y - camera))
            else:
                screen.blit(p.red_1, (p.x, p.y - camera))

def generateplatforms(initial):
    y = 900
    start = -100

    global startY, score
    
    if (initial == True):
        startY = -100

        while (y > -70):
            p = Platform.Platform()
            p.getKind(score)
            p.y = y
            p.startY = start
            platforms.append(p)
            y -= 30
            start += 30
            startY = start       
    else:
        p = Platform.Platform()
        
        if (score <= 2500):
            difficulty = 50
        elif (score < 4000):
            difficulty = 60
        else: 
            difficulty = 70

        p.y = platforms[-1].y - difficulty
        startY += difficulty
        p.startY = startY
        p.getKind(score)
        platforms.append(p)

def update():
    drawplatforms()
    screen.blit(font.render("Score: " +str(score), -1, (0, 0, 0)), (25, 710))
    screen.blit(font.render("Generation: " +str(generation), -1, (0, 0, 0)), (25, 650))


def eval_genomes(genomes, config):
    clock = pygame.time.Clock()
    savedDoodler = []

    nets = []
    doodlers = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        doodlers.append(Player.Player())
        ge.append(genome)

    global Time, score, camera, generation, highestScore, cameraTime
            
    run = True
    generateplatforms(True)
    while run and len(doodlers) > 0:
        screen.fill((255,255,255))
        clock.tick(120)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break
        currentTime = tm.time()

        if (currentTime - cameraTime > 15):
            for d in doodlers:
                index = doodlers.index(d)
                ge[index].fitness = (score - 200)**2
                nets.pop(index)
                ge.pop(index)
                doodlers.pop(index)
            doodlers.clear()
        update()

        for d in doodlers:
            index = doodlers.index(d)
            ge[index].fitness = score**2

            d.move(d.think(nets[index], platforms))
            drawPlayer(d)
            playerUpdate(d)

            updateplatforms(d)

            if(d.y - camera > 800): 
                nets.pop(index)
                ge.pop(index)
                doodlers.pop(index)

        if(score > highestScore):
            highestScore = score
            
        screen.blit(font.render("Alive: " +str(len(doodlers)), -1, (0, 0, 0)), (25, 680))
        screen.blit(font.render("High Score: " +str(highestScore), -1, (0, 0, 0)), (25, 740))
        pygame.display.update()
    print("GEN: " + str(generation) + " FITNESS: " + str(score))
    camera = 0
    Time = tm.time()
    score = 0
    doodlers.clear()
    platforms.clear()
    generateplatforms(True)
    generation += 1
    cameraTime = Time


def runAI(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)

    p = neat.Population(config)

    # p.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # p.add_reporter(stats)
    winner = p.run(eval_genomes, 50)

    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.txt')
    runAI(config_path)