#!/usr/bin/env python3

import csv
from datetime import datetime
from glob import glob
from os import getenv
import os.path
import sys
from time import asctime
from typing import Iterable
from typing import Iterator
from typing import Union

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tck
import pandas as pd


#
# Parameters
#
ANNOTATIONS_FILE = getenv("ANNOTATIONS_FILE", "metrics/annotations.txt")
METRICS_SRC = (
    sys.argv[1:] if len(sys.argv) > 1 else [getenv("METRICS_SRC", "metrics/*.csv")]
)
OUTPUT_DIR = getenv("OUTPUT_DIR", "metrics/")

FIG_WIDTH = int(getenv("FIG_WIDTH", 8))
FIG_HEIGHT = int(getenv("FIG_HEIGHT", 10))

PLOT_OPTIONS = {
    "dpi": 300,
    "bbox_inches": "tight",
}


#
# Helper functions and classes
#
class ColorCycler(Iterable):
    """Cyclic generator of values, with method to restore original state."""

    def __init__(self) -> None:
        self.values = [
            "tab:blue",
            "tab:orange",
            "tab:green",
            "tab:red",
            "tab:purple",
            "tab:brown",
            "tab:pink",
            "tab:gray",
            "tab:olive",
            "tab:cyan",
        ]
        self.initial = self.values.copy()

    def __iter__(self) -> Iterator[str]:
        return next(self)

    def __next__(self) -> str:
        value = self.values[0]
        self.values = self.values[1:] + self.values[:1]
        return value

    def reset(self) -> None:
        self.values = self.initial.copy()


class MyLogFormatter(tck.LogFormatter):
    """Custom formatter for logarithmic axis.

    Displays all values as `10^{exponent}`, except for `10^0` and `10^1`,
    which instead are simply displayed as `1` and `10` respectively.
    """

    def _num_to_string(self, v, vmin, vmax):
        num = str(v)
        exponent = len(num) - 3

        if exponent == 0:
            return "1"
        elif exponent == 1:
            return "10"
        else:
            return f"$10^{exponent}$"


def is_csv(path: str) -> bool:
    """Checks whether a given path specifies a CSV file.

    Parameters
    ----------
    path : str
        A path to check whether it points to a CSV file.

    Returns
    -------
    result : bool
        True when the file exists and was recognized as a valid CSV file
        by the csv.Sniffer class; False otherwise.
    """
    with open(path, "rt") as handle:
        try:
            csv.Sniffer().sniff(handle.read(1024))
            return True

        except Exception:
            return False


def find_sources(*search_paths: str) -> list[str]:
    """Returns list of paths to CSV files found under specified search paths.

    Parameters
    ----------
    *search_paths : str
        A direct path or a glob pattern specifying where to look for CSV files.
        When the path points to an existing directory, all regular files within
        that directory are checked. The function accepts any number parameters.

    Returns
    -------
    sources : list[str]
        A sorted list of paths to discovered CSV files.
    """
    sources = []

    for path in search_paths:
        if os.path.isfile(path):
            sources.append(path)

        elif os.path.isdir(path):
            sources.extend(
                os.path.join(path, file)
                for file in os.listdir(path)
                if os.path.isfile(os.path.join(path, file))
            )

        else:  # try glob expansion
            sources.extend(
                candidate for candidate in glob(path) if os.path.isfile(candidate)
            )

    # Filter-out non-csv files
    sources = sorted(path for path in sources if is_csv(path))

    if not sources:
        print("ERROR No sources found in specified paths:", *search_paths)
        sys.exit(1)

    return sources


def load_csv(path: str, source: Union[str, None] = None) -> pd.DataFrame:
    """Reads a CSV file from given path and loads into a DataFrame object.

    Parameters
    ----------
    path : str
        A path to CSV file to read into the DataFrame format.
    source : str | None
        Additional label to annotate the data (default: None).

    Returns
    -------
    df : pd.DataFrame
        The DataFrame object produced from the source CSV file.
    """
    df = pd.read_csv(path, delimiter=r",\s*", engine="python")
    df = df.rename(columns=lambda x: x.strip('"'))  # strip quotes from headers
    df["Time"] = pd.to_datetime(df["Time"], format="%Y-%m-%d_%H:%M:%S")

    if source:
        df.insert(1, "source", source)

    return df


