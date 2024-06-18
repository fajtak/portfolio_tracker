import pandas as pd
from datetime import date
import yfinance as yf
from forex_python.converter import CurrencyRates
import requests
import json

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from IPython.display import display, HTML


# currancy exchange oprions:
# https://github.com/fawazahmed0/exchange-api?tab=readme-ov-file
# https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024.5.16/v1/currencies/usd.json

# https://github.com/tim-hub/sanic-currency-exchange-rates-api
# https://exchange-rate.bai.uno/api/2024-05-18?base=USD&symbols=CZK

def save_exchange_rates() -> None:
    with open("exchange_rates.json", "w") as outfile:
        #json.dump(exchange_rates, outfile)
        json.dump({k: v for k, v in exchange_rates.items() if "tmp" not in k}, outfile)


def read_exchange_rates() -> dict[str, float]:
    try:
        with open("exchange_rates.json") as infile:
            return json.load(infile)
    except:
        return {}


exchange_rates = read_exchange_rates()


def read_trades(filter: list[str] = [], file="trades.tsv") -> pd.DataFrame:
    data = pd.read_csv(file, sep="\t", comment="#")
    return data[~data["ticker"].isin(filter)]


def read_watchlist() -> pd.DataFrame:
    data = pd.read_csv("watchlist.tsv", sep="\t", comment="#")
    return data


def get_exchange_rates() -> dict[str, float]:
    currencies = ["USD"]
    currency_rates = {"CZK": 1.0}
    c = CurrencyRates()
    for currency in currencies:
        currency_rates[currency] = c.get_rate(currency, "CZK", date.today())
    return currency_rates


def transform_date(date_str: str) -> str:
    if "." in date_str:
        return f"{date_str.split('.')[2]}-{date_str.split('.')[1]:0>2}-{date_str.split('.')[0]:0>2}"
    else:
        return date_str

def get_exchange_rate(currency: str, date_in: str) -> float:
    if currency.lower() == "czk":
        return 1.0
    #if type(date_in) is type(""):
    #    date_in = date.fromisoformat(transform_date(date_in))
    if type(date_in) is type(date.today()):
        date_in = f"{date_in}"
    date_in = transform_date(date_in)
    if f"{currency}_{date_in}" in exchange_rates:
        return exchange_rates[f"{currency}_{date_in}"]
    if f"{currency}_{date_in}_we" in exchange_rates:
        return exchange_rates[f"{currency}_{date_in}_we"]
    if f"{currency}_{date_in}_tmp" in exchange_rates:
        return exchange_rates[f"{currency}_{date_in}_tmp"]
    try:
        res = requests.get(f"https://exchange-rate.bai.uno/api/{date_in}?base={currency}&symbols=CZK").json()
    except:
        print(f"CurrencyRates for {currency} from {date_in} not ready")
    else:
        if res["date"] == date_in:
            exchange_rates[f"{currency}_{date_in}"] = res["rates"]["CZK"]
        else:
            if (date.today() - date.fromisoformat(date_in)).days > 5:
                exchange_rates[f"{currency}_{date_in}_we"] = res["rates"]["CZK"]
            else:
                print(f"WARNING: ussing older currency rate for {currency}. {res['date']} instead {date_in}")
                exchange_rates[f"{currency}_{date_in}_tmp"] = res["rates"]["CZK"]
    print("Exchange rate called")
    return res["rates"]["CZK"]


def get_exchange_rate_problematic(currency: str, date_in: str) -> float:
    if currency.lower() == "czk":
        return 1.0
    if type(date_in) is type(""):
        date_in = date.fromisoformat(transform_date(date_in))
    if f"{currency}_{date_in}" in exchange_rates:
        return exchange_rates[f"{currency}_{date_in}"]
    c = CurrencyRates()
    try:
        rate: float = c.get_rate(currency, "CZK", date_in)
    except:
        print(f"CurrencyRates for {currency} from {date_in} not ready")

        #print([x for x in exchange_rates.keys()])
        #print(currency)
        return exchange_rates[[x for x in exchange_rates.keys() if currency in x][-1]]
    else:
        exchange_rates[f"{currency}_{date_in}"] = rate
    print("Exchange rate called")
    return rate


def get_exchange_rate_fixer(currency: str, date_str: str) -> float():
    if currency.lower() == "czk":
        return 1.0
    trans_date = transform_date(date_str)
    # https://fixer.io/quickstart
    results = requests.get(
        f"http://data.fixer.io/api/{trans_date}?access_key=a716e49c4344c0f5799d4f60ac69f40f&format=1"
    )


def get_total_price_in_czk(row: pd.DataFrame) -> float:
    return row["units"] * row["price"] * get_exchange_rate(row["currency"], row["date"])


def get_current_price(row: pd.DataFrame) -> float:
    if row["ticker"].lower() == "btc-usd":
        return yf.Ticker(row["ticker"]).basic_info["lastPrice"] * get_exchange_rate(
            "EUR", date.today()
        )
    else:
        return yf.Ticker(row["ticker"]).basic_info["lastPrice"] * get_exchange_rate(
            row["currency"], date.today()
        )


