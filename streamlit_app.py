import pandas as pd #pip install pandas openpyxl
import streamlit as st #pip install streamlit
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title='Auswertung HSV',
                   page_icon=":bowling:",
                   layout='wide')

#dataframe der Tabelle 'Eingabe'
def get_data_from_excel():
    df = pd.read_excel(io='/workspaces/Auswertung_HSV/HSV24_25.xlsx', sheet_name='Eingabe',
                       usecols='B:AM', header=1)
    df = df.drop(columns=['S-NR','ID','Team',])
    df=df.reset_index(drop=True)
    df=df.reindex(columns=['Name','Datum','Spieltag', 'Gegner', 'Ort', 'Modus',
                           'GES', 'Volle', 'Räumer', 'Fehler', 'SP', 'MP', 'GEGGES', 'Position',
                           'S1', 'S2', 'S3', 'S4',
                           'V1', 'V2', 'V3', 'V4',
                           'R1', 'R2', 'R3', 'R4',
                           'F1', 'F2', 'F3', 'F4',
                           'S1P', 'S2P', 'S3P', 'S4P','Wo'])
    df=df.dropna(subset=['GES'])
    return df

df=get_data_from_excel()


#Sidebar

st.sidebar.header('Nutze folgende Filter:')
name = st.sidebar.multiselect('Wähle einen Namen:',
                              options=df['Name'].unique(),
                              default=df.at[0,'Name']
                                                            )
if not name:
    name=df.at[0,'Name']

wo= st.sidebar.multiselect('Wähle H/A:',
                              options=df['Wo'].unique(),
                              default=df['Wo'].unique()
                              )
if not wo:
    wo=df['Wo'].unique()

modus= st.sidebar.multiselect('Wähle den Modus:',
                              options=df['Modus'].unique(),
                              default=df['Modus'].unique()
                              )
if not modus:
    modus=df['Modus'].unique()

df_selection = df[df['Name'].isin(name) & df['Wo'].isin(wo) & df['Modus'].isin(modus)]
df_selection=df_selection.sort_values(by='Datum')
#Datums Umformungen
df_selection['Time']=(df_selection['Datum']-pd.Timestamp("2022-01-01"))// pd.Timedelta('1D')
df_selection['Datum']=df_selection['Datum'].dt.strftime("%d/%m/%Y")

# Mainpage

st.title(':sparkles: Auswertung HSV :sparkles:')
st.markdown("##")

# TOP KPI's
average_score=int(round(df_selection['GES'].mean(),0))
average_points = 0 if df_selection['MP'].dropna().empty else int(round(df_selection['MP'].mean() * 100, 0))
average_all=int(round(df_selection['Volle'].mean(),0))
average_clearoff=int(round(df_selection['Räumer'].mean(),0))
average_faults=int(round(df_selection['Fehler'].mean(),0))
max_score=int(df_selection['GES'].max())
person=df_selection['Name'].unique().squeeze()
#Trend
m,b=np.polyfit(df_selection['Time'],df_selection['GES'],1)
m=round(m*7,2)
STABW=int(round(df_selection['GES'].std(),0))

st.header(person)
first_column, second_column = st.columns(2)
with first_column:
    st.subheader("Durchschnittliches Ergebnis")
    f"{average_score} Holz"

    st.subheader("Bestes Ergebnis")
    f"{max_score} Holz"

    st.subheader("Durchschnittliche Mannschaftspunkte")
    f"{average_points} %"

    st.subheader("Trend")
    f'{m} Holz pro Woche'

with second_column:
    st.subheader("Durchschnittliche Volle")
    f"{average_all} Holz"

    st.subheader("Durchschnittliche Räumer")
    f"{average_clearoff} Holz"

    st.subheader("Durchschnittliche Fehler")
    f"{average_faults} Fehler"

    st.subheader("Standartabweichung")
    f'± {STABW} Holz vom Durchschnitt'


st.markdown("---")

#Diagramm

fig_df=df_selection[['Gegner','GES','Volle','Räumer','Wo','Datum']]
fig_df['Schnitt']=average_score
fig_df['Gegner']=fig_df['Gegner']+' ['+ fig_df['Wo'] + '] - ' + fig_df['Datum']
fig_df['row_number']=range(1,len(fig_df)+1)

fig=go.Figure()
#Gesamtergebnis als Scatterplot
fig.add_trace(go.Scatter(
    x=fig_df['Gegner'],
    y=fig_df['GES'],
    mode='markers+text',
    text=fig_df['GES'],
    textfont_size=14,
    texttemplate='<b>%{text}</b>',
    textposition='top center',
    marker=dict(size=12,symbol='octagon-dot',color='#000',line=dict(width=2, color='#996515')),
    name='Gesamt',
    ))
