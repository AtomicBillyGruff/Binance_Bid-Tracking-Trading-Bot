import plotly.graph_objects as go


def calc_peaks():
    # peak_num = int(input("how many peaks?"))
    peak_high = float(input("In[ High Price : "))
    peak_low = float(input("In[ Low Price   : "))

    peak_dif = peak_high - peak_low
    print("\nPeak Difference : $", peak_dif)
    peak_POC = (peak_dif / peak_low) * 100
    print("in %",peak_POC)

    return

calc_peaks()











# fig = go.Figure(data=go.Bar(y=[2,3,1]))
# fig.write_html('first_figure.html', auto_open=True)
#

