#https://gist.github.com/asherepa/5181206
# http://home.dsoft.org.ua/img/donut.png
# http://home.dsoft.org.ua/img/donut_gradient_off.png


import os
import sys
import cairo
import cairoplot

from django.http import HttpResponse
from bitfund.core.settings.server import STATICFILES_DIRS
from bitfund.project.decorators import disallow_not_public_unless_maintainer
import bitfund.core.cairoplot

#@disallow_not_public_unless_maintainer
def chart_image(request):
    chart_filename = 'donut.png'
    chart_abspathname = STATICFILES_DIRS[0]+"img/charts/"+chart_filename


    TOTAL_DEGREES = 360

    ARGB_DONUT_CHART_PLEDGES = (0.345, 0.435, 0.0196, 1, 'solid')
    ARGB_DONUT_CHART_REDONATIONS = (0.553, 0.702, 0.0314, 1, 'linear')
    ARGB_DONUT_CHART_OTHER_SOURCES = (0.937, 0.737, 0.035, 1, 'radial')
    ARGB_DONUT_CHART_BACKGROUND = (0.929, 0.922, 0.922, 1, 'linear')

    plegdes_degrees = 20
    redonations_degrees = 10
    other_sources_degrees = 20

    background_degrees = TOTAL_DEGREES-(plegdes_degrees+redonations_degrees+other_sources_degrees)


    background = cairo.LinearGradient(300, 0, 300, 400)
    background.add_color_stop_rgb(0, 0.4, 0.4, 0.4)
    background.add_color_stop_rgb(1.0, 0.1, 0.1, 0.1)

    data = {'1' : plegdes_degrees, '2' : redonations_degrees, '3' : other_sources_degrees, '4' : background_degrees}
    radius_list = (6, 6, 4, 2)
    shadow_parts = (True, True, False, False)
    colors = [ARGB_DONUT_CHART_PLEDGES, ARGB_DONUT_CHART_REDONATIONS, ARGB_DONUT_CHART_OTHER_SOURCES, ARGB_DONUT_CHART_BACKGROUND]


# RGBCOLOR_DONUT_CHART_PLEDGES = '586F05'
# RGBCOLOR_DONUT_CHART_REDONATIONS = '8DB308'
# RGBCOLOR_DONUT_CHART_OTHER_SOURCES = 'EFBC09'
# RGBCOLOR_DONUT_CHART_BACKGROUND = 'EDEBEA'

    cairoplot.donut_plot(chart_abspathname, data, 900, 900, background='transparent',
                         gradient=True,
                         shadow=True,
                         shadow_parts=shadow_parts,
                         inner_radius=1,
                         colors=colors,
                         radius_list=radius_list)

    # colors_mix = [ 'red',                     #R
    #                (0, 1, 0, 0.75, 'solid'),  #G
    #                (1, 1, 0, 0.75, 'linear'), #Y
    #                (0, 0, 1, 0.75, 'radial')] #B

    # cairoplot.donut_plot('donut_transp.png', data, 800, 600, background = 'transparent',
    #                      gradient = True,
    #                      shadow = True,
    #                      shadow_parts = shadow_parts, inner_radius = 0.8,
    #                      colors = colors_mix, radius_list = radius_list)
    #
    # cairoplot.donut_plot('donut_gradient_off.png', data, 800, 600, background = 'transparent',
    #                      gradient = False,
    #                      shadow = True,
    #                      shadow_parts = shadow_parts, inner_radius = 0.8,
    #                      colors = colors, radius_list = radius_list)
    #
    # cairoplot.donut_plot('donut_gradient_background.png', data, 800, 600, background = background,
    #                      gradient = False,
    #                      shadow = True,
    #                      shadow_parts = shadow_parts, inner_radius = 0.8,
    #                      colors = colors, radius_list = radius_list)


    response = HttpResponse(mimetype='image/png')
    response['Content-Length'] = os.path.getsize(chart_abspathname)
    response.write(open(chart_abspathname, 'r').read())

    return response

