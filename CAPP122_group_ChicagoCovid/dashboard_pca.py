import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import datetime
import data_modeling as dm
import data_analyzing as da

# load data
database_cross = pd.read_csv("databases/cross_section_database " + \
                      str(datetime.date.today()) + ".csv", index_col=0)
pca_var = [col for col in database_cross.columns \
            if not col.startswith('majority')]
full_df, loadings = dm.do_pca(database_cross)

database_ts = pd.read_csv("databases/ts_database " + \
                          str(datetime.date.today()) + ".csv", index_col=0)

non_ts_var = ["week_number", "week_end", "row_id", "zip_code_location", "date",
              "population", "year"]
cs_var = [col for col in database_cross.columns \
          if not col.startswith(('majority', 'population'))]

# Launch dashboard

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(children='Dashboard of Covid-19 in Chicago by Zip Code',
            style={'textAlign': 'center'}),
    # Top Left
    html.Div([
        html.H4(children='Time Series of Variable by Zipcode',
                style={'textAlign': 'center'}),
        html.Div([
            html.H6(children='Select a Zip Code: '),
            dcc.Dropdown(
                id='crossfilter-zipcode-ts',
                options=[{'label': i, 'value': int(i)} \
                         for i in database_ts.index.unique() if i != "Unknown"],
                value=60601,
                searchable=True
            )], style={"display": "inline-block", "width": "40%"}),
        html.Div([
            html.H6(children='Select a Variable to Plot: '),
            dcc.Dropdown(
                id='crossfilter-var-ts',
                options=[{'label': var, 'value': var} \
                       for var in database_ts.columns if var in cs_var],
                value='tests_weekly'
            )], style={'display': 'inline-block', 'width': '50%',
                       'vertical-align': 'top'}),
        dcc.Graph(
            id='var_time_series',
            config={'autosizable': True, 'responsive': False}
        ),
        html.Div([
            html.H6(children="Select Week"),
            dcc.RangeSlider(
                id='week-slider',
                min=database_ts['week_number'].min(),
                max=database_ts['week_number'].max(),
                value=(database_ts['week_number'].min(),
                       database_ts['week_number'].max()),
                marks={str(week): str(week) for week in \
                        database_ts['week_number'].unique() if week % 4 == 0},
            step=1)]),], style={'width': '49%', 'display': 'inline-block',
                   'vertical-align': 'top'}),
    # Top Right
    html.Div([
        html.H4(children="Prediced Variable Conditional on Majority Race",
                style={'textAlign': 'center'}),
        html.Div([
            html.H6(children='Select a Variable to Predict: '),
            dcc.Dropdown(
                id='crossfilter-var-pred',
                options=[{'label': var, 'value': str(var)} \
                    for var in database_cross.columns if var in cs_var],
                value='tests_weekly'
            )], style={'display': 'inline-block', 'width': '50%',
                       'vertical-align': 'top'}),
        html.Div([
            dcc.Graph(
                id='prediction-fig',
                config={'autosizable': True, 'responsive': False})
            ]),
        html.Div([
            html.H4(children='K Nearest Neighbors Prediction',
                    style={'textAlign': 'center'}),
            html.H6(children='Select K',
                    style={'textAlign': 'center'}),
            dcc.Dropdown(
                id='crossfilter-knn-pred',
                options=[{'label': i, 'value': i} for i in range(1, 11)],
                value=5
            ),
            dcc.Textarea(
                id='knn-output',
                value='KNN Comparison',
                style={'width': '100%', 'height': '20%',
                       'font-family': 'Times New Roman',
                       'font-size': '22px'})
        ])], style={'width': '49%', 'display': 'inline-block',
                    'vertical-align': 'top'}),
    # bottom panel
    html.Div([
        html.H2(children='Select Another Component'),
        dcc.Dropdown(
            id='crossfilter-pca-axis',
            options=[{'label': i, 'value': i - 1} for i in range(2, 7)],
            value=1
        ),
        html.H4(children='PCA Correlation Plot', style={'textAlign': 'center'}),
        dcc.Graph(
            id='pca-figure-with-dropdown',
            config={'autosizable': True, 'responsive': True}
        )], style={'width': '60%',
                   'display': 'inline-block'}),
    html.Div([
        html.H4(children='Scatterplot of Principal Components by Zipcode',
                style={'textAlign': 'center'}),
        dcc.Graph(
            id='scatter-with-zipcode',
            hoverData={'points': [{'hovertext': '60601'}]},
            config={'autosizable': True, 'responsive': True},
        )], style={'width': '39%', 'display': 'inline-block'})
])


@app.callback(
    Output('var_time_series', 'figure'),
    [Input('crossfilter-zipcode-ts', 'value'),
     Input('crossfilter-var-ts', 'value'),
     Input('week-slider', 'value')])


