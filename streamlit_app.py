import pandas as pd #pip install pandas openpyxl
import streamlit as st #pip install streamlit
import plotly.express as px #pip install plotly-express
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title='Auswertung HSV',
                   page_icon=":bowling:",
                   layout='wide')

#dataframe der Tabelle 'Eingabe'
def get_data_from_excel():
    df = pd.read_excel(io='HSV24_25.xlsx', sheet_name='Eingabe',
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

fig_df=df_selection[['Gegner','GES','Volle','Räumer','Wo','Datum','Time']]
fig_df=fig_df.sort_values(by='Time', ascending=False)
fig_df['Schnitt']=average_score
fig_df['Gegner']=fig_df['Gegner']+' ['+ fig_df['Wo'] + '] - ' + fig_df['Datum']
fig_df['row_number']=range(1,len(fig_df)+1)

fig=go.Figure()
#Gesamtergebnis als Scatterplot
fig.add_trace(go.Scatter(
    y=fig_df['Gegner'],
    x=fig_df['GES'],
    mode='markers+text',
    text=fig_df['GES'],
    textfont_size=16,
    texttemplate='<b>%{text}</b>',
    textposition='middle right',
    marker=dict(size=12,symbol='octagon-dot',color='#000',line=dict(width=2, color='#996515')),
    name='Gesamt',
    ))
fig.add_trace(go.Scatter(
    y=fig_df['Gegner'],
    x=fig_df['Schnitt'],
    mode='lines',
    line=dict(color='red', width=1),
    name="Schnitt"
))

#Volle Bar
fig.add_trace(go.Bar(
    y=fig_df['Gegner'],
    x=fig_df['Volle'],
    text=fig_df['Volle'],
    name='Volle',
    marker_color='#fcc200',
    textposition='inside',
    insidetextanchor='end',
    texttemplate='<b>%{text}</b>',
    orientation='h',
    marker=dict(
        line=dict(
            color='black',
            width=2
        )
    )
))
#Räumer Bar
fig.add_trace(go.Bar(
    y=fig_df['Gegner'],
    x=fig_df['Räumer'],
    text=fig_df['Räumer'],
    name='Räumer',
    marker_color='#fff000',
    textposition='inside',
    insidetextanchor='start',
    texttemplate='<b>%{text}</b>',
    orientation='h',
    marker=dict(
        line=dict(
            color='black',
            width=2
        )
    )
))
fig.update_layout(
    barmode='stack',
    xaxis_title='Holz',
    margin=dict(t=10, b=10),
    xaxis=dict(range=(250,650),showgrid=True),
    height=600,
    bargap=0.2,
    autosize=True,

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

df_to_display=df_selection.iloc[:, :-2]
st.dataframe(df_to_display)

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

auswertung_bahnen=pd.DataFrame(index=range(5), columns=range(5))
auswertung_bahnen.index=['Gesamt', 'Volle', 'Räumer', 'Fehler', 'Satzpunkte']
auswertung_bahnen.columns=['Schnitt', 'Bahn 1', 'Bahn 2', 'Bahn 3', 'Bahn 4']

auswertung_bahnen.loc['Gesamt','Schnitt']=S_avg
auswertung_bahnen.loc['Gesamt','Bahn 1']=S1
auswertung_bahnen.loc['Gesamt','Bahn 2']=S2
auswertung_bahnen.loc['Gesamt','Bahn 3']=S3
auswertung_bahnen.loc['Gesamt','Bahn 4']=S4
auswertung_bahnen.loc['Volle','Schnitt']=V_avg
auswertung_bahnen.loc['Volle','Bahn 1']=V1
auswertung_bahnen.loc['Volle','Bahn 2']=V2
auswertung_bahnen.loc['Volle','Bahn 3']=V3
auswertung_bahnen.loc['Volle','Bahn 4']=V4
auswertung_bahnen.loc['Räumer','Schnitt']=R_avg
auswertung_bahnen.loc['Räumer','Bahn 1']=R1
auswertung_bahnen.loc['Räumer','Bahn 2']=R2
auswertung_bahnen.loc['Räumer','Bahn 3']=R3
auswertung_bahnen.loc['Räumer','Bahn 4']=R4
auswertung_bahnen.loc['Fehler','Schnitt']=F_avg
auswertung_bahnen.loc['Fehler','Bahn 1']=F1
auswertung_bahnen.loc['Fehler','Bahn 2']=F2
auswertung_bahnen.loc['Fehler','Bahn 3']=F3
auswertung_bahnen.loc['Fehler','Bahn 4']=F4
auswertung_bahnen.loc['Satzpunkte','Schnitt']=str(P_avg) + ' %'
auswertung_bahnen.loc['Satzpunkte','Bahn 1']=str(P1) + ' %'
auswertung_bahnen.loc['Satzpunkte','Bahn 2']=str(P2) + ' %'
auswertung_bahnen.loc['Satzpunkte','Bahn 3']=str(P3) + ' %'
auswertung_bahnen.loc['Satzpunkte','Bahn 4']=str(P4) + ' %'

st.dataframe(auswertung_bahnen)

st.markdown("---")

#Rekorde---------------------------------------------------------------------------------------

#Gesamtrekord
max_GES=0 if df_selection['GES'].dropna().empty else int(round(df_selection['GES'].max(), 0))
Gegner_max_GES=df_selection.query('GES==@max_GES')['Gegner'].iloc[0]
Ort_max_GES=df_selection.query('GES==@max_GES')['Ort'].iloc[0]
Date_max_GES=df_selection.query('GES==@max_GES')['Datum'].iloc[0]

#Vollen-Rekord
max_V=0 if df_selection['Volle'].dropna().empty else int(round(df_selection['Volle'].max(), 0))
Gegner_max_V=df_selection.query('Volle==@max_V')['Gegner'].iloc[0]
Ort_max_V=df_selection.query('Volle==@max_V')['Ort'].iloc[0]
Date_max_V=df_selection.query('Volle==@max_V')['Datum'].iloc[0]

#Räumer-Rekord
max_R=0 if df_selection['Räumer'].dropna().empty else int(round(df_selection['Räumer'].max(), 0))
Gegner_max_R=df_selection.query('Räumer==@max_R')['Gegner'].iloc[0]
Ort_max_R=df_selection.query('Räumer==@max_R')['Ort'].iloc[0]
Date_max_R=df_selection.query('Räumer==@max_R')['Datum'].iloc[0]

#Bahn-Rekord
col_maxes = df_selection[['S1', 'S2', 'S3', 'S4']].max()
max_B = int(round(col_maxes.max(),0))
column_with_overall_max = col_maxes.idxmax()
Gegner_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Gegner'].iloc[0]
Ort_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Ort'].iloc[0]
Date_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Datum'].iloc[0]

st.header('Rekorde :trophy: ')

rekorde=pd.DataFrame(index=range(4), columns=range(4))
rekorde.index=['Gesamt', 'Volle', 'Räumer', 'Bahn']
rekorde.columns=['Ergebnis', 'Gegner', 'Ort', 'Datum']

rekorde.loc['Gesamt','Ergebnis']=max_GES
rekorde.loc['Gesamt','Gegner']=str(Gegner_max_GES)
rekorde.loc['Gesamt','Ort']=str(Ort_max_GES)
rekorde.loc['Gesamt','Datum']=str(Date_max_GES)

rekorde.loc['Volle','Ergebnis']=max_V
rekorde.loc['Volle','Gegner']=str(Gegner_max_V)
rekorde.loc['Volle','Ort']=str(Ort_max_V)
rekorde.loc['Volle','Datum']=str(Date_max_V)

rekorde.loc['Räumer','Ergebnis']=max_R
rekorde.loc['Räumer','Gegner']=str(Gegner_max_R)
rekorde.loc['Räumer','Ort']=str(Ort_max_R)
rekorde.loc['Räumer','Datum']=str(Date_max_R)

rekorde.loc['Bahn','Ergebnis']=max_B
rekorde.loc['Bahn','Gegner']=str(Gegner_max_B)
rekorde.loc['Bahn','Ort']=str(Ort_max_B)
rekorde.loc['Bahn','Datum']=str(Date_max_B)



st.dataframe(rekorde)
st.markdown("---")


#Positionen------------------------------------------------------------

st.header('Position :game_die: ')

position=pd.DataFrame(index=range(2), columns=range(6))
position.index=['Anzahl', 'Gewinnrate in %']
position.columns=[1,2,3,4,5,6]

for i in range(6):
    value_counts=(df_selection['Position']==i+1).sum()
    position.loc['Anzahl',i+1]=value_counts
    position_df=df_selection[df_selection['Position']==i+1][['Datum','MP']]
    win_rate=position_df['MP'].mean()
    position.loc['Gewinnrate in %',i+1]=win_rate*100

st.dataframe(position)
