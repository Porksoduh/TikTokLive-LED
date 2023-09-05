# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

#General Imports
import time
import datetime
import board
import neopixel
import sys
import RPi.GPIO as GPIO
import random
import numpy as np

#adafruit imports
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.sparklepulse import SparklePulse

#TikTokLive Connector imports
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent, LiveEndEvent, LikeEvent
from TikTokLive.types.errors import LiveNotFound, FailedConnection


# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(unique_id="@laps3d", **(
        {# Whether to process initial data (cached chats, etc.)
                "process_initial_data": False,
        # Custom timeout for Webcast API requests
                #"ws_timeout": 12.0,
                #"http_timeout": 12.0
        }
    )
)

button = 4
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Set pin button to be an input pin and set initial value to be pulled down


#Setup Neos
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 275
num_front_pixels = 133

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

#neopixel settings
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

#pixels ranges to divide the matrix in 3 sections
botxy = range(0,92)
midzl = range(92, 100)
topz = range(100,125)
midzr = range(125,133)
midsr = range(133,149)
midsr1 = range(255,275)
tops = range(149,181)
tops1 = range(216,255) 
midsl = range(181,216)

#pixel ranges to divide the matrix in 2 sections
lowerled = range(0,92)
upperled = range(92,274)

ledHoldColor = (0,0,0)

#turn off LED while button is pressed for timelapse photo and set color after 2 seconds
def ledoff(channel):
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(2.0)
    cyclerave(datetime.timedelta(seconds=1))
    #rainbow_cycle(0.001, datetime.timedelta(seconds=1))

def ledhold(channel):
    global ledHoldColor
    pixels.fill(ledHoldColor)
    pixels.show()
    time.sleep(2.0)
    cyclerave(datetime.timedelta(seconds=1))



          
#detect y axis button press to turn off LED for timelapse
GPIO.add_event_detect(button, GPIO.FALLING, callback=ledhold, bouncetime=2000)


#random Color picker
def randColor():
    global ledHoldColor
    global colorTup
    #pick random numbers for rgb values
    x = list(range(0,255))  
    randX = random.choice(x)
    if randX < 125:
        x = list(range(125,255))
    else:
        x = list(range(0,125))
    randY = random.choice(x)
    randZ = 0
    colorTup = (randX,randY,randZ)
    colorList = list(colorTup)
    np.random.shuffle(colorList)
    # Converting back to tuple
    colorTup = tuple(colorList)



#apply a collor ot each section of the printer
def tricolor(bot, mid, top):
    global botxy, midsl, midsr, midzl, midzr, topz, tops, tops1, midsr1, ledHoldColor
    for b in botxy:
        pixels[b] = bot
    for msl in midsl:
        pixels[msl] = mid
    for msr in midsr:
        pixels[msr] = mid
    for mzl in midzl:
        pixels[mzl] = mid
    for mzr in midzr:
        pixels[mzr] = mid
    for msr1 in midsr1:
        pixels[msr1] = mid
    for tz in topz:
        pixels[tz] = top
    for ts in tops:
        pixels[ts] = top
    for ts1 in tops1:
        pixels[ts1] = top
    
    if GPIO.input(button) == GPIO.HIGH:    
        pixels.show()
    else:
        pixels.fill(ledHoldColor)
        pixels.show()


#apply a color to each section of the printer
def dualcolor(bot, top):
    global lowerled, upperled, ledHoldColor
    for l in lowerled:
        pixels[l] = bot
    for u in upperled:
        pixels[u] = top
    if GPIO.input(button) == GPIO.HIGH:    
        pixels.show()
    else:
        pixels.fill(ledHoldColor)
        pixels.show()


#rainbow color changes
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

