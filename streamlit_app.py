import pandas as pd #pip install pandas openpyxl
import streamlit as st #pip install streamlit
import plotly.express as px #pip install plotly-express
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import os

st.set_page_config(page_title='Auswertung HSV',
                   page_icon=":bowling:",
                   layout='wide')

#dataframe der Tabelle 'Eingabe'
def get_data_from_excel():
    df_24_25 = pd.read_excel(io='HSV24_25.xlsx', sheet_name='Eingabe',
                       usecols='B:AM', header=1)
    df_25_26 = pd.read_excel(io='HSV25_26.xlsx', sheet_name='Eingabe',
                       usecols='B:AM', header=1)
    df_23_24 = pd.read_excel(io='HSV23_24.xlsx', sheet_name='Eingabe',
                       usecols='B:AM', header=1)
    df_22_23 = pd.read_excel(io='HSV22_23.xlsx', sheet_name='Eingabe',
                       usecols='B:AM', header=1)
    df = pd.concat([df_22_23, df_23_24, df_24_25, df_25_26], ignore_index=True)
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


# Beispiel: Datumsspalte bereits datetime
df['Datum'] = pd.to_datetime(df['Datum'])

# Saison berechnen: 01.07.YYYY bis 30.06.YYYY+1
def get_saison(date):
    year = date.year
    if date.month >= 7:
        return f"{year}/{year+1}"
    else:
        return f"{year-1}/{year}"

df['Saison'] = df['Datum'].apply(get_saison)

tab1, tab2, tab3 = st.tabs(["Spieler Analyse", "Vergleichstabelle", "Auswertung Heimbahnen"])


