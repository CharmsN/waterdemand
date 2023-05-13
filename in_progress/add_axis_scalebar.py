def add_axis_elements(ax):
    # Define tick locations and label text
    x_ticks = [100000, 200000, 300000, 400000, 500000, 600000, 700000]
    y_ticks = [100000, 200000, 300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000]
    x_tick_labels = [str(x) for x in x_ticks]
    y_tick_labels = [str(y) for y in y_ticks]

    # Add vertical gridlines
    ax.vlines(x=x_ticks, ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], color='gray', linestyle=':', linewidth=0.5)

    # Add horizontal gridlines
    ax.hlines(y=y_ticks, xmin=ax.get_xlim()[0], xmax=ax.get_xlim()[1], color='gray', linestyle=':', linewidth=0.5)

    # Add labels to x-axis
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels, fontsize=8)

    # Add labels to y-axis
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels, fontsize=8)

    # Add scalebar
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_scale = (xlim[1] - xlim[0]) / 5  # set the scalebar to 1/5 of the x-axis range
    y_scale = (ylim[1] - ylim[0]) / 20  # set the scalebar to 1/20 of the y-axis range
    scalebar_length = 100000  # length of the scalebar in meters
    scalebar_x = xlim[1] - x_scale - scalebar_length
    scalebar_y = ylim[1] - y_scale  # move scalebar to top of the plot
    ax.plot([scalebar_x, scalebar_x + scalebar_length], [scalebar_y, scalebar_y], linewidth=3, color='black')
    ax.text(scalebar_x + scalebar_length / 2, scalebar_y - y_scale, '100 km', ha='center', va='top')

    # Remove x-axis and y-axis label
    ax.set_xlabel('')
    ax.set_ylabel('')
