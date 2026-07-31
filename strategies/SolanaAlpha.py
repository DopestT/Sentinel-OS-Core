"""Freqtrade strategy using RSI and Bollinger Band mean reversion signals."""

from freqtrade.strategy import IStrategy
import talib.abstract as ta
from pandas import DataFrame


class SolanaAlpha(IStrategy):
    """Long-only, five-minute mean reversion strategy."""

    INTERFACE_VERSION = 3
    timeframe = "5m"
    can_short = False

    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    minimal_roi = {
        "0": 0.05,
        "15": 0.02,
        "40": 0.015,
        "120": 0.01,
    }

    def populate_indicators(
        self, dataframe: DataFrame, metadata: dict
    ) -> DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

        bollinger = ta.BBANDS(
            dataframe,
            timeperiod=20,
            nbdevup=2.0,
            nbdevdn=2.0,
        )
        dataframe["bb_lowerband"] = bollinger["lowerband"]
        dataframe["bb_middleband"] = bollinger["middleband"]
        dataframe["bb_upperband"] = bollinger["upperband"]

        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(
        self, dataframe: DataFrame, metadata: dict
    ) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] < 35)
                & (dataframe["close"] < dataframe["bb_lowerband"])
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(
        self, dataframe: DataFrame, metadata: dict
    ) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["rsi"] > 70)
                | (dataframe["close"] > dataframe["bb_upperband"])
            ),
            "exit_long",
        ] = 1
        return dataframe
