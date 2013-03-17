#https://gist.github.com/asherepa/5181206
# http://home.dsoft.org.ua/img/donut.png
# http://home.dsoft.org.ua/img/donut_gradient_off.png


import cairo
import os
import sys

from django.http import HttpResponse
from bitfund.core.settings.server import STATICFILES_DIRS
from bitfund.project.decorators import disallow_not_public_unless_maintainer
import bitfund.core.cairoplot

#@disallow_not_public_unless_maintainer
def chart_image(request):
    chart_filename = 'donut.png'
    chart_abspathname = STATICFILES_DIRS[0]+"img/charts/"+chart_filename

    #sys.path.append('/usr/local/lib/python2.7/dist-packages/cairoplot')

    # try:
    #     import cairoplot
    # except:
    #     print "Module cairoplot needed"
    #     sys.exit(-1)

    background = cairo.LinearGradient(300, 0, 300, 400)
    background.add_color_stop_rgb(0, 0.4, 0.4, 0.4)
    background.add_color_stop_rgb(1.0, 0.1, 0.1, 0.1)

    data = {'1' : 300, '2' : 300, '3' : 300, '4' : 300}
    radius_list = (60, 40, 20, 60)
    shadow_parts = (True, False, True, False)
    colors = ['red', 'green', 'yellow', 'blue']
    colors_mix = [ 'red',                     #R
                   (0, 1, 0, 0.75, 'solid'),  #G
                   (1, 1, 0, 0.75, 'linear'), #Y
                   (0, 0, 1, 0.75, 'radial')] #B

    cairoplot.donut_plot(chart_abspathname, data, 800, 600, background = 'transparent',
                         gradient = True,
                         shadow = True,
                         shadow_parts = shadow_parts, inner_radius = 0.8,
                         colors = colors, radius_list = radius_list)

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

