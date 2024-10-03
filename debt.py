import numpy as np
import plotly.graph_objects as go

# Initial parameters
principal = 1000
leverage = 3
initial_price = 5
total_asset_value = principal * leverage

# Initial debt values
initial_debt_usdt = (principal * leverage) / 2 - principal
initial_debt_ton = (principal * leverage) / 2 / initial_price
initial_debt_total = initial_debt_usdt + initial_debt_ton * initial_price

# Calculate the constant k (product of USDT and TON in the pool)
k = (principal * leverage / 2) * (principal * leverage / 2 / initial_price)

# Price change rate range from -90% to 90%
price_change_rates = np.linspace(-0.9, 0.9, 100)
debt_rates = []
actual_prices = []

# Calculate debt rates for each price change rate
for r in price_change_rates:
    new_price = (1 + r) * initial_price
    actual_prices.append(new_price)

    # Recalculate USDT and TON amounts using the CPMM formula
    new_ton_amount = np.sqrt(k / new_price)
    new_usdt_amount = k / new_ton_amount

    # Recalculate total asset value
    new_total_asset_value = new_usdt_amount + new_ton_amount * new_price

    # New debt values
    new_debt_value = initial_debt_usdt + initial_debt_ton * new_price

    # Calculate debt rate
    debt_rate = (new_debt_value / new_total_asset_value) * 100
    debt_rates.append(debt_rate)

# Find the intersection point where the debt rate crosses the liquidation threshold (80%)
threshold = 80
intersections_x = []
intersections_y = []

# Search for intersections
for i in range(len(debt_rates) - 1):
    if (debt_rates[i] < threshold and debt_rates[i + 1] >= threshold) or (debt_rates[i] > threshold and debt_rates[i + 1] <= threshold):
        # Linear interpolation to estimate the x-coordinate of the intersection
        slope = (debt_rates[i + 1] - debt_rates[i]) / (actual_prices[i + 1] - actual_prices[i])
        intersect_x = actual_prices[i] + (threshold - debt_rates[i]) / slope
        intersect_y = threshold
        intersections_x.append(intersect_x)
        intersections_y.append(intersect_y)

# Plot the curve using Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(x=actual_prices, y=debt_rates, mode="lines", name="Debt Rate", line=dict(color="blue", width=2)))

# Add horizontal red line for the liquidation threshold (y = 80%)
fig.add_trace(go.Scatter(x=[min(actual_prices), max(actual_prices)], y=[80, 80], mode="lines", name="Liquidation Threshold (80%)", line=dict(color="red", width=2, dash="dash")))

# Add vertical line for the initial price
fig.add_trace(go.Scatter(x=[initial_price, initial_price], y=[0, 100], mode="lines", name="Initial Price", line=dict(color="grey", width=2, dash="dot")))

# Add vertical line for each intersection
for intersect_x in intersections_x:
    fig.add_trace(go.Scatter(x=[intersect_x, intersect_x], y=[0, 100], mode="lines", name=f"Liquidation Price = {intersect_x:.2f} USDT", line=dict(color="green", width=1, dash="dot")))

# Add markers for intersection points
fig.add_trace(go.Scatter(x=intersections_x, y=intersections_y, mode="markers", name="Liquidation Point", marker=dict(color="red", size=8, symbol="x")))

# Update layout for beautification
fig.update_layout(
    width=1200,
    height=800,
    title={"text": "Debt Rate vs. TON Price with Liquidation Threshold", "x": 0.5, "xanchor": "center", "yanchor": "top"},
    xaxis=dict(
        title="TON Price (USDT)",
        range=[min(actual_prices), max(actual_prices)],
        showgrid=True,
        gridwidth=0.5,
        gridcolor="LightGray",
        tickmode="array",
        tickvals=sorted(actual_prices[::10] + intersections_x),  # Standard ticks plus intersection points and initial price
        ticktext=[f"{val:.2f}" for val in sorted(actual_prices[::10] + intersections_x)],  # Format tick labels
    ),
    yaxis=dict(title="Debt Rate (%)", range=[0, 100], showgrid=True, gridwidth=0.5, gridcolor="LightGray"),
    template="plotly_white",
    plot_bgcolor="white",
)

fig.show()
fig.write_html("html/debt.html")
fig.write_image("images/debt.png")
