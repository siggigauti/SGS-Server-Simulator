import plotly.plotly as py
import plotly.graph_objs as go


class AutoGraphs():

    _data = []
    file_name = None

    def __init__(self, file_name):
        self.file_name = file_name
        with open(file_name + '.txt') as file:  # File given must have data in a line-by-line fashion
            self._data = file.read().splitlines()

    def create_line_graph(self):
        x_length = len(self._data)  # Get the length of X
        x_s = []
        for x in range(0, x_length):
            x_s.append(x)

        trace = go.Scatter(
            x=x_s,
            y=self._data
        )
        data = [trace]
        py.iplot(data, filename=self.file_name)  # Creates a linegraph with given name. Can see @ plot.ly/~siggigauti

    def create_histo_graph(self):
        data = [go.Histogram(x=self._data)]
        py.iplot(data, filename=self.file_name)