def show_portfolio_breakdown(data: pd.DataFrame) -> None:
    fig = make_subplots(
        rows=1,
        cols=3,
        specs=[[{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]],
        subplot_titles=("Type", "Currency", "Ticker"),
        horizontal_spacing=0.15,
    )
    fig.add_trace(
        go.Pie(
            labels=data.type,
            values=data.total_price,
            hole=0.5,
            marker=dict(line=dict(color="black", width=2)),
            legendgroup="1",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Pie(
            labels=data.currency,
            values=data.total_price,
            hole=0.5,
            marker=dict(line=dict(color="black", width=2)),
            legendgroup="2",
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Pie(
            labels=data.ticker,
            values=data.total_price,
            hole=0.5,
            marker=dict(line=dict(color="black", width=2)),
            legendgroup="3",
        ),
        row=1,
        col=3,
    )
    fig.update_layout(
        title="Portfolio Breakdown",
        template="plotly_dark",
        width=1200,
        height=600,
    )
    fig.show()


def show_portfolio_growth(data: pd.DataFrame) -> None:
    fig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "bar"}], [{"type": "bar"}]],
        subplot_titles=("Percentage", "Money"),
        vertical_spacing=0.15,
    )
    fig.add_trace(go.Bar(x=data.ticker, y=data.change), row=1, col=1)
    fig.add_trace(go.Bar(x=data.ticker, y=data.profit), row=2, col=1)
    fig.update_layout(
        title="Portfolio Growth",
        template="plotly_dark",
        width=1200,
        height=800,
    )
    fig.show()


def collect_historical_data(data: pd.DataFrame) -> pd.DataFrame:
    symbols = data["ticker"].unique()
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        stock_history_data = stock.history("max")
        stock_history_data.to_csv(f"history_data/{symbol}.txt", sep="\t")


def calculate_columns(data: pd.DataFrame) -> None:
    data["total_price"] = data.apply(get_total_price_in_czk, axis=1)
    data["current_price"] = data.apply(get_current_price, axis=1)
    data["current_total_price"] = data["current_price"] * data["units"]
    data["profit"] = data["current_total_price"] - data["total_price"]
    data["change"] = (data["current_total_price"] / data["total_price"] * 100) - 100
    data["date"] = data["date"].apply(transform_date)


def get_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary = (
        data.groupby("ticker")[["units", "total_price", "currency", "type"]]
        .agg(
            {"units": "sum", "total_price": "sum", "currency": "first", "type": "first"}
        )
        .reset_index()
    )
    summary["mean_price"] = summary["total_price"] / summary["units"]
    summary["current_price"] = summary.apply(get_current_price, axis=1)
    summary["current_total_price"] = summary["current_price"] * summary["units"]
    summary["profit"] = summary["current_total_price"] - summary["total_price"]
    summary["change"] = (summary["current_price"] / summary["mean_price"] * 100) - 100
    return summary


def get_overview(data: pd.DataFrame) -> None:
    current_overall_portfolio_price = data["current_total_price"].sum()
    overall_portfolio_price = data["total_price"].sum()
    overall_appreciation = current_overall_portfolio_price - overall_portfolio_price

    # Vytvoření textového výstupu
    text_output = f"""
	<div style="display:flex; justify-content: space-between;">

		<div style="width: 350px; background-color:#f2f2f2; padding:20px; border-radius: 10px;">
			<h2>Celková hodnota portfolia</h2>
			<p style="font-size:18px; color:#008080;">{current_overall_portfolio_price:.2f} Kc</p>
		</div>

		<div style="width: 350px; background-color:#f2f2f2; padding:20px; border-radius: 10px;">
			<h2>Investováno</h2>
			<p style="font-size:18px; color:#008080;">{overall_portfolio_price:.2f} Kc</p>
		</div>

		<div style="width: 350px; background-color:#f2f2f2; padding:20px; border-radius: 10px;">
			<h2>Celkové nerealizované zhodnocení</h2>
			<p style="font-size:18px; color:#008080;">{overall_appreciation:.2f} Kc</p>
			<p style="font-size:15px; color:#008080;">{overall_appreciation/overall_portfolio_price*100:.2f} % z investované částky</p>
		</div>
	</d
	"""

    # Zobrazení textového výstupu
    display(HTML(text_output))


