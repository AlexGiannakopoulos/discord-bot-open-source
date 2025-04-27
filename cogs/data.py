import os
import json
import datetime


class Data():
    def __init__(self, bot):
        self.bot = bot

    # Data storage using JSON files)
    def load_data(filename):
        try:
            with open(f'data/{filename}.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    # Helper class to encode datetime automatically
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return super().default(obj)

    # Helper function to serialize datetime objects for JSON
    @staticmethod
    def serialize_datetime(obj):
        if isinstance(obj, dict):
            return {k: Data.serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Data.serialize_datetime(i) for i in obj]
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return obj    

    @staticmethod                   #doesnt use self 
    def save_data(data, filename):
        os.makedirs('data', exist_ok=True)
        with open(f'data/{filename}.json', 'w') as f:
            json.dump(data, f, indent=4, cls=Data.DateTimeEncoder)

async def setup(bot):
    await bot.add_cog(Data(bot))
