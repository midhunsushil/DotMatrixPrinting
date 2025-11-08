# escp2.py
from jinja2 import pass_context

ESC = '\x1b'
CR = '\x0d'
LF = '\x0a'
FF = '\x0c'
NEWLINE = CR+LF
SET_UNIT = ESC + '(U' + chr(1) + chr(0)
INIT = ESC + '@'
ESCP = ESC + 'P' #- Selects 10.5-point, 10-cpi character printing
ESCM = ESC + 'M' #- Selects 10.5-point, 12-cpi character printing
ESCl = ESC + 'l' #- Left Margin
ESCQ = ESC + 'Q' # Right Margin
PAGE_LENGTH = ESC + '(C' + chr(2) + chr(0) # Page Length
PAGE_FORMAT = ESC + '(c' + chr(4) + chr(0) #+ chr(0) + chr(1) + chr(196) + chr(14) # Page top and bottom Margin
ASSIGN_CHAR_TABLE = ESC + '(t' + chr(3) + chr(0) # Assign Character Table: d1,d2,d3
SET_CHAR_TABLE = ESC + 't' # Character Table: n
SET_POINT = ESC + 'X' # font pitch and point: m nl nh
SET_BOLD = ESC + 'E' # Bold
UNSET_BOLD = ESC + 'F' # Unbold
SET_FONT = ESC + 'k' # font
SET_SCORE = ESC + '(-' + chr(3) + chr(0) + chr(1) # score
SET_HORI_POS = ESC + '$' # absolute horizontal position: nl,nh

def get_param(value, bytes=1):
    if bytes == 2:
        return chr(round(value%256)) + chr(round(value//256))
    return chr(round(value))

@pass_context
def calculate_center_inch(ctx, text_width_inch):
    return ctx.get('page')['width']/2-text_width_inch/2

@pass_context
def set_unit(ctx):
    # Sets the unit to m/3600 inch
    m = ctx.get('page')['defined_unit'] * 3600
    return SET_UNIT+get_param(m)

@pass_context
def set_left_right_margin(ctx, margin_left=None, margin_right=None):
    page = ctx.get('page')
    if margin_left:
        margin_left = margin_left
    elif page.get('margin_left', None):
        margin_left = page['margin_left']
    else:
        margin_left = 0.5
    if margin_right:
        margin_right = margin_right
    elif page.get('margin_right', None):
        margin_right = page['margin_right']
    else:
        margin_right = margin_left
    return ESCP + ESCl + get_param(margin_right*12) + ESCQ + get_param((page['width'] - margin_right)*12)

@pass_context
def set_page_length_width(ctx):
    # Sets page length to length inches
    page = ctx.get('page')
    page_length_units = page['length']/page['defined_unit']
    return PAGE_LENGTH + get_param(page_length_units, 2)

@pass_context
def set_top_bottom_margin(ctx, top_margin, bottom_margin):
    page =  ctx.get('page')
    defined_unit = page['defined_unit']
    top_margin_units = top_margin/defined_unit
    bottom_margin_units = (page['length']-bottom_margin)/defined_unit
    return PAGE_FORMAT + get_param(top_margin_units, 2) + get_param(bottom_margin_units, 2)

@pass_context
def set_hori_pos(ctx, position_inch):
    position_units = position_inch / ctx.get('page')['defined_unit']
    return SET_HORI_POS + get_param(position_units, 2)

def set_font(font=1):
    return SET_FONT + get_param(font)

def set_char_table(table=1):
    return SET_CHAR_TABLE + get_param(table)

def set_font_size(point_size, proportional=True):
    m = 1 if proportional else 0
    n = point_size * 2
    return SET_POINT + get_param(m) + get_param(n,2)

def register_jinja_globals(env):
    """Register all template helpers in Jinja environment"""
    env.globals.update({
        'INIT': INIT,
        'FF': FF,
        'SET_BOLD': SET_BOLD,
        'ASSIGN_CHAR_TABLE': ASSIGN_CHAR_TABLE,
        'NEWLINE': NEWLINE,
        'UNSET_BOLD': UNSET_BOLD,
        'SET_SCORE': SET_SCORE,
        'chr': chr,
        'set_unit': set_unit,
        'set_left_right_margin': set_left_right_margin,
        'set_page_length_width': set_page_length_width,
        'set_top_bottom_margin': set_top_bottom_margin,
        'set_char_table': set_char_table,
        'set_font_size': set_font_size,
        'set_font': set_font,
        'set_hori_pos': set_hori_pos,
        'calculate_center_inch': calculate_center_inch,
    })

__all__ = [register_jinja_globals]