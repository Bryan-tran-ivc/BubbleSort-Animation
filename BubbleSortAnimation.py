import random
import sys

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

BACKGROUND = "#FFFFFF"        
FOREGROUND = "#0A0A0A"        
MUTED_FG = "#737373"          
BORDER = "#E5E5E5"            

BAR_IDLE = "#E5E5E5"          
BAR_SORTED = "#A3A3A3"        
BAR_COMPARE = "#171717"       
BAR_SWAP = "#E7000B"          

def pick_font():
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in ("Inter", "Geist", "Helvetica Neue", "Helvetica", "Arial",
                 "DejaVu Sans"):
        if name in installed:
            return name
    return "sans-serif"

#Algorithm
def bubble_sort(arr):
    #Bubble sort implemented as a generator.
    n = len(arr)
    comparisons = swaps = passes = 0

    for i in range(n - 1):
        passes += 1
        swapped_in_pass = False

        # After pass i, the last i elements are already in place.
        for j in range(n - 1 - i):
            comparisons += 1
            # Frame 1: highlight the pair we are about to compare.
            yield dict(arr=arr, pair=(j, j + 1), swapped=False,
                       sorted_from=n - i, comparisons=comparisons,
                       swaps=swaps, passes=passes)

            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped_in_pass = True
                # Frame 2: show the same pair again after the swap.
                yield dict(arr=arr, pair=(j, j + 1), swapped=True,
                           sorted_from=n - i, comparisons=comparisons,
                           swaps=swaps, passes=passes)

        # Early exit: no swaps in a full pass means the list is sorted.
        if not swapped_in_pass:
            break

    # Final frame: everything is sorted.
    yield dict(arr=arr, pair=None, swapped=False, sorted_from=0,
               comparisons=comparisons, swaps=swaps, passes=passes)

# Visualization
def show_graph(n=40, interval=25, show=True):
    data = list(range(1, n + 1))
    random.shuffle(data)

    plt.rcParams["font.family"] = pick_font()
    fig_w, fig_h = 11, 6.4
    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=BACKGROUND)

    # Card background 
    # Create a rounded panel behind the chart to give the visualization a
    # "card" look. `mutation_aspect` keeps the rounded corners visually
    # consistent even when the figure is wider than it is tall.
    panel = FancyBboxPatch(
        (0.025, 0.04), 0.95, 0.92,
        boxstyle="round,pad=0,rounding_size=0.018",
        mutation_aspect=fig_h / fig_w,
        transform=fig.transFigure, facecolor=BACKGROUND,
        edgecolor=BORDER, linewidth=1.2, zorder=-10)  # draw behind the axes
    fig.add_artist(panel)

    # Header: title, description and live stats 
    fig.text(0.055, 0.895, "Bubble Sort", fontsize=19, fontweight="semibold",
             color=FOREGROUND, va="center")
    fig.text(0.055, 0.845,
             "Swaps neighbouring items until the list is in order.",
             fontsize=10.5, color=MUTED_FG, va="center")

    stat_labels = ("Passes", "Comparisons", "Swaps")
    stat_x = (0.64, 0.75, 0.87)
    stat_values = []
    for label, x in zip(stat_labels, stat_x):
        fig.text(x, 0.905, label, fontsize=9.5, color=MUTED_FG, va="center")
        stat_values.append(
            fig.text(x, 0.855, "0", fontsize=17, fontweight="semibold",
                     color=FOREGROUND, va="center"))

    # Divider under the header.
    fig.add_artist(Line2D([0.025, 0.975], [0.795, 0.795],
                          transform=fig.transFigure, color=BORDER, lw=1.2))

    # Bars 
    ax = fig.add_axes([0.055, 0.17, 0.89, 0.58])
    ax.patch.set_alpha(0)  # transparent so the card shows through
    bars = ax.bar(range(n), data, width=0.72, color=BAR_IDLE, edgecolor="none")

    ax.set_xlim(-0.8, n - 0.2)
    ax.set_ylim(0, n * 1.04)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)

    # Legend (small dots, muted text) 
    items = (("Unsorted", BAR_IDLE), ("Comparing", BAR_COMPARE),
             ("Swapped", BAR_SWAP), ("Sorted", BAR_SORTED))
    handles = [Line2D([], [], marker="o", linestyle="", markersize=8,
                      markerfacecolor=color, markeredgecolor="none", label=lbl)
               for lbl, color in items]
    legend = fig.legend(handles=handles, loc="center left",
                        bbox_to_anchor=(0.045, 0.095), ncol=4, frameon=False,
                        fontsize=10, handletextpad=0.3, columnspacing=1.8)
    for text in legend.get_texts():
        text.set_color(MUTED_FG)

    fig.text(0.945, 0.095, "space: pause / resume", fontsize=9,
             color=MUTED_FG, ha="right", va="center")

    # Animation 
    def update(frame):
        arr = frame["arr"]
        pair = frame["pair"]
        sorted_from = frame["sorted_from"]
        finished = pair is None

        for idx, (bar, value) in enumerate(zip(bars, arr)):
            bar.set_height(value)
            if idx >= sorted_from:
                color = BAR_SORTED
            elif pair and idx in pair:
                color = BAR_SWAP if frame["swapped"] else BAR_COMPARE
            else:
                color = BAR_IDLE
            bar.set_facecolor(color)

        stat_values[0].set_text(str(frame["passes"]))
        stat_values[1].set_text(str(frame["comparisons"]))
        stat_values[2].set_text(str(frame["swaps"]))
        if finished:
            for bar in bars:
                bar.set_facecolor(FOREGROUND)  # final state: solid and calm

    anim = FuncAnimation(fig, update, frames=bubble_sort(data),
                         interval=interval, repeat=False,
                         cache_frame_data=False)

    # Space bar toggles pause / resume.
    paused = [False]

    def on_key(event):
        if event.key == " ":
            if paused[0]:
                anim.resume()
            else:
                anim.pause()
            paused[0] = not paused[0]

    fig.canvas.mpl_connect("key_press_event", on_key)

    if show:
        plt.show()
    return fig, anim

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    show_graph(size)
