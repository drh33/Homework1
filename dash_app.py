import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
from os import listdir, remove
import pickle
from time import sleep

from helper_functions import * # this statement imports all functions from your helper_functions file!

# Run your helper function to clear out any io files left over from old runs
# 1:
check_for_and_del_io_files()

# Make a Dash app!
app = dash.Dash(__name__)


# Define the layout.
app.layout = html.Div([

    # Section title
    html.H1("Section 1: Fetch & Display exchange rate historical data"),

    # Currency pair text input, within its own div.
    html.Div(
        [
            "Input Currency: ",
            # Your text input object goes here:
            dcc.Input(id = 'the_input', value = 'USDCAD', type = 'text')
        ],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block'}
    ),
    # Submit button:
    html.Button('Submit', id = 'submit-button', n_clicks = 0)
    ,
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id = 'the_output', children = 'Enter a currency code and press "Submit".'),
    html.Div([
        # Candlestick graph goes here:
        dcc.Graph(id='candlestick-graph')
    ]),
    # Another line break
    html.Br(),
    # Section title
    html.H1("Section 2: Make a Trade"),
    # Div to confirm what trade was made
    html.Div(id='trade-output'),
    # Radio items to select buy or sell
    dcc.RadioItems(
        id = 'Buy_Or_Sell',
        options = [{'label': 'Buy', 'value': 'Buy'}, {'label': 'Sell', 'value': 'Sell'}],
        value = 'Buy',
        labelStyle = {'display': 'inline-block'}
    )
    ,
    # Text input for the currency pair to be traded
    dcc.Input(id = 'currency-pair', value = 'USDCAD', type = 'text')
    ,
    # Numeric input for the trade amount
    dcc.Input(id = 'trade-amount', value = 'initial value', type = 'number')
    ,
    # Submit button for the trade
    html.Button('Submit', id = 'submit-trade', n_clicks = 0)

])

# Callback for what to do when submit-button is pressed
@app.callback(
    # there's more than one output here, so you have to use square brackets to pass it in as an array.
    [dash.dependencies.Output('candlestick-graph', 'figure'),
     dash.dependencies.Output('the_output', 'children')],
    dash.dependencies.Input('submit-button', 'n_clicks'),
    dash.dependencies.State('the_input', 'value')
)
def update_candlestick_graph(n_clicks, value): # n_clicks doesn't get used, we only include it for the dependency.
    # Now we're going to save the value of currency-input as a text file.
    a = open('currency_pair.txt', 'w')
    a.write(value)
    a.close()
    # Wait until ibkr_app runs the query and saves the historical prices csv
    while not os.path.isfile('currency_pair_history.csv'):
        sleep(1)
    if os.path.isfile('currency_pair_history.csv'):
        # Read in the historical prices
        b = open('currency_pair_history.csv')
        df = b.read()
        b.close()
    # Remove the file 'currency_pair_history.csv'
        os.remove('currency_pair_History.csv')
    # Make the candlestick figure
        fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df['date'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close']
         )])
    # Give the candlestick figure a title
        html.H1("Currency Candlestick Graph")
    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
        return ('Submitted query for ' + value), fig

# Callback for what to do when trade-button is pressed
@app.callback(
    dash.dependencies.Output('trade-output', 'children'),
    dash.dependencies.Input('submit-trade', 'n_clicks'),
    dash.dependencies.State('currency-pair', 'value'),
    dash.dependencies.State('trade-amount', 'value'),
    # We DON'T want to start executing trades just because n_clicks was initialized to 0!!!
    prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt): # Still don't use n_clicks, but we need the dependency

    # Make the message that we want to send back to trade-output
    msg = 'You {} {} {}.'.format(
        action,
        trade_amt,
        trade_currency
    )
    # Make our trade_order object -- a DICTIONARY.
    trade_order = {
        'action': action,
        'trade_currency': trade_currency,
        'trade_amt': trade_amt
    }

    # Dump trade_order as a pickle object to a file connection opened with write-in-binary ("wb") permission:
    pickle.dump(trade_order, open("trade_order.p", "wb"))

    # Return the message, which goes to the trade-output div's "children" attribute.
    return msg

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
