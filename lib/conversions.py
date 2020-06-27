""" Handy conversion utils """

MBAR_CONV = 33.8639
ALTITUDE = 4837

def c_to_f(tempc):
    return (tempc * (9/5)) + 32

def adjust_for_altitude(reading, alt=ALTITUDE):
    correction = (alt / 1000) * MBAR_CONV
    return reading + correction

def hpa_to_inhg(hpa):
    return hpa / MBAR_CONV

