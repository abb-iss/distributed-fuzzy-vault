"""
    Plots minutiae
"""

import matplotlib.pyplot as plt
import math


class MinutiaePlotter:
    arrow_length = 10

    @staticmethod
    def plot_minutiae(minutia_list, window, style):
        """
        plot list of minutiae
        :param minutia_list: list of Minutia
        :param window: number of window
        """
        def plot_minutia_arrow(x, y, theta, arrow_length):
            """ calculates arrow lengths along x, y direction with arrow base x/y coordinates according to
                MinutiaPlotter.arrow_length and plots them """
            plt.arrow(x, y, arrow_length * math.cos(math.radians(theta)), arrow_length * math.sin(math.radians(theta)),
                      width=1, head_width=6)
        # new window to plot into
        plt.figure(window)
        for m in minutia_list:
            plt.plot(m.x, m.y, style)
            # plt.annotate(f'({m.x}, {m.y}, {m.theta}°)', (m.x, m.y), textcoords='data')
            plot_minutia_arrow(m.x, m.y, m.theta, MinutiaePlotter.arrow_length)
        # set and plot axis according to first element in minutia_list
        m = minutia_list[0]
        plt.axis([m.X_MIN, m.X_MAX, m.Y_MIN, m.Y_MAX])
        # fixed axis
        # plt.axis([-300, 300, -300, 300])
        plt.arrow(m.X_MIN, 0, m.X_MAX - m.X_MIN, 0, length_includes_head=True,
                  linestyle=':', color='k')
        plt.arrow(0, m.Y_MIN, 0, m.Y_MAX - m.Y_MIN, length_includes_head=True,
                  linestyle=':', color='k')

    @staticmethod
    def plot_minutia(minutia, window, style):
        plt.figure(window)
        plt.plot(minutia.x, minutia.y, style)

    @staticmethod
    def show_plot():
        plt.ylabel('Minutiae y-coordinate')
        plt.xlabel('Minutiae x-coordinate')
        plt.show()

