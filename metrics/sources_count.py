# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from matplotlib import pyplot
from mpld3 import save_html

DATABASE_URL = "postgresql://public-udd-mirror:public-udd-mirror@\
public-udd-mirror.xvm.mit.edu:5432/udd"
VCS_TYPES = ["arch", "bzr", "cvs", "darcs", "git", "hg", "mtn", "svn"]
COLORS = ["cyan", "green", "lime", "salmon", "red", "pink", "purple", "blue"]


def get_data_set():
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


def generate_plots():
    data_set = get_data_set()
    dates = [item["date"] for item in data_set]

    fig, ax = pyplot.subplots()
    ax.set_title("Sources count")
    for vcs, color in zip(VCS_TYPES, COLORS):
        ax.plot(dates, [item[vcs] for item in data_set], color, label=vcs)
    ax.legend(loc="upper left")
    pyplot.savefig("sources_count.png")
    save_html(fig, "sources_count.html")


if __name__ == "__main__":
    generate_plots()
