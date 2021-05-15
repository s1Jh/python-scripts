# ==== Imports ====
import pygame
import pygame.freetype
from collections import deque
from math import sqrt

# ==== Runtime constants ====
# how many samples to take for calculating the average bpm
AVG_SAMPLES = 10
# size of the screen edge, screen is always square
SSIZE = 640
# yup, it's font size
FONT_SIZE = 20
# how many lines of information are shown on the screen (max 4)
INFO_LEVEL = 3
# how fast do circles expand? (pixels per second)
CIRCLE_ANIM_RATE = 50
# should the program dump stats into the console?
QUIET = True

# hit detection margins
# "if it's within n seconds, you're on track"
HINT_T_ONTIME_MARGIN = 0.1
# "if it's within n seconds, you're a bit too early or late"
HINT_A_BIT_MARGIN = 0.2
# "if it's within n seconds, you're very early or late"
HINT_A_VERY_MARGIN = 0.5

# colors
# color of the hint text
HINT_FONT_COLOR = (255, 255, 255, 255)
# color of the info text
INFO_FONT_COLOR = (128, 128, 128, 255)
# color of the circles
CIRCLE_COLOR = (255, 0, 0, 255)

# ==== Function declerations ====

def to_bpm(time: float):
    """Converts the time passed in (seconds) into beats per minute."""
    if (time != 0):
        return 60 / time
    else:
        return 0

def main():
    """Main function."""
    # ==== Initialization ====
    pygame.init()
    screen = pygame.display.set_mode((SSIZE, SSIZE))
    pygame.display.set_caption("Rhytm")
    font = pygame.freetype.SysFont("DejaVu Sans", FONT_SIZE)
    
    # ==== Variable declerations ====
    # checks the current state of the program
    running = True

    # these are for keeping a constant change over frames
    fps_time_last = pygame.time.get_ticks()
    fps_delta = 0.0

    # this is for timing the beat
    time_last = pygame.time.get_ticks()

    # here's the current delay
    beat_delay = 0.0
    # bpm, inverse of beat_delay
    beat = 0
    # this is how much we deviate from the average
    beat_diff = 0.0
    # here's where we store the delays between presses
    avg_samples = deque([0]*AVG_SAMPLES)
    # here's the average delay of the afforementioned
    avg_delay = 0.0
    avg_bpm = 0

    # strings to store info lines
    info_lines = [""] * 4
    # string to accumulate the hint text into
    # timing: "on time" / "late" / "early"
    # adjective: "very" / "bit too" / ""
    hint = ""
    # list of tempo circles
    circles = []
    
    while running:
        # ==== Timekeeping ====
        fps_delta = (pygame.time.get_ticks() - fps_time_last) / 1000
        fps_time_last = pygame.time.get_ticks()
        
        # ==== Input ====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYUP:
                # user has hit a key, calculate the delay since the 
                # last press and add it to the samples
                # the delay since the last smack
                beat_delay = (pygame.time.get_ticks() - time_last) / 1000
                # push it to our shift queue
                avg_samples.popleft()
                avg_samples.append(beat_delay)
                # save the last time the user smacked something
                time_last = pygame.time.get_ticks()
                # how much do we deviate from the current average
                beat_diff = avg_delay - beat_delay
                
                # also add another visualization circle 
                circles.append(0)
        
        # ==== Calculations ====
        # get the average delay between the samples
        avg_delay = sum(avg_samples) / len(avg_samples)
        # convert that to bpm for easier reading
        avg_bpm = to_bpm(avg_delay)
        beat = to_bpm(beat_delay)
        
        # ==== Infographics ====
        # fill out the info line strings
        info_lines[0] = 'beat: {:.2f} bpm ({:.2f} s)'.format(beat, beat_delay)
        info_lines[1] = "off:  {:.2f} s".format(beat_diff)
        info_lines[2] = "avg:  {:.2f} bpm ({:.2f} s)".format(avg_bpm, avg_delay)
        info_lines[3] = f"samples: {avg_samples}"
        
        # dump the info into the console if we need to
        if not QUIET:
            for line in info_lines:
                print(line)
        
        # construct the hint
        hint = ""
        
        if (abs(beat_diff) >= HINT_A_VERY_MARGIN):
            hint += "very "
        elif (abs(beat_diff) >= HINT_A_BIT_MARGIN):
            hint += "bit too "
            
        if (abs(beat_diff) <= HINT_T_ONTIME_MARGIN):
            hint += "on time"
        elif (beat_diff > 0.0):
            hint += "early"
        elif (beat_diff < 0.0):
            hint += "late"

        # now check if any have escaped the screen size
        circles = list(filter(lambda x: x < SSIZE / sqrt(2), circles))

        # ==== Drawing ====
        screen.fill((0, 0, 0))
        
        # draw the background circles
        for i in range(len(circles)):
            circles[i] += CIRCLE_ANIM_RATE * fps_delta
            pygame.draw.circle(screen, CIRCLE_COLOR, (SSIZE / 2, SSIZE / 2), circles[i], 2)
        
        # render all the info lines
        for i in range(min(len(info_lines), INFO_LEVEL)):
            font.render_to(screen, (0, i * FONT_SIZE * 1.2), info_lines[i], fgcolor=INFO_FONT_COLOR)
        
        # render the hint to the middle of the screen
        # the size of this text is changing constantly
        # so we must recalculate it's position on every frame
        metrics = font.get_rect(hint, size=FONT_SIZE * 2)
        metrics.x = (SSIZE - metrics.w) / 2
        metrics.y = (SSIZE - metrics.h) / 2
        font.render_to(screen, metrics, hint, fgcolor=HINT_FONT_COLOR, size=FONT_SIZE * 2)
            
        # === Ending the frame off ====
        pygame.event.pump()
        pygame.display.flip()
    
    # === Cleanup ====
    pygame.quit()
    
if __name__ == '__main__':
    main()
