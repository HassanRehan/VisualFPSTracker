import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from plotly.offline import plot
import webbrowser
from datetime import datetime
import os
import colorsys

# Read the Excel file
df = pd.read_excel("merged_data.xlsx")

# Read the CSV file with the new format
session_df = pd.read_csv("session_data.csv")

# Convert the session data to an HTML table
session_html_table = session_df.drop(columns=['Date', 'Time']).to_html(index=False, classes='styled-table')

# Plot 1: Grenade heatmap
df_2dhist = pd.DataFrame({
    x_label: grp['Tactical Grenade'].value_counts()
    for x_label, grp in df.groupby('Lethal Grenade')
})
heatmap = go.Heatmap(z=df_2dhist.values, x=df_2dhist.columns, y=df_2dhist.index, colorscale='Teal')
fig1 = go.Figure(data=[heatmap])
fig1.update_layout(title='Grenade Usage Heatmap Over Time', xaxis_title='Lethal Grenade', yaxis_title='Tactical Grenade')

# Plot 2: Scatter plot for killcam status
fig2 = make_subplots()
df_sorted = df.sort_values('Elapsed Time (s)', ascending=True)
for series_name, series in df_sorted.groupby('Killcam Status'):
    fig2.add_trace(go.Scatter(x=series['Elapsed Time (s)'], y=series['Killcam Status'], mode='markers', name=series_name))
fig2.update_layout(title='Killcam Status Over Time', xaxis_title='Elapsed Time (s)', yaxis_title='Killcam Status')

# Plot 3: Bar plot for gun name
gun_counts = df['Weapon'].value_counts()
# Define a list of colors for each unique weapon
unique_weapons = gun_counts.index
def pastel_color(index, total):
    hue = index / total
    lightness = 0.8
    saturation = 0.5
    rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
    return '#%02x%02x%02x' % (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

colors = [pastel_color(i, len(unique_weapons)) for i in range(len(unique_weapons))]
bar_gun = go.Bar(
    x=gun_counts.values,
    y=gun_counts.index,
    orientation='h',
    marker=dict(color=colors)
)
fig3 = go.Figure(data=[bar_gun])
fig3.update_layout(title='Weapon Total Time', xaxis_title='Elapsed Time (s)', yaxis_title='Weapon')

# Plot 4: Line plot for bullet count over time
line_bullet = go.Scatter(x=df['Elapsed Time (s)'], y=df['Bullet Count'], mode='lines', name='Bullet Count')
fig4 = go.Figure(data=[line_bullet])
fig4.update_layout(title='Bullet Count Over Time', xaxis_title='Elapsed Time (s)', yaxis_title='Bullet Count', showlegend=True)

# Plot 5: Bar plot for enemy in sight grouped by size
enemy_in_sight_grouped_counts = df.groupby('Enemy in Sight').size()
colors = ['#ff6961', '#77dd77']  # Pastel green and pastel red
bar_enemy_in_sight_grouped = go.Bar(
    x=enemy_in_sight_grouped_counts.values,
    y=enemy_in_sight_grouped_counts.index,
    orientation='h',
    marker=dict(color=colors)
)
fig5 = go.Figure(data=[bar_enemy_in_sight_grouped])
fig5.update_layout(title='Enemy in Sight Breakdown', xaxis_title='Elapsed Time (s)', yaxis_title='Enemy in Sight')

# Plot 6: Line plot for player score and enemy score over time
line_player_score = go.Scatter(x=df['Elapsed Time (s)'], y=df['Player Score'], mode='lines', name='Player Score')
line_enemy_score = go.Scatter(x=df['Elapsed Time (s)'], y=df['Enemy Score'], mode='lines', name='Enemy Score')
fig6 = go.Figure(data=[line_player_score, line_enemy_score])
fig6.update_layout(title='Player and Enemy Score Over Time', xaxis_title='Elapsed Time (s)', yaxis_title='Score')

# Generate HTML for each plot
plot(fig1, filename='plots/plot1.html', auto_open=False, include_plotlyjs=True)
plot(fig2, filename='plots/plot2.html', auto_open=False, include_plotlyjs=False)
plot(fig3, filename='plots/plot3.html', auto_open=False, include_plotlyjs=False)
plot(fig4, filename='plots/plot4.html', auto_open=False, include_plotlyjs=False)
plot(fig5, filename='plots/plot5.html', auto_open=False, include_plotlyjs=False)
plot(fig6, filename='plots/plot6.html', auto_open=False, include_plotlyjs=False)

# Combine all HTML files into one with a grid layout

# Extract the date and time from the session_df
session_date = session_df['Date'].iloc[0]
session_time = session_df['Time'].iloc[0]
human_readable_timestamp = f'{session_date} - {session_time}'

# Create a safe version of the timestamp for the filename
safe_timestamp = human_readable_timestamp.replace(':', '-').replace(' ', '_')

# Create the filename with the timestamp
filename = f'playhistory/data_{safe_timestamp}.html'
absolute_filename = os.path.abspath(filename)

with open(absolute_filename, 'w', encoding='utf-8') as outfile:
    outfile.write('<html><head><title>Combined Plots</title><style>')
    outfile.write('.grid-container { display: grid; grid-template-columns: auto auto; gap: 10px; }')
    outfile.write('.grid-item { padding: 10px; }')
    outfile.write('.styled-table { border-collapse: collapse; margin: 25px 0; font-size: 0.9em; font-family: sans-serif; min-width: 400px; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15); }')
    outfile.write('.styled-table thead tr { background-color: #333; color: #ffffff; text-align: left; }')
    outfile.write('.styled-table th, .styled-table td { padding: 12px 15px; }')
    outfile.write('.styled-table tbody tr { border-bottom: 1px solid #dddddd; }')
    outfile.write('.styled-table tbody tr:nth-of-type(even) { background-color: #f3f3f3; }')
    outfile.write('.styled-table tbody tr:last-of-type { border-bottom: 2px solid #333; }')
    outfile.write('</style></head><body>')
    
    # Write the session data table at the top with the timestamp    
    outfile.write(f'<h2 style="font-family: sans-serif; color: #333; text-align: center;">Session Data - {human_readable_timestamp}</h2>')
    outfile.write('<div style="display: flex; justify-content: center;">')
    outfile.write(session_html_table)
    outfile.write('</div>')
    
    outfile.write('<div class="grid-container">')
    for i in range(1, 7):
        with open(f'plots/plot{i}.html', encoding='utf-8') as infile:
            outfile.write('<div class="grid-item">')
            outfile.write(infile.read())
            outfile.write('</div>')
    outfile.write('</div></body></html>')

# Show combined graphs in the browser
webbrowser.open(f'file://{absolute_filename}')