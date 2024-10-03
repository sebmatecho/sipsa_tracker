# Food Prices Tracker: Colombian case
#### by [Sébastien Lozano-Forero](https://www.linkedin.com/in/sebastienlozanoforero/)

## Overview

This project is a fully automated data pipeline for scraping, processing, and ingesting food price reports published weekly by DANE (Departamento Administrativo Nacional de Estadística), Colombia's national statistical office. DANE is responsible for collecting, analyzing, and disseminating statistical information to support decision-making in the public and private sectors across various domains such as demographics, economics, and agriculture.

### What is SIPSA?

The **[SIPSA](https://www.dane.gov.co/index.php/estadisticas-por-tema/agropecuario/sistema-de-informacion-de-precios-sipsa) (Sistema de Información de Precios del Sector Agropecuario)**
 is one of DANE’s key projects, focused on monitoring and reporting agricultural prices across Colombia’s main markets. Each week, SIPSA publishes reports detailing the wholesale prices of various agricultural products (fruits, vegetables, grains, etc.) from major Colombian marketplaces. This data is crucial for understanding trends in food prices, supporting government policy, business decision-making, and providing insights into the agricultural economy.

### What Does This Project Do?

This project automates the process of collecting and processing SIPSA’s weekly reports. It performs the following operations:

1. **Scraping**: Downloads the weekly food price reports from the DANE website.
2. **Data Processing**: Cleans and transforms the data into a structured format.
3. **AWS Integration**:
   - Uploads raw files and processed data to an S3 bucket for storage.
   - Inserts the cleaned data into a PostgreSQL database hosted on AWS RDS for further analysis.
4. **Validation**: Ensures data quality and consistency using custom validation rules (e.g., checking city names, product names, price ranges, and trends).
5. **Tracking**: Tracks processed files to avoid duplicate downloads or database inserts.

This project aimes to demonstrate proficiency in web scraping, data engineering, cloud services, and data quality management. 

---

## Features

- **Automated Web Scraping**: Scrapes weekly reports of food prices in Colombian marketplaces from DANE’s website.
- **Data Cleaning & Validation**: Cleans data, validates city names, product names, prices, trends, and categorizes them into different food categories.
- **AWS Integration**: 
  - **S3**: Uploads both raw and processed data to S3 for archival.
  - **RDS**: Inserts the cleaned data into a PostgreSQL database hosted on AWS RDS.
- **Data Processing**: Handles both Excel and CSV formats with different structures (multi-tab files).
- **Logging & Monitoring**: Comprehensive logging of pipeline activities, with logs uploaded to S3.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Setup](#setup)
- [How to Run](#how-to-run)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)

---

## Project Structure

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
## Requirements
### Software
- Python 3.9+
- PostgreSQL (AWS RDS for cloud deployment)
- AWS S3 for file storage

## Setup

1. Clone the Repository
```bash
git clone https://github.com/sebmatecho/sipsa_tracker.git
cd sipsa_tracker
```
2. Set Up a Virtual Environment
It’s recommended to use a virtual environment to manage dependencies:

```bash
Copy code
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
3. Install the Required Libraries
```bash
pip install -r requirements.txt
```
4. Configure Environment Variables
Create a .env file in the root directory and add the following variables:

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

## How to Run
1. Run the Data Pipeline Locally
You can execute the entire data pipeline by running the following command:

```bash
python -m src.ProcessHandler
```
This will start the scraping process, download the weekly reports, clean and validate the data, and finally insert it into the PostgreSQL database.

2. Running the Tests
The tests directory contains unit tests for each module in the project. You can run the tests using pytest:

```bash
pytest tests/
```