with tab1:
    # Filter horizontal als erste Zeile
    col1, col2, col3 = st.columns(3)

    st.title(':sparkles: Auswertung individuell :sparkles:')
    st.markdown("##")

    with col1:
        name = st.selectbox(
            'Wähle einen Namen:',
            options=df['Name'].unique(),
            index=0  # Standardauswahl (erste Zeile)
        )

    with col2:
        wo = st.multiselect(
            "H/A:",
            options=df['Wo'].unique(),
            default=df['Wo'].unique(),
            key="tab1_wo"  # eindeutiger Schlüssel
        )
        if not wo:
            wo = df['Wo'].unique()

    with col3:
        saison = st.multiselect(
            'Wähle Saison:',
            options=df['Saison'].unique(),
            default=df['Saison'].unique(),
            key="tab1_saison"
        )
        if not saison:
            saison = df['Saison'].unique()

    df_selection = df[
        (df['Name'] == name) &
        df['Wo'].isin(wo) &
        df['Saison'].isin(saison)
    ].sort_values(by='Datum')


    #Datums Umformungen
    df_selection['Datum'] = pd.to_datetime(df_selection['Datum'], errors='coerce')
    REFERENCE_DATE = pd.Timestamp("2022-01-01")

    df_selection['Time'] = (
        df_selection['Datum'] - REFERENCE_DATE
    ).dt.days

    # Mainpage



    # TOP KPI's
    average_score=int(round(df_selection['GES'].mean(),0))
    average_points = 0 if df_selection['MP'].dropna().empty else int(round(df_selection['MP'].mean() * 100, 0))
    average_all=int(round(df_selection['Volle'].mean(),0))
    average_clearoff=int(round(df_selection['Räumer'].mean(),0))
    average_faults=int(round(df_selection['Fehler'].mean(),0))
    max_score=int(df_selection['GES'].max())
    person=df_selection['Name'].unique()
    person=str(person)
    #Trend
    m,b=np.polyfit(df_selection['Time'],df_selection['GES'],1)
    m=round(m*7,2)
    STABW=int(round(df_selection['GES'].std(),0))

    st.header(name)
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
    fig_df['Gegner'] = (
        fig_df['Gegner']
        + ' [' + fig_df['Wo'] + '] - '
        + fig_df['Datum'].dt.strftime("%d.%m.%Y")
    )
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
    df_to_display['Datum'] = df_to_display['Datum'].dt.strftime("%d.%m.%Y")
    st.dataframe(df_to_display)

    st.markdown("---")

    # Auswertung nach Bahnen
    # Gesamt Bahn
    cols_S = ['S1', 'S2', 'S3', 'S4']

    # Mittelwerte pro Spalte berechnen:
    # - NaN werden automatisch ignoriert
    # - wenn eine Spalte nur NaN enthält → wird zu 0
    # - Ergebnis wird auf ganze Zahlen gerundet
    means_S = df_selection[cols_S].mean().fillna(0).round(0).astype(int)

    S1 = means_S['S1']
    S2 = means_S['S2']
    S3 = means_S['S3']
    S4 = means_S['S4']

    # Gesamt-Durchschnitt über alle Spalten:
    # - zuerst Mittelwert je Spalte, dann Durchschnitt dieser Werte
    # - wenn alle Werte NaN sind → Ergebnis 0
    S_avg = int(round(df_selection[cols_S].mean().mean(), 0)) if df_selection[cols_S].notna().any().any() else 0

    cols_V = ['V1', 'V2', 'V3', 'V4']
    means_V=df_selection[cols_V].mean().fillna(0).round(0).astype(int)
    V1 = means_V ['V1']
    V2 = means_V['V2']
    V3 = means_V['V3']
    V4 = means_V['V4']
    V_avg=int(round(df_selection[cols_V].mean().mean(),0)) if df_selection[cols_V].notna().any().any() else 0

    cols_R = ['R1', 'R2', 'R3', 'R4']
    means_R = df_selection[cols_R].mean().fillna(0).round(0).astype(int)
    R1 = means_R['R1']
    R2 = means_R['R2']
    R3 = means_R['R3']
    R4 = means_R['R4']
    R_avg = int(round(df_selection[cols_R].mean().mean(), 0)) if df_selection[cols_R].notna().any().any() else 0

    cols_F = ['F1', 'F2', 'F3', 'F4']
    means_F = df_selection[cols_F].mean().fillna(0).round(0).astype(int)
    F1 = means_F['F1']
    F2 = means_F['F2']
    F3 = means_F['F3']
    F4 = means_F['F4']
    F_avg = int(round(df_selection[cols_F].mean().mean(), 0)) if df_selection[cols_F].notna().any().any() else 0

    cols_P = ['S1P', 'S2P', 'S3P', 'S4P']
    means_P = (df_selection[cols_P].mean() * 100).fillna(0).round(0).astype(int)
    P1 = means_P['S1P']
    P2 = means_P['S2P']
    P3 = means_P['S3P']
    P4 = means_P['S4P']
    P_avg = int(round(df_selection[cols_P].mean().mean() * 100, 0)) if df_selection[cols_P].notna().any().any() else 0

    st.header("Auswertung nach Bahnen :bowling:")

    auswertung_bahnen = pd.DataFrame({
        'Schnitt': [S_avg, V_avg, R_avg, F_avg, f"{P_avg} %"],
        'Bahn 1': [S1, V1, R1, F1, f"{P1} %"],
        'Bahn 2': [S2, V2, R2, F2, f"{P2} %"],
        'Bahn 3': [S3, V3, R3, F3, f"{P3} %"],
        'Bahn 4': [S4, V4, R4, F4, f"{P4} %"],
    }, index=['Gesamt', 'Volle', 'Räumer', 'Fehler', 'Satzpunkte'])

    st.dataframe(auswertung_bahnen)

    st.markdown("---")

    #Rekorde---------------------------------------------------------------------------------------

    #Gesamtrekord
    max_GES=0 if df_selection['GES'].dropna().empty else int(round(df_selection['GES'].max(), 0))
    Gegner_max_GES=df_selection.query('GES==@max_GES')['Gegner'].iloc[0]
    Ort_max_GES=df_selection.query('GES==@max_GES')['Ort'].iloc[0]
    Date_max_GES=df_selection.query('GES==@max_GES')['Datum'].iloc[0]
    Date_max_GES = Date_max_GES.strftime("%d.%m.%Y")

    #Vollen-Rekord
    max_V=0 if df_selection['Volle'].dropna().empty else int(round(df_selection['Volle'].max(), 0))
    Gegner_max_V=df_selection.query('Volle==@max_V')['Gegner'].iloc[0]
    Ort_max_V=df_selection.query('Volle==@max_V')['Ort'].iloc[0]
    Date_max_V=df_selection.query('Volle==@max_V')['Datum'].iloc[0]
    Date_max_V = Date_max_V.strftime("%d.%m.%Y")

    #Räumer-Rekord
    max_R=0 if df_selection['Räumer'].dropna().empty else int(round(df_selection['Räumer'].max(), 0))
    Gegner_max_R=df_selection.query('Räumer==@max_R')['Gegner'].iloc[0]
    Ort_max_R=df_selection.query('Räumer==@max_R')['Ort'].iloc[0]
    Date_max_R=df_selection.query('Räumer==@max_R')['Datum'].iloc[0]
    Date_max_R= Date_max_R.strftime("%d.%m.%Y")

    #Bahn-Rekord
    col_maxes = df_selection[['S1', 'S2', 'S3', 'S4']].max()
    max_B = int(round(col_maxes.max(),0))
    column_with_overall_max = col_maxes.idxmax()
    Gegner_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Gegner'].iloc[0]
    Ort_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Ort'].iloc[0]
    Date_max_B=df_selection.loc[df_selection[column_with_overall_max] == max_B, 'Datum'].iloc[0]
    Date_max_B = Date_max_B.strftime("%d.%m.%Y")

    st.header('Rekorde :trophy: ')

    rekorde = pd.DataFrame({
        'Ergebnis': [max_GES, max_V, max_R, max_B],
        'Gegner': [str(Gegner_max_GES), str(Gegner_max_V), str(Gegner_max_R), str(Gegner_max_B)],
        'Ort': [str(Ort_max_GES), str(Ort_max_V), str(Ort_max_R), str(Ort_max_B)],
        'Datum': [str(Date_max_GES), str(Date_max_V), str(Date_max_R), str(Date_max_B)],
    }, index=['Gesamt', 'Volle', 'Räumer', 'Bahn'])


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
    st.markdown("---")

    # Volle - Räumer - Verhältnis------------------------------------------------------------

    st.header(' :chart_with_upwards_trend: Volle-Räumer-Verhältnis :chart_with_downwards_trend: ')

    x_min, x_max = 200, 450
    y_min, y_max = 50, 250

    fig = px.scatter(
        df_selection,
        x='Volle',
        y='Räumer',
        symbol_sequence=['x'],  # Kreuze
        title='Volle vs. Räumer'
    )

    # Gelbe Linie y = 2x, innerhalb der Achsenlimits
    fig.add_shape(
        type="line",
        x0=x_min,
        y0=max(y_min, 0.5 * x_min),  # nicht unter y_min
        x1=x_max,
        y1=min(y_max, 0.5 * x_max),  # nicht über y_max
        line=dict(color="gold", dash="dash", width=2)
    )

    # Achsenlimits
    fig.update_xaxes(range=[x_min, x_max])
    fig.update_yaxes(range=[y_min, y_max])

    st.plotly_chart(fig)
    st.text('Die gelbe Gerade zeigt das Verhältnis 2:1 an - also doppelt so viele Volle wie Räumer.' )
    st.text('Liegen die Punkte über der Geraden bist du in den Räumern besser. Liegen die Punkte darunter, laufen die Vollen besser.')

