# Realtor_bot

# Setup

применение схемы базы данных: 

liquibase \
  --driver=org.postgresql.Driver \
  --url="jdbc:postgresql://localhost:5434/property_db" \
  --username=user \
  --password=password \
  --changeLogFile=migrations/main_base_changelog.xml \
  update
