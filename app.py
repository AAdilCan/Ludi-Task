import json
from datetime import timedelta, datetime
import matplotlib.pyplot as plt

import plotly
from flask import Flask, render_template
import plotly.graph_objs as go

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
@app.route('/main_page')
def company_user_table():
    users_data = load_data('users.json')
    simulations_data = load_data('simulations.json')
    company_user_count = summarize_users_by_company(users_data,simulations_data)
    return render_template('users_by_company.html',company_user_count=company_user_count)

def summarize_users_by_company(users_data, simulations_data):
    simulations = simulations_data['simulations']
    users = users_data['users']
    simulation_to_company = {sim['simulation_id']: sim['company_id'] for sim in simulations}
    company_id_to_name = {sim['company_id']: sim['company_name'] for sim in simulations}

    company_user_count = {}

    for user in users:
        simulation_id = user['simulation_id']
        company_id = simulation_to_company.get(simulation_id)

        if company_id:
            if company_id in company_user_count:
                company_user_count[company_id] += 1
            else:
                company_user_count[company_id] = 1

    company_name_user_count = {}
    for company_id, count in company_user_count.items():
        company_name = company_id_to_name.get(company_id)
        if company_name:
            company_name_user_count[company_name] = count

    return company_name_user_count

def excel_to_datetime(excel_date):
    EXCEL_DATE_ORIGIN = datetime(1899, 12, 30) #Not sure but says this on the internet
    days = int(excel_date)
    fractional_day = excel_date - days
    datetime_value = EXCEL_DATE_ORIGIN + timedelta(days=days, seconds=fractional_day * 86400)
    return datetime_value


def users_by_company_daily(users_data, simulations_data, company_name):
    simulations = simulations_data['simulations']
    users = users_data['users']

    simulation_to_company_id = {sim['simulation_id']: sim['company_id'] for sim in simulations}
    company_id_to_name = {sim['company_id']: sim['company_name'] for sim in simulations}

    company_id_for_ludi = next((company_id for company_id, name in company_id_to_name.items() if name == company_name),
                               None)

    daily_user_count = {}

    for user in users:
        company_id = simulation_to_company_id.get(user['simulation_id'])
        if company_id == company_id_for_ludi:
            signup_date = excel_to_datetime(float(user['signup_datetime']))
            date_only = signup_date.date()
            if date_only in daily_user_count:
                daily_user_count[date_only] += 1
            else:
                daily_user_count[date_only] = 1

    return daily_user_count


@app.route('/plotly')
def plotly_graph():
    daily_data = users_by_company_daily(load_data('users.json'), load_data('simulations.json'), 'Ludi Inhouse')
    dates = list(daily_data.keys())
    counts = list(daily_data.values())

    # Creating a scatter plot with lines and markers
    fig = go.Figure([go.Scatter(x=dates, y=counts, mode='markers', marker=dict(symbol='circle'))])

    # Customizing the layout
    fig.update_layout(
        title='Daily Registrations for Ludi Inhouse',
        xaxis_title='Date',
        yaxis_title='Number of Users',
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('plotly_graph.html', graphJSON=graphJSON)


def load_data(filename):
    with open(f'data/{filename}') as file:
        return json.load(file)
if __name__ == '__main__':
    app.run(debug=True, port=5001)
