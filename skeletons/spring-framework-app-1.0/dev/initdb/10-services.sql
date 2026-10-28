-- One database and one user per service, as the chart gives each service a PostgreSQL of its own.
CREATE USER ${{ values.entities }} PASSWORD '${{ values.entities }}';
CREATE DATABASE ${{ values.entities }} OWNER ${{ values.entities }};
CREATE USER notifier PASSWORD 'notifier';
CREATE DATABASE notifier OWNER notifier;