def draw(
    ax: plt.Axes,
    x: Iterable[float],
    y: Iterable[float],
    z: Union[Iterable[float], None] = None,
    color: Union[str, None] = None,
    label: Union[str, None] = None,
) -> None:
    """Plots a line chart in the given subplot object.

    Parameters
    ----------
    ax : plt.Axes
        A subplot object in which the data should be plotted.
    x : Iterable[float]
        The values (coordinates) along X-axis to be plotted.
    y : Iterable[float]
        The values (coordinates) along Y-axis to be plotted;
        must have the same number of elements as parameter `x`.
    z : Iterable[float]
        Additional values (coordinates) along Y-axis to be plotted;
        must have the same number of elements as parameter `x`.
    color : str | None
        The color name or hex RGB string to be used in the plot,
        or None for the matplotlib to automatically pick one (default: None).
    label : str | None
        Additional label to annotate the data in plot (default: None).
    """
    if z is not None:
        ax.fill_between(x, z, color=color, alpha=0.25)

    ax.fill_between(x, y, color=color, alpha=0.25)
    ax.plot(x, y, color=color, alpha=1.0, label=label)


def set_xaxis(axs: Iterable[plt.Axes]) -> None:
    """Configures one common X-axis for the defined subplot objects.

    Parameters
    ----------
    axs : Iterable[plt.Axes]
        A collection of subplot objects in which the data were plotted.
    """
    for ax in axs:
        ax.label_outer()

    ax = axs[-1]  # Just for clarity: all calls below refer to the last axis

    my_fmt = mdates.DateFormatter(r"%b %d, $\mathbf{%H:%M:%S}$")
    ax.xaxis.set_major_formatter(my_fmt)

    my_fmt = mdates.DateFormatter(r"$%H:%M:%S$")
    ax.xaxis.set_minor_formatter(my_fmt)
    ax.xaxis.set_minor_locator(tck.AutoMinorLocator())

    # NOTE: tick_params() is nicer to use, but only set_xticks() allows setting
    #       the horizontal alignment of labels (which is good for long labels)
    for arg in ({"minor": False}, {"minor": True}):
        ax.set_xticks(
            ax.get_xticks(**arg),
            ax.get_xticklabels(**arg),
            **arg,
            size=8,
            rotation=45,
            ha="right",
            rotation_mode="anchor",
        )


def set_yaxis(
    ax: plt.Axes,
    ylabel: str = "value []",
    ylim_bottom: Union[int, None] = 0,
    ylim_top: Union[int, None] = None,
    yscale: str = "linear",
) -> None:
    """Configures the Y-axis in the given subplot object.

    Parameters
    ----------
    ax : plt.Axes
        A subplot object in which the data should be plotted.
    ylabel : str
        A text label to be displayed next to Y-axis (default: 'value []').
    ylim_bottom : int | None
        A lower-bound value to be set on the Y-axis,
        or None for the matplotlib to automatically pick one (default: 0).
    ylim_top : int | None
        An upper-bound value to be set on the Y-axis,
        or None for the matplotlib to automatically pick one (default: None).
    yscale : str
        A name of matplotlib axis scale type to apply (default: 'linear').
    """
    if yscale == "log" and ylim_bottom == 0:
        ylim_bottom = 1
    if yscale == "log" and not ylim_top:
        ymax = int(ax.get_ylim()[1])
        ylim_top = max(1000, 10 ** len(str(ymax)))

    ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=ylim_bottom, top=ylim_top)
    ax.set_yscale(yscale)

    if yscale == "log":
        ax.yaxis.set_major_formatter(MyLogFormatter(labelOnlyBase=True))
        ax.yaxis.set_minor_formatter(tck.NullFormatter())
        ax.yaxis.set_major_locator(tck.LogLocator(base=10, numticks=10))
        ax.yaxis.set_minor_locator(
            tck.LogLocator(base=10, subs=(0.25, 0.5, 0.75), numticks=10)
        )
    else:
        ax.yaxis.set_minor_locator(tck.AutoMinorLocator())

    ax.grid(which="both", axis="both", linewidth=0.5, linestyle="dotted")


