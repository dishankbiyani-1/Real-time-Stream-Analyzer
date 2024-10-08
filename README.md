# Description

This project utilizes Docker for containerization. It includes a Django container running Python 3.11 and a Dejavu container running Python 3.8, with PostgreSQL 10.7 as the database. The project involves capturing audio streams, identifying songs using Dejavu, and managing songs and streams via an admin panel.

## Prerequisites

- Docker installed on your machine

## Setup Instructions

- Build Docker containers.

1. ```bash
   docker-compose build
   ```

## Running the Project

1. Start Docker containers.

   ```bash
   docker-compose up -d
   ```
<!-- 2. Before accessing the admin panel, you need to run migrations in the Django container. Follow these steps depending on your Docker setup:

### For Docker Desktop users:
- Open the Docker Desktop interface.
- Navigate to the "Containers" tab.
- Find django container, and click on 3 dots then click on open in terminal.
- Run the following command:
   ```bash
   python manage.py migrate
   ```

### Using Terminal
- Find the container ID or name of the running Django container by executing:
   ```bash
   docker ps
   ```
- Access the Django container's shell:
   ```bash
   docker exec -it <container_id_or_name> /bin/bash
   ```
- Once inside the container, run the migration command:
   ```bash
   python manage.py migrate
   ``` -->
2. Access the admin panel in your browser.

   Visit [http://localhost:8000/admin](http://localhost:8000/admin)
3. Log in using the following credentials:

   - Username: admin
   - Password: 12345

## Setting Up Songs and Streams

1. In the admin panel, navigate to **Songs**.
2. Add songs data for Dejavu. Ensure song files have the extensions `.mp3` or `.wav`.
3. Navigate to **Streams** and add stream data.

## Capturing Streams and Identifying Songs

1. Visit [http://localhost:8000/stream/url-listing/](http://localhost:8000/stream/url-listing/)
2. Click on **Refresh Dejavu data** button to feed songs data to Dejavu. Only necessary if new songs are added.
3. Click **Start Stream Capture** to begin recording audio files and identifying songs.

## Viewing Recorded Data

1. Refresh the page.
2. Click on **View Stream Chunks** to see the recorded data.

## Important Notes

- Ensure songs data is fed to Dejavu before starting stream capture.
- Upload songs from the admin panel first.
- Song files must have the extensions `.mp3` or `.wav`.
