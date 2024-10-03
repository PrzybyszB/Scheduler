from datetime import datetime

def convert_txt_to_json(txt_content):
    lines = txt_content.splitlines()
    header = lines[0].split(",")  
    json_data = []

    for line in lines[1:]:
        values = line.split(",")
        json_data.append(dict(zip(header, values)))

    return json_data

    # stop_times.txt contain trip ID and stops_id in order(stop_sequence) and last stop(stop_headsign)
    
    # --> trips.txt with Trip ID contain route_id --> route_id

with open('stop_times.txt', 'r', encoding='utf-8-sig') as file:
    stop_times_data = file.read()

with open('trips.txt', 'r', encoding='utf-8-sig') as file:
    trips_data = file.read()

with open('stops.txt', 'r', encoding='utf-8-sig') as file:
    stops_data = file.read()

with open('calendar.txt', 'r', encoding='utf-8-sig') as file:
    calendar_data = file.read()

# with open('GTFS-ZTM/GTFS-ZTM-STATIC/stop_times.txt', 'r', encoding='utf-8-sig') as file:
#     stop_times_data = file.read()
# with open('GTFS-ZTM/GTFS-ZTM-STATIC/trips.txt', 'r', encoding='utf-8-sig') as file:
#     trips_data = file.read()
# with open('GTFS-ZTM/GTFS-ZTM-STATIC/stops.txt', 'r', encoding='utf-8-sig') as file:
#     stops_data = file.read()
# with open('GTFS-ZTM/GTFS-ZTM-STATIC/calendar.txt', 'r', encoding='utf-8-sig') as file:
#     calendar_data = file.read()
    

stop_times_json_data = convert_txt_to_json(stop_times_data)
trips_json_data = convert_txt_to_json(trips_data)
stops_json_data = convert_txt_to_json(stops_data)
calendar_json_data = convert_txt_to_json(calendar_data)


routes = {}
stops_dict = {}

      
route_id ="16"

# Make dict with stops
stops_dict = {}
for stops in stops_json_data:
    stop_id = stops['stop_id']
    stop_name = stops['stop_name']
    stops_dict[stop_id] = stop_name

# Itereting data from trips.txt to get trip_id
for trips in trips_json_data:
    trips_route_id = trips['route_id']
    if trips_route_id == route_id:
        trip_id = trips['trip_id']
        direction_id = trips['direction_id']
        service_id = trips['service_id']
        routes[trip_id] = {
            'direction_id': direction_id,
            'service_id': service_id,
            'stops': []
        }
        
# Itereting data from stop_times.txt to get departure time and trip_id
for stop_times in stop_times_json_data:
    stop_times_trip_id = stop_times['trip_id']
    stop_times_stop_id = stop_times['stop_id']
    departure_time = stop_times['departure_time']
    stop_headsign = stop_times['stop_headsign']
    
    # Check that stop_times_trip_id is the same like in trip_id in routes
    if stop_times_trip_id in routes:
        stop_name = stops_dict.get(stop_times_stop_id, None)
        if stop_name:
            routes[stop_times_trip_id]['stops'].append({
                'stop_id': stop_times_stop_id,
                'stop_name': stop_name,
                'departure_time': departure_time,
                'stop_headsign': stop_headsign,
            })


# Itereting departure time on stops for trip id 
departure_times = {}
departure_times_list = []
monday = []
tuesday = []
wednesday = []
thursday = []
friday = []
saturday = []
sunday = []


for trip_id, trip_details in routes.items():
    direction_id = trip_details['direction_id']
    service_id = trip_details['service_id']
    
    for stop in trip_details['stops']:
        stop_headsign = stop['stop_headsign']
        stop_name = stop['stop_name']

        if stop['stop_id'] == "214":
            departure_time = stop['departure_time']

            print(f'Trip id: {trip_id},Direction_id : {direction_id} Services ID : {service_id}, Departure Times: {departure_time}')

            if 'departure_time_list' not in departure_times:
                    # Chciałem na początku zrobić nazwa przystanku  i reszta danych i z tego zrobic liste departure_time ale pokazały sie duplikaty godzin i sie okazało że jeszcze jest services_id który wyznacza dni tygodnia w któe kursuje
                    departure_times = {
                        'stop_name': stop_name,
                        'stop_headsign': stop_headsign,
                        'departure_times_list': departure_times_list
                    }
            departure_time_obj = datetime.strptime(departure_time, "%H:%M:%S").time()
            departure_times['departure_times_list'].append(departure_time_obj)