def set_legend(fig: plt.Figure, axs: Iterable[plt.Axes]) -> None:
    """Configures the legend to be displayed in the figure.

    Parameters
    ----------
    fig : plt.Figure
        A figure object in which the legend should be displayed.
    axs : Iterable[plt.Axes]
        A collection of subplot objects in which the data were plotted.
    """
    handles, labels = axs[-1].get_legend_handles_labels()
    if handles and labels:
        fig.legend(handles, labels, loc="outside upper center", mode="expand", ncol=4)


def subplot(
    ax: plt.Axes,
    df: pd.DataFrame,
    x: str = "Time",
    y: str = "cpu",
    z: Union[str, None] = None,
    loop: Union[str, None] = None,
    color: Union[str, ColorCycler, None] = None,
    reset: bool = False,
    ylabel: str = "value []",
    ylim_bottom: Union[int, None] = 0,
    ylim_top: Union[int, None] = None,
    yscale: str = "linear",
) -> None:
    """Generates a complete chart from one or multiple data series.

    Parameters
    ----------
    ax : plt.Axes
        A subplot object in which the data should be plotted.
    df : pd.DataFrame
        The DataFrame object containing all the data to be plotted.
    x : str
        The column name in the DataFrame object (given as the `df` parameter)
        containing the values for X-axis (default: 'Time').
    y : str
        The column name or expression to extract the desired values for Y-axis
        from the DataFrame object given as the `df` parameter (default: 'cpu').
    z : str | None
        The column name or expression to extract the additional values
        for Y-axis from the given DataFrame object (default: None).
    loop : str | None
        The optional column name in the Dataframe object (the `df` parameter)
        which contains entries that shall be used to split the output values
        (from `y` parameter) and draw as the separate labelled data series;
        if not specified, a single data series is assumed (default: None).
    color : str | ColorCycler | None
        The color name or hex RGB string to be used in the plot,
        or the instance of ColorCycler specifying set of color names,
        or None for the default ColorCycler (default: None).
    reset : bool
        Sets whether to reset the ColorCycler instance between subplots,
        ignored if given `color` parameter is not ColorCycler (default: False).
    ylabel : str
        A text label to be displayed next to Y-axis (default: 'value []').
    ylim_bottom : int | None
        A lower-bound value to be set on the Y-axis,
        or None for the matplotlib to automatically pick one (default: 0).
    ylim_top : int | None
        An upper-bound value to be set on the Y-axis,
        or None for the matplotlib to automatically pick one (default: None).
    yscale : str
        A name of matplotlib axis scale type to apply (default: 'linear').
    """
    if reset and isinstance(color, ColorCycler):
        color.reset()

    if yscale == "log":
        y += "+ 0.001"  # ensure non-zero values

    if loop:
        for item in df[loop].unique():
            c = next(color) if isinstance(color, ColorCycler) else color
            draw(
                ax=ax,
                x=df.query(f'{loop} == "{item}"')[x],
                y=df.query(f'{loop} == "{item}"').eval(y),
                z=df.query(f'{loop} == "{item}"').eval(z) if z else None,
                color=c,
                label=item,
            )
    else:
        draw(
            ax=ax,
            x=df[x],
            y=df.eval(y),
            z=df.eval(z) if z else None,
            color=next(color) if isinstance(color, ColorCycler) else color,
        )

    set_yaxis(
        ax=ax, ylabel=ylabel, ylim_bottom=ylim_bottom, ylim_top=ylim_top, yscale=yscale
    )


def annotate(axs: Iterable[plt.Axes]) -> None:
    """Draws vertical annotation lines on the interesting time marks.

    Parameters
    ----------
    axs : Iterable[plt.Axes]
        A collection of subplot objects in which the data were plotted.
    """
    if not os.path.isfile(ANNOTATIONS_FILE):
        print("WARNING No annotations dafa found in file:", ANNOTATIONS_FILE)
        return

    with open(ANNOTATIONS_FILE) as file:
        data = file.read().strip().split("\n")

    for annotation in data:
        try:
            time, details = annotation.split(" | ", maxsplit=1)
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S,%f")
        except (ValueError, TypeError):
            print("WARNING Skipping malformed annotation line:", annotation.strip())
            continue

        if details.startswith("PLAY"):
            color = "darkred"

        elif details.startswith("TASK [kustomize_deploy"):
            color = "navy"

        elif details.startswith("TASK [test_operator"):
            color = "darkgreen"

        else:  # generic
            color = "grey"

        for ax in axs:
            ax.axvline(time, color=color, ls="--", alpha=0.5)


