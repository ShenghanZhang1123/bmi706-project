import streamlit as st
import pandas as pd
import altair as alt

df = pd.read_csv('./merged_clean_data.csv')
df['Gender'] = df['Gender'].replace({1: 'Male', 2: 'Female'})
df['Race'] = df['Race'].replace({1: 'Mexican American', 2: 'Other Hispanic', 3: 'Non-Hispanic White', 4: 'Non-Hispanic Black', 6: 'Non-Hispanic Asian', 7: 'Other'})
df['Diabetes'] = df['Diabetes'].replace({1: 'Yes', 2: 'No', 3: 'Borderline', 7: 'Refused', 9: 'Don\'t Know'})

# Sidebar for navigation
st.set_page_config(layout="wide")
st.sidebar.title('Analysis Dashboard')
section = st.sidebar.radio('Select Section:', ['Home', 'Correlation Analysis', 'Group-wise BMI Comparison', 'Group-wise BMI Trend over Age', 'Regression Analysis',
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
    st.title('BMI Trend over Age by Categorical Variables')
    st.write('Plot the BMI Trend over Age across different categories')
    category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])

    # Multiselect to choose which specific categories to display
    selected_categories = st.multiselect(f'Select {category} to display:', df[category].unique(), default=df[category].unique()[0])

    # Filter the dataframe based on selected categories
    if selected_categories:
        filtered_df = df[df[category].isin(selected_categories)]
    else:
        filtered_df = df  # Show all if none are selected

    # Group by the selected category and plot the trend
    line_chart = alt.Chart(filtered_df).mark_line().encode(
        x='Age',  # Age on x-axis
        y='mean(BMI)',
        color=alt.Color(category + ':O', scale=alt.Scale(scheme='category10'))  # Apply distinct colors
    ).properties(
        title=f'BMI Trend over Age by {category}'
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)

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

    st.altair_chart(interaction_plot, use_container_width=True, use_container_height=True)

