# Staytus Exporter

Отдаёт в формате prometheus метрики по состоянию заведённых в [staytus](https://github.com/adamcooke/staytus) сервисов.

## Метрики

```
# HELP service_status Service Status
# TYPE service_status gauge
service_status{service_permalink="web-application",service_status="ok"} 0.0
service_status{service_permalink="web-application",service_status="minor"} 1.0
service_status{service_permalink="web-application",service_status="major"} 0.0
service_status{service_permalink="web-application",service_status="maintenance"} 0.0
service_status{service_permalink="api",service_status="ok"} 0.0
service_status{service_permalink="api",service_status="minor"} 0.0
service_status{service_permalink="api",service_status="major"} 0.0
service_status{service_permalink="api",service_status="maintenance"} 1.0
service_status{service_permalink="public-website",service_status="ok"} 0.0
service_status{service_permalink="public-website",service_status="minor"} 0.0
service_status{service_permalink="public-website",service_status="major"} 1.0
service_status{service_permalink="public-website",service_status="maintenance"} 0.0
service_status{service_permalink="customer-support",service_status="ok"} 1.0
service_status{service_permalink="customer-support",service_status="minor"} 0.0
service_status{service_permalink="customer-support",service_status="major"} 0.0
service_status{service_permalink="customer-support",service_status="maintenance"} 0.0
# HELP staytus_health Staytus Health
# TYPE staytus_health gauge
staytus_health{staytus_health="healthy"} 1.0
staytus_health{staytus_health="unhealthy"} 0.0
```

- `service_status` содержит 2 лэйбла: `service_permalink` (уникальный человекочитаемый идентификатор сервиса из staytus) и `service_status` (одно из 4х типов состояний сервиса: `ok`, `minor`, `major` или `maintenance`) в качестве значения может быть 1 (означает, что сервис `service_permalink` пребывает в состоянии `service_status`) или 0 (не пребывает в указанном состоянии);
- `staytus_health` содержит лэйбл `staytus_health` (принимает 2 значения: `healthy`, если staytus нормально взаимодействует с экспортером, или `unhealthy`, если при взаимодействии возникают ошибки).

## Конфигурация

Экспортер принимает конфигурацию через переменные окружения.

| Переменная | Значение по умолчанию | Описание |
| --- | --- | --- |
| **POLLING_INTERVAL_SECONDS** | 2 | интервал опроса staytus |
| **EXPORTER_PORT** | 9877 | порт, на котором отдаются метрики |
| **STAYTUS_API_URL** | http://localhost:8787/ | url staytus, по которому экспортер запрашивает данные о сервисах |
| **STAYTUS_API_TOKEN** | - | **обязательный** токен API staytus |
| **STAYTUS_API_SECRET** | - | **обязательный** секрет от токена |
| **DEBUG** | False | Включение дебажных логов (что бы включить, задать "True", "true", "1" или "yes") |

## Разработка

### Локальная среда

Создать [виртуальное окружение python](https://docs.python.org/3/library/venv.html):
```bash
python3 -m venv venv
```

Установить зависимости:
```bash
./venv/bin/python3 -m pip install -r src/requirements.txt -r tests/requirements.txt
```

Поднять локальный staytus:
```bash
docker-compose up
```

В первый раз придётся пройти wizard настройки staytus в [его webUI](http://localhost:8787/). Какими значениями заполнять поля большого значения для целей локальной разработки не имеет. По итогу нужно обязательно выпустить [токен доступа к API](http://localhost:8787/admin/api/tokens) и забрать значение токена и его секрета.

Подготовить файл с переменными окружения:
```bash
cat .env.sample > .env
```

После руками вписать **STAYTUS_API_TOKEN** и **STAYTUS_API_SECRET**, которые забрали из webUI.

### Перед комитом

Нижеперечисленные шаги дублируются в CI.

Проверить, что контейнер с экспортером собирается и работает
```bash
docker-compose -f docker-compose.yaml -f docker-compose.exporter.yaml up --build
```

Прогнать unit-тесты:
```bash
./venv/bin/python3 -m pytest tests
```

Отформатировать код и импорты:
```bash
./venv/bin/python3 -m isort src
./venv/bin/python3 -m black src
```

Проверить код pylint и mypy:
```bash
./venv/bin/python3 -m pylint src
./venv/bin/python3 -m mypy src
```
