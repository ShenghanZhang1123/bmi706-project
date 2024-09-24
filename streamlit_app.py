import streamlit as st
import pandas as pd
import altair as alt


# Load your dataset here (replace with your file path)
@st.cache
def load_data():
    # Simulating a dataframe similar to the one you shared in the image
    df = pd.DataFrame({
        'BMI': [27.9, 23.4, 31.1, 22.7, 30.4, 35.6, 28.9],
        'Gender': [1, 2, 1, 2, 1, 2, 1],
        'Race': [3, 1, 4, 2, 3, 5, 3],
        'Age': [45, 34, 67, 29, 50, 40, 52],
        'Income Ratio': [1.5, 2.0, 4.5, 3.2, 1.9, 0.8, 2.4],
        'LDL': [120, 130, 110, 100, 140, 150, 125],
        'Blood Pressure': [120, 110, 130, 115, 125, 135, 128],
        'Diabetes': [1, 2, 2, 1, 2, 1, 2]
    })
    return df


df = load_data()

# Sidebar for navigation
st.sidebar.title('Analysis Dashboard')
section = st.sidebar.radio('Select Section:', ['Home', 'Correlation Analysis', 'Group-wise BMI', 'Regression Analysis',
                                               'Interaction Effects'])

# Page 1: Home
if section == 'Home':
    st.title('BMI and Health Factors Dashboard')
    st.write(
        'This dashboard provides a series of analyses and visualizations exploring the relationship between BMI and various health factors.')
    st.write('Data Preview:')
    st.write(df.head())

# Page 2: Correlation Analysis
elif section == 'Correlation Analysis':
    st.title('Correlation Analysis')
    st.write('Explore the relationships between BMI and other continuous variables.')

    # Correlation heatmap using Altair
    corr = df[['BMI', 'Age', 'Income Ratio', 'LDL', 'Blood Pressure']].corr().reset_index().melt('index')
    corr_chart = alt.Chart(corr).mark_rect().encode(
        x='index:O',
        y='variable:O',
        color='value:Q',
        tooltip=['index', 'variable', 'value']
    ).properties(title='Correlation Heatmap')

    st.altair_chart(corr_chart, use_container_width=True)

    # Scatter plot with dropdown for variable selection
    variable = st.selectbox('Select variable to plot against BMI', ['Age', 'Income Ratio', 'LDL', 'Blood Pressure'])

    scatter_chart = alt.Chart(df).mark_circle(size=60).encode(
        x=variable,
        y='BMI',
        tooltip=[variable, 'BMI']
    ).interactive()

    st.altair_chart(scatter_chart, use_container_width=True)

# Page 3: Group-wise BMI Analysis (Categorical)
elif section == 'Group-wise BMI':
    st.title('BMI by Categorical Variables')
    st.write('Compare BMI across different categories (Gender, Race, Diabetes).')

    category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])

    boxplot = alt.Chart(df).mark_boxplot().encode(
        x=category + ':O',
        y='BMI:Q',
        tooltip=['BMI', category]
    ).properties(
        title=f'BMI by {category}'
    )

    st.altair_chart(boxplot, use_container_width=True)

# Page 4: Regression Analysis
elif section == 'Regression Analysis':
    st.title('Regression Analysis')
    st.write('Perform linear regression to see how multiple factors affect BMI.')

    st.write(
        'Note: For simplicity, we are not performing a full regression here, but visualizing linear relationships.')

    # Regression-like scatter plot with trend line
    variable = st.selectbox('Select variable for regression plot:', ['Age', 'Income Ratio', 'LDL', 'Blood Pressure'])

    regression_chart = alt.Chart(df).mark_point().encode(
        x=variable,
        y='BMI'
    ).interactive() + alt.Chart(df).transform_regression(variable, 'BMI').mark_line()

    st.altair_chart(regression_chart, use_container_width=True)

# Page 5: Interaction Effects
elif section == 'Interaction Effects':
    st.title('Interaction Effects')
    st.write('Explore the interaction between Age and Gender on BMI.')

    interaction_plot = alt.Chart(df).mark_circle().encode(
        x='Age:Q',
        y='BMI:Q',
        color='Gender:N',
        size='Income Ratio:Q',
        tooltip=['Age', 'BMI', 'Gender', 'Income Ratio']
    ).properties(
        title='Interaction of Age, Gender, and BMI'
    ).interactive()

    st.altair_chart(interaction_plot, use_container_width=True)

