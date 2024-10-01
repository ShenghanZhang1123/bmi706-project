import streamlit as st
import pandas as pd
import altair as alt

df = pd.read_csv('./merged_clean_data.csv')

# Sidebar for navigation
st.sidebar.title('Analysis Dashboard')
section = st.sidebar.radio('Select Section:', ['Home', 'Correlation Analysis', 'Group-wise BMI', 'Group-wise BMI Trend over Age', 'Regression Analysis',
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
elif section == 'Group-wise BMI Comparison':
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

elif section == 'Group-wise BMI Trend over Age':
    category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])

    # Group by Gender (assuming the column for Gender is 'RIAGENDR')
    line_chart = alt.Chart(df).mark_line().encode(
        x='Age',  # Age on x-axis
        y='BMI',
        color=category  # Color lines by Gender
    ).interactive()

# Page 4: Regression Analysis
elif section == 'Regression Analysis':
    st.title('Regression Analysis')
    st.write('Perform linear regression to see how multiple factors affect BMI.')

    st.write(
        'Note: For simplicity, we are not performing a full regression here, but visualizing linear relationships.')

    # Regression-like scatter plot with trend line
    variable = st.selectbox('Select variable for regression plot:', ['Age', 'Income Ratio', 'LDL', 'Blood Pressure'])

    regression_chart = alt.Chart(df).mark_point().encode(
        x=alt.X(variable, type='quantitative'),
        y=alt.Y('BMI', type='quantitative'),
    ).interactive() + alt.Chart(df).transform_regression(variable, 'BMI').mark_line().encode(
        x=variable,
        y='BMI',
        color=alt.value('red')
    )

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