def get_dividends(data: pd.DataFrame) -> pd.DataFrame:
    dividends = pd.DataFrame(
        columns=["name","ticker", "date", "year", "total_gain_czk", "currency"]
    )
    for ticker in data["ticker"].unique():
        stock = yf.Ticker(ticker)
        currency = data[data["ticker"] == ticker].iloc[0]["currency"]
        name = data[data["ticker"] == ticker].iloc[0]["name"]
        # stock_dividends = stock.actions.reset_index()
        stock_dividends = stock.dividends.reset_index()
        if len(stock_dividends) == 0:
            continue
        stock_dividends["Date"] = stock_dividends["Date"].dt.strftime("%Y-%m-%d")
        stock_dividends["year"] = stock_dividends["Date"].str.split("-", expand=True)[0]
        if (
            ticker == "KOMB.PR"
            and not stock_dividends["Date"].str.contains("2023").any()
        ):
            stock_dividends.loc[len(stock_dividends)] = ["2023-04-20", 60.42, "2023"]
        stock_dividends["units"] = stock_dividends["Date"].apply(
            lambda x: data[(data["date"] <= x) & (data["ticker"] == ticker)][
                "units"
            ].sum()
        )
        stock_dividends = stock_dividends[stock_dividends["units"] != 0]
        stock_dividends["total_gain"] = (
            stock_dividends["Dividends"] * stock_dividends["units"]
        )
        stock_dividends["total_gain_czk"] = (
            stock_dividends["Date"].apply(lambda x: get_exchange_rate(currency, x))
            * stock_dividends["total_gain"]
        )
        for index, row in stock_dividends.iterrows():
            dividends.loc[len(dividends)] = [
                name,
                ticker,
                row["Date"],
                row["year"],
                row["total_gain_czk"],
                currency,
            ]
    return dividends


def get_dividend_prediction(data: pd.DataFrame, year: int) -> None:
    dividends = pd.DataFrame(
        columns=["ticker", "date", "year", "total_gain_czk", "currency"]
    )
    for ticker in data["ticker"].unique():
        stock = yf.Ticker(ticker)
        currency = data[data["ticker"] == ticker].iloc[0]["currency"]
        # stock_dividends = stock.actions.reset_index()
        stock_dividends = stock.dividends.reset_index()
        if len(stock_dividends) == 0:
            continue
        # print(stock_dividends)
        stock_dividends["Date"] = stock_dividends["Date"] + pd.DateOffset(years=1)
        stock_dividends["Date"] = stock_dividends["Date"].dt.strftime("%Y-%m-%d")
        stock_dividends["year"] = stock_dividends["Date"].str.split("-", expand=True)[0]
        if (
            ticker == "KOMB.PR"
            and not stock_dividends["Date"].str.contains("2024").any()
        ):
            stock_dividends.loc[len(stock_dividends)] = ["2024-04-20", 60.42, "2024"]
        stock_dividends["units"] = stock_dividends["Date"].apply(
            lambda x: data[(data["date"] <= x) & (data["ticker"] == ticker)][
                "units"
            ].sum()
        )
        stock_dividends = stock_dividends[
            (stock_dividends["units"] != 0) & (stock_dividends["year"] == str(year))
        ]
        # print(ticker,stock_dividends)
        stock_dividends["total_gain"] = (
            stock_dividends["Dividends"] * stock_dividends["units"]
        )
        stock_dividends["total_gain_czk"] = (
            stock_dividends["Date"].apply(lambda x: get_exchange_rate(currency, x))
            * stock_dividends["total_gain"]
        )
        for index, row in stock_dividends.iterrows():
            dividends.loc[len(dividends)] = [
                ticker,
                row["Date"],
                row["year"],
                row["total_gain_czk"],
                currency,
            ]
    return dividends


if __name__ == "__main__":
    # trades = read_trades(filter=["BTC-USD","IWDA.AS"])
    trades = read_trades()
    print(trades)
    collect_historical_data(trades)
    trades["total_price"] = trades.apply(get_total_price_in_czk, axis=1)
    print(trades)
    summary = (
        trades.groupby("ticker")[["units", "total_price", "currency", "type"]]
        .agg(
            {"units": "sum", "total_price": "sum", "currency": "first", "type": "first"}
        )
        .reset_index()
    )
    summary["mean_price"] = summary["total_price"] / summary["units"]
    print(summary)
    summary["current_price"] = summary.apply(get_current_price, axis=1)
    summary["current_total_price"] = summary["current_price"] * summary["units"]
    summary["profit"] = summary["current_total_price"] - summary["total_price"]
    summary["change"] = (summary["current_price"] / summary["mean_price"] * 100) - 100
    print(summary)
    print(summary["total_price"].sum(), summary["current_total_price"].sum())
    print(
        "Celkovy zisk:",
        summary["current_total_price"].sum() - summary["total_price"].sum(),
    )
    print(
        "Celkove zhodnoceni:",
        (summary["current_total_price"].sum() - summary["total_price"].sum())
        / summary["total_price"].sum(),
    )

    print(
        summary.groupby("type")["current_total_price"].agg("sum")
        / summary["current_total_price"].sum()
    )
    print(
        summary.groupby("currency")["current_total_price"].agg("sum")
        / summary["current_total_price"].sum()
    )
    print(
        summary.groupby("ticker")["current_total_price"].agg("sum")
        / summary["current_total_price"].sum()
    )

    show_portfolio_breakdown(summary)
    show_portfolio_growth(summary)
    save_exchange_rates()
