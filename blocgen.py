import pygame, sys
import pygame.freetype

"""
    Generates an image of a block scheme circuit.
    usage:
        python blocgen.py --inputs <space separated list of input signals> --outputs <space separated list of output signals>
"""

SCALE = 4

THICKNESS = 2*SCALE
SPACING = 20*SCALE
FONT_SIZE = 20*SCALE
BLOCK_WIDTH = 60*SCALE
LEG_LENGTH = 40*SCALE
PAD = 6*SCALE

def main():
    inputs = []
    outputs = []
    mode = 0
    
    for arg in sys.argv:
        if arg == "--inputs":
            mode = 1
            continue
        if arg == "--outputs":
            mode = 2
            continue
            
        if mode == 1:
            inputs.append(arg)
        elif mode == 2:
            outputs.append(arg)
            
    pygame.init()
    pygame.freetype.init()
    
    font = pygame.freetype.SysFont("DejaVu Sans", FONT_SIZE)
    widest_text = 0
    for leg in inputs + outputs:
        contender = font.get_rect(leg)
        if contender.width > widest_text:
            widest_text = contender.w
    
    inputc = len(inputs)
    outputc = len(outputs)
    
    print(f"Inputs ({inputc}): {inputs} Outputs ({outputc}): {outputs}")
    
    ioffset = 0
    ooffset = 0
    
    if inputc >= outputc:
        canvas_height = inputc * SPACING
        ooffset = SPACING * (inputc - outputc) / 2
    else:
        canvas_height = outputc * SPACING
        ioffset = SPACING * (outputc - inputc) / 2

    canvas = pygame.Surface(
        (
        BLOCK_WIDTH + 2*LEG_LENGTH + 2*widest_text + PAD * 2,
        canvas_height + PAD * 2
        )
    )
    
    canvas.fill((255, 255, 255))
    
    # draw the block body
    pygame.draw.rect(
        canvas, 
        (0, 0, 0), 
        pygame.Rect(
            LEG_LENGTH + widest_text + PAD, 
            PAD, BLOCK_WIDTH, 
            canvas_height
        ),
        THICKNESS
    )
    
    # draw the legs
    for i in range(inputc):
        pygame.draw.line(
            canvas, 
            (0, 0, 0), 
            (
                PAD + widest_text, 
                SPACING/2+i*SPACING + ioffset + PAD
            ), 
            (
                PAD + widest_text + LEG_LENGTH, 
                SPACING/2+i*SPACING + ioffset + PAD
            ),
            THICKNESS
        )
        font.render_to(
            canvas, 
            (
                PAD, 
                i*SPACING + FONT_SIZE/4 + ioffset + PAD
            ), 
            inputs[i]
        )
    
    for i in range(outputc):
        pygame.draw.line(
            canvas, 
            (0, 0, 0), 
            (
                PAD + widest_text + LEG_LENGTH + BLOCK_WIDTH, 
                SPACING/2+i*SPACING + ooffset + PAD
            ), 
            (
                PAD + widest_text + 2*LEG_LENGTH + BLOCK_WIDTH, 
                SPACING/2+i*SPACING + ooffset + PAD
            ),
            THICKNESS
        )
        font.render_to(
            canvas, 
            (
                LEG_LENGTH*2 + widest_text + BLOCK_WIDTH + PAD*2, 
                i*SPACING + FONT_SIZE/4 + ooffset + PAD
            ), 
            outputs[i]
        )
    
    pygame.image.save(canvas, "output.png")
        
    pygame.freetype.quit()
    pygame.quit()

if __name__ == '__main__':
    main()
