# Stock Data and Analysis API: Value-Added Financial Data Service

## 🎯 Project Overview

This project presents a robust and intelligent **RESTful API** built with **FastAPI** that serves as a high-value intermediary layer for financial market data. It addresses the common challenge of consuming raw, often complex, third-party API responses by **transforming Finnhub.io's extensive financial data into a clean, standardized, and immediately insightful format** for developers and applications.

The API demonstrates key principles of modern backend development, including:
* **Efficient Data Ingestion & Validation**
* **Intelligent Data Processing & Enrichment**
* **Modular API Design**
* **Performance Optimization (Caching)**
* **Secure Configuration Management**

This project serves as a showcase of my ability to design, develop, and deploy scalable and maintainable API solutions.

## ✨ Key Features & Demonstrated Skills

This API goes beyond a simple proxy, offering enhanced functionality:

* **Comprehensive Company Data:**
    * Retrieves and presents core company profile information (e.g., industry, country, IPO date) from Finnhub.
    * *Skill Highlight:* Data serialization, external API integration.

* **Intelligent Key Financial Metrics Analysis:**
    * Fetches essential financial ratios (P/E, P/S, ROE, ROA, etc.) for a given stock symbol.
    * **Value-Add:** Automatically provides **qualitative assessments** of a company's **valuation (Undervalued/Fair/Overvalued), profitability (High/Moderate/Low), and liquidity (Strong/Adequate/Weak)** based on industry best practices and predefined thresholds.
    * *Skill Highlight:* Data transformation, conditional logic, business rule implementation, analytical processing.

* **Structured & Enriched Financial Statements:**
    * Accesses detailed Income Statements, Balance Sheets, and Cash Flow Statements.
    * **Value-Add:** Flattens Finnhub's nested and often inconsistent `us-gaap` accounting concepts into **clean, human-readable fields** (e.g., `net_income`, `total_assets`).
    * **Value-Add:** Dynamically calculates and includes common financial ratios (e.g., Gross Margin, Operating Margin, Current Ratio, Debt-to-Equity) directly from the raw statement line items.
    * **Value-Add:** Provides **Year-over-Year (YoY) growth percentages** for critical indicators like Revenue and Net Income by intelligently processing historical filings.
    * **Value-Add:** Offers a **simplified overall financial health status** (e.g., 'Strong', 'Stable', 'Concerning') derived from key statement metrics.
    * *Skill Highlight:* Complex data parsing, nested JSON handling, custom data aggregation, financial analysis logic, algorithmic processing.

* **Optimized Performance with Caching:**
    * Implements an **in-memory caching mechanism** for Finnhub API responses.
    * *Benefit:* Significantly reduces redundant external API calls, leading to faster response times for repeat requests and efficient consumption of API quotas.
    * *Skill Highlight:* Performance optimization, cache invalidation strategies, resource management.

* **Robust API Design & Development:**
    * Built using **FastAPI**, leveraging its asynchronous capabilities for high performance.
    * Utilizes **Pydantic** for declarative data validation and clear API schema definition, ensuring data integrity for both incoming and outgoing payloads.
    * Employs **Dependency Injection** for managing shared resources like the API key, promoting modularity and testability.
    * Follows a **modular project structure** with clear separation of concerns (endpoints, services, schemas, config).
    * Provides **automatic, interactive API documentation** (Swagger UI & ReDoc) for easy exploration and testing.
    * *Skill Highlight:* API development, asynchronous programming, data modeling, framework proficiency, software architecture.

* **Secure Configuration Management:**
    * Loads sensitive API keys securely from environment variables using `python-dotenv`.
    * *Skill Highlight:* Security best practices, environment variable management.

## 🚀 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/BufferOverthrow/fastapi-financial-data-service.git
    cd fastapi-financial-data-service # Or your local root directory name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    ```

3.  **Install project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Or you can run `pip install fastapi uvicorn httpx pydantic python-dotenv`)*

4.  **Configure Finnhub API Key:**
    * Obtain a free API key from [Finnhub.io](https://finnhub.io/).
    * In the **root directory** of the project (same level as the `app/` folder), create a file named `.env` and add your API key:
        ```
        FINNHUB_API_KEY="YOUR_ACTUAL_FINNHUB_API_KEY_HERE"
        ```
        *(Replace `YOUR_ACTUAL_FINNHUB_API_KEY_HERE` with your actual key.)*

### Running the Application

From the project's root directory (where `app/` is located):

```bash
uvicorn app.main:app --reload
```
The API will be served locally, typically at `http://127.0.0.1:8000`.

## 🌐 API Endpoints & Documentation

Access the **interactive API documentation** (Swagger UI) at:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

This documentation provides details on all available endpoints, request parameters, response schemas, and allows you to test them directly.

Key endpoint categories include (all prefixed with `/api`):
* `/api/company/{symbol}/profile`
* `/api/company/{symbol}/key-metrics`
* `/api/company/{symbol}/financial-statements-summary`

## 💡 Future Enhancements

Potential areas for further development include:

* **Advanced Caching Strategies:** Implement more sophisticated caching using external solutions like Redis for production readiness.
* **User Authentication & Authorization:** Secure endpoints with user-based authentication (e.g., OAuth2, JWT).
* **Database Integration:** Persist data or user-specific preferences to a database.
* **More Advanced Analytics:** Develop deeper financial analysis features, potentially including machine learning models for forecasting or risk assessment.
* **Asynchronous Tasks:** Offload long-running processing to background tasks.

---

## Contact

Wynndyll Montero
https://www.linkedin.com/in/codealchemy/
https://github.com/BufferOverthrow

---