def update_var_timeseries(zipcode, var, week):
    '''
    Update the time series figure by user's input

    Inputs:
      zipcode (int): zip code represented as integer
      var (str): the name of variable of interest
      week (tuple): a tuple of the start and the end week

    Output:
      fig_ts: a figure of time series data
    '''
    week_start, week_end = week
    df_ts = database_ts.loc[(database_ts['week_number'] <= week_end) & \
                            (database_ts['week_number'] >= week_start), :]
    mask = df_ts.index == zipcode
    df_ts = df_ts[mask]
    fig_ts = px.line(df_ts, x='week_end', y=var)
    fig_ts.update_xaxes(title_text='Time')
    return fig_ts


@app.callback(
    dash.dependencies.Output('prediction-fig', 'figure'),
    [dash.dependencies.Input('crossfilter-zipcode-ts', 'value'),
     dash.dependencies.Input('crossfilter-var-pred', 'value')])


def update_prediction_fig(zipcode, var):
    '''
    Update the prediction figure by user's input

    Inputs:
      zipcode (int): zip code represented as integer
      var (str): the name of variable of interest

    Output:
      fig_pred: a figure of prediction bar chart
    '''
    pred = dm.predict_outcome(database_cross, var)
    pred_zipcode = pred[pred.index == zipcode]
    fig_pred = px.bar(x=pred.columns, y=pred_zipcode.iloc[0, :],
                      color=pred.columns,
                      labels=dict(x = 'Majority Race', y = var,
                                  color = 'Majority Race'),
                      height=350)
    return fig_pred


@app.callback(
    dash.dependencies.Output('knn-output', 'value'),
    [dash.dependencies.Input('crossfilter-zipcode-ts', 'value'),
     dash.dependencies.Input('crossfilter-knn-pred', 'value'),
     dash.dependencies.Input('crossfilter-var-pred', 'value')])


def update_knn_output(zipcode, k, var):
    '''
    Update the KNN result by user's input

    Inputs:
      zipcode (int): zip code represented as integer
      k (int): the parameter k
      var (str): the name of variable of interest

    Output:
      result (str): a string of result of knn prediction
    '''
    result_dict = da.compare_to_neighbors(zipcode, k, var)
    result = ('''The value on variable {} from Zip code {} is {}''' + \
             ''' that from its {} nearest neighbors.
             ''').format(var, zipcode,
                         result_dict[var]['value']['result'], k)
    return result


def update_pca_cor(axis):
    '''
    Update PCA correlation plot by user's input

    Inputs:
      axis (int): the number of another principal component

    Ouput:
      fig_pca: a figure of pca correlation plot
    '''
    best_var = dm.best_represented(loadings)
    loading_filtered = loadings.loc[:, best_var]

    fig_pca = px.scatter(x=loading_filtered.loc[0, ],
                         y=loading_filtered.loc[axis, ],
                         size_max=0.5, hover_name=best_var,
                         height=500)
    fig_pca.update_xaxes(title_text='Loadings on Principal Component 1')
    fig_pca.update_yaxes(title_text='Loadings on Principal Component ' + \
                            str(axis + 1))

    for i, var in enumerate(best_var):
        fig_pca.add_shape(
            type='line', line={"width": 0.5},
            x0=0, y0=0,
            x1=loading_filtered.iloc[0, i],
            y1=loading_filtered.iloc[axis, i]
        )
        fig_pca.add_annotation(
            x=loading_filtered.iloc[0, i],
            y=loading_filtered.iloc[axis, i],
            ax=0, ay=0,
            xanchor="center",
            yanchor="bottom",
            text=var, font={"size": 7}
        )
    return fig_pca


def update_pca_scatter(axis, zipcode):
    '''
    Update PCA scatterplot by user's input

    Input:
      axis (int): the number of another principal component
      zipcode (int): the zipcode

    Output:
      fig_zip: a figure of scatterplot by zip code
    '''
    x_name = 'principal_component1'
    y_name = ('principal_component' + str(axis + 1))
    fig_zip = px.scatter(full_df, x=x_name,
                         y=y_name,
                         hover_name=full_df.index, height=400)
    fig_zip.update_xaxes(title_text='Principal Component 1')
    fig_zip.update_yaxes(title_text='Principal Component ' + str(axis + 1))

    zip_df = full_df.loc[zipcode, [x_name, y_name]]
    fig_zip.add_scatter(x = [zip_df[0]], y = [zip_df[1]], mode="markers",
                        marker=dict(size=5, color="red"),
                        name=str(zipcode))

    return fig_zip


@app.callback(
    dash.dependencies.Output('pca-figure-with-dropdown', 'figure'),
    dash.dependencies.Output('scatter-with-zipcode', 'figure'),
    dash.dependencies.Input('crossfilter-pca-axis', 'value'),
    dash.dependencies.Input('crossfilter-zipcode-ts', 'value'))


def update_figure(axis, zipcode):
    '''
    Update two PCA figures by user's input

    Input:
      axis (int): the number of another principal component
      zipcode (int): the zipcode

    Output:
      fig_pca, fig_zip: figures of PCA correlation plots and PCA scatterplot
    '''
    fig_pca = update_pca_cor(axis)
    fig_zip = update_pca_scatter(axis, zipcode)

    return fig_pca, fig_zip


if __name__ == '__main__':
    app.run_server(debug=True)