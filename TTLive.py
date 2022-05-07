# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

#General Imports
import time
import datetime
import board
import neopixel
import sys

#adafruit imports
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.blink import Blink

#TikTokLive Connector imports
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, GiftEvent

# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(
    unique_id="@laps3d", **(
        {
            # Whether to process initial data (cached chats, etc.)
                "process_initial_data": False,
            # How frequently to poll Webcast API
                "polling_interval_ms": 500,
        }
    )
)
#
#Setup Neos
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 197
num_front_pixels = 133

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER)

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
  stop = datetime.datetime.now() + duration
  while datetime.datetime.now() < stop:
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)
  else:
        pixels.fill((180, 0, 255))
        pixels.show()

#define color cycle
colorcyclerave = ColorCycle(pixels, speed=0.2)
blinkstrobe = Blink(pixels, speed=0.05, color=(255, 255, 255))

def cyclerave(duration):
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        colorcyclerave.animate()
    else:
        pixels.fill((255, 0, 0))
        pixels.show()

def strobe(duration):
    stop = datetime.datetime.now() + duration
    while datetime.datetime.now() < stop:
        blinkstrobe.animate()
    else:
        pixels.fill((0, 255, 0))
        pixels.show()


#define rear color chase
right_rear_pixels = range(133, 164, 1)
def rearcomet(rcolor, fcolor, wait):
    for r in right_rear_pixels:
        l = 329 - r
        pixels[r] = rcolor    
        pixels[l]= rcolor
        for i in range(132):
            pixels[i] = fcolor
        pixels.show()
        time.sleep(wait)



#Connect Event
@client.on("connect")
async def on_connect(_: ConnectEvent):
    strobe(datetime.timedelta(seconds=3))


#Comment Event
@client.on("comment")
async def on_comment(event: CommentEvent):
    cmtset = {event.comment}
    cmt = " ".join(cmtset)
    if "rainbow" in cmt.lower():
        rainbow_cycle(0.001, datetime.timedelta(seconds=4))
    elif "green" in cmt.lower():
        pixels.fill((0, 255, 0))
        pixels.show()
    elif "blue" in cmt.lower():
        pixels.fill((0, 0, 255))
        pixels.show()
    elif "red" in cmt.lower():
        pixels.fill((255, 0, 0))
        pixels.show()
    elif "crimson" in cmt.lower():
        pixels.fill((175, 0, 42))
        pixels.show()
    elif "purple" in cmt.lower():
        pixels.fill((180, 0, 255))
        pixels.show()
    elif "violet" in cmt.lower():
        pixels.fill((143, 0, 255))
        pixels.show()
    elif "yellow" in cmt.lower():
        pixels.fill((255, 255, 0))
        pixels.show()
    elif "jade" in cmt.lower():
        pixels.fill((0, 255, 40))
        pixels.show()
    elif "orange" in cmt.lower():
        pixels.fill((255, 40, 0))
        pixels.show()
    elif "pink" in cmt.lower():
        pixels.fill((255, 0, 127))
        pixels.show()
    elif "light blue" in cmt.lower():
        pixels.fill((0, 255, 255))
        pixels.show()
    elif "teal" in cmt.lower():
        pixels.fill((0, 255, 120))
        pixels.show()
    elif "cyan" in cmt.lower():
        pixels.fill((0, 255, 120))
        pixels.show()
    elif "aquamarine" in cmt.lower():
        pixels.fill((127, 255, 212))
        pixels.show()
    elif "white" in cmt.lower():
        pixels.fill((255, 255, 255))
        pixels.show()
    elif "rave" in cmt.lower():
        cyclerave(datetime.timedelta(seconds=5))
    elif "comet" in cmt.lower():
        rearcomet((0, 255, 255) , (143, 0, 255) , 0.01)
        pixels.fill((0, 0, 0))
        pixels.show()
        rearcomet((0, 255, 120) , (143, 0, 255) , 0.01)
        pixels.fill((0, 0, 0))
        pixels.show()
        rearcomet((127, 255, 212) , (143, 0, 255) , 0.001)
        pixels.fill((0, 0, 0))
        pixels.show()



@client.on("gift")
async def on_gift(event: GiftEvent):
    # If it's type 1 and the streak is over
    if event.gift.gift_type == 1:
        if event.gift.repeat_end == 1:
            strobe(datetime.timedelta(seconds=3))

    # It's not type 1, which means it can't have a streak & is automatically over
    elif event.gift.gift_type != 1:
        strobe(datetime.timedelta(seconds=5))
	
# Define handling an event via "callback"
client.add_listener("comment", on_comment)

if __name__ == '__main__':
    try:
        #Run the client and block the main thread
        # await client.start() to run non-blocking
        client.run()
    except KeyboardInterrupt:
        print("Killed by user")
        pixels.fill((0, 0, 0))
        pixels.show()
        sys.exit(0)
