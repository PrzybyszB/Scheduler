# MPK Scheduler App

## Overview
This application provides a scheduler for public transport (MPK) in Poznań. It utilizes data from [ZTM Poznań](https://www.ztm.poznan.pl/otwarte-dane/dla-deweloperow/) provided in GTFS format. 
Currently: 
- You can check the active bus lines and their routes.
- The timetable for each stop is available for the entire week.
- You can also search for a stop and see its location on the map. 
The backend is built with Django, Celery, Redis, and PostgreSQL, while the frontend is build in Next.js. Come and visit http://srv28.mikr.us:20361/

## Features

1. **GTFS Integration**: 
   - Integrates data from ZTM Poznań in GTFS format for accurate public transport information.

2. **Schedule Update Mechanism**:
   - Implements a Django function to fetch the latest MPK schedule data from the GTFS.
   - Uses Celery with Redis to queue and asynchronously execute schedule update tasks.


## Planned/WIP 

1. **GTFS-Realtime Integration**: 
   - Integrates data from ZTM's GTFS-realtime feed to provide live updates on public transport schedules.

2. **User Accounts and Subscriptions**: 
   - Users can create accounts and purchase subscriptions. 
   - Subscriptions allow users to plan routes, save them as favorites, and access premium features.

3. **Premium Features**:
   - Premium users can access features like saving favorite journey times, viewing bus delay statistics, and receiving notifications about schedule changes (e.g., via email or push notifications).
   - Premium users can also access data science insights on bus delays and more.

4. **Custom Route Creation**:
   - Users can create and save custom routes and plan journeys according to their preferences. 
   - Queries for journey schedules are processed asynchronously for better performance.



## Technologies Used
- Python
- Django
- Celery
- Redis
- PostgreSQL
- React (for frontend development)
- HTML/CSS/JavaScript (for basic frontend styling and functionality)

## Installation

1. Clone the repository to your local machine:

    ```
    git clone https://github.com/PrzybyszB/Scheduler
    ```

2. Navigate to the project directory:

    ```
    cd Scheduler/backend
    ```

3. Make sure that the time for downloading files is set to the desired value in celery.py

4. Run the application using Docker Compose:

    ```
    docker-compose up --build
    ```


## Contributors
- Bartosz Przybysz https://github.com/PrzybyszB