fig.add_trace(go.Scatter(
    x=fig_df['Gegner'],
    y=fig_df['Schnitt'],
    mode='lines',
    line=dict(color='red', width=1, dash='dash'),
    name="Schnitt"
))

#Volle Bar
fig.add_trace(go.Bar(
    x=fig_df['Gegner'],
    y=fig_df['Volle'],
    text=fig_df['Volle'],
    name='Volle',
    marker_color='#fcc200',
    textposition='inside',
    insidetextanchor='middle',
    texttemplate='<b>%{text}</b>'
))
#Räumer Bar
fig.add_trace(go.Bar(
    x=fig_df['Gegner'],
    y=fig_df['Räumer'],
    text=fig_df['Räumer'],
    name='Räumer',
    marker_color='#fff000',
    textposition='inside',
    insidetextanchor='middle',
    texttemplate='<b>%{text}</b>'
))
fig.update_layout(
    barmode='stack',
    yaxis_title='Holz',
    margin=dict(b=20,t=50)
   )


st.plotly_chart(fig)

st.markdown("---")

#Hide streamlit style

hide_st_style= """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                <style>
                """

st.dataframe(df_selection)

st.markdown("---")

# Auswertung nach Bahnen
if df_selection[['S1','S2','S3','S4']].stack().empty: S_avg=0
else: S_avg=int(round(df_selection[['S1','S2','S3','S4']].stack().mean(), 0))
S1 = 0 if df_selection['S1'].dropna().empty else int(round(df_selection['S1'].mean(), 0))
S2 = 0 if df_selection['S2'].dropna().empty else int(round(df_selection['S2'].mean(), 0))
S3 = 0 if df_selection['S3'].dropna().empty else int(round(df_selection['S3'].mean(), 0))
S4 = 0 if df_selection['S4'].dropna().empty else int(round(df_selection['S4'].mean(), 0))

if df_selection[['V1','V2','V3','V4']].stack().empty: V_avg=0
else: V_avg=int(round(df_selection[['V1','V2','V3','V4']].stack().mean(), 0))
V1 = 0 if df_selection['V1'].dropna().empty else int(round(df_selection['V1'].mean(), 0))
V2 = 0 if df_selection['V2'].dropna().empty else int(round(df_selection['V2'].mean(), 0))
V3 = 0 if df_selection['V3'].dropna().empty else int(round(df_selection['V3'].mean(), 0))
V4 = 0 if df_selection['V4'].dropna().empty else int(round(df_selection['V4'].mean(), 0))

if df_selection[['R1','R2','R3','R4']].stack().empty: R_avg=0
else: R_avg=int(round(df_selection[['R1','R2','R3','R4']].stack().mean(), 0))
R1 = 0 if df_selection['R1'].dropna().empty else int(round(df_selection['R1'].mean(), 0))
R2 = 0 if df_selection['R2'].dropna().empty else int(round(df_selection['R2'].mean(), 0))
R3 = 0 if df_selection['R3'].dropna().empty else int(round(df_selection['R3'].mean(), 0))
R4 = 0 if df_selection['R4'].dropna().empty else int(round(df_selection['R4'].mean(), 0))

if df_selection[['F1','F2','F3','F4']].stack().empty: F_avg=0
else: F_avg=int(round(df_selection[['F1','F2','F3','F4']].stack().mean(), 0))
F1 = 0 if df_selection['F1'].dropna().empty else int(round(df_selection['F1'].mean(), 0))
F2 = 0 if df_selection['F2'].dropna().empty else int(round(df_selection['F2'].mean(), 0))
F3 = 0 if df_selection['F3'].dropna().empty else int(round(df_selection['F3'].mean(), 0))
F4 = 0 if df_selection['F4'].dropna().empty else int(round(df_selection['F4'].mean(), 0))

if df_selection[['S1P','S2P','S3P','S4P']].stack().empty: P_avg=0
else: P_avg=int(round(df_selection[['S1P','S2P','S3P','S4P']].stack().mean()*100, 0))
P1 = 0 if df_selection['S1P'].dropna().empty else int(round(df_selection['S1P'].mean()*100, 0))
P2 = 0 if df_selection['S2P'].dropna().empty else int(round(df_selection['S2P'].mean()*100, 0))
P3 = 0 if df_selection['S3P'].dropna().empty else int(round(df_selection['S3P'].mean()*100, 0))
P4 = 0 if df_selection['S4P'].dropna().empty else int(round(df_selection['S4P'].mean()*100, 0))

