# **SIPSApp - Exploring Colombian Food Prices**  
#### by [Sébastien Lozano-Forero](https://www.linkedin.com/in/sebastienlozanoforero/)

## **Overview**

The **Food Prices Tracker** is a comprehensive data analysis platform that provides insights into food price dynamics in Colombia using weekly data published by **DANE (Departamento Administrativo Nacional de Estadística)**, the national statistical office of Colombia. This project automates the collection, cleaning, validation, and analysis of the **SIPSA (Sistema de Información de Precios del Sector Agropecuario)** dataset to provide data-driven insights into agricultural pricing.

### **Project Purpose and Importance**

The main goal of this project is to facilitate a deeper understanding of food price trends and **affordability** across various cities and marketplaces in Colombia. It aims to:
- Support policymakers in addressing **food security** and **inflation** concerns.
- Help businesses, farmers, and the general public to make informed decisions.
- Highlight regional disparities in food prices and trends that could be valuable for designing targeted interventions.

The project demonstrates the power of **data engineering** combined with **interactive data analysis** to explore real-world challenges in food markets.

### **What is SIPSA?**

The **[SIPSA](https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa)** (Sistema de Información de Precios del Sector Agropecuario) is a project managed by DANE that monitors and reports agricultural prices across Colombia's primary marketplaces. Each week, SIPSA releases reports on wholesale food prices, providing critical data to understand food price trends, market disruptions, and overall agricultural economics.

### **What Does This Project Do?**

The Food Prices Tracker automates the entire data processing workflow:
1. **Scraping**: Automatically downloads weekly food price reports from DANE's website.
2. **Data Cleaning & Processing**: Validates, transforms, and structures the data for analysis.
3. **AWS Integration**:
   - Uploads raw files to an **S3 bucket** for archival.
   - Stores cleaned data in a **PostgreSQL database** hosted on **AWS RDS**.
4. **Data Analysis & Visualizations**:
   - Provides interactive visualizations, including **price trends, affordability rankings,** and **price changes** over time using **Streamlit**.
5. **Data Quality Validation**: Ensures the integrity of city names, product names, price ranges, and trends for consistent and reliable analysis.

---

## **Project Features**

### **1. Automated Data Pipeline**
The project is a fully automated data pipeline for the collection, processing, and ingestion of SIPSA's weekly reports. It consists of:
- **Automated Web Scraping**: Weekly reports on food prices are downloaded from DANE’s official website.
- **Data Cleaning & Validation**: Cleaning the raw data, validating city and product names, and organizing it into structured formats.
- **Data Processing**: The system handles files in **Excel and CSV** formats and is capable of working with different structures such as multi-tab files.

### **2. Data Storage and Cloud Integration**
- **AWS S3**: Both raw and processed data are uploaded to AWS S3, ensuring data reliability, access, and storage.
- **AWS RDS**: A **PostgreSQL** database hosted on AWS RDS is used to store cleaned data for analysis.

### **3. Visualization Platform**
- **Streamlit Web Application**: The data analysis results are presented via an interactive **Streamlit** application. This app provides the following:
  - **Interactive Analysis**: Visualizations showcasing price trends, affordability rankings, city comparisons, and category-specific trends.
  - **Insights & Reporting**: Tools for examining **weekly price changes**, **seasonality**, and **affordability** at the regional level, allowing for an intuitive understanding of complex food market trends.

### **4. Recent Additions**
- **Price Change Detection**:
  - Recent features enable identifying **products with extreme price changes**, helping to track significant price increases or decreases between weeks. This helps stakeholders detect **market disruptions** or other anomalies.
- **Affordability Analysis**:
  - Users can see **top and bottom products** by affordability in a city, providing clear insights into **food affordability** for Colombian citizens.
- **Seasonality and Price Trends**:
  - Seasonal decomposition and price trend analysis, allowing stakeholders to understand **trends, seasonal effects,** and **market dynamics**.

---

## **Table of Contents**

