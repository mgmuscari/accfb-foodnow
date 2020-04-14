import re
import math
from fractions import Fraction
from text_to_num import text2num


def translate_number_string(string):
    try:
        text2num(string, 'en')
    except Exception:
        return 1


def truthy_string(string):
    return re.search('(s(i|í)|y(es)?)', string) is not None


def readable_distance(meters, language):
    total_distance = (meters / 1000.0)
    unit = 'kilometro'
    if language == 'en_US':
        total_distance = total_distance * 0.621371
        unit = 'mile'
    unit_distance = math.floor(total_distance)
    unit_fraction = total_distance - unit_distance
    fraction = Fraction(int(round(unit_fraction * 4)), 4)
    fraction_text = ''
    if fraction.numerator > 0 and fraction.denominator > 1:
        if language == 'en_US':
            denoms = {2: 'half', 4: 'quarter'}
        else:
            denoms = {2: 'media', 4: 'cuarto'}
        fraction_text = '{} {}'.format(fraction.numerator, denoms[fraction.denominator])
        if fraction.numerator > 1:
            fraction_text = fraction_text + 's'
    if unit_distance == 0:
        if len(fraction_text) > 0:
            if language == 'en_US':
                return fraction_text + ' of a ' + unit
            else:
                return fraction_text + ' de ' + unit
        else:
            if language == 'en_US':
                return '1 quarter of a mile'
            else:
                return '1 cuarto de kilometro'
    if unit_distance > 1:
        unit = unit + 's'
    if len(fraction_text) > 0:
        if language == 'en_US':
            fraction_text = ' and ' + fraction_text
        else:
            fraction_text = ' y ' + fraction_text
    return str(int(unit_distance)) + fraction_text + ' ' + unit