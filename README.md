# MyNHANES

**MyNHANES** is an open-source data platform designed to simplify access, integration, and transformation of public health data from the [National Health and Nutrition Examination Survey (NHANES)](https://www.cdc.gov/nchs/nhanes/index.htm).

Unlike the official NHANES portal — where datasets are fragmented across cycles and require manual download and parsing — MyNHANES offers a structured environment to **ingest**, **transform**, **standardize**, and **query** NHANES data as a unified relational database.

---

## ✨ Highlights

- ✅ Unified access to raw data across NHANES cycles
- 🔍 Full metadata integration and search via variables, tags, and cycles
- 🧪 Rule-based transformation engine for derived variables
- 🧭 Web-based interface for non-programmers (Django Admin)
- 📦 Export-ready data for analysis (CSV)
- 📖 Transparent logs and versioning of all steps
- 🔄 Syncs with public GitHub repository for master data and rule definitions

---

## 📦 Installation

```bash
pip install mynhanes
```

After installation, use the CLI with enviroment activated:

```bash
mynhanes deploy --type local
mynhanes runserver
```

Then access the admin interface at:
[http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 🚀 (optional) Example of other commands

```bash
# Deploy local DB and import master data
mynhanes deploy --type local

# Run ingestion for marked datasets
mynhanes ingestion_nhanes --type db

# Apply active transformation rules
mynhanes transformation

# Export query reports
mynhanes query --fields_report
```

---

## 🧭 How It Works

### 1. Master Data

- Imported from [`MyNHANES_DataHub`](https://github.com/YOUR_ORG/MyNHANES_DataHub)
- Includes: Cycles, Datasets, Variables, Tags, Rules

### 2. Ingestion

- Downloads `.XPT` and `.HTM` files
- Parses metadata and values
- Stores data in the local relational model (`Data`)

### 3. Transformation

- Each rule is a Python script mapped to input/output variables
- Rules run automatically or manually via admin/CLI
- Results are versioned and saved alongside raw data

### 4. Query & Export

- Use QueryStructures and QueryColumns to define reusable queries
- Export structured CSVs across cycles with selected variables

---

## 🧪 Example Use Case

You want to identify NHANES participants likely to have Parkinson’s Disease based on their medication.

With MyNHANES, you can:

- Enable relevant datasets (`RXQ_RX`, `DEMO`)
- Apply a transformation rule (`rule_parkinson`)
- Export the final dataset for modeling

> All steps are documented, logged, and reproducible: https://github.com/HallLab/MyNHANES/tree/main/rules/rule_00001

---

## 🧠 Scientific Vision

MyNHANES is built to support research that demands:

- Harmonized datasets across cycles
- Rapid exploration and export of clean variables
- Transparent data derivation pipelines
- Integration with tools like R, Python, or Jupyter Notebooks

It empowers data scientists, epidemiologists, and clinical researchers to focus on **analysis**, not manual preprocessing.

---

## 🤝 Contributing

We welcome contributions from the community!

- 📥 Submit issues or feature requests
- 🧪 Contribute transformation rules to the `rules/` folder
- 🗂 Help improve tagging and variable descriptions
- 📊 Share notebooks or case studies using MyNHANES data

---

## 🔗 Repositories

- Core App: [https://github.com/HallLab/MyNHANES](https://github.com/HallLab/MyNHANES)
- DataHub: [https://github.com/HallLab/MyNHANES_DataHub](https://github.com/HallLab/MyNHANES_DataHub)

---

## 📄 License

This project is licensed under the MIT License.

---

## 📬 Contact

For questions or collaboration inquiries, please contact:
**Andre Rico** – ricoa@pennmedicine.upenn.edu
or open an issue in the [GitHub repository](https://github.com/HallLab/MyNHANES/issues).

---