#method to run rainbow cycle for X seconds
def rainbow_cycle(wait, duration):  
    global ledHoldColor 
    global colorTup
    randColor()
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        for j in range(255):        
                for i in range(num_pixels):
                    pixel_index = (i * 256 // num_pixels) + j
                    pixels[i] = wheel(pixel_index & 255)
                if GPIO.input(button) == GPIO.HIGH:    
                    pixels.show()
                else:
                    pixels.fill(ledHoldColor)
                    pixels.show()
                time.sleep(wait)
    else:
        pixels.fill(colorTup)
        pixels.show()


#define color cycle
colorcyclerave = ColorCycle(pixels, speed=0.2)


def cyclerave(duration):
    global ledHoldColor
    global colorTup
    randColor()
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        if GPIO.input(button) == GPIO.HIGH:
            colorcyclerave.animate()
        else:
            pixels.fill(ledHoldColor)
            pixels.show()
    else:
        pixels.fill(colorTup)
        pixels.show()



def randSparkle(duration):
    global ledHoldColor
    #pick random numbers for rgb values
    x = list(range(0,255))  
    randX = random.choice(x)
    if randX < 125:
        x = list(range(125,255))
    else:
        x = list(range(0,125))
    randY = random.choice(x)
    randZ = 0
    colorTup = (randX,randY,randZ)
    colorList = list(colorTup)
    np.random.shuffle(colorList)
    # Converting back to tuple
    colorTup = tuple(colorList)
    global lowerled, upperled
    for l in lowerled:
        pixels[l] = colorTup
    for u in upperled:
        pixels[u] = ((0,0,0))
    pixels.show()
    #define sparkle effect
    sparkle = Sparkle(pixels, speed=0.1, color=colorTup, num_sparkles=100)
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        if GPIO.input(button) == GPIO.HIGH:
            sparkle.animate()
        else:
            pixels.fill(ledHoldColor)
            pixels.show()
    else:
        pixels.fill(colorTup)
        pixels.show()



def strobe(duration, rgb):
    global ledHoldColor
    global colorTup
    randColor()
    blinkstrobe = Blink(pixels, speed=0.05, color=rgb)
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        if GPIO.input(button) == GPIO.HIGH:
            blinkstrobe.animate()
        else:
            pixels.fill(ledHoldColor)
            pixels.show()
    else:
        pixels.fill(colorTup)
        pixels.show()


#define rear color chase
right_rear_pixels = range(133, 164, 1)
def rearcomet(rcolor, fcolor, wait):
    global ledHoldColor
    for r in right_rear_pixels:
        l = 329 - r
        rr = r + 106
        lr = 365 - r
        pixels[r] = rcolor    
        pixels[l]= rcolor
        pixels[rr] = rcolor
        pixels[lr] = rcolor
        for i in range(132):
            pixels[i] = fcolor
        if GPIO.input(button) == GPIO.HIGH:    
            pixels.show()
        else:
            pixels.fill(ledHoldColor)
            pixels.show()
        time.sleep(wait)


#cycles the rear comet through a few colors
def cometcycle():
    global colorTup
    randColor()
    pixels.fill((0, 0, 0))
    pixels.show()
    rearcomet((0, 255, 255) , (143, 0, 255) , 0.02) #light blue
    pixels.fill((0, 0, 0))
    pixels.show()
    rearcomet((0, 255, 120) , (0, 255, 255) , 0.02) #teal-cyan
    pixels.fill((0, 0, 0))
    pixels.show()
    rearcomet((127, 255, 212) , (0, 255, 120) , 0.02) #aquamarine
    pixels.fill((0, 0, 0))
    pixels.show()
    rearcomet((0, 0, 255) , (127, 255, 212) , 0.02) #blue
    pixels.fill(colorTup)
    pixels.show()


#sets led to solid color
def setcolor(color):
    global ledHoldColor
    pixels.fill(color)
    if GPIO.input(button) == GPIO.HIGH:    
        pixels.show()
    else:
        pixels.fill(ledHoldColor)
        pixels.show()

def blackled(duration):
    global ledHoldColor
    global colorTup
    randColor()
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        if GPIO.input(button) == GPIO.HIGH:
            pixels.fill((0, 0, 0))
            pixels.show()
        else:
            pixels.fill(ledHoldColor)
            pixels.show()
    else:
        pixels.fill(colorTup)
        pixels.show()

def altDualColor(c1, c2, duration):
    global ledHoldColor, lowerled, upperled
    global colorTup
    randColor()
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:        
        for l in lowerled:
            pixels[l] = c1
        for u in upperled:
            pixels[u] = c2
        if GPIO.input(button) == GPIO.HIGH:    
            pixels.show()
        else:
            pixels.fill(ledHoldColor)
            pixels.show()
    else:
        stop = datetime.datetime.now() + duration
        while datetime.datetime.now() < stop:
            for l in lowerled:
                pixels[l] = c2
            for u in upperled:
                pixels[u] = c1
            if GPIO.input(button) == GPIO.HIGH:    
                pixels.show()
            else:
                pixels.fill(ledHoldColor)
                pixels.show()
        else:
            stop = datetime.datetime.now() + duration
            while datetime.datetime.now() < stop:
                for l in lowerled:
                    pixels[l] = c1
                for u in upperled:
                    pixels[u] = c2
                if GPIO.input(button) == GPIO.HIGH:    
                    pixels.show()
                else:
                    pixels.fill(ledHoldColor)
                    pixels.show()
            else:
                stop = datetime.datetime.now() + duration
                while datetime.datetime.now() < stop:
                    for l in lowerled:
                        pixels[l] = c2
                    for u in upperled:
                        pixels[u] = c1
                    if GPIO.input(button) == GPIO.HIGH:    
                        pixels.show()
                    else:
                        pixels.fill(ledHoldColor)
                        pixels.show()
                else:
                    pixels.fill(colorTup)
                    pixels.show()


#Connect Event
@client.on("connect")
async def on_connect(_: ConnectEvent):
    strobe(datetime.timedelta(seconds=1), (255,0,255))


likesthres = 5000
@client.on("like")
async def on_like(event: LikeEvent):
    global likesthres
    if event.total_likes > likesthres:
        rainbow_cycle(0.001, datetime.timedelta(seconds=10))
        likesthres += 5000
    #print("Someone liked the stream!")
    #print(event.totalLikeCount) 


#Comment Event
@client.on("comment")
async def on_comment(event: CommentEvent):
    if GPIO.input(button) == GPIO.HIGH:
        #cmtset = {event.comment}
        #change comment to string
        cmt = " ".join({event.comment})
        if "rainbow" in cmt.lower():
            rainbow_cycle(0.001, datetime.timedelta(seconds=5))
        elif "peep" in cmt.lower():
            rainbow_cycle(0.001, datetime.timedelta(seconds=7))    
        elif "green" in cmt.lower():
            setcolor((0, 255, 0))
        elif "black" in cmt.lower():
            blackled(datetime.timedelta(seconds=0.5))
        elif "blue" in cmt.lower():
            setcolor((0, 0, 255))
        elif "red" in cmt.lower():
            setcolor((255, 0, 0))
        elif "crimson" in cmt.lower():
            setcolor((175, 0, 42))
        elif "purple" in cmt.lower():
            setcolor((180, 0, 255))
        elif "violet" in cmt.lower():
            setcolor((143, 0, 255))
        elif "yellow" in cmt.lower():
            setcolor((255, 255, 0))
        elif "jade" in cmt.lower():
            setcolor((0, 255, 40))
        elif "orange" in cmt.lower():
            setcolor((255, 40, 0))
        elif "pink" in cmt.lower():
            setcolor((255, 0, 127))
        elif "light blue" in cmt.lower():
            setcolor((0, 255, 255))
        elif "teal" in cmt.lower():
            setcolor((0, 255, 120))
        elif "cyan" in cmt.lower():
            setcolor((0, 255, 120))
        elif "aquamarine" in cmt.lower():
            setcolor((127, 255, 212))
        elif "white" in cmt.lower():
            setcolor((255, 255, 255))
        elif "lime" in cmt.lower():
            setcolor((50,205,50))
        elif "beige" in cmt.lower():
            setcolor((200,173,127))
        #animations-multi 
        elif "christmas" in cmt.lower():
            altDualColor((255,0,0),(0,255,0),datetime.timedelta(seconds=0.5))
        elif "sparkle" in cmt.lower():
            randSparkle(datetime.timedelta(seconds=3))
        elif "rave" in cmt.lower():
            cyclerave(datetime.timedelta(seconds=5))
        elif "creeper" in cmt.lower():
            strobe(datetime.timedelta(seconds=3), (0,255,0))
        elif "grimace" in cmt.lower():
            strobe(datetime.timedelta(seconds=3), (180, 0, 255))
        elif "comet" in cmt.lower():
            cometcycle()
        elif "trans" in cmt.lower():
            tricolor((0, 255, 255), (255, 255, 255), (241,156,187))
        elif "pan" in cmt.lower():
            tricolor((0, 0, 255), (255, 255, 0), (229,43,80))
        elif "poland" in cmt.lower():
            dualcolor((255, 0, 0), (255, 255, 255))
        elif "germany" in cmt.lower():
            tricolor((255, 255, 0), (255, 0, 0), (0, 0, 0))    
        elif "portugal" in cmt.lower():
            dualcolor((0, 255, 0), (255, 0, 0))
        elif "spain" in cmt.lower():
            tricolor((255, 0, 0), (255, 255, 0), (255, 0, 0))
        elif "sweden" in cmt.lower():
            dualcolor((255, 255, 0), (0, 0, 255))
        elif "ukraine" in cmt.lower():
            dualcolor((0, 0, 255), (255, 255, 0))    
        elif "philippines" in cmt.lower():
            tricolor((255, 255, 255), (255, 0, 0), (0, 0, 255))
        elif "israel" in cmt.lower():
            tricolor((0, 0, 255), (255, 255, 255), (0, 0, 255))
        elif "palestine" in cmt.lower():
            tricolor((0, 0, 0), (255, 255, 255), (0, 255, 0))
        elif "netherlands" in cmt.lower():
            tricolor((0, 0, 255), (255, 255, 255), (255, 0, 0))
        elif "france" in cmt.lower():
            tricolor((0, 0, 255), (255, 255, 255), (255, 0, 0))
        elif "ireland" in cmt.lower():
            tricolor((0, 255, 0), (255, 255, 255), (255, 40, 0))  
        elif "italy" in cmt.lower():
            tricolor((0, 255, 0), (255, 255, 255), (255, 0, 0))
        elif "australia" in cmt.lower():
            tricolor((0, 0, 255), (255, 0, 0), (255, 255, 255))
        elif "germany" in cmt.lower():
            tricolor((0, 0, 0), (255, 255, 255), (255, 0, 0))
        elif "belgium" in cmt.lower():
            tricolor((0, 0, 0), (255, 255, 0), (255, 0, 0))
        elif "canada" in cmt.lower():
            tricolor((255, 0, 0), (255, 255, 255), (255, 0, 0))
        elif "denmark" in cmt.lower():
            tricolor((255, 0, 0), (255, 255, 255), (255, 0, 0))
        elif "mexico" in cmt.lower():
            tricolor((0, 255, 0), (255, 255, 255), (255, 0, 0))
        elif "india" in cmt.lower():
            tricolor((0, 255, 0), (255, 255, 255), (255, 40, 0)) 
        elif "uk" in cmt.lower():
            tricolor((0, 0, 255), (255, 0, 0), (255, 255, 255))
        elif "usa" in cmt.lower():
            tricolor((255, 0, 0), (255, 255, 255), (0, 0, 255))
        elif "puerto rico" in cmt.lower():
            tricolor((255, 0, 0), (0, 0, 255), (255, 255, 255))
        elif "brazil" in cmt.lower():
            tricolor((0, 0, 255), (255, 255, 0), (0, 255, 0))
    else:
        pixels.fill((0, 0, 0))
        pixels.show()


@client.on("gift")
async def on_gift(event: GiftEvent):
    # If it's type 1 and the streak is over
    if event.gift.gift_type == 1:
        if event.gift.repeat_end == 1:
            strobe(datetime.timedelta(seconds=3), (255,255,255))

    # It's not type 1, which means it can't have a streak & is automatically over
    elif event.gift.gift_type != 1:
        strobe(datetime.timedelta(seconds=5),(255,255,255))


@client.on("live_end")
async def on_connect(event: LiveEndEvent):
        client.stop()
        pixels.fill((0, 0, 0))
        pixels.show()
        sys.exit(0)


@client.on("error")
async def on_connect(error: Exception):
    # Handle the error
    # Otherwise, log the error
    client._log_error(error)



if __name__ == '__main__':
    try:
        #Run the client and block the main thread
        client.run()
        # await client.start() to run non-blocking
        
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
        client.stop()
        sys.exit(0)



	

