from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
import talib.abstract as ta
from pandas import DataFrame


class SolanaAlpha(IStrategy):
    # --- Strategy Settings ---
    INTERFACE_VERSION = 3
    timeframe = '5m'
    can_short = False  # Set to True only if using Futures

    # --- Risk Management (Production Standard) ---
    stoploss = -0.10  # Hard stop at 10%
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    # ROI Table: Sell quickly if profit hits targets
    minimal_roi = {
        "0": 0.05,      # 5% profit at 0 mins
        "15": 0.02,     # 2% profit after 15 mins
        "40": 0.015,    # 1.5% profit after 40 mins
        "120": 0.01     # 1% profit after 2 hours
    }

    # --- 1. INDICATORS (The Eyes) ---
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']

        # ATR (Average True Range) for Volatility detection
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        return dataframe

    # --- 2. ENTRY LOGIC (The Brain) ---
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < 35) &  # Oversold condition
                (dataframe['close'] < dataframe['bb_lowerband']) &  # Price below lower band
                (dataframe['volume'] > 0)  # Ensure there is liquidity
            ),
            'enter_long'] = 1
        return dataframe

    # --- 3. EXIT LOGIC (The Hands) ---
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > 70) |  # Overbought exit
                (dataframe['close'] > dataframe['bb_upperband'])  # Above upper band exit
            ),
            'exit_long'] = 1
        return dataframe
