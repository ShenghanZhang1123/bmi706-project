import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

df = pd.read_csv('./merged_clean_data.csv')
df['Gender'] = df['Gender'].replace({1: 'Male', 2: 'Female'})
df['Race'] = df['Race'].replace({1: 'Mexican American', 2: 'Other Hispanic', 3: 'Non-Hispanic White', 4: 'Non-Hispanic Black', 6: 'Non-Hispanic Asian', 7: 'Other'})
df['Diabetes'] = df['Diabetes'].replace({1: 'Yes', 2: 'No', 3: 'Borderline', 7: 'Refused', 9: 'Don\'t Know'})

# Sidebar for navigation
st.set_page_config(layout="wide")
st.sidebar.title('Analysis Dashboard')
section = st.sidebar.radio('Select Section:', ['Home', 'Correlation Analysis', 'Group-wise BMI Comparison', 'Group-wise BMI Trend over Age',
                                               'BMI Distribution'])

# Page 1: Home
if section == 'Home':
    st.title('BMI and Health Factors Dashboard')
    st.write(
        'This dashboard provides a series of analyses and visualizations exploring the relationship between BMI and various health factors.')
    st.write('Data Preview:')
    #st.write(df.head())

    st.dataframe(df.head(15), height=500, use_container_width=True)

# Page 2: Correlation Analysis
elif section == 'Correlation Analysis':
    # Create two columns
    st.title('Correlation Analysis')
    st.write('Explore the relationships between BMI and other continuous variables.')

    var_set = {'Age', 'Income Ratio', 'LDL', 'Blood Pressure'}

    # Scatter plot with dropdown for variable selection
    variable = st.selectbox('Select variable to plot against BMI and conduct linear regression',
                            sorted(var_set))

    # Multiselect to choose which specific categories to display
    selected_categories = st.multiselect(f'Select additional variables to display:', sorted(var_set.difference({variable})))

    col1, col2 = st.columns([1, 2])

    # Correlation heatmap using Altair
    corr = df[['BMI', variable]+list(selected_categories)].corr().reset_index().melt('index')
    corr_chart = alt.Chart(corr).mark_rect().encode(
        x='index:O',
        y='variable:O',
        color='value:Q',
        tooltip=['index', 'variable', 'value']
    ).properties(title='Correlation Heatmap', height=500, width=500)

    with col1:
        st.altair_chart(corr_chart)

    diff_y = df['BMI'].max() - df['BMI'].min()
    domain_min_y = df['BMI'].min() - diff_y * 0.02
    domain_max_y = df['BMI'].max() + diff_y * 0.02

    diff = df[variable].max() - df[variable].min()
    domain_min = df[variable].min() - diff * 0.02
    domain_max = df[variable].max() + diff * 0.02

    regression_chart = alt.Chart(df).mark_point().encode(
        x=alt.X(variable, type='quantitative', scale=alt.Scale(domain=[domain_min, domain_max])),
        y=alt.Y('BMI', type='quantitative', scale=alt.Scale(domain=[domain_min_y, domain_max_y])),
    ).properties(title='Regression Analysis', height=600, width=600).interactive() + alt.Chart(df).transform_regression(variable, 'BMI').mark_line().encode(
        x=variable,
        y='BMI',
        color=alt.value('red')
    ).properties(height=600).interactive()

    with col2:
        st.altair_chart(regression_chart, use_container_width=True)

# Page 3: Group-wise BMI Analysis (Categorical)
elif section == 'Group-wise BMI Comparison':
    st.title('BMI by Categorical Variables')
    st.write('Compare BMI across different categories (Gender, Race, Diabetes).')

    category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])

    col1, col2 = st.columns(2)

    # Calculate mean and standard deviation for BMI per race
    bmi_stats = df.groupby(category)['BMI'].agg(['mean', 'std']).reset_index()

    # Bar plot with error bars
    bar = alt.Chart(bmi_stats).mark_bar().encode(
        x=alt.X(f'{category}:N', title=category),
        y=alt.Y('mean:Q', title='Mean BMI'),
        color=alt.Color(f'{category}:N', scale=alt.Scale(scheme='category10'))
    )

    error_bars = alt.Chart(bmi_stats).mark_errorbar().encode(
        x=alt.X(f'{category}:N'),
        y=alt.Y('mean:Q', title='Standard Deviation'),
        yError='std:Q'
    )

    # Combine the bar chart with error bars
    bar_with_error = bar + error_bars

    bar_with_error = bar_with_error.properties(
        height=600,
        title=f'BMI by {category}'
    )

    # Strip plot with jitter
    strip_plot = alt.Chart(df).mark_circle(size=100).encode(
        x=alt.X(f'{category}:N', title=category),
        y=alt.Y('BMI:Q', title='BMI')
    ).properties(
        height=600,
        title=f'Strip Plot of BMI by {category}'
    ).transform_calculate(
        # Adding jitter to avoid overlap
        jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
    ).encode(
        x=alt.X(f'{category}:N', title=category),
        y=alt.Y('BMI:Q', title='BMI'),
        color=alt.Color(f'{category}:N', scale=alt.Scale(scheme='category10'))
    ).interactive()

    with col1:
        st.altair_chart(bar_with_error, use_container_width=True)

    with col2:
        st.altair_chart(strip_plot, use_container_width=True)

elif section == 'Group-wise BMI Trend over Age':
    st.title('BMI Trend over Age by Categorical Variables')
    st.write('Plot the BMI Trend over Age across different categories')
    category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])

    # Multiselect to choose which specific categories to display
    selected_categories = st.multiselect(f'Select {category} to display:', df[category].unique())

    # Filter the dataframe based on selected categories
    if selected_categories:
        filtered_df = df[df[category].isin(selected_categories)]
    else:
        filtered_df = df  # Show all if none are selected

    # Group by the selected category and plot the trend
    line_chart = alt.Chart(filtered_df).mark_line().encode(
        x=alt.X('Age'),  # Age on x-axis
        y=alt.Y('mean(BMI)', scale=alt.Scale(domain=[15, 60])),  # BMI on y-axis
        color=alt.Color(category + ':O', scale=alt.Scale(scheme='category10'))  # Apply distinct colors
    ).properties(
        height=300,
        title=f'BMI Trend over Age by {category}'
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)

# Page 4: Interaction Effects
elif section == 'BMI Distribution':
    st.title('BMI Distribution Analysis')
    st.write('Customize the distribution plot based on both categorical and continuous variables.')

    category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])
    continuous = st.selectbox('Select continuous variable:', ['Income Ratio', 'LDL', 'Blood Pressure'])

    # Multiselect to choose which specific categories to display
    selected_categories = st.multiselect(f'Select {category} to display:', df[category].unique())

    # Filter the dataframe based on selected categories
    if selected_categories:
        filtered_df = df[df[category].isin(selected_categories)]
    else:
        filtered_df = df  # Show all if none are selected

    diff = df['Age'].max() - df['Age'].min()
    domain_min = df['Age'].min() - diff * 0.02
    domain_max = df['Age'].max() + diff * 0.02

    interaction_plot = alt.Chart(filtered_df).mark_circle().encode(
        x=alt.X('Age:Q', scale=alt.Scale(domain=[domain_min, domain_max])),
        y='BMI:Q',
        color=alt.Color(category + ':O', scale=alt.Scale(scheme='category10')),
        size=continuous + ':Q',
        tooltip=['Age', 'BMI', 'Gender', 'Income Ratio']
    ).properties(
        height=550,
        title='Interaction of Age, Gender, and BMI'
    ).interactive()

    st.altair_chart(interaction_plot, use_container_width=True)