# Sorted time object
sorted_departure_times = sorted(departure_times_list)
# for time in sorted_departure_times:
#     print(time)    
'''
CHAT


Pobranie wszystkich plików calendar.txt z Redis: Możesz pobrać wszystkie dostępne pliki z Redis, gdzie każdy plik ma ograniczony TTL do 15 dni. W ten sposób masz dostęp tylko do najnowszych danych.

Łączenie plików: Wczytujesz wszystkie pliki do jednego zbioru danych, np. do listy lub DataFrame (jeśli korzystasz z Pythona i pandas).

Sprawdzanie daty: Wyszukujesz rozkłady, które obejmują dzisiejszą datę (start_date <= dzisiaj <= end_date).

Wybór odpowiednich dni: Jeżeli znajdziesz rozkład dla dzisiejszego dnia, sprawdzasz, czy zawiera on jedynki (1) dla każdego dnia tygodnia. Jeżeli brakuje jedynek dla niektórych dni, wracasz do poprzednich plików i uzupełniasz brakujące dni.

Cofanie się o plik, jeśli brak dni: Jeżeli w jednym pliku brakuje informacji o jakimś dniu tygodnia, pobierasz dane z wcześniejszego pliku, aż znajdziesz pełny zestaw jedynek na cały tydzień.

import redis
import pandas as pd
from datetime import datetime

# 1. Połączenie z Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 2. Pobranie wszystkich plików calendar.txt z Redis (zakładamy, że pliki są zapisane w formacie CSV)
calendar_keys = r.keys('calendar*')  # Pobierz klucze, które zawierają calendar.txt
calendars = []

for key in calendar_keys:
    csv_data = r.get(key).decode('utf-8')  # Pobierz i zdekoduj dane z Redis
    df = pd.read_csv(pd.compat.StringIO(csv_data))  # Konwersja CSV na DataFrame
    calendars.append(df)

# 3. Połączenie wszystkich kalendarzy w jeden DataFrame
calendar_df = pd.concat(calendars)

# Funkcja sprawdzająca czy data mieści się w przedziale dat
def is_date_in_range(row, date):
    start = datetime.strptime(str(row['start_date']), '%Y%m%d')
    end = datetime.strptime(str(row['end_date']), '%Y%m%d')
    return start <= date <= end

# 4. Funkcja do pobierania aktywnego service_id na podstawie daty
def get_service_ids_for_date(date):
    day_of_week = date.strftime('%A').lower()  # np. 'monday', 'tuesday'
    
    # Filtracja danych pod kątem daty
    valid_rows = calendar_df[
        (calendar_df.apply(is_date_in_range, axis=1, date=date)) &  # Data w zakresie
        (calendar_df[day_of_week] == 1)  # Odpowiedni dzień tygodnia ma wartość 1
    ]
    
    # Zwraca listę service_id
    return valid_rows['service_id'].tolist()

# 5. Szukanie pełnego tygodnia z jedynkami
def get_full_week_schedule(date):
    current_date = date
    full_week = {}  # Przechowujemy dni tygodnia z jedynkami
    
    # Dni tygodnia w formacie 'monday', 'tuesday' itd.
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for day in days_of_week:
        while day not in full_week:
            service_ids = get_service_ids_for_date(current_date)
            if service_ids:
                full_week[day] = service_ids
            else:
                # Cofamy się o jeden plik (czyli szukamy wcześniejszych danych)
                current_date = current_date - timedelta(days=1)
    
    return full_week

# 6. Wywołanie funkcji i wyświetlenie rozkładu na cały tydzień
today = datetime.now()
schedule = get_full_week_schedule(today)
print(schedule)


'''
    

