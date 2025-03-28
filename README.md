# E-commerce Sales Dashboard

_Empower e-commerce success with actionable insights from your sales data._

[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen)](https://dsci-532-2025-29-e-commerce-dashboard.onrender.com/)

_See our dashboard in action!_

![App in Action](img/demo.gif)

## Welcome!

Welcome to our E-Commerce Sales Dashboard! This project is designed to empower e-commerce clothing store managers with a powerful tool to analyze the sales performance. Built by a data science consultancy firm, this dashboard transforms raw sales data into actionable insights for smarter decision-making.

## Motivation and Purpose

Running an e-commerce clothing store comes with unique challenges: managing a wide variety of product SKUs, keeping up with fast-changing fashion trends, and making sense of massive sales datasets. For store managers, understanding whether sales align with market demand or if adjustments to inventory and marketing are needed can feel overwhelming.

That’s where the E-Commerce Sales Dashboard steps in. Our goal is to simplify data analysis by providing a clear, interactive view of sales performance and regional trends. Whether you're tracking revenue, comparing fulfillment methods, or identifying top-performing regions, this dashboard helps you stay ahead in the competitive world of e-commerce.

## What Can You Do with This Dashboard?

This dashboard is built for e-commerce clothing store managers running online stores in India. With it, you can:

- **Explore Sales Trends**: Visualize how sales fluctuate over time and spot patterns.

- **Compare Regions**: See which states or regions drive the most revenue and pinpoint areas with lower sales.

- **Identify Top Products**: Discover the best-selling products in each region.

- **Analyze Fulfillment**: Compare Amazon Fulfilled vs. Merchant Fulfilled orders to optimize logistics.

- **Understand Promotions**: Assess how discounts impact sales performance.

What are you waiting for? Try our dashboard [here](https://dsci-532-2025-29-e-commerce-dashboard.onrender.com/)!

## Who Is This For?

#### 1. Store Managers Looking to Use the Dashboard
If you’re an e-commerce professional in India, this tool is for you! Whether you’re managing inventory, refining marketing strategies, or negotiating with delivery partners, the dashboard provides a high-level overview of your sales data to support data-driven decisions. No technical expertise required—just dive in and explore!

**Need Help?** If you have questions or run into issues, feel free to [open an issue](https://github.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard/issues) and label it as "help wanted" on this repository. We’re here to assist!

#### 2. Developers and Contributors
Interested in running the dashboard locally or contributing to its development? We’d love your help! This project is built with a passion for data science and e-commerce, and we welcome contributors who want to enhance its features or adapt it for other datasets. Keep reading for setup instructions and contribution details!


## Installation and Running Locally

Want to run the dashboard on your machine? Follow these steps:

### Prerequisites

- `Python 3.11+`
- `git`

### Setup

1. **Clone the Repository:**

```bash
git clone https://github.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard.git
cd e-commerce-sales-dashboard
```

2. **Install Dependencies:**

**For users without `conda`:**

```bash
pip install -r requirements.txt
```

**For `conda` users:**

1. Create conda environment
```bash
conda env create -n e-commerce-dashboard -f environment.yml
```

2. Activate conda environment
```bash
conda activate e-commerce-dashboard
```

If the environment already exists and you want to update it:
```bash
conda env update -n e-commerce-dashboard -f environment.yml
```


3. **Run the App:**
```bash
python -m src.app
```

Navigate to `http://127.0.0.1:8050/`  (or the specified port) in your browser to see the dashboard. 

## Contributing
We’d love for you to contribute to this project! Whether it’s adding new features, improving visualizations, or fixing bugs, your input is valuable. Check out our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get started.

If you are new to open source, make sure to check out issues labeled "good first issue" - these are great entry points to get started!

## Support
Encountered a problem or have a question? Please open an [issue](https://github.com/UBC-MDS/DSCI-532_2025_29_e-commerce-dashboard/issues) on this repository, and we’ll get back to you as soon as possible.

## Contributors
Jenson Chang, Shashank Hosahalli Shivamurthy, Sienko Ikhabi, Yajing Liu

## License

This project is dual-licensed:
- Source code: MIT License
- Reports in `reports/` and Images in `img/`: Creative Commons Attribution 4.0 International (CC BY 4.0)

See [LICENSE.md](LICENSE.md) for details.