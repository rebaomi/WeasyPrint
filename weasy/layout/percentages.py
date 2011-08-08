# coding: utf8

#  WeasyPrint converts web documents (HTML, CSS, ...) to PDF.
#  Copyright (C) 2011  Simon Sapin
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


from ..css.utils import get_single_keyword
from ..formatting_structure import boxes


def pixel_value(value):
    """
    Return the numeric value of a pixel length or None.
    """
    if len(value) == 1 and value[0].type == 'DIMENSION' \
            and value[0].dimension == 'px':
        # cssutils promises that `DimensionValue.value` is an int or float
        assert isinstance(value[0].value, (int, float))
        return value[0].value
    # 0 may not have a units
    elif len(value) == 1 and value[0].value == 0:
        return 0
    else:
        # Not a pixel length
        return None


def percentage_value(value):
    """
    Return the numeric value of a percentage or None.
    """
    if len(value) == 1 and value[0].type == 'PERCENTAGE': \
        # cssutils promises that `DimensionValue.value` is an int or float
        assert isinstance(value[0].value, (int, float))
        return value[0].value
    else:
        # Not a percentage
        return None


def resolve_one_percentage(box, property_name, refer_to,
                           allowed_keywords=None):
    """
    Set a used length value from a computed length value.
    `refer_to` is the length for 100%.

    If `refer_to` is not a number, it just replaces percentages.
    """
    # box.style has computed values
    values = box.style[property_name]
    pixels = pixel_value(values)
    if pixels is not None:
        # Absolute length (was converted to pixels in "computed values")
        result = pixels
    else:
        percentage = percentage_value(values)
        if percentage is not None:
            if isinstance(refer_to, (int, float)):
                # A percentage
                result = percentage * refer_to / 100.
            else:
                # Replace percentages when we have no refer_to that
                # makes sense.
                result = refer_to
        else:
            # Some other values such as 'auto' may be allowed
            result = get_single_keyword(values)
            assert allowed_keywords and result in allowed_keywords
    # box attributes are used values
    setattr(box, property_name.replace('-', '_'), result)


def resolve_percentages(box):
    """
    Set used values as attributes of the box object.
    """
    # cb = containing block
    cb_width, cb_height = box.containing_block_size()
    if isinstance(box, boxes.PageBox):
        maybe_height = cb_height
    else:
        maybe_height = cb_width
    resolve_one_percentage(box, 'margin-left', cb_width, ['auto'])
    resolve_one_percentage(box, 'margin-right', cb_width, ['auto'])
    resolve_one_percentage(box, 'margin-top', maybe_height, ['auto'])
    resolve_one_percentage(box, 'margin-bottom', maybe_height, ['auto'])
    resolve_one_percentage(box, 'padding-left', cb_width)
    resolve_one_percentage(box, 'padding-right', cb_width)
    resolve_one_percentage(box, 'padding-top', maybe_height)
    resolve_one_percentage(box, 'padding-bottom', maybe_height)
    resolve_one_percentage(box, 'text-indent', cb_width)
    resolve_one_percentage(box, 'min-width', cb_width)
    resolve_one_percentage(box, 'max-width', cb_width, ['none'])
    resolve_one_percentage(box, 'width', cb_width, ['auto'])

    # TODO: background-position?
    # XXX later: top, bottom, left and right on positioned elements

    if cb_height == 'auto':
        # Special handling when the height of the containing block
        # depends on its content.
        resolve_one_percentage(box, 'min-height', 0)
        resolve_one_percentage(box, 'max-height', None, ['none'])
        resolve_one_percentage(box, 'height', 'auto', ['auto'])
    else:
        resolve_one_percentage(box, 'min-height', cb_height)
        resolve_one_percentage(box, 'max-height', cb_height, ['none'])
        resolve_one_percentage(box, 'height', cb_height, ['auto'])

    # Used value == computed value
    box.border_top_width = box.style.border_top_width
    box.border_right_width = box.style.border_right_width
    box.border_bottom_width = box.style.border_bottom_width
    box.border_left_width = box.style.border_left_width
