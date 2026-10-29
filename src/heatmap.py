
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Read the adjusted closing prices
prices = pd.read_csv(
    "../data/combined_adj_close.csv",
    index_col=0,
    parse_dates=True
)

prices = prices.sort_index()

# Calculate daily returns
returns = prices.pct_change(fill_method=None).dropna(how="any")

# Calculate the correlation matrix
correlation = returns.corr()


# Create an output folder
Path("results").mkdir(exist_ok=True)

# Save the numerical correlation matrix
correlation.to_csv("results/asset_correlations.csv")

# Create the heatmap
fig, ax = plt.subplots(figsize=(10, 8))

heatmap = ax.imshow(
    correlation,
    cmap="coolwarm",
    vmin=-1,
    vmax=1
)

# Label the axes with ticker names
tickers = correlation.columns

ax.set_xticks(range(len(tickers)))
ax.set_yticks(range(len(tickers)))

ax.set_xticklabels(tickers, rotation=45, ha="right")
ax.set_yticklabels(tickers)

# Display the correlation value in each cell
for row in range(len(tickers)):
    for col in range(len(tickers)):
        value = correlation.iloc[row, col]

        ax.text(
            col,
            row,
            f"{value:.2f}",
            ha="center",
            va="center",
            color="white" if abs(value) > 0.6 else "black"
        )

# Add a color scale
fig.colorbar(heatmap, ax=ax, label="Correlation")

ax.set_title("Stock Daily Return Correlation Heatmap")

fig.tight_layout()

# Save and display the chart
fig.savefig("results/asset_correlation_heatmap.png", dpi=200)

plt.show()
