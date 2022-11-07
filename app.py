import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, dcc
import pandas as pd
import numpy as np
import altair as alt

# importation des données CSV
df_medal = pd.read_csv('archive/olympic_medals.csv')
df_host = pd.read_csv('archive/olympic_hosts.csv')
df_athlete = pd.read_csv('archive/olympic_athletes.csv')
df_result = pd.read_csv('archive/olympic_results.csv')


PLOTLY_LOGO = "assets/images/earth.png"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# make a reuseable navitem for the different examples
nav_item = dbc.NavItem(dbc.NavLink("Choix du pays : ", href="#"))

# make a reuseable dropdown for the different examples
dropdown = dcc.Dropdown(
    options=[
        {'label': 'Grande Bretagne', 'value': 'GBR'},
        {'label': 'France', 'value': 'FRA'},
        {'label': 'Etats Unis', 'value': 'USA'},
        {'label': 'Japon', 'value': 'JPN'},
        {'label': 'Australie', 'value': 'AUS'},
        {'label': 'Allemagne', 'value': 'GER'},
    ],
    value='GBR',
    id='demo-dropdown',
)


# this example that adds a logo to the navbar brand
logo = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                        dbc.Col(dbc.NavbarBrand(
                            "Logo", className="ms-2", id="logo_country")),
                    ],
                    align="center",
                    className="g-0",
                ),
                href="#",
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                dbc.Nav(
                    [nav_item, dropdown],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
    ),
    color="dark",
    dark=True,
    className="mb-5",
)
row = html.Div(
    [
        dbc.Row(dbc.Col(html.Iframe(
            id='medal_per_participation',
            style={'border-width': '0', 'width': '100%', 'height': '450px'}
        ),
            width={"size": 6, "offset": 3},
            className="border rounded")),
        dbc.Row(
            [
                dbc.Col(html.Iframe(
                    id='dd-output-container',
                    style={'border-width': '0',
                        'width': '100%', 'height': '600px'}
                ),
                    md=6),
                dbc.Col(html.Iframe(
                    id='10best_athlete',
                    style={'border-width': '0',
                        'width': '100%', 'height': '600px'}
                ),
                    md=6),
            ]
        ),
    ]
)
app.layout = html.Div(
    [logo, row],
)


# we use a callback to toggle the collapse on small screens
def toggle_navbar_collapse(n, n_clicks):
    print(n_clicks)
    if n:

        return not n_clicks
    return n_clicks

# the same function (toggle_navbar_collapse) is used in all three callbacks
# Nombre de médailles gagnées par édition


@app.callback(
    Output('dd-output-container', 'srcDoc'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    code_country = value

    df_gbr = df_result.merge(
        df_host, left_on='slug_game', right_on='game_slug')

    df_gbr = df_gbr[(df_gbr.game_season == 'Summer') & (
        df_gbr.country_3_letter_code == code_country)]

    medal_per_date = df_gbr.groupby(['game_year'])[
        'medal_type'].count().reset_index()

    source = medal_per_date.from_records({
        'Année': medal_per_date['game_year'],
        'Médailles': medal_per_date['medal_type']
    })

    lines = alt.Chart(source).mark_line(point=True, color="blue").encode(
        alt.X('Année'),
        alt.Y('Médailles')).properties(
        title="Nombre de médailles gagnées par édition", width=600, height=500)

    text = lines.mark_text(
        align='center',
        baseline='middle',
        dx=0,  # décalage x
        dy=-15
    ).encode(
        text='Médailles'
    )

    return lines.to_html()

# Diagramme des 20 meilleurs athlètes


@app.callback(
    Output('10best_athlete', 'srcDoc'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    df = df_medal.merge(df_host, left_on='slug_game', right_on='game_slug')
    df = df[(df.game_season == 'Summer') & (df.country_3_letter_code == value)]
    df_medal_by_athlete = df.groupby(['athlete_full_name'])[
        'medal_type'].count().nlargest(20).reset_index(name="count")

    source = df_medal_by_athlete.from_records({
        'Athlète': df_medal_by_athlete['athlete_full_name'],
        'Médailles': df_medal_by_athlete['count']
    })
    chart4 = alt.Chart(source).mark_bar().encode(
        alt.X('Athlète', sort=None),
        alt.Y('Médailles')).properties(
        title="Diagramme des 20 meilleurs athlètes")
    return chart4.to_html()

# Change le titre par les 3 lettres du pays


@app.callback(
    Output('logo_country', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    return value

# Nombre de médailles par participation pour toutes les éditions


@app.callback(
    Output('medal_per_participation', 'srcDoc'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    df_gbr = df_result.merge(
        df_host, left_on='slug_game', right_on='game_slug')
    df_gbr = df_gbr[(df_gbr.game_season == 'Summer') &
                    (df_gbr.country_3_letter_code == value)]
    nuage = df_gbr.groupby(['game_year', 'slug_game'])[
        'country_3_letter_code', 'medal_type'].count()
    nuage.sort_values(by=['game_year'], inplace=True)
    nuage = nuage.reset_index()

    source = nuage.from_records({
        'Participants': nuage['country_3_letter_code'],
        'Médailles': nuage['medal_type'],
        'JO': nuage["slug_game"],
    })

    bar = alt.Chart(source).mark_bar().encode(
        alt.X('JO', sort=None),
        y='Participants:Q'
    ).properties(
        title="Nombre de médailles par participation pour toutes les éditions")

    bar2 = alt.Chart(source).mark_bar(color='green').encode(
        alt.X('JO', sort=None),
        y='Médailles:Q'
    )

    line = alt.Chart(source).mark_line(color='orange').transform_window(
        # The field to average
        rolling_mean='mean(Médailles)',
        # The number of values before and after the current value to include.
        frame=[-9, 0]
    ).encode(
        alt.X('JO', title='Edition JO', axis=alt.Axis(
            labelAngle=-45, labelOverlap=False), sort=None),
        y='rolling_mean:Q'
    )

    chart8 = (bar + bar2 + line).properties(width=600)
    return chart8.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)
