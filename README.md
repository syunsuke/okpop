<div align="center">

# 🐙 OKPOP

### OKPOP Knows Population of Osaka Prefecture

**Collect. Process. Store. Analyze.**

大阪府の人口データを収集・整形・蓄積・分析するための  
Python-based population data toolkit.

---

`Python` · `pandas` · `SQLite` · `Streamlit` · `Quarto` · `uv`

</div>

## 🏯 About OKPOP

**OKPOP** is a toolkit for working with population data published by
Osaka Prefecture.

大阪府が公表する人口統計データを取得・整形し、
SQLiteデータベースとして蓄積するためのPythonプロジェクトです。

OKPOP handles multiple types of population statistics:

- **Census** — 国勢調査
- **Estimated Population** — 推計人口
- **Revised Population** — 補正人口
- **Population by 5-Year Age Group** — 年齢5歳階級別人口

Raw Excel files are transformed into structured data and stored in SQLite,
making them easier to query, analyze, visualize, and report.


## ⚡ Workflow

```text
             Osaka Prefecture
                    │
                    ▼
              Excel / CSV
                    │
                    ▼
          ┌─────────────────┐
          │      OKPOP      │
          │                 │
          │ Python + pandas │
          └────────┬────────┘
                   │
                   ▼
                SQLite
                   │
          ┌────────┼────────┐
          │        │        │
          ▼        ▼        ▼
      Analysis  Streamlit  Quarto
                           Reports
```


## 🗂 Project Structure

```text
okpop/
├── src/
│   └── okpop/          # Python package
│       ├── database.py
│       ├── census.py
│       ├── suikei.py
│       ├── hosei.py
│       └── kubun.py
│
├── sql/                # Database schema and views
│
├── data/
│   ├── raw/            # Original population data
│   ├── db/             # SQLite databases
│   └── output/         # Generated data
│
├── app/                # Streamlit application
├── report/             # Quarto reports
├── tests/              # Tests
│
├── pyproject.toml
└── README.md
```


## 🐍 Development

OKPOP uses **uv** for Python project and dependency management.

Clone the repository:

```bash
git clone git@github.com:syunsuke/okpop.git
cd okpop
```

Create/synchronize the development environment:

```bash
uv sync
```

Run OKPOP:

```bash
uv run okpop
```


## 🧰 Tech Stack

| | Technology | Role |
|---|---|---|
| 🐍 | Python | Data processing |
| 🐼 | pandas | Data transformation |
| 🗄️ | SQLite | Population database |
| 🎈 | Streamlit | Interactive UI |
| 📊 | Quarto | Analysis & reports |
| ⚡ | uv | Python project management |


## 🗃 Population Data

The OKPOP database is designed to integrate several types of
population statistics.

| Data | Table | Description |
|---|---|---|
| 国勢調査 | `census` | Population measured by the national census |
| 推計人口 | `suikei` | Monthly estimated population |
| 補正人口 | `hosei` | Revised population estimates |
| 5歳階級人口 | `population_age5_v001` | Population by 5-year age group (85+) |
| 5歳階級人口 | `population_age5_v002` | Population by 5-year age group (95+) |


## 🐙 Why "OKPOP"?

**OKPOP** is a recursive acronym:

> **OKPOP Knows Population of Osaka Prefecture**

which expands forever:

```text
OKPOP
└── OKPOP Knows Population of Osaka Prefecture
    └── OKPOP Knows Population of Osaka Prefecture
        └── OKPOP Knows Population of Osaka Prefecture
            └── ...
```

**Because OKPOP knows Osaka's population. 🐙**


---

<div align="center">

**OKPOP**

*Population data for Osaka Prefecture.*

🐙

</div>
