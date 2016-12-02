from itertools import cycle, islice
import numpy as np
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.palettes import PuBu as palette
from bokeh.document import Document
from cesium import featureset
from .config import cfg


def feature_scatterplot(fset_path, features_to_plot):
    """Create scatter plot of feature set.

    Parameters
    ----------
    fset_path : str
        Path to feature set to be plotted.
    features_to_plot : list of str
        List of feature names to be plotted.

    Returns
    -------
    json
        Returns d.to_json where `d` is an instance of
        `bokeh.Document`.
    """

    fset = featureset.from_netcdf(fset_path, engine=cfg['xr_engine'])
    fset = fset.drop('target')
    X = fset.to_dataframe()[features_to_plot]
    if 'target' in fset and fset.target.values.dtype != np.float:
        y = fset.target.values
        labels = np.unique(y)
    else:
        y = [None] * len(X)
        labels = [None]

    if len(labels) in palette:
        colors = palette[len(labels)]
    else:
        all_colors = sorted(palette.items(), key=lambda x: x[0],
                            reverse=True)[0][1]
        colors = list(islice(cycle(all_colors), len(labels)))

    plots = np.array([[figure(width=300, height=200)
                       for j in range(len(features_to_plot))]
                      for i in range(len(features_to_plot))])
    for (i, j), p in np.ndenumerate(plots):
        for l, c in zip(labels, colors):
            if l is not None:
                inds = np.where(y == l)[0]
            else:
                inds = np.arange(len(X))
            p.circle(X.values[inds, i], X.values[inds, j], color=c,
                     legend=(l if (i == j and l is not None) else None))
            p.legend.location = 'bottom_right'
            p.legend.label_text_font_size = '6pt'
            p.legend.spacing = 0
            p.legend.padding = 0
            p.xaxis.axis_label = features_to_plot[i]
            p.yaxis.axis_label = features_to_plot[j]

    plot = gridplot(plots.tolist(), ncol=len(features_to_plot), mergetools=True)
    d = Document()
    d.add_root(p)
    json_data = d.to_json()
    return json_data, None


#def prediction_heatmap(pred_path):
#    with xr.open_dataset(pred_path, engine=cfg['xr_engine']) as pset:
#        pred_df = pd.DataFrame(pset.prediction.values, index=pset.name,
#                               columns=pset.class_label.values)
#    pred_labels = pred_df.idxmax(axis=1)
#    C = confusion_matrix(pset.target, pred_labels)
#    row_sums = C.sum(axis=1)
#    C = C / row_sums[:, np.newaxis]
#    fig = FF.create_annotated_heatmap(C, x=[str(el) for el in
#                                            pset.class_label.values],
#                                      y=[str(el) for el in
#                                         pset.class_label.values],
#                                      colorscale='Viridis')
#
#    py.plot(fig, auto_open=False, output_type='div')
#
#    return fig.data, fig.layout
