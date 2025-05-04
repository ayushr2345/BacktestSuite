import os
import time
import pyotp
import sqlite3
import pandas as pd
from py5paisa import FivePaisaClient
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()


class FivePaisaDownloader:
    def __init__(self, creds: dict, totp_secret: str):
        """
            creds = {
                "APP_NAME"      : "<YOUR_APP_NAME>",
                "USER_ID"       : "<YOUR_USER_ID>",
                "APP_SOURCE"    : "<YOUR_APP_SOURCE>",
                "PASSWORD"      : "<YOUR_PASSWORD>",
                "USER_KEY"      : "<YOUR_USER_KEY>",
                "ENCRYPTION_KEY": "<YOUR_ENCRYPTION_KEY>"
            }
        """
        self.creds = creds
        self.totp = pyotp.TOTP(totp_secret)
        self.client = None
        self.data_path = "data"
        self.scrip_master = "data/scrip_master.db"
        self.time_list = ['1m', '5m', '10m', '15m', '30m', '60m', '1d']
        self.exch_map = {
            'N': 'NSE',
            'B': 'BSE',
            'M': 'MCX',
            'n': 'NCDEX'
        }
        self.exchange_segment_map = {
            'c': 'Cash',
            'd': 'Derivatives',
            'u': 'Currency_Derivatives',
            'x': 'NCDEX_Commodity',
            'y': 'NSE_BSE_Commodity'
        }

    def generate_totp(self) -> str:
        return self.totp.now()

    def connect(self):
        print("Connecting to 5Paisa...")
        self.client = FivePaisaClient(cred = self.creds)

        for attempt in range(2):  # 2 attempts max: first try + one retry
            try:
                resp = self.client.get_totp_session(
                    os.getenv("CLIENT_ID"),
                    self.generate_totp(),
                    os.getenv("APP_PIN")
                )
                if resp is None:
                    raise Exception("Login response is None")
                print("Logged in to 5Paisa successfully.")
                break  # Successful login, exit loop
            except Exception as e:
                if attempt == 0:
                    print(f"Login failed, retrying in 30 seconds...\nError: {e}")
                    time.sleep(30)
                else:
                    raise Exception("Could not log in to 5Paisa after retry. Please verify your credentials.")
        self.check_and_update_scrip_master()

    def check_and_update_scrip_master(self):
        file_path = "data/scrip_master.csv"
        needs_update = True

        if not os.path.exists(self.data_path):
            print(f"Directory {self.data_path} does not exist. Creating it")
            os.makedirs(self.data_path)

        if os.path.exists(file_path):
            modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if datetime.now() - modified_time < timedelta(days=7):
                print("scrip_master.csv is up to date.")
                needs_update = False
            else:
                print("scrip_master.csv is older than 7 days. Updating...")

        if needs_update:
            scrip_data_frame = self.client.get_scrips()
            if (scrip_data_frame is None):
                raise Exception(f"Could not fetch Scrip Master.")
            scrip_data_frame.to_csv(file_path, index=False)
            print("scrip_master.csv has been updated.")

        self.setup_database()
        self.store_scrip_master_to_db(csv_path=file_path)

    def setup_database(self):
        """
        Sets up the scrip master SQLite database and table.
        Creates the table if it does not already exist
        """
        conn = sqlite3.connect(self.scrip_master)
        cursor = conn.cursor()
    
        # Create table with only the necessary fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrip_master (
                Exch TEXT,
                ExchType TEXT,
                ScripCode INTEGER PRIMARY KEY,
                Name TEXT,
                Expiry TEXT,
                StrikeRate REAL,
                FullName TEXT
            )
        ''')
    
        conn.commit()
        print(f"Database setup completed at {self.scrip_master}")
        return conn

    def store_scrip_master_to_db(self, csv_path: str):
        df = pd.read_csv(csv_path)
        selected_cols = ["Exch", "ExchType", "ScripCode", "Name", "Expiry", "StrikeRate", "FullName"]
        df = df[selected_cols]

        conn = sqlite3.connect(self.scrip_master)
        df.to_sql("scrip_master", conn, if_exists="replace", index=False)
        conn.close()
        print("Scrip master stored to DB successfully.")

    def get_scrip_code_by_name(self, name: str) -> int:
        conn = sqlite3.connect(self.scrip_master)
        cursor = conn.cursor()

        print (f"Searching Scrip code for Scrip name: {name}")
        print (f"Searching NSE for Scrip name: {name}")
        # 1. Try exact match in NSE
        cursor.execute(
            "SELECT ScripCode FROM scrip_master WHERE Name = ? AND Exch = 'N' COLLATE NOCASE", 
            (name,)
        )
        result = cursor.fetchone()

        print (f"Searching BSE for Scrip name: {name}")
        # 2. If not found, try exact match in BSE
        if not result:
            cursor.execute(
                "SELECT ScripCode FROM scrip_master WHERE Name = ? AND Exch = 'B' COLLATE NOCASE", 
                (name,)
            )
            result = cursor.fetchone()

        searched_partially = False
        print (f"Searching NSE partially for Scrip name: {name}")
        # 3. If still not found, try partial match in NSE
        if not result:
            searched_partially = True
            cursor.execute(
                "SELECT ScripCode FROM scrip_master WHERE Name LIKE ? AND Exch = 'N' COLLATE NOCASE LIMIT 1", 
                (f"%{name}%",)
            )
            result = cursor.fetchone()

        print (f"Searching BSE partially for Scrip name: {name}")
        # 4. If still not found, try partial match in BSE
        if not result:
            searched_partially = True
            cursor.execute(
                "SELECT ScripCode FROM scrip_master WHERE Name LIKE ? AND Exch = 'B' COLLATE NOCASE LIMIT 1", 
                (f"%{name}%",)
            )
            result = cursor.fetchone()

        if searched_partially is True:
            print (f"For Scrip name: {name}, the scrip code is partially searched with scrip code being: {result[0]}. Please verify that the correct Scrip is fetched!!! ")
        conn.close()
        return result[0] if result else None

    def get_scrip_name_by_code(self, scrip_code: int) -> tuple:
        """
        Returns a tuple of (Name, FullName, Exch) for the given ScripCode.
        """
        conn = sqlite3.connect(self.scrip_master)
        cursor = conn.cursor()
    
        cursor.execute(
            "SELECT Name, FullName, Exch FROM scrip_master WHERE ScripCode = ?", 
            (scrip_code,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            name, full_name, exch = result
            print(f"ScripCode {scrip_code} corresponds to: {name} ({full_name}), Exchange: {exch}")
            return result
        else:
            print(f"No scrip found with ScripCode {scrip_code}")
            return None


    def validate_exchange_segment_and_time(self, time: str, Exch: str, ExchangeSegment: str):
        if time not in self.time_list:
            raise Exception("Invalid Time Frame, it should be within ['1m', '5m', '10m', '15m', '30m', '60m', '1d'].")
        if Exch not in self.exch_map:
            raise Exception("Invalid Exchange, it should be within ['N', 'B', 'M', 'n'].")
        if ExchangeSegment not in self.exchange_segment_map:
            raise Exception("Invalid Exchange Segment, it should be within ['c', 'd', 'u', 'x', 'y'].")

    def get_historical_data(self, Exch: str, ExchangeSegment: str, ScripNames: list, time: str, From: str, To: str):
        """
            Exch:            "<N (NSE), B (BSE), M (MCX), n (NCDEX)>",
            ExchangeSegment: "<c (Cash), d (Derivatives), u (Currency Derivatives), x (NCDEX Commodity), y (NSE & BSE Commodity)>",
            ScripCode:       <Scrip-Code from Scrip master>,
            time:            "<1m, 5m, 10m, 15m, 30m, 60m, 1d>",
            From:            "<YYYY-MM-DD>",
            To:              "<YYYY-MM-DD>"
        """

        if (Exch == "" or ExchangeSegment == "" or len(ScripNames) == 0 or time == "" or From == "" or To == ""):
            raise Exception("Aruments missing. Please provide all the arguments")
        if self.client is None:
            raise Exception("Not connected. Call connect() first.")
        self.validate_exchange_segment_and_time(time, Exch, ExchangeSegment)

        fetched_scrip_codes = []
        for i in range(0, len(ScripNames)):
            fetched_scrip_code = self.get_scrip_code_by_name(ScripNames[i])
            if fetched_scrip_code is None:
                raise Exception(f"No matches found for the scrip name ")
            fetched_scrip_codes.append(fetched_scrip_code)

        if len(fetched_scrip_codes) != len(ScripNames):
            raise Exception("Could not find scrip codes for all the Scrip names provided")

        scrip_codes_map = dict(zip(fetched_scrip_codes, ScripNames))
        print("Printing Scrip Codes and their corresponding Names:")
        for scrip_code in scrip_codes_map:
            print (f"{scrip_code} : {scrip_codes_map[scrip_code]}")

        exchange_name = self.exch_map.get(Exch, Exch)
        exchange_segment_name = self.exchange_segment_map.get(ExchangeSegment, ExchangeSegment)

        if (time == '1d'):
            for scrip_code in scrip_codes_map:
                ScripCode = scrip_code
                ScripName = scrip_codes_map[scrip_code]
                print(f"Fetching data for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {From} to {To}.")
                file_name = f"data/{ScripName}/{ScripName}_{exchange_name}_{exchange_segment_name}_{time}_{From}_to_{To}.csv"
                if (os.path.exists(file_name)):
                    print(f"Data already exists for {ScripName} at {file_name}, skipping download.")
                    return

                data_frame = self.client.historical_data(Exch, ExchangeSegment, ScripCode, time, From, To)
                if (data_frame is None):
                    raise Exception(f"Could not fetch historical data for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {From} to {To}.")
                if (data_frame.empty):
                    print(f"No data found for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {From} to {To}.")
                    return

                data_frame['Datetime'] = data_frame['Datetime'].apply(lambda x: datetime.strptime(str(x), "%Y-%m-%dT%H:%M:%S").date())
                self.save_to_csv(data_frame, file_name)
        else:
            self.get_historical_intraday_data(Exch, ExchangeSegment, scrip_codes_map, time, From, To)

    def get_historical_intraday_data(self, Exch: str, ExchangeSegment: str, ScripCodesMap: dict, time: str, From: str, To: str):
        """
            Exch:            "<N (NSE), B (BSE), M (MCX), n (NCDEX)>",
            ExchangeSegment: "<c (Cash), d (Derivatives), u (Currency Derivatives), x (NCDEX Commodity), y (NSE & BSE Commodity)>",
            ScripCode:       <Scrip-Code from Scrip master>,
            time:            "<1m, 5m, 10m, 15m, 30m, 60m>",
            From:            "<YYYY-MM-DD>",
            To:              "<YYYY-MM-DD>"
        """
        time_list = ['1m', '5m', '10m', '15m', '30m', '60m']
        if time not in time_list:
            raise Exception("Invalid Time Frame, it should be within ['1m', '5m', '10m', '15m', '30m', '60m'].")
        if ScripCodesMap is None:
            raise Exception(f"Empty Dict received in get_intraday_historocal_data()")

        exchange_name = self.exch_map.get(Exch, Exch)
        exchange_segment_name = self.exchange_segment_map.get(ExchangeSegment, ExchangeSegment)

        for scrip_code in ScripCodesMap:
            ScripCode = scrip_code
            ScripName = ScripCodesMap[scrip_code]
            file_name = f"data/{ScripName}/{ScripName}_{exchange_name}_{exchange_segment_name}_{time}_{From}_to_{To}.csv"
            if (os.path.exists(file_name)):
                print(f"Data already exists for {ScripName} at {file_name}, skipping download.")
                return

            print(f"Fetching intraday data for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {From} to {To}.")

            start_date = datetime.strptime(From, "%Y-%m-%d")
            end_date = datetime.strptime(To, "%Y-%m-%d")
            data_frames = []
            time_delta = timedelta(days=180)
            current_date = start_date

            while current_date < end_date:
                current_end_date = min(end_date, current_date + time_delta)
                data_frame = self.client.historical_data(Exch, ExchangeSegment, ScripCode, time, current_date.strftime("%Y-%m-%d"), current_end_date.strftime("%Y-%m-%d"))
                if (data_frame is None):
                    raise Exception(f"Could not fetch historical data for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {current_date} to {current_end_date}.")
                if (data_frame.empty):
                    print(f"No data found for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {current_date} to {current_end_date}.")
                    current_date = current_end_date + timedelta(1)
                    continue

                data_frames.append(data_frame)
                current_date = current_end_date + timedelta(1)

            if (len(data_frames) == 0):
                raise Exception(f"No data found for {ScripName} belonging to Exchange {exchange_name} and segment {exchange_segment_name} for {time} interval from {From} to {To}.")
            print(f"As time period is greater than 6 months: {From} to {To}, downloaded data in chunks of 6 months")
            complete_data_frame = pd.concat(data_frames)

            self.save_to_csv(complete_data_frame, file_name)

    def save_to_csv(self, df: pd.DataFrame, filename: str):
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Creating it")
            os.makedirs(directory)

        print(f"Saving to {filename}...")
        df.to_csv(filename, index=False)
        print("Saved successfully.")
