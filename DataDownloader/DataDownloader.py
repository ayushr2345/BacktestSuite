print ("Data Downloader")
def download_data(
    symbol = "",
    timeFrame = "",
    startDate = "",
    endDate = ""
    ):
    print("We are inside download_data function")
    if (symbol == "" or timeFrame == "" or startDate == "" or endDate == ""):
        raise ValueError("All parameters must be provided")
    else:
        print("All parameters are provided")
    print(f"Downloading data for {symbol} on {timeFrame} timeframe from {startDate} to {endDate}")
    # Add code to download data from the API here