with tab2:
    st.title(':sparkles: Auswertung Vergleich :sparkles:')
    st.markdown("##")

    # Filter horizontal als erste Zeile
    col1, col2, col3,col4 = st.columns(4)

    with col1:
        wo_filter = st.multiselect(
        "H/A:",
        options=df['Wo'].unique(),
        default=df['Wo'].unique(),
        key="tab2_wo"  # eindeutiger Schlüssel
        )
    with col2:
        saison_filter = st.multiselect(
        "Wähle Saison:",
        options=df['Saison'].unique(),
        default=df['Saison'].unique(),
        key="tab2_saison"
        )
    with col3:
        metric1 = st.selectbox(
            "Wähle die Spalte für Vergleich:",
            options=['GES', 'Fehler', 'Volle','MP','SP'],
            key="metric1"
        )
    with col4:
        metric2 = st.selectbox(
            "Wähle die Spalte für Vergleich:",
            options=['GES', 'Fehler', 'Volle', 'MP', 'SP'],
            key="metric2"
        )
    df_filtered = df[
        df['Wo'].isin(wo_filter) &
        df['Saison'].isin(saison_filter)
    ]
    df_compare1 = df_filtered.groupby('Name')[metric1].agg(
        Anzahl_Spiele='count',
        Mittelwert='mean',
        Standardabweichung='std',
        Minimum='min',
        Maximum='max'
    ).reset_index()
    df_compare2 = df_filtered.groupby('Name')[metric2].agg(
        Anzahl_Spiele='count',
        Mittelwert='mean',
        Standardabweichung='std',
        Minimum='min',
        Maximum='max'
    ).reset_index()



    df_compare1 = df_compare1.sort_values(by='Mittelwert', ascending=False)
    df_compare2 = df_compare2.sort_values(by='Mittelwert', ascending=False)

    Col1, Col2 = st.columns(2)
    with Col1:
        st.dataframe(df_compare1)
    with Col2:
        st.dataframe(df_compare2)



