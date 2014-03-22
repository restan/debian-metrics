# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from numpy import array
from matplotlib import pyplot
from matplotlib.colors import hsv_to_rgb
from mpld3 import save_html

DATABASE_URL = "postgresql://public-udd-mirror:public-udd-mirror@\
public-udd-mirror.xvm.mit.edu:5432/udd"
VCS_TYPES = ["arch", "bzr", "cvs", "darcs", "git", "hg", "mtn", "svn"]


def get_rgb_color(hue):
    """Convert hue (from HSV) to three element tuple representing RGB color.
    Hue must be a float value between 0.0 and 1.0. Returned color has maximum
    saturation and brightness.

    get_rgb_color(0.0) -> (1.0, 0.0, 0.0) # Red
    get_rgb_color(1.0/3) -> (0.0, 1.0, 0.0) # Green
    get_rgb_color(2.0/3) -> (0.0, 0.0, 1.0) # Blue
    get_rgb_color(1.0) -> (1.0, 0.0, 0.0) # Red
    """
    if not 0.0 <= hue <= 1.0:
        raise ValueError("Hue must be a float value between 0.0 and 1.0")
    return tuple(hsv_to_rgb(array([[[hue, 1.0, 1.0]]]))[0][0])


def get_data_set():
    """Fetch data from history.sources_count table and return it
    as a list of dicts
    """
    engine = create_engine(DATABASE_URL)
    connection = engine.connect()
    vcs_column_prefix = "vcstype_"
    vcs_columns = ["%s%s" % (vcs_column_prefix, vcs) for vcs in VCS_TYPES]
    query = "select date(ts) as ts, %(vcs_columns)s " \
            "from history.sources_count " \
            "group by date(ts), %(vcs_columns)s " \
            "order by date(ts)" % {
                "vcs_columns": ", ".join(vcs_columns)
            }
    results = []
    rows = connection.execute(query)
    for row in rows:
        result = {
            "date": row["ts"]
        }
        result.update({
            vcs: row["vcstype_%s" % vcs] for vcs in VCS_TYPES
        })
        results.append(result)
    connection.close()
    return results


def generate_plots(image_filename=None, html_filename=None):
    """Generate static and/or dynamic plots for sources count metric"""
    if not (image_filename or html_filename):
        return
    data_set = get_data_set()
    dates = [item["date"] for item in data_set]

    fig, ax = pyplot.subplots()
    ax.set_title("Sources count")
    ax.legend(loc="upper left")
    for i, vcs in enumerate(VCS_TYPES):
        col = get_rgb_color(i*1.0/len(VCS_TYPES))
        ax.plot(dates, [item[vcs] for item in data_set], color=col, label=vcs)
    if image_filename:
        # Save static plot as image
        pyplot.savefig(image_filename)
    if html_filename:
        # Save dynamic plot as html document
        save_html(fig, html_filename)


if __name__ == "__main__":
    generate_plots(
        image_filename="sources_count.png",
        html_filename="sources_count.html"
    )
