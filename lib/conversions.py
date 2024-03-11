""" Handy conversion utils """

MBAR_CONV = 33.8639
ALTITUDE = 4837

CORA = .00035
CORB = .02718
CORC = 1.39538
CORD = .0018
CORE = -.003333333
CORF = -.001923077
CORG = 1.130128205

PARA = 116.6020682
PARB = 2.769034857

RZERO = 40.98

def c_to_f(tempc):
    return (tempc * (9/5)) + 32

def adjust_for_altitude(reading, alt=ALTITUDE):
    correction = (alt / 1000) * MBAR_CONV
    return reading + correction

def hpa_to_inhg(hpa):
    return hpa / MBAR_CONV

def get_correction_factor(temperature, humidity):
    if temperature < 20:
        return CORA * temperature * temperature - CORB * temperature + CORC - (humidity - 33.0) * CORD
    else:
        return CORE * temperature + CORF * humidity + CORG

def get_corrected_resistance(temperature, humidity, resistance):
    return resistance / get_correction_factor(temperature, humidity)

def get_corrected_pm(temperature, humidity, resistance, rzero):
    return PARA * pow((get_corrected_resistance(temperature, humidity, resistance) / rzero), -PARB)
