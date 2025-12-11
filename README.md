# Board Games Analysis: Price, Rating & Market Dynamics

## Overview

This project analyzes board games from BoardGameGeek (BGG) combined with real market pricing data. The goal is to understand what makes games valuable, how they're priced in the market, and what factors drive success. We use a mix of data visualization, statistical modeling, and machine learning to explore these questions.

## What's the Project About?

We started with BoardGameGeek data containing thousands of games with their ratings, mechanics, player counts, and more. We then matched these games with real market pricing data and built models to understand the relationships between game features and prices.


## Files in This Project

The main data files we've worked with:

- `bgg_dataset.csv` - Raw game data from BoardGameGeek
- `products_with_edition.csv` - Market pricing and edition information
- `bgg_final.csv` - Cleaned BGG data with additional features
- `bgg_mechanics_exploded.csv` - Individual game mechanics broken out by row
- `bgg_model_ready.csv` - Processed data ready for machine learning
- `products_model_ready` - Market data in model-ready format

The code files:

- `Final_notebook.ipynb` - The main analysis notebook with all visualizations and models
- `data_collections.py` - Script for collecting data from APIs

## How the Analysis Works

The analysis breaks down into a few main parts:

### 1. Data Preparation

We start by loading the game data and market prices, then clean everything up. This includes:
- Converting all prices to USD for consistency
- Handling missing values
- Removing duplicates
- Creating new features like "rating per dollar"

### 2. Exploring the Data

We create lots of visualizations to understand what we're looking at:
- Price distributions and rating distributions
- How different game types compare
- Relationships between price and quality
- Which mechanics are most common
- How success rankings correlate with prices

### 3. Building Models

We use a few different approaches:
- **Linear regression** to see which features matter for pricing
- **Causal inference** using Double Machine Learning to understand cause-and-effect relationships
- **Random forests** for non-linear predictions of game prices

### 4. Finding Insights

From the models, we can identify which game characteristics are actually driving prices, and we calculate value metrics like "complexity per dollar" to find which games offer the best value.

## Some Important Notes

- When we collect new data, there are small delays between API requests to be respectful to the servers
- All prices get converted to USD using standard exchange rates
- We focus on "new" condition products to keep the analysis consistent
- Some games might not have pricing data, but our code handles that gracefully


## References

- Data comes from [BoardGameGeek](https://www.boardgamegeek.com/)
- Built with standard Python data science tools: pandas, scikit-learn, and statsmodels

## Data Sources
-The primary dataset used in this study was obtained from BoardGameGeek (BGG)
- A public API from the BGG website to extract products
