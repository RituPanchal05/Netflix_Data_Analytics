# 🎬 Netflix Content Analytics Dashboard

<div align="center">

![Python](https://img.shields.io/badge/Python-3.14.4-blue?style=for-the-badge\&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-black?style=for-the-badge\&logo=pandas)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge\&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-blueviolet?style=for-the-badge\&logo=plotly)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=for-the-badge\&logo=sqlite)
![EDA](https://img.shields.io/badge/EDA-Exploratory%20Data%20Analysis-success?style=for-the-badge)


Interactive Netflix analytics dashboard built using **Python, Pandas, SQL, Streamlit, and Plotly** to analyze global Netflix content trends, genres, ratings, countries, and release patterns.

</div>

---


## Project Overview

This project was created to practice and strengthen skills in:

* Data Cleaning
* Exploratory Data Analysis (EDA)
* SQL Analytics
* Data Visualization
* Dashboard Development

The dashboard provides interactive insights into Netflix content through charts, filters, KPIs, and trend analysis.

---

## Features

* Interactive Streamlit Dashboard
* Netflix-inspired Dark Theme
* KPI Cards
* Interactive Plotly Visualizations
* Genre & Rating Analysis
* Country-wise Analysis
* Trend Analysis
* Search & Filtering
* SQL Integration using SQLite

---

## Dashboard Preview


<img width="100%" alt="dashboard" src="https://github.com/RituPanchal05/Netflix_Data_Analytics/blob/main/visuals/Dashbord/1.png">


<img width="100%" alt="geo" src="https://github.com/RituPanchal05/Netflix_Data_Analytics/blob/main/visuals/Dashbord/2.png">


<img width="100%" alt="genres" src="https://github.com/RituPanchal05/Netflix_Data_Analytics/blob/main/visuals/Dashbord/6.png">

<img width="100%" alt="genres" src="https://github.com/RituPanchal05/Netflix_Data_Analytics/blob/main/visuals/Dashbord/7.png">

---

## Tech Stack

* Python
* Pandas
* NumPy
* SQLite
* Streamlit
* Plotly
* Matplotlib
* Seaborn

---

## Project Structure

```bash id="ok8n6n"
Netflix_Data_Analytics/
│
├── data/
├── notebooks/
├── sql/
├── dashboard/
├── visuals/
├── reports/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository:

```bash id="zjlwm0"
git clone https://github.com/RituPanchal05/Netflix_Data_Analytics.git

cd Netflix_Data_Analytics
```

Install dependencies:

```bash id="jlwm12"
pip install -r requirements.txt
```

---

## Run the Dashboard

```bash id="jlwm90"
streamlit run dashboard/dashboard.py
```

---

## Dashboard Sections

### Overview

* KPI Metrics
* Movies vs TV Shows
* Rating Distribution
* Top Directors

### Geography

* Country-wise Content Distribution
* Global Content Map

### Genres

* Genre Popularity Analysis
* Genre Heatmaps

### Trends

* Content Growth Analysis
* Monthly Additions Pattern

### Explore

* Search Titles
* Interactive Filtering

---

## Key Insights

* Movies dominate Netflix content compared to TV Shows.
* Netflix content additions increased significantly after 2015.
* The United States contributes the highest number of titles.
* Drama and International genres are among the most popular.

---

## SQL Analytics

Performed SQL-based analysis using SQLite including:

* Aggregate Functions
* GROUP BY Queries
* Ranking Queries
* Trend Analysis

Example query:

```sql id="jlwm8r"
SELECT release_year,
       COUNT(*) AS total_releases
FROM netflix
GROUP BY release_year;
```

---

## Learning Outcomes

This project helped improve practical understanding of:

* Data Cleaning
* EDA
* SQL Integration
* Dashboard Development
* Business-Oriented Analytics

---