def plot(
    df: pd.DataFrame,
    output: str,
    title: Union[str, None] = None,
    loop: Union[str, None] = None,
    color: Union[str, ColorCycler, None] = None,
    reset: bool = False,
) -> None:
    """Produces the figure and saves it as PDF file under a given output path.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame object containing all the data to be plotted.
    output : str
        The path where the generated plot should be saved as PDF file.
    title : str | None
        The text to be displayed on top of the produced figure (default: None).
    loop : str | None
        The optional column name in the Dataframe object (the `df` parameter)
        which contains entries that shall be used to split the output values
        (from `y` parameter) and draw as the separate labelled data series;
        if not specified, a single data series is assumed (default: None).
    color : str | ColorCycler | None
        The color name or hex RGB string to be used in the plot,
        or the instance of ColorCycler specifying set of color names,
        or None for the default ColorCycler (default: None).
    reset : bool
        Sets whether to reset the ColorCycler instance between subplots,
        ignored if given `color` parameter is not ColorCycler (default: False).
    """
    plt.rcdefaults()

    fig, axs = plt.subplots(nrows=6, sharex=True, layout="constrained")

    if not color:
        color = ColorCycler()

    if title:
        fig.suptitle(title, fontsize=16)

    annotate(axs)

    # NOTE: the argument of Pandas query() & eval() is expected to be a valid
    #       Python expression, which does not allow any special characters
    #       (e.g. dots); the backticks can be used to specify column names
    #       with such characters, so below instead of 'mem.used' we need
    #       to specify '`mem.used`' for some of the `y` parameters.
    subplot(
        axs[0],
        df,
        y="cpu + sys",
        z="sys",
        loop=loop,
        color=color,
        reset=reset,
        ylabel="CPU [%]",
        ylim_top=100,
    )

    subplot(
        axs[1],
        df,
        y="100 * (1 - `mem.freemem` / `mem.physmem`)",
        z="100 * (1 - `mem.util.available` / `mem.physmem`)",
        loop=loop,
        color=color,
        reset=reset,
        ylabel="RAM [%]",
        ylim_top=100,
    )

    subplot(
        axs[2],
        df,
        y="`disk.all.read_bytes`",
        loop=loop,
        color=color,
        reset=reset,
        ylabel="Read [kB/s]",
        ylim_top=10**6,
        yscale="log",
    )

    subplot(
        axs[3],
        df,
        y="`disk.all.write_bytes`",
        loop=loop,
        color=color,
        reset=reset,
        ylabel="Write [kB/s]",
        ylim_top=10**6,
        yscale="log",
    )

    subplot(
        axs[4],
        df,
        y="kbin",
        loop=loop,
        color=color,
        reset=reset,
        ylabel="Net in [kB/s]",
        ylim_top=10**6,
        yscale="log",
    )

    subplot(
        axs[5],
        df,
        y="kbout",
        loop=loop,
        color=color,
        reset=reset,
        ylabel="Net out [kB/s]",
        ylim_top=10**6,
        yscale="log",
    )

    set_xaxis(axs)
    set_legend(fig, axs)

    fig.set_figwidth(
        max(
            FIG_WIDTH,
            2
            * df["Time"]
            .agg(["min", "max"])
            .diff()
            .dropna()
            .iloc[0]
            .ceil("h")
            .components.hours,
        )
    )
    fig.set_figheight(FIG_HEIGHT)
    fig.savefig(output, format="pdf", **PLOT_OPTIONS)


#
# Main section
#
if __name__ == "__main__":
    try:
        paths = find_sources(*METRICS_SRC)
        dfs = []

        for path in paths:
            print(asctime(), "Loading:", path)
            hostname = os.path.splitext(os.path.basename(path))[0]
            dfs.append(load_csv(path, hostname))

        df = pd.concat(dfs)
        del dfs

        for hostname in sorted(df["source"].unique()):
            path = os.path.join(OUTPUT_DIR, f"{hostname}.pdf")
            print(asctime(), "Generating:", path)
            plot(df.query(f'source == "{hostname}"'), output=path, title=hostname)

        path = os.path.join(OUTPUT_DIR, "all.pdf")
        print(asctime(), "Generating:", path)
        plot(df, output=path, loop="source", reset=True)

        print(asctime(), "Done!")

    except KeyboardInterrupt:
        print(flush=True)
