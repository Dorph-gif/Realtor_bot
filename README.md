# Realtor_bot

# Setup

применение схемы базы данных: 

с запущенной базой данных применить src.database_service.create_tables

или

liquibase \
  --driver=org.postgresql.Driver \
  --url="jdbc:postgresql://localhost:5434/property_db" \
  --username=user \
  --password=password \
  --changeLogFile=migrations/main_base_changelog.xml \
  update

# Launch

Запуск происходит командой docker-compose up --build
