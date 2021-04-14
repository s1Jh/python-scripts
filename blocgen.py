import pygame, sys
import pygame.freetype

"""
    This is horrible code.
    But it does what I need to and I sorta know how to extend it.

    Generates an image of a block scheme circuit.
    usage:
        refer to --help or the block of text bellow this
        
"""

SCALE = 20

THICKNESS = 2*SCALE
SPACING = 20*SCALE
FONT_SIZE = 15*SCALE
BLOCK_WIDTH = 60*SCALE
LEG_LENGTH = 40*SCALE
PAD = 6*SCALE
NEG_CIRCLE = 8*SCALE
CLOCK_LENGTH = 15*SCALE
CLOCK_SPAN = 10*SCALE

def main():
    inputs = []
    outputs = []
    mode = 0

    filename = "output.png"
    
    for i, arg in enumerate(sys.argv):
        if arg.find("-i") != -1:
            mode = 1
            continue
        if arg.find("-o") != -1:
            mode = 2
            continue
        if arg.find("-h") != -1:
            print(
                "Usage: py blocgen.py [arguments] --inputs [input name:[input type]]... --outputs[output name:[output type]]...\n"
                "Arguments:\n"
                "\t-h/--help\t\tShow this dialogue\n"
                "\t-f/--file\t\tSelect the filename to save the image under\n"
                "\t-i/--inputs\t\tEnter inputs\n"
                "\t-o/--outputs\t\tEnter outputs\n"
                "Input/output format:\n"
                "\tInputs and outputs are in a name:type format, name must be a string of unbroken alphanumeric characters. If no type is specified, it automatically defaults to \"normal\".\n"
                "\tTypes:\n"
                "\t\tnormal\t\tLeg is connected straight to the block.\n"
                "\t\tnegated\t\tLeg has a circle placed at it's connection point.\n"
                "\t\tclock\t\tLeg has a triangle pointing into the block, indicating that it's activated with the rising edge.\n"
                "\t\tclock_negated\tLeg has both a triangle and a negation symbol to indicate that it's activated with the falling edge."
            )
            sys.exit(0)
            
        if arg.find("-f") != -1:
            if i < len(sys.argv):
                filename = sys.argv[i+1]
                print(f"Will save as {filename}")
            else:
                print("Filename parameter specified but no value passed in")
                
        if mode == 1:
            if ':' in arg:
                inputs.append(arg.split(':'))
            else:
                inputs.append([arg, "normal"])
        elif mode == 2:
            if ':' in arg:
                outputs.append(arg.split(':'))
            else:
                outputs.append([arg, "normal"])
    
    inputc = len(inputs)
    outputc = len(outputs)
    
    print(f"Inputs ({inputc}): {inputs}\nOutputs ({outputc}): {outputs}")
           
    pygame.init()
    pygame.freetype.init()
    
    font = pygame.freetype.SysFont("DejaVu Sans", FONT_SIZE)
    widest_text = 0
    for leg in inputs + outputs:
        contender = font.get_rect(leg[0])
        if contender.width > widest_text:
            widest_text = contender.w
     
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
                PAD + widest_text + LEG_LENGTH - (NEG_CIRCLE if inputs[i][1].find("negated") != -1 else 0), 
                SPACING/2+i*SPACING + ioffset + PAD
            ),
            THICKNESS
        )
        area = font.render_to(
            canvas, 
            (
                PAD, 
                i*SPACING + FONT_SIZE/4 + ioffset + PAD
            ), 
            inputs[i][0]
        )
        
        if inputs[i][1].find("negated") != -1:
            pygame.draw.circle(
                canvas,
                (0, 0, 0),
                (
                    PAD + widest_text + LEG_LENGTH - NEG_CIRCLE / 2,
                    SPACING/2+i*SPACING + ioffset + PAD
                ),
                NEG_CIRCLE / 2,
                THICKNESS
            )
            pygame.draw.line(
                canvas,
                (0, 0, 0),
                (area.x, area.y - THICKNESS), (area.x + area.w, area.y - THICKNESS),
                int(THICKNESS / 2)
            )
        if inputs[i][1].find("clock") != -1:
            pygame.draw.lines(
                canvas,
                (0, 0, 0),
                False,
                (
                    (
                        PAD + widest_text + LEG_LENGTH,
                        SPACING/2+i*SPACING + ioffset + PAD - CLOCK_SPAN / 2
                    ),
                    (
                        PAD + widest_text + LEG_LENGTH + CLOCK_LENGTH,
                        SPACING/2+i*SPACING + ioffset + PAD
                    ),
                    (
                        PAD + widest_text + LEG_LENGTH,
                        SPACING/2+i*SPACING + ioffset + PAD + CLOCK_SPAN / 2
                    ),
                    (
                        PAD + widest_text + LEG_LENGTH + CLOCK_LENGTH,
                        SPACING/2+i*SPACING + ioffset + PAD
                    )
                ),
                THICKNESS
            )
    
    for i in range(outputc):
        pygame.draw.line(
            canvas, 
            (0, 0, 0), 
            (
                PAD + widest_text + LEG_LENGTH + BLOCK_WIDTH + (NEG_CIRCLE if outputs[i][1].find("negated") != -1 else 0), 
                SPACING/2+i*SPACING + ooffset + PAD
            ), 
            (
                PAD + widest_text + 2*LEG_LENGTH + BLOCK_WIDTH, 
                SPACING/2+i*SPACING + ooffset + PAD
            ),
            THICKNESS
        )
        area = font.render_to(
            canvas, 
            (
                LEG_LENGTH*2 + widest_text + BLOCK_WIDTH + PAD*2, 
                i*SPACING + FONT_SIZE/4 + ooffset + PAD
            ), 
            outputs[i][0]
        )
        
        if outputs[i][1].find("negated") != -1:
            pygame.draw.circle(
                canvas,
                (0, 0, 0),
                (
                    PAD + widest_text + LEG_LENGTH + BLOCK_WIDTH + NEG_CIRCLE / 2,
                    SPACING/2+i*SPACING + ooffset + PAD
                ),
                NEG_CIRCLE / 2,
                THICKNESS
            )
            pygame.draw.line(
                canvas,
                (0, 0, 0),
                (area.x, area.y - THICKNESS), (area.x + area.w, area.y - THICKNESS),
                int(THICKNESS / 2)
            )
        if outputs[i][1].find("clock") != -1:
            pygame.draw.lines(
                canvas,
                (0, 0, 0),
                False,
                (
                    (
                        PAD + widest_text + BLOCK_WIDTH + LEG_LENGTH,
                        SPACING/2+i*SPACING + ooffset + PAD - CLOCK_SPAN / 2
                    ),
                    (
                        PAD + widest_text + BLOCK_WIDTH + LEG_LENGTH - CLOCK_LENGTH,
                        SPACING/2+i*SPACING + ooffset + PAD
                    ),
                    (
                        PAD + widest_text + BLOCK_WIDTH + LEG_LENGTH,
                        SPACING/2+i*SPACING + ooffset + PAD + CLOCK_SPAN / 2
                    ),
                    (
                        PAD + widest_text + BLOCK_WIDTH + LEG_LENGTH - CLOCK_LENGTH,
                        SPACING/2+i*SPACING + ooffset + PAD
                    )
                ),
                THICKNESS
            )
    
    pygame.image.save(canvas, filename)
        
    pygame.freetype.quit()
    pygame.quit()

if __name__ == '__main__':
    main()
