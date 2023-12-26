# Aviasales test task

![CI](https://github.com/aminabbasov/aviasales-test-task/actions/workflows/CI.yml/badge.svg) [![Maintainability](https://api.codeclimate.com/v1/badges/7f37e5b2cab5e7bdf685/maintainability)](https://codeclimate.com/github/aminabbasov/aviasales-test-task/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/7f37e5b2cab5e7bdf685/test_coverage)](https://codeclimate.com/github/aminabbasov/aviasales-test-task/test_coverage)

This is a web-service using FastAPI with lxml and Docker. Dependencies managed with [pip-tools](https://github.com/jazzband/pip-tools/). Maintains code quality with [Ruff](https://github.com/astral-sh/ruff). Configured for testing with Pytest.


## Description

At first, I planned to create two separate repositories with test tasks for the "Gates team" and the "Assisted team," but during the process, I realized that the differences in requirements are pretty small (in my opinion). Therefore, I decided to merge them into a single solution. And this is the first time me working with FastAPI, Pydantic and lxml, so if I didn't use some of the common best practices, sorry, I just don't know about them. 


## Inaccurate requirements

> This part will be in Russian for the reason of cultural code.

**Assisted team**

1. Возможны случаи, когда под запрос подходит больше одного варианта маршрута. Так как условия разрешения таких конфликтов не определены, ответ включает списком все подходящие под условие рейсы.

2. В первом требовании просят найти варианты перелета по определенному направлению (из DXB в BKK). Однако из условия неясно, должен ли перелет быть прямым, и следует ли искать варианты только для `<OnwardPricedItinerary>`, либо же для `<ReturnPricedItinerary>` включительно. Аналогично, если непрямые перелеты допускаются, неясно подойдет ли вариант, когда перелет соответствует направлению, но не является пунктом назначения (транзитный рейс). Поэтому при реалзиации эндпоинта я реализовал поиск по всем направлениям включая обратное, и добавил флаг `direct` для настройки. Так же имеется флаг `transit`, чтобы искать только по конечным назначениям, либо же включать в поиск и транзитные рейсы. По умолчанию `direct` и `transit` установлены в `False`.

**Gates team**

1. Честно говоря, требования этого задания вызывали у меня очень много вопросов, и в реальных условиях я бы обязательно все уточнил, но т.к. это тестовое задание и нечеткость создана специально для оценки самостоятельных решений, я сделаю реалзиацию по минимому, чтобы в случае чего, функциональность можно было легко изменить.

2. В требовании указано "вывести списком отличия", но первые три пункта в принципе имеют мало связи с "отличиями", и их можно узнать сделав запрос к эндпоинтам для Assisted team. К тому же, мне трудно поверить что результат требует так мало информации (не запрашиваются номер полета, название перевозчика, тип билета и т.д.). Если же требуется вывести информацию для всех отличающихся маршрутов, то такая постановка задачи сама по себе имеет мало смысла, ибо любое изменение условий будет провоцировать изменение цены (пункт 3), и собственно, самих условий (пункт 4), а значит в списке отличий будут буквально все маршруты.

3. Последние два пункта неясны, непонятно относительно какого запроса нужно искать изменения условий и маршрутов, и что подразумевается под условиями. Поэтому я выведу отличия без приоритезации, и за условия буду засчитывать:

    + Включают ли маршруты из результата обратный путь, или это билеты в один конец.
    + Уникальные курсы маршрутов, без учета времени и других параметров. (Если хотя бы один из файлов не содержит обратные маршруты, то они не учитываются)
    + Какого типа и сколько пассажиров включается в рассчет стоимости билета. 


## Installing on a local machine

This project requires `python >= 3.12` and `docker >= 4.24`. It may work with an erlier versions, but it's undetermined.

Deps are managed by [pip-tools](https://github.com/jazzband/pip-tools) with requirements stored in [pyproject.toml](https://github.com/jazzband/pip-tools#requirements-from-pyprojecttoml).

Run the server:

```bash
docker compose up -d
```

If you want to make changes to the code while a container is running:

```bash
docker compose watch
```


## Usage

To test endpoints use curl, [httpie](https://httpie.io/) (my personal preference) or any other API platform:

```bash
# curl
curl -X POST -F "xml_file=@src/RS_Via-3.xml" <link>

# httpie
http --form --unsorted POST <link> xml_file@src/RS_Via-3.xml

# link example - "http://localhost:8000/api/v1/via/itineraries/optimal"
# or "http://localhost:8000/api/v1/via/itineraries/specified?source=DWC&destination=BKK"
```

To get all endpoints, go to http://localhost:8000/docs

---

To test the code, [virtual environment](https://docs.python.org/3/library/venv.html) should installed and activated.

## Improvement ideas

1. Add the ability to search for multi-city trips in `XMLDataProcessor`. As an option, the [strategy](https://refactoring.guru/design-patterns/strategy) design pattern can be used.

2. Edit pydantic schemas to be more reusable. They are currently pretty hardcoded to be used only with via.com XML responses.

3. Definitely, there are a lot of ways to improve and refactor the code to find the _optimal itinerary_. I made just a brief and simple implementation. (This is my first time doing data analytics, please don't be too harsh :з)

4. For sure, if new integrations are added, it would be better to organize the code for each partner in a separate directory within the `api` folder. _For example:_ `api/via/*`.

5. In my tests, there are some blank spots, ideally they should be filled in. I didn't want to spend time on that because it's a test task, and I'm confident in the results, but of course this is vulnerability.

And... The XML file `RS_Via-3.xml` has dates from the year 2018 for all routes, but its request time in `AirFareSearchResponse` is from the year 2015. It is not a problem for a test task; I just wanted to notice about it :)

## License

[MIT](https://choosealicense.com/licenses/mit/)