# escp2.py
ESC = "\x1B"
SI  = "\x0F"  # condensed (≈17 CPI) on
DC2 = "\x12"  # condensed off
FF  = "\x0C"  # form feed

def set_unit(m=10):
    # Sets the unit to m/3600 inch
    return ESC + "(U"+"10"+m

def init():
    return ESC + "@"

def bold_on():
    return ESC + "E"

def bold_off():
    return ESC + "F"

def condensed_on():
    return SI

def condensed_off():
    return DC2

def set_lpi(n=6):
    # ESC 'A' n : n/72 inch line spacing ≈ 6 LPI => n=12
    n_val = 12 if n == 6 else 8  # crude: 6 LPI or 9 LPI
    return ESC + "A" + chr(n_val)

def set_cpi(cpi=17):
    # Common presets; varies by model
    if cpi in (16, 17):
        return condensed_on()
    elif cpi == 10:
        return condensed_off() + ESC + "P"   # 10 CPI
    elif cpi == 12:
        return condensed_off() + ESC + "M"   # 12 CPI
    else:
        return condensed_on()  # fallback

def page_setup(cpi=17, lpi=6, top_skips=0):
    return init() + set_cpi(cpi) + set_lpi(lpi) + ("\n" * top_skips)

def form_feed():
    return FF