st.header("Auswertung nach Bahnen :bowling:")
name_column, avg_column, b1_column, b2_column, b3_column, b4_column = st.columns(6)
with name_column:
    st.subheader('')
    st.subheader("Gesamt")
    st.subheader("Volle")
    st.subheader("Räumer")
    st.subheader("Fehler")
    st.subheader("Satzpunkte")

with avg_column:
    st.subheader("Schnitt")
    st.subheader(f'{S_avg}')
    st.subheader(f'{V_avg}')
    st.subheader(f'{R_avg}')
    st.subheader(f'{F_avg}')
    st.subheader(f'{P_avg} %')

with b1_column:
    st.subheader("Bahn :one:")
    st.subheader(f'{S1}')
    st.subheader(f'{V1}')
    st.subheader(f'{R1}')
    st.subheader(f'{F1}')
    st.subheader(f'{P1} %')

with b2_column:
    st.subheader("Bahn :two:")
    st.subheader(f'{S2}')
    st.subheader(f'{V2}')
    st.subheader(f'{R2}')
    st.subheader(f'{F2}')
    st.subheader(f'{P2} %')

with b3_column:
    st.subheader("Bahn :three:")
    st.subheader(f'{S3}')
    st.subheader(f'{V3}')
    st.subheader(f'{R3}')
    st.subheader(f'{F3}')
    st.subheader(f'{P3} %')

with b4_column:
    st.subheader("Bahn :four:")
    st.subheader(f'{S4}')
    st.subheader(f'{V4}')
    st.subheader(f'{R4}')
    st.subheader(f'{F4}')
    st.subheader(f'{P4} %')

st.markdown("---")

#Rekorde---------------------------------------------------------------------------------------

#Gesamtrekord
max_GES=0 if df_selection['GES'].dropna().empty else int(round(df_selection['GES'].max(), 0))
Gegner_max_GES=df_selection.query('GES==@max_GES')['Gegner'].squeeze()
Ort_max_GES=df_selection.query('GES==@max_GES')['Ort'].squeeze()
Date_max_GES=df_selection.query('GES==@max_GES')['Datum'].squeeze()

#Vollen-Rekord
max_V=0 if df_selection['Volle'].dropna().empty else int(round(df_selection['Volle'].max(), 0))
Gegner_max_V=df_selection.query('Volle==@max_V')['Gegner'].squeeze()
Ort_max_V=df_selection.query('Volle==@max_V')['Ort'].squeeze()
Date_max_V=df_selection.query('Volle==@max_V')['Datum'].squeeze()

#Räumer-Rekord
max_R=0 if df_selection['Räumer'].dropna().empty else int(round(df_selection['Räumer'].max(), 0))
Gegner_max_R=df_selection.query('Räumer==@max_R')['Gegner'].squeeze()
Ort_max_R=df_selection.query('Räumer==@max_R')['Ort'].squeeze()
Date_max_R=df_selection.query('Räumer==@max_R')['Datum'].squeeze()

#Bahn-Rekord
col_maxes = df_selection[['S1', 'S2', 'S3', 'S4']].max()
max_B = int(round(col_maxes.max(),0))
column_with_overall_max = col_maxes.idxmax()
Gegner_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Gegner'].squeeze()
Ort_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Ort'].squeeze()
Date_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Datum'].squeeze()

st.header('Rekorde :trophy: ')

cat_column, max_column, geg_column, ort_column, date_column = st.columns(5)

with cat_column:
    st.subheader(" ")
    st.subheader("Gesamt")
    st.subheader("Volle")
    st.subheader("Räumer")
    st.subheader("Bahn")

with max_column:
    st.subheader("Ergebnis")
    st.subheader(f'{max_GES}')
    st.subheader(f'{max_V}')
    st.subheader(f'{max_R}')
    st.subheader(f'{max_B}')

with geg_column:
    st.subheader("Gegner")
    st.markdown(f"### <span style='font-size: 20px'>{Gegner_max_GES}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Gegner_max_V}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Gegner_max_R}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Gegner_max_B}</span>", unsafe_allow_html=True)


with ort_column:
    st.subheader("Ort")
    st.markdown(f"### <span style='font-size: 20px'>{Ort_max_GES}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Ort_max_V}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Ort_max_R}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Ort_max_B}</span>", unsafe_allow_html=True)

with date_column:
    st.subheader("Datum")
    st.markdown(f"### <span style='font-size: 20px'>{Date_max_GES}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Date_max_V}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Date_max_R}</span>", unsafe_allow_html=True)
    st.markdown(f"### <span style='font-size: 20px'>{Date_max_B}</span>", unsafe_allow_html=True)