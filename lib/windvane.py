class Windvane:
    def __init__(self):
        pass
    
    def direction_text( self, dir ):
#        dir = int(dir * 100)
        dir = int(dir * .2)
        if dir in range(239, 260):
            return ("N  ", 0.0)
        if dir in range(111, 140):
            return ("NNE", 22.5)
        if dir in range(140, 171):
            return ("NE ", 45.0)
        if dir in range(24, 28):
            return ("ENE", 67.5)
        if dir in range(28, 35):
            return ("E  ", 90.0)
        if dir in range(1, 24):
            return ("ESE", 112.5)
        if dir in range(50, 69):
            return ("SE ", 135.0)
        if dir in range(35, 50):
            return ("SSE", 157.5)
        if dir in range(85, 111):
            return ("S  ", 180.0)
        if dir in range(69, 85):
            return ("SSW", 202.5)
        if dir in range(198, 214):
            return ("SW ", 225.0)
        if dir in range(171, 198):
            return ("WSW", 247.5)
        if dir in range(295, 400):
            return ("W  ", 270.0)
        if dir in range(260, 276):
            return ("WNW", 292.5)
        if dir in range(276, 295):
            return ("NW ", 315.0)
        if dir in range(214, 239):
            return ("NNW", 337.5)
        return (str(dir), dir)
