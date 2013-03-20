#!/usr/bin/env python
import cairo
import os
import sys

sys.path.append(os.path.dirname(__file__) + "/cairoplot")
import cairoplot

background = cairo.LinearGradient(300, 0, 300, 400)
background.add_color_stop_rgb(0, 0.4, 0.4, 0.4)
background.add_color_stop_rgb(1.0, 0.1, 0.1, 0.1)


data = {'1': 300, '2': 300, '3': 300, '4': 300}
radius_list = (60, 40, 20, 60)
shadow_parts = (True, True, True, True)
colors = ['red', 'green', 'yellow', 'blue']
colors_mix = ['red',                     #R
              (0, 1, 0, 0.75, 'solid'),  #G
              (1, 1, 0, 0.75, 'linear'), #Y
              (0, 0, 1, 0.75, 'radial')] #B

cairoplot.donut_plot('donut_transp.png', data, 800, 600,
                     background='transparent',
                     gradient=True,
                     shadow=True,
                     shadow_parts=shadow_parts,
                     inner_radius=0.8,
                     colors=colors_mix,
                     radius_list=radius_list)

cairoplot.donut_plot('donut.png', data, 800, 600, background = 'transparent',
                    gradient = True,
                    shadow = True,
                    shadow_parts = shadow_parts,
                    inner_radius = 0.8,
                    colors = colors,
                    radius_list = radius_list)

cairoplot.donut_plot('donut_gradient_off.png', data, 800, 600, background = 'transparent', 
                    gradient = False, 
                    shadow = True,
                    shadow_parts = shadow_parts, inner_radius = 0.8, 
                    colors = colors, radius_list = radius_list)


cairoplot.donut_plot('donut_gradient_off_background.png', data, 800, 600, background = background, 
                    gradient=False, 
                    shadow=True,
                    shadow_parts=shadow_parts,
                    inner_radius=0.8, 
                    colors=colors,
                    radius_list=radius_list)