- [Project Structure](#project-structure)
- [Setup](#setup)
- [How to Run](#how-to-run)
- [Streamlit Application Overview](#streamlit-application-overview)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)

---

## **Project Structure**

```bash
├── src/
│   ├── DataCollector.py        # Handles scraping and file collection
│   ├── DataIngestor.py         # Ingests processed data into PostgreSQL
│   ├── DataValidator.py        # Validates and cleans the collected data
│   ├── DataWrangler.py         # Extracts and transforms the data from files
│   ├── FileNameBuilder.py      # Handles file path construction and organization
│   ├── logging_setup.py        # Sets up logging for the pipeline
│   ├── ProcessHandler.py       # Orchestrates the entire data pipeline
├── tests/                      # Unit tests for each module
├── logs/                       # Logs directory (generated during runtime)
├── README.md                   # This README file
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables for AWS and PostgreSQL credentials
```

---

## **Setup**

### **Software Requirements**
- **Python 3.9+**
- **PostgreSQL** (AWS RDS for cloud deployment)
- **AWS S3** for file storage

### **Installation and Configuration**

1. **Clone the Repository**:
```bash
git clone https://github.com/sebmatecho/sipsa_tracker.git
cd sipsa_tracker
```

2. **Set Up a Virtual Environment**:
   It’s recommended to use a virtual environment to manage dependencies:
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install the Required Libraries**:
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add the following variables:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_s3_bucket_name
RDS_HOSTNAME=your_rds_hostname
RDS_PORT=your_rds_port
RDS_DB_NAME=your_rds_db_name
RDS_USERNAME=your_rds_username
RDS_PASSWORD=your_rds_password
```

---

## **How to Run**

### **1. Running the Data Pipeline Locally**
To execute the entire data pipeline and automate data ingestion, run:
```bash
python -m src.ProcessHandler
```
This will start the scraping process, download weekly reports, clean and validate the data, and insert it into the PostgreSQL database.

### **2. Running the Streamlit Application**
To visualize the analysis results:
```bash
streamlit run app.py
```
This will start the interactive Streamlit application where users can navigate through different analyses, such as **price trends**, **affordability rankings**, and **seasonality**.

### **3. Running the Tests**
The `tests/` directory contains unit tests for each module in the project. You can run the tests using **pytest**:
```bash
pytest tests/
```

---

## **Streamlit Application Overview**

The Streamlit application provides an interactive interface for analyzing and visualizing food price data:

- **Introduction to SIPSA Project**:
  - Provides context about the project, data sources, and motivation.
  - Visualizes the overall **composition of data** (number of records by city and category).

- **Price Trends Across Time**:
  - View **price evolution by category** either nationwide or city-specific.
  - Allows users to select **cities of interest** and visualize trends within specific food categories.

- **Individual Products**:
  - Explore **price trends** for individual products, either **nation-wide** or by specific **cities**.
  - Offers insights into seasonal trends, and significant price movements for particular items.

- **Product Affordability**:
  - Displays **affordability rankings** for products within a given city.
  - Identifies the **top and bottom products** based on affordability (as a percentage of weekly income).

- **Marketplaces Exploration**:
  - Users can explore **price distributions** across different marketplaces, for either specific products or entire categories.

- **Seasonal Decomposition**:
  - Allows for **seasonal decomposition** of product prices, providing an in-depth view of **trends, seasonality**, and **residuals** in price data.

---

## **Future Improvements**

### **1. Enhanced Affordability Analysis**
- **What-if Scenarios**: Introduce features that simulate potential future events, such as income changes, and analyze their impact on affordability.

### **2. Broader Data Coverage**
- Work towards reducing **urban bias** by improving data collection from **smaller towns** and rural areas in collaboration with **DANE** or similar stakeholders.

### **3. Real-Time Alerts**
- Implement **real-time anomaly detection** to track unusual price changes, allowing for **automated alerts** that inform users when drastic changes are observed.

### **4. Interactivity and Predictive Modeling**
- Expand **interactivity** within the Streamlit app, allowing for more customization.
- Introduce **predictive models** for forecasting future price trends, empowering users to take action based on expected changes.

---

*Food Prices Tracker: Colombian Case - An interactive exploration of food prices, affordability, and agricultural dynamics.*

