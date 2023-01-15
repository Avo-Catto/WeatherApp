"""
Developed by AVCDO

Used 2 API's:
    https://opencagedata.com/
    https://open-meteo.com/
"""

from urllib.request import urlopen
from json import load
from ctypes import WinDLL
from ssl import _create_unverified_context
from datetime import datetime
from sys import argv


class parser:
    def __init__(self) -> None:
        self.args = argv
        self.__looking_for = {}

    def add_arg(self, short:str, access_name:str) -> None:
        """Add callable args."""

        self.__looking_for.update({
                short.strip(): access_name.strip()
            })
    
    def get_args(self) -> dict:
        """Get callable args with parsed args as dict."""

        output = {}

        try:
            for short, name in self.__looking_for.items():
                output.update({
                    name: self.args[self.args.index(short) + 1].strip()
                })

        except Exception:
            pass

        return output

# args
argparser = parser()
argparser.add_arg('-p', 'place')
args = argparser.get_args()

# API's
COORDS_API = 'https://api.opencagedata.com/geocode/v1/json?q={}&key={}'
COORDS_KEY = '09d8ae166e94487ea1f673eeddbf4b04'
COORDS_JSON = (
    ['geometry', 'lat'], ['geometry', 'lng'], ['annotations', 'timezone', 'name'], 
    ['components', 'country'], ['components', 'postcode'], ['components', 'town'],
    ['components', 'city']
)

WEATHER_API = 'https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}&precipitation_hours&current_weather=1&daily=temperature_2m_max&daily=temperature_2m_min&daily=sunrise&daily=sunset&timezone={}'

# Colors
CYAN = '\033[0;36m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RESET = '\033[0m'


def fix_windows_colors() -> None:
    """Fix colors for windows console."""

    kernel = WinDLL('kernel32')
    kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)
    del kernel


def average(*nums:float) -> float:
    """Calculate average of many numbers."""

    avr = 0.0
    for i in nums:
        avr += i

    return round(avr / len(nums), 1)


def get_sun_time(times:list) -> list[str]:
    """Slice date and time and return time."""

    suntimes = []
    for i in times:
        suntimes.append(i.split(sep='T')[1])

    return suntimes


def get_days() -> list[str]:
    """Get names of days."""
    
    days = []
    today = datetime.today().weekday()

    for i in range(7):
        match today + i:
            case 0: days.append('Monday')
            case 1: days.append('Tuesday')
            case 2: days.append('Wednesday')
            case 3: days.append('Thursday')
            case 4: days.append('Friday')
            case 5: days.append('Saturday')
            case 6: days.append('Sunday')
            case 7: 
                days.append('Monday')
                today = -1

    return days


def get_data_by_keys(dic:dict, keys:tuple) -> dict:
    """Generate dictionary with all keys from bigger dictionary."""

    output = {}
    for acc in keys:
        val = dic.get(acc[0])
        acc.pop(0)

        for key in acc:
            val = val.get(key)

        output.update({acc[-1]: val})

    return output


def get_weather(place:str) -> dict:
    """Get weather by name of place."""

    # get coords by place name
    with urlopen(COORDS_API.format(place.encode(), COORDS_KEY)) as data:
        meta = load(data).get('results')[0]
        meta = get_data_by_keys(meta, COORDS_JSON)
        addr = (meta.get('postcode') if meta.get('postcode') is not None else '', meta.get('town') if meta.get('town') is not None else meta.get('city'), meta.get('country'))
    
    # get weather data
    with urlopen(WEATHER_API.format(meta.get('lat'), meta.get('lng'), meta.get('name')), context=_create_unverified_context()) as meta:
        meta = load(meta)
        curr = meta.get('current_weather').get('temperature')
        meta = meta.get('daily')
        
        temperatures = []
        times = meta.get('time')
        sunrise = get_sun_time(meta.get('sunrise'))
        sunset = get_sun_time(meta.get('sunset'))
        days = get_days()
        
        for idx in range(7): # assign temperatures
            temperatures.append(average(meta.get('temperature_2m_max')[idx], meta.get('temperature_2m_min')[idx]))
    
    # display data
    fix_windows_colors()
    print(f'\n{YELLOW}Forecast for: {BLUE}{addr[0]} {addr[1]}, {addr[2]}\n')
    print(f'{CYAN}Current temperature: {RED}{curr} °C\n')

    for idx, day in enumerate(days):
        print(f'\n{YELLOW}{day} {RESET}| {BLUE}{times[idx]}\n')
        print(f'{CYAN}Average temperature:  {RED}{temperatures[idx]} °C')
        print(f'{CYAN}Sunrise:              {RED}{sunrise[idx]}')
        print(f'{CYAN}Sunset:               {RED}{sunset[idx]}\n')
    
    print(RESET)


if __name__ == '__main__':
    try:
        get_weather(args.get('place'))
    except:
        print('\nNeed help?\n\tTry: weatherapp.exe -p [town]/[district]\n\tExample: weatherapp.exe -p Berlin\n')