with tab3:
    st.title(':house_with_garden: Auswertung Heimbahnen :house_with_garden:')
    st.markdown("##")


    # Daten von den Scoresheets laden
    @st.cache_data
    def load_scoresheets():
        return pd.read_parquet("Scorsheets_Hirschfeld.parquet")


    scoresheets_df = load_scoresheets()
    scoresheets_df["Datum"] = pd.to_datetime(scoresheets_df.iloc[:, 0], errors="coerce")
    scoresheets_df["Jahr"] = scoresheets_df["Datum"].dt.year
    scoresheets_df=scoresheets_df.drop(scoresheets_df.columns[[1,2]],axis=1)

    # Filter horizontal als erste Zeile
    col1, col2 = st.columns(2)

    # Annahme: erste Spalte enthält das Jahr (oder wurde bereits extrahiert)
    #Namensfilter
    with col1:
        names = scoresheets_df.iloc[:, 1].dropna().unique()
        selected_name = st.selectbox("Name wählen", sorted(names))

    # Nach Name filtern
    filtered_scoresheets_df = scoresheets_df[
        scoresheets_df.iloc[:, 1] == selected_name
        ]

    # Jahres-Filter (Spalte 2)
    with col2:
        min_year = int(filtered_scoresheets_df["Jahr"].min())
        max_year = int(filtered_scoresheets_df["Jahr"].max())

        if min_year == max_year:
            st.info(f"Nur ein Jahr vorhanden: {min_year}")
            year_range = (min_year, max_year)
        else:
            year_range = st.slider(
                "Wähle Jahr(e)",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )

    # Nach Jahr filtern
    final_df = filtered_scoresheets_df[
        (filtered_scoresheets_df["Jahr"] >= year_range[0]) &
        (filtered_scoresheets_df["Jahr"] <= year_range[1])
    ]
    no_games=(final_df.iloc[:,2]==120).sum()

    st.write(f"Du hast in der Zeitspanne {no_games} aufgezeichnete Spiele gespielt")

    st.header(" :clipboard: Auswertung Hirschelder Bahnen :clipboard: ")
    Rows = []

    for bahn in range (4):
        volle_hb=final_df[(final_df.iloc[:,7]==0) & (final_df.iloc[:,9]==bahn)].iloc[:,12].mean()
        räumer_hb = final_df[(final_df.iloc[:, 7] == 1) & (final_df.iloc[:, 9] == bahn)].iloc[:, 12].mean()
        gesamt_hb = volle_hb+räumer_hb
        fehler_hb = final_df[final_df.iloc[:, 9] == bahn].iloc[:, 13].mean()
        max_volle_hb=final_df[(final_df.iloc[:,7]==0) & (final_df.iloc[:,9]==bahn)].iloc[:,12].max()
        min_volle_hb = final_df[(final_df.iloc[:, 7] == 0) & (final_df.iloc[:, 9] == bahn)].iloc[:, 12].min()
        max_räumer_hb = final_df[(final_df.iloc[:, 7] == 1) & (final_df.iloc[:, 9] == bahn)].iloc[:, 12].max()
        min_räumer_hb = final_df[(final_df.iloc[:, 7] == 1) & (final_df.iloc[:, 9] == bahn)].iloc[:, 12].min()
        max_fehler_hb = final_df[final_df.iloc[:, 9] == bahn].iloc[:, 13].max()
        min_fehler_hb = final_df[final_df.iloc[:, 9] == bahn].iloc[:, 13].min()
        max_ges_hb = (final_df.loc[(final_df.iloc[:, 3] == 15) & (final_df.iloc[:,9]==bahn)].iloc[:, 12]
                      .reset_index(drop=True).groupby(lambda i: i // 2).sum().max())
        min_ges_hb = (final_df.loc[(final_df.iloc[:, 3] == 15) & (final_df.iloc[:,9]==bahn)].iloc[:, 12]
                      .reset_index(drop=True).groupby(lambda i: i // 2).sum().min())

        Rows.append([bahn, round(volle_hb, 2), round(räumer_hb, 2), round(gesamt_hb, 2), round(fehler_hb, 2),
                     round(max_volle_hb, 0), round(min_volle_hb, 0),  round(max_räumer_hb, 0), round(min_räumer_hb,0),
                     round(max_fehler_hb, 0), round(min_fehler_hb, 0), round(max_ges_hb, 0), round(min_ges_hb, 0)])
    Bahnen_df = pd.DataFrame(Rows, columns=[
        "Bahn", "Volle", "Räumer", "Gesamt", "Fehler",
        "Max. Volle", "Min. Volle",
        "Max. Räumer", "Min. Räumer",
        "Max. Fehler", "Min. Fehler",
        "Max. Gesamt", "Min. Gesamt"
    ])

    Bahnen_df["Bahn"] = Bahnen_df["Bahn"] + 1

    num_cols = 4

    rows_bahn = [
        Bahnen_df.iloc[i:i + num_cols]
        for i in range(0, len(Bahnen_df), num_cols)
    ]

    for row_group in rows_bahn:
        cols = st.columns(len(row_group))

        for col, (_, row) in zip(cols, row_group.iterrows()):
            with col:
                html = f"""
    <div style="background-color:#111827;
                padding:16px;
                border-radius:14px;
                text-align:center;
                color:white;
                box-shadow:0 6px 14px rgba(0,0,0,0.4);">

    <h3>Bahn {int(row['Bahn'])}</h3>

    <p>Volle: {row['Volle']:.2f}</p>
    <p style="font-size:12px;color:#9ca3af;">
    Max: {row['Max. Volle']:.2f} | Min: {row['Min. Volle']:.2f}
    </p>

    <p>Räumer: {row['Räumer']:.2f}</p>
    <p style="font-size:12px;color:#9ca3af;">
    Max: {row['Max. Räumer']:.2f} | Min: {row['Min. Räumer']:.2f}
    </p>

    <p style="font-size:24px;font-weight:bold;color:#4ade80;">
    Gesamt: {row['Gesamt']:.2f}
    </p>
    <p style="font-size:12px;color:#9ca3af;">
    Max: {row['Max. Gesamt']:.2f} | Min: {row['Min. Gesamt']:.2f}
    </p>

    <p style="color:#f87171;">
    Fehler: {row['Fehler']:.2f}
    </p>
    <p style="font-size:12px;color:#9ca3af;">
    Max: {row['Max. Fehler']:.2f} | Min: {row['Min. Fehler']:.2f}
    </p>

    </div>
    """
                st.markdown(html, unsafe_allow_html=True)

    st.header(" :microscope: Durchschnittlicher Wurfertrag pro Spiel :microscope:")
    st.text("Gibt an, wie oft du im Schnitt welche Kegelanzahl getroffen hast.")
    st.text("Beispiel: Steht bei - Volle 5 - eine 12.34 spielst du im Schnitt pro Spiel 12 mal eine 5 in die Vollen.")
    rows = []

    for wurf in range(10):
        volle_val = ((final_df.iloc[:, 7] == 0) & (final_df.iloc[:, 4] == wurf)).sum() / no_games
        räumer_val = ((final_df.iloc[:, 7] == 1) & (final_df.iloc[:, 4] == wurf)).sum() / no_games
        gesamt_val = (final_df.iloc[:, 4] == wurf).sum() / no_games
        w16_val = ((final_df.iloc[:,3]==1) & (final_df.iloc[:,7]==1) & (final_df.iloc[:,4] == wurf)).sum() /no_games
        anwurf_val = ((final_df.iloc[:,7] == 1) & (final_df.iloc[:, 4] == wurf) & (final_df.iloc[:, 5].shift(1) == 511)).sum() / no_games

        rows.append([wurf, round(volle_val, 2), round(räumer_val, 2), round(gesamt_val, 2), round(w16_val, 2), round(anwurf_val, 2)] )

    Wurfertrag_df = pd.DataFrame(rows, columns=["Kegel getroffen", "Volle", "Räumer", "Gesamt","Wurf 16","Anwurf"])

    st.subheader("Volle (grün) und Räumer (gelb)")
    fig_vr = px.bar(Wurfertrag_df,x="Kegel getroffen",y=["Volle","Räumer"],barmode="group", text_auto=".2f",
                    color_discrete_map={"Volle":"green","Räumer":"orange"})
    fig_vr.update_traces(textposition='outside')
    fig_vr.update_xaxes(tickmode='linear', title_text="Kegel getroffen")
    fig_vr.update_yaxes(title_text="durchschnittliche Anzahl pro Spiel")
    st.plotly_chart(fig_vr, use_container_width=True)

    st.subheader("Wurf 16 (rot) und Anwurf (blau)")
    fig_a16 = px.bar(Wurfertrag_df, x="Kegel getroffen", y=["Wurf 16", "Anwurf"], barmode="group", text_auto=".2f",
                     color_discrete_map={"Wurf 16":"red","Anwurf":"blue"})
    fig_a16.update_traces(textposition='outside')
    fig_a16.update_xaxes(tickmode='linear', title_text="Kegel getroffen")
    fig_a16.update_yaxes(title_text="durchschnittliche Anzahl pro Spiel")
    st.plotly_chart(fig_a16, use_container_width=True)

    BASE_DIR=os.path.dirname(os.path.abspath(__file__))
    def get_image_path(value):
        value=int(value)
        return os.path.join(BASE_DIR, "kegelbilder", f"{value}.png")  # ggf. .jpg anpassen
    def render_image(path):
        if os.path.exists(path):
            return f'<img src="{path}" width="50">'
        return "Kein Bild"


    st.header(" :crystal_ball: Am häufigsten gespielte Bilder:crystal_ball:")

    col_b1, col_b2, col_b3 = st.columns(3)

    # --------------------
    # Volle
    # --------------------
    with col_b1:
        st.subheader("Volle")
        st.text("Das sind die 10 Bilder, welche du am häufigsten in Vollen triffst")

        top10_v = (
            final_df[final_df.iloc[:, 7] == 0]
            .iloc[:, 5]
            .value_counts()
            .head(10)
        )

        top10_v_df = top10_v.reset_index()
        top10_v_df.columns = ["Wert", "Anzahl"]
        top10_v_df["Anzahl"] = round(top10_v_df["Anzahl"] / no_games, 2)

        for _, row in top10_v_df.iterrows():
            st.write(f"{row['Anzahl']} mal pro Spiel")
            st.image(get_image_path(row["Wert"]), width=80)

    # --------------------
    # Fehler
    # --------------------
    with col_b2:
        st.subheader("Fehler")
        st.text("Das sind die 10 Bilder, wo du am häufigsten Fehler machst.")

        top10_f = (
            final_df[final_df.iloc[:, 6] == 1]
            .iloc[:, 5]
            .value_counts()
            .head(10)
        )

        top10_f_df = top10_f.reset_index()
        top10_f_df.columns = ["Wert", "Anzahl"]
        top10_f_df["Anzahl"] = round(top10_f_df["Anzahl"] / no_games, 2)

        for _, row in top10_f_df.iterrows():
            st.write(f"{row['Anzahl']} mal pro Spiel")
            st.image(get_image_path(row["Wert"]), width=80)

    # --------------------
    # Anwürfe
    # --------------------
    with col_b3:
        st.subheader("Anwürfe in den Räumern")
        st.text("Das sind die 10 Bilder, welche du am häufigsten in den Räumern anwürfst")
        mask = (
            (final_df.iloc[:, 7] == 1) &
            (final_df.iloc[:, 5].shift(1) == 511)
        )

        top10_a = (
            final_df[mask]
            .iloc[:, 5]
            .value_counts()
            .head(10)
        )

        top10_a_df = top10_a.reset_index()
        top10_a_df.columns = ["Wert", "Anzahl"]
        top10_a_df["Anzahl"] = round(top10_a_df["Anzahl"] / no_games, 2)

        for _, row in top10_a_df.iterrows():
            st.write(f"{row['Anzahl']} mal pro Spiel")
            st.image(get_image_path(row["Wert"]), width=80)

    st.header("Weitere Statistiken")
    st.subheader(":stopwatch:Zeit:stopwatch:")
    st.text(f"Schnellste Bahn: {12-final_df[(final_df.iloc[:,3]==15)&(final_df.iloc[:,7]==1)].iloc[:,15].max()/10} Minuten")
    st.text(f"Langsamste Bahn: {12-final_df[(final_df.iloc[:,3]==15)&(final_df.iloc[:,7]==1)].iloc[:,15].min()/10} Minuten")
    st.text(f"durchschnittliche Zeit pro Bahn: {round(12-final_df[(final_df.iloc[:,3]==15)&(final_df.iloc[:,7]==1)].iloc[:,15].mean()/10,2)} Minuten")

    st.subheader(" :warning: Karten :warning:")
    denominator_yellow = final_df[final_df.iloc[:, 2] == 120].iloc[:, 10].sum()

    st.text(
        f"Aller {round(no_games / denominator_yellow, 2) if denominator_yellow != 0 else '---'} Spiele bekommst du eine gelbe Karte."
    )

    denominator_red = final_df[final_df.iloc[:, 2] == 120].iloc[:, 11].sum()

    st.text(
        f"Aller {round(no_games / denominator_red, 2) if denominator_red != 0 else '---'} Spiele bekommst du eine rote Karte."
    )

    st.header(":pager: Wurfanalyse :pager:")
    Wurf=st.slider("Wähle einen Wurf", min_value=1, max_value=120,value=1)

    st.text("Die Wahrscheinlichkeit, welche Zahl du bei welchem Wurf spielst.")
    st.text("Je mehr Spiele von dir aufgezeichnet wurden, desto besser sind die Wahrscheinlichkeiten.")

    wa_list =[]
    for p in range(10):
        wa = round(((final_df.iloc[:, 2] == Wurf) & (final_df.iloc[:, 4] == p)).sum() / no_games * 100,0)
        wb_max = final_df[final_df.iloc[:,2]== Wurf].iloc[:,5].max()
        wa_list.append({
            "Wurf": p,
            "WA": wa
        })
    wa_df = pd.DataFrame(wa_list)

    fig_wa = px.bar(wa_df, x="Wurf", y="WA",text_auto=".2f")
    fig_wa.update_traces(textposition='outside')
    fig_wa.update_xaxes(tickmode='linear', title_text="Kegel getroffen")
    fig_wa.update_yaxes(title_text="Wahrscheinlichkeit in %")
    st.plotly_chart(fig_wa, use_container_width=True)



