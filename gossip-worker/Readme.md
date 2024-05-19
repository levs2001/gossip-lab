# Запуск
Используйте 21ю java [eclipse/temurin](https://projects.eclipse.org/projects/adoptium.temurin). Сбилдите jar-ник:

```shell
./gradlew clean build -x test
```

Сбилдите docker образ:

```shell
docker build -t leo-gossip-worker:0.0.1 .
```

# Использование
Для документации и примеров запросов развернут swagger, если приложение запущено,
он доступен по ссылке: http://localhost:8080/swagger-ui/index.html
