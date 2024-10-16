import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

df = pd.read_csv('./merged_clean_data.csv')
df['Gender'] = df['Gender'].replace({1: 'Male', 2: 'Female'})
df['Race'] = df['Race'].replace({1: 'Mexican American', 2: 'Other Hispanic', 3: 'Non-Hispanic White', 4: 'Non-Hispanic Black', 6: 'Non-Hispanic Asian', 7: 'Other'})
df['Diabetes'] = df['Diabetes'].replace({1: 'Yes', 2: 'No', 3: 'Borderline', 7: 'Refused', 9: 'Don\'t Know'})

st.set_page_config(layout="wide")
st.sidebar.title('Analysis Dashboard')
section = st.sidebar.radio('Select Section:', ['Home', 'Correlation Analysis', 'Group-wise BMI Comparison',
                                               'BMI Age Distribution', 'test'])

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
    st.title('Correlation Analysis')
    st.write('Explore the relationships between BMI and other continuous variables.')

    var_set = {'Age', 'Income Ratio', 'LDL', 'Blood Pressure'}

    variable = st.selectbox('Select variable to plot against BMI and conduct linear regression',
                            sorted(var_set))

    selected_categories = st.multiselect(f'Select additional variables to display:', sorted(var_set.difference({variable})))

    col1, col2 = st.columns([1, 2])

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

    # Calculate mean and standard deviation for BMI per category
    bmi_stats = df.groupby(category)['BMI'].agg(['mean', 'std']).reset_index()

    # Define a selection
    # Create a selector to link bar chart and strip plot
    selection = alt.selection_multi(fields=[category], bind='legend')

    # Bar plot with error bars and selection
    bar = alt.Chart(bmi_stats).mark_bar().encode(
        x=alt.X(f'{category}:N', title=category),
        y=alt.Y('mean:Q', title='Mean BMI'),
        color=alt.Color(f'{category}:N', legend=alt.Legend(title=category)),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        selection
    )

    error_bars = alt.Chart(bmi_stats).mark_errorbar().encode(
        x=alt.X(f'{category}:N'),
        y=alt.Y('mean:Q', title='Mean BMI'),
        yError='std:Q'
    )

    # Combine the bar chart with error bars
    bar_with_error = (bar + error_bars).properties(
        height=600,
        title=f'BMI by {category}'
    )

    # Strip plot with jitter and filtering based on selection
    strip_plot = alt.Chart(df).mark_circle(size=100).encode(
        x=alt.X(f'{category}:N', title=category),
        y=alt.Y('BMI:Q', title='BMI'),
        color=alt.Color(f'{category}:N', legend=None),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).properties(
        height=600,
        title=f'Strip Plot of BMI by {category}'
    )

    # Combining both views using Altair's vertical concatenation with linking
    linked_views = bar_with_error & strip_plot

    # Display the linked charts
    st.altair_chart(linked_views, use_container_width=True)

# Page 4: Interaction Effects
elif section == 'BMI Age Distribution':
    st.title('BMI Age Distribution')
    st.write('Customize the distribution plot based on both categorical and continuous variables.')

    plot_type = st.radio(
        "Select visualization type:",
        ('Scatter Plot', 'Line Plot'), horizontal=True
    )

    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox('Select category:', ['Gender', 'Race', 'Diabetes'])
    with col2:
        continuous = st.selectbox('Select continuous variable:', ['Income Ratio', 'LDL', 'Blood Pressure'])

    selected_categories = st.multiselect(f'Select {category} to display:', df[category].unique())

    if selected_categories:
        filtered_df = df[df[category].isin(selected_categories)]
    else:
        filtered_df = df

    diff = df['Age'].max() - df['Age'].min()
    domain_min = df['Age'].min() - diff * 0.02
    domain_max = df['Age'].max() + diff * 0.02

    scatter_plot = alt.Chart(filtered_df).mark_circle(opacity=0.7).encode(
        x=alt.X('Age:Q', scale=alt.Scale(domain=[domain_min, domain_max])),
        y='BMI:Q',
        color=alt.Color(category + ':O', scale=alt.Scale(scheme='category10')),
        size=continuous + ':Q',
        tooltip=['Age', 'BMI', 'Gender', 'Income Ratio']
    ).properties(
        height=550
    ).interactive()

    line_plot = alt.Chart(filtered_df).mark_line(strokeWidth=3).encode(
        x=alt.X('Age'),
        y=alt.Y('mean(BMI)', scale=alt.Scale(domain=[15, 60])),
        color=alt.Color(category + ':O', scale=alt.Scale(scheme='category10'))
    ).properties(
        height=550
    ).interactive()

    if plot_type == 'Scatter Plot':
        st.altair_chart(scatter_plot, use_container_width=True)
    elif plot_type == 'Line Plot':
        st.altair_chart(line_plot, use_container_width=True)

elif section == 'test':
    import streamlit as st
    import pandas as pd
    import altair as alt
    import numpy as np

    # Simulating the dataframe
    np.random.seed(42)
    df = pd.DataFrame({
        'BMI': np.random.uniform(18, 40, 500),
        'Race': np.random.choice(['White', 'Black', 'Asian', 'Hispanic'], 500),
        'Gender': np.random.choice(['Male', 'Female'], 500)
    })

    # Streamlit layout
    st.title("BMI Distribution by Race and Gender")

    # Categorical variable selection
    category = st.selectbox("Select a categorical variable:", ['Race', 'Gender'])

    # Create a selection object in Altair
    selection = alt.selection_multi(fields=[category], bind='legend')

    # First view: Histogram of BMI with color encoding based on the selected categorical variable
    hist_chart = alt.Chart(df).mark_bar().encode(
        alt.X('BMI:Q', bin=alt.Bin(maxbins=30), title='BMI'),
        alt.Y('count()', title='Number of People'),
        alt.Color(f'{category}:N', legend=alt.Legend(title=category)),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        selection
    ).properties(
        width=400,
        height=300,
        title=f"BMI Distribution by {category}"
    )

    # Second view: Bar chart showing counts per category
    bar_chart = alt.Chart(df).mark_bar().encode(
        alt.X(f'{category}:N', title=f'{category} Category'),
        alt.Y('count()', title='Number of People'),
        alt.Color(f'{category}:N', legend=None),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2))
    ).properties(
        width=400,
        height=300,
        title=f"Count of People by {category}"
    )

    # Combining both views using Altair's vertical concatenation with linking
    linked_views = hist_chart & bar_chart

    # Display the linked charts
    st.altair_chart(linked_views, use_container_width=True)

