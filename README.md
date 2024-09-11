# MPK Scheduler App

## Overview
This application provides a scheduler and route planner for public transport (MPK) in Poznań. It utilizes data from [ZTM Poznań](https://www.ztm.poznan.pl/pl/dla-deweloperow/) provided in GTFS and GTFS-Realtime formats. The backend is built with Django, Celery, Redis, and PostgreSQL, while the frontend is planned to be developed in React.

## Features

1. **GTFS and GTFS-Realtime Integration**: Integrates data from ZTM Poznań in GTFS and GTFS-Realtime formats for accurate and real-time public transport information.

2. **User Account and Subscriptions**: Users can create accounts and purchase subscriptions. Subscriptions allow users to plan routes and save them as favorites.

3. **App Interface**: The app interface will be developed in React.

4. **Premium Features**: 
   - Three premium subscription options, with longer durations offering discounts.
   - Premium users can save favorite journey times, view statistics on bus delays (e.g., most delayed buses, common delay hours), and utilize data science features (subject to terms of service for data usage).

5. **Schedule Update Mechanism**:
   - Implements a Django function to fetch the latest MPK schedule data from the GTFS and GTFS-Realtime feeds.
   - Uses Celery with Redis to queue and asynchronously execute schedule update tasks.

6. **Real-time Notifications**:
   - Premium users receive notifications about changes in their chosen bus or tram schedules.
   - Implements a mechanism to track changes in schedule data and generate notifications (e.g., email or push notifications).

7. **Route Creation**:
   - Allows users to create custom routes and plan journeys.
   - Queries related to journey schedules are processed asynchronously using a task queue manager, optimizing user experience.

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

3. Run the application using Docker Compose:

    ```
    docker-compose up --build
    ```

5. Frontend will be on Nginx, actually work in progress (learning about frontend)


## Contributors
- Bartosz Przybysz https://github.com/PrzybyszB