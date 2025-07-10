# PAKTON Evaluation & Experiments Frontend

[![React](https://img.shields.io/badge/React-19.1.0-blue.svg)](https://reactjs.org/)
[![Node.js](https://img.shields.io/badge/Node.js-LTS-green.svg)](https://nodejs.org/)
[![Docker](https://img.shields.io/badge/Docker-supported-2496ED.svg)](https://www.docker.com/)

A modern React-based dashboard for visualizing and analyzing the experiments and evaluation results from the PAKTON research project. This interactive frontend provides comprehensive data visualization tools including charts, heatmaps, radar plots, and statistical comparisons for both automated G-Eval assessments and human evaluation studies.

## 🚀 Features

- **Interactive Data Visualization**: Multiple chart types including bar charts, scatter plots, box plots, heatmaps, and radar charts
- **Dual Evaluation Systems**: Support for both G-Eval automated assessment and human evaluation workflows
- **Experiment Comparison**: Side-by-side analysis of different model performances
- **Responsive Design**: Mobile-friendly interface with adaptive layouts
- **Real-time Data**: Dynamic loading and visualization of evaluation datasets
- **Export Capabilities**: Download charts and data for further analysis

## 🛠 Technology Stack

- **Frontend Framework**: React 19.1.0
- **Routing**: React Router DOM 7.5.0
- **Data Visualization**: Recharts 2.15.2
- **Styling**: CSS3 with responsive design
- **Data Processing**: PapaParse for CSV handling
- **Testing**: React Testing Library & Jest
- **Containerization**: Docker & Docker Compose

## 📦 Quick Start

### Option 1: Docker Setup (Recommended)

The fastest way to get started is using Docker:

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd Frontend

# Build and start the container
docker-compose up --build

# For background execution
docker-compose up -d

# Access the application at http://localhost:3001
```

To stop the application:
```bash
docker-compose down
```

### Option 2: Manual Setup

If you prefer to run the application locally:

#### Prerequisites
- Node.js (LTS version recommended)
- npm or yarn package manager

#### Installation & Execution

1. **Install dependencies**
   ```bash
   npm install --legacy-peer-deps
   ```

2. **Start development server**
   ```bash
   npm start
   ```
   The application will be available at `http://localhost:3000`

3. **Build for production**
   ```bash
   npm run build
   
   # Serve the build (requires serve package)
   npx serve -s build -l 3000
   ```

## 📁 Project Structure

```
Frontend/
├── public/                                           # Static assets
│   ├── data/                                         # Evaluation datasets acquired from experiments
│   │   ├── geval_aggregated_evaluation_scores.json
│   │   ├── geval_scores.json
│   │   ├── human_aggregated_votes.json
│   │   └── human_evaluation/                         # CSV files for different question types
│   └── index.html
├── src/
│   ├── components/                                   # Reusable UI components
│   │   ├── BarChartView.js                           # Bar chart visualization
│   │   ├── BoxPlotView.js                            # Box plot for statistical analysis
│   │   ├── HeatmapView.js                            # Correlation heatmaps
│   │   ├── RadarChartView.js                         # Multi-dimensional comparisons
│   │   ├── ScatterPlotView.js                        # Correlation analysis
│   │   └── WinPlotView.js                            # Win/loss comparisons
│   ├── pages/                                        # Main application pages
│   │   ├── HomePage/                                 # Landing page with overview
│   │   ├── GevalExperimentsPage/                     # G-Eval results dashboard
│   │   ├── HumanEvaluationPage/                      # Human evaluation interface
│   │   ├── HumanEvaluationDashboard/                 # Human evaluation analytics
│   │   ├── ExperimentDetails/                        # Detailed experiment analysis
│   │   └── AboutPage/                                # Project information
│   ├── constants/                                    # Application constants
│   │   ├── availableQuestions.js                     # Question type definitions
│   │   └── evaluationCriteria.js                     # Evaluation metrics
│   ├── utils/                                        # Utility functions
│   ├── App.js                                        # Main application component
│   └── index.js                                      # Application entry point
├── docker-compose.yml                                # Docker configuration
├── Dockerfile                                        # Container build instructions
└── package.json                                      # Dependencies and scripts
```

## 🎯 Usage

### Navigation

The application features a responsive navigation bar with the following sections:

- **Home**: Overview and introduction to the evaluation system
- **G-Eval Experiments**: Automated evaluation results and comparisons
- **Human Evaluation**: Interactive dashboard for human assessment data
- **Human Dashboard**: Aggregated analysis of human evaluation results
- **About**: Information about the PAKTON project

### Data Visualization Types

1. **Bar Charts**: Compare model performances across different metrics
2. **Scatter Plots**: Analyze correlations between evaluation criteria
3. **Box Plots**: Statistical distribution analysis
4. **Heatmaps**: Correlation matrices and pattern identification
5. **Radar Charts**: Multi-dimensional model comparison
6. **Win Plots**: Head-to-head model performance comparisons

### Supported Evaluation Types

- **G-Eval Automated Assessment**: Quantitative metrics and scores
- **Human Evaluation**: Qualitative assessments across multiple criteria:
  - AI Definition Questions
  - Complaints Analysis
  - Emotions Recognition
  - Obligations Assessment
  - Risk Articles Evaluation
  - Scope Analysis

## 📊 Data Sources

The application processes evaluation data from:
- JSON files containing G-Eval scores and aggregated results
- CSV files with human evaluation responses
- Structured datasets for different question types and evaluation criteria

## 🐳 Docker Configuration

The Docker setup includes:
- **Port Mapping**: Container port 3000 → Host port 3001
- **Volume Mounting**: Hot-reloading for development
- **Legacy Dependencies**: Configured for compatibility