'''
Route_id = 16
Departure_time = 4:26:00
Stops_id = 214
Stos_name = Piaśnicka Rynek

There is four duplicate data above, in diffrent trips_id

Trip_id = "1_5197686^N+", "3_5201188^N" , "5_5206981^N+", "7_5211349^N+"

but in trips.txt we got service_id,

Trip_id ---> "1_5197686^N+" ---> service_id 1
Trip_id ---> "3_5201188^N" ---> service_id 3
Trip_id ---> "5_5206981^N+"---> service_id 5
Trip_id ---> "7_5211349^N+" ---> service_id 7

service_id lead us to calendar.txt that conatin calendary of routes.
chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.ztm.poznan.pl/assets/pliki/Specyfikacja-GTFS-04.02.2022.pdf

Dane w gtfs sa wrzucane w różne dni i np jeżeli wrzucą w piatek i obowiazują do niedzieli to calendar.txt nie zawiera informacji o kursach od pon-czw, jak powinienm ustawić rozkład jazdy dla danego przystnaku ? Jeżeli w calendar txt jest none to zostaw dane z poprzedniego pliku ? ale te service id sie zmieniaja


SCHEMATY wyszukane nie różne xD
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday
1,0,1,1,1,0,0,0
1,0,1,0,0,0,0,0
3,0,0,0,0,0,1,0
4,0,0,0,0,0,0,1
4,1,0,0,0,0,0,0
5,1,0,0,0,0,0,0
7,0,0,0,0,1,0,0


jeden calendar.txt wygląda tak 23.08.2024-25.08.2024

service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
9,0,0,0,0,0,0,1,20240823,20240825
7,0,0,0,0,1,0,0,20240823,20240825
3,0,0,0,0,0,1,0,20240823,20240825

drugi calendar.txt wygląda tak 31.08.2024-05.09.2024

service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
4,0,0,0,0,0,0,1,20240831,20240905
1,0,1,1,1,0,0,0,20240831,20240905
5,1,0,0,0,0,0,0,20240831,20240905
3,0,0,0,0,0,1,0,20240831,20240905

trzeci(obecny) calendar.txt wygląda tak 07.09.2024-30.09.2024

service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
4,0,0,0,0,0,0,1,20240907,20240930
1,0,1,1,1,0,0,0,20240907,20240930
5,1,0,0,0,0,0,0,20240907,20240930
7,0,0,0,0,1,0,0,20240907,20240930
3,0,0,0,0,0,1,0,20240907,20240930

czwarty calendar.txt wygląda tak 03.09.2024-08.09.2024

service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
4,0,0,0,0,0,0,1,20240903,20240908
1,0,1,1,1,0,0,0,20240903,20240908
7,0,0,0,0,1,0,0,20240903,20240908
3,0,0,0,0,0,1,0,20240903,20240908

piąty calendar.txt wygląda tak 14.06.2024-16.06.2024

service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
4,0,0,0,0,0,0,1,20240614,20240616
7,0,0,0,0,1,0,0,20240614,20240616
3,0,0,0,0,0,1,0,20240614,20240616

szósty calendar.txt wygląda tak 01.04.2024-02.04-2024

service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
4,1,0,0,0,0,0,0,20240401,20240402
1,0,1,0,0,0,0,0,20240401,20240402

--------------------TEST CZY JAK WEZMIE SIE ZMIANT Z CALEGO TYGODNIA TO BEDZIE GIT----------


Pt-nd
23.08.2024-25.08.2024
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
9,0,0,0,0,0,0,1,20240823,20240825
7,0,0,0,0,1,0,0,20240823,20240825
3,0,0,0,0,0,1,0,20240823,20240825

Pon-sob
26.08.2024-31.08.2024
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
1,0,1,1,1,0,0,0,20240826,20240831
5,1,0,0,0,0,0,0,20240826,20240831
7,0,0,0,0,1,0,0,20240826,20240831
3,0,0,0,0,0,1,0,20240826,20240831

wt-sob
27.08.2024-31.08.2024
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
1,0,1,1,1,0,0,0,20240827,20240831
7,0,0,0,0,1,0,0,20240827,20240831
3,0,0,0,0,0,1,0,20240827,20240831

śr-pt
28.08.2024-30.08.2024
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
1,0,0,1,1,0,0,0,20240828,20240830
7,0,0,0,0,1,0,0,20240828,20240830

sob-czw
31.08.2024-05.09.2024
service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date
4,0,0,0,0,0,0,1,20240831,20240905
1,0,1,1,1,0,0,0,20240831,20240905
5,1,0,0,0,0,0,0,20240831,20240905
3,0,0,0,0,0,1,0,20240831,20240905

Pomysł
Wziąc wszystkie calendar.txt które redis posiada (timetolive 15dni), zrobic z nich jeden wielki plik i sprawdzasz dzisiejsza date, jeżeli w tych plikach w redisie znajduja sie dane in range dzisiejsza data to wybierasz ten co jest najlbizej daty  i bierziesz z niego 1 dla poszcególnych dni, jezęli nie ma dla jakiś  dni jeden to cofasz się o jeden plik do  tyłui tak długo aż nie będzie cały tydzień mial jedynek ?




Thats how it is
routes = { trip_id, {
                    'direction_id' : direction_id
                    'stops' = [{   
                                'stop_id' : stop_id
                                'stop_name' : stop_name
                                'departure_time': departure_time
                                'stop_headsign' : stop_headsign
                                                                    }]}

Output

dict_items([('"1_4936732^N+"', 

            {'direction_id': '0', 'stops': 
            [{'stop_id': '221', 'stop_name': '"Franowo"', 'departure_time': '04:22:00', 'stop_headsign': '"OS. SOBIESKIEGO"'},
            {'stop_id': '219', 'stop_name': '"Szwajcarska"', 'departure_time': '04:23:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '218', 'stop_name': '"Szwedzka"', 'departure_time': '04:24:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '216', 'stop_name': '"Piaśnicka/Kurlandzka"', 'departure_time': '04:25:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '214', 'stop_name': '"Piaśnicka Rynek"', 'departure_time': '04:26:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '212', 'stop_name': '"Os. Lecha"', 'departure_time': '04:28:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '223', 'stop_name': '"Os. Tysiąclecia"', 'departure_time': '04:29:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '4215', 'stop_name': '"Łacina"', 'departure_time': '04:30:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '225', 'stop_name': '"Polanka"', 'departure_time': '04:31:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '161', 'stop_name': '"Kórnicka"', 'departure_time': '04:32:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '3196', 'stop_name': '"Kórnicka"', 'departure_time': '04:33:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '164', 'stop_name': '"Politechnika"', 'departure_time': '04:34:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '240', 'stop_name': '"Most Św. Rocha"', 'departure_time': '04:35:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '166', 'stop_name': '"Pl. Bernardyński"', 'departure_time': '04:36:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '123', 'stop_name': '"Wrocławska"', 'departure_time': '04:37:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '121', 'stop_name': '"Aleje Marcinkowskiego"', 'departure_time': '04:38:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '119', 'stop_name': '"27 Grudnia"', 'departure_time': '04:39:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '118', 'stop_name': '"Fredry"', 'departure_time': '04:41:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '5', 'stop_name': '"Most Teatralny"', 'departure_time': '04:42:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '16', 'stop_name': '"Słowiańska"', 'departure_time': '04:45:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '24', 'stop_name': '"Aleje Solidarności"', 'departure_time': '04:46:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '26', 'stop_name': '"Lechicka Poznań Plaza"', 'departure_time': '04:47:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '28', 'stop_name': '"Kurpińskiego"', 'departure_time': '04:48:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '30', 'stop_name': '"Szymanowskiego"', 'departure_time': '04:50:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}, 
            {'stop_id': '3', 'stop_name': '"Os. Sobieskiego"', 'departure_time': '04:51:00', 'stop_headsign': '"OS. SOBIESKIEGO"'}]}),

            





Route id = 16
Trip_id = trip_id_1
Stop_Headsign = stop_headsign_1
Direction_id = direction_id_1
Service_id = service_id
Departure_time = [stop_id_1 stop_name_1 departure_tiem: 4:26:00, 
                stop_id_1 stop_name_1 departure_tiem:4:40:00, 
                stop_id_1 stop_name_1 departure_tiem:4:50:00,
                ....
                stop_id_1 stop_name_1 departure_tiem: 22:39:00]

Route id = 16
Trip_id = trip_id_2
Stop_Headsign = stop_headsign_2
Direction_id = direction_id_2
Departure_time = [stop_id_1 stop_name_1 departure_tiem: 4:26:00, 
                stop_id_1 stop_name_1 departure_tiem:4:40:00, 
                stop_id_1 stop_name_1 departure_tiem:4:50:00,
                ....
                stop_id_1 stop_name_1 departure_tiem: 22:39:00]

'''
