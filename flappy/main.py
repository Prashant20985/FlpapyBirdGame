import random
import sys
import pygame
from pygame.locals import *

# Global variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUND_Y = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = "gallery/sprites/bird.png"
BACKGROUND = "gallery/sprites/background.png"
PIPE = "gallery/sprites/pipe.png"


# shows welcome img on screen
def welcomeScreen():
    playerX = int(SCREENWIDTH / 5)
    playerY = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    messageX = int((SCREENWIDTH - GAME_SPRITES['message'].get_height()) / 7)
    messagey = int((SCREENHEIGHT * 0.13))
    baseX = 0

    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # if user clicks space or up key, start game
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerX, playerY))
                SCREEN.blit(GAME_SPRITES['base'], (baseX, GROUND_Y))
                SCREEN.blit(GAME_SPRITES['message'], (messageX, messagey))

                pygame.display.update()
                FPSCLOCK.tick(FPS)


def mainGame():
    score = 0
    playerX = int(SCREENWIDTH / 5)
    playerY = int(SCREENHEIGHT / 2)
    baseX = 0

    # Create 2 pipes for blitting on screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENHEIGHT + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    # list of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENHEIGHT + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccV = -8  # velocity while flying
    playerFlapped = False  # it is true only when bird is flying

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playerY > 0:
                    playerVelY = playerFlapAccV
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerX, playerY, upperPipes, lowerPipes)
        # Player is Crashed
        if crashTest:
            return

        # Check for Scores
        playerMidPos = playerX + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your Score Is {score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playerY = playerY + min(playerVelY, GROUND_Y - playerY - playerHeight)

        # move pipes to left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # add a new pipe when the first pipe about to go to the cross the screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of screen remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # blit our sprites
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (baseX, GROUND_Y))
        SCREEN.blit(GAME_SPRITES['player'], (playerX, playerY))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerX, playerY, upperPipes, lowerPipes):
    if playerY > GROUND_Y - 25 or playerY < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if playerY < pipeHeight + pipe['y'] and abs(playerX - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playerY + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerX - pipe['x']) < \
                GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False


# generate position of pipes
def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENHEIGHT + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},
        {'x': pipeX, 'y': y2}
    ]
    return pipe


if __name__ == '__main__':
    pygame.init()  # initialize pygame modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')

    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha()
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()

    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()

    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha(),
    )

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()

    # game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    while True:
        welcomeScreen()
        mainGame()
