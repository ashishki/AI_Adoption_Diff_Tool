# AI Adoption Diff Tool

Детерминированный CLI для измерения изменений в кодовой базе до и после внедрения AI-ассистента (Cursor, GitHub Copilot, Claude Code и др.).

## Зачем это нужно

Когда команда начинает использовать AI-инструмент для написания кода, интуитивно хочется понять: **а стало ли лучше?** Этот инструмент отвечает на вопрос конкретными метриками — без предположений, только по истории git.

Типичные вопросы, на которые отвечает инструмент:

- Изменился ли темп разработки (частота и размер коммитов)?
- Стало ли больше правок и откатов (`revert`, `fix`)?
- Растёт ли доля тестового кода?
- Появились ли "горячие" файлы, которые постоянно переписываются?
- Насколько изменения сконцентрированы в одних директориях?

> **Важно:** метрики показывают корреляцию, а не причинно-следственную связь. Инструмент честно об этом предупреждает в каждом отчёте.

## Что измеряется

Инструмент сравнивает **окно до** и **окно после** даты внедрения AI (по умолчанию ±90 дней).

| Метрика | Описание |
|---------|----------|
| Commit size | Среднее, медиана и p90 строк на коммит |
| Files touched | Среднее, медиана и p90 файлов на коммит |
| Churn rate | Доля удалённых строк от общего числа изменений |
| Revert frequency | Доля коммитов с `revert`/`fix`/`fixup`/`hotfix` в заголовке |
| Test-to-code ratio | Отношение изменений в тест-файлах к не-тест-файлам |
| Boilerplate signal | Доля коммитов, добавляющих `__init__.py`, `conftest.py` или пустые файлы |
| Hot-file instability | Число файлов, изменённых более чем в 10% коммитов |
| Directory concentration | Доля изменений в топ-3 директориях |

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/ashishki/AI_Adoption_Diff_Tool
cd AI_Adoption_Diff_Tool

# Создать и активировать виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate

# Установить
pip install -e .
```

Требования: Python ≥ 3.11.

## Использование

### Базовый сценарий — известная дата внедрения

```bash
ai-diff analyze \
  --repo /path/to/your/repo \
  --date 2024-06-01 \
  --tool cursor \
  --output ./reports
```

Создаёт `reports/report.json` и `reports/report.md`.

### С HTML-отчётом

```bash
ai-diff analyze \
  --repo /path/to/your/repo \
  --date 2024-06-01 \
  --tool copilot \
  --format html \
  --output ./reports
```

Создаёт `report.json`, `report.md` и `report.html`.

### Автоматическое определение даты внедрения

Если дата неизвестна, инструмент ищет сигналы в истории репозитория (`.cursorrules`, `.github/copilot-instructions.md`, `AGENTS.md`, папка `.claude/`, скачок частоты коммитов):

```bash
ai-diff analyze \
  --repo /path/to/your/repo \
  --tool claude_code
```

### Анализ GitHub-репозитория

```bash
export GITHUB_TOKEN=ghp_...

ai-diff analyze \
  --repo https://github.com/owner/repo \
  --date 2024-03-15 \
  --tool cursor
```

Токен используется только для клонирования. Он **никогда не попадает в логи**.

### Все опции

| Флаг | По умолчанию | Описание |
|------|-------------|----------|
| `--repo` | (обязательный) | Путь к локальному репозиторию или URL GitHub |
| `--date` | (авто) | Дата внедрения в формате YYYY-MM-DD |
| `--tool` | `unknown` | `cursor`, `copilot`, `claude_code`, `unknown` |
| `--format` | `json` | `json` — только JSON; `html` — JSON + MD + HTML; `both` — то же |
| `--output` | `./output` | Директория для отчётов |

## Структура отчёта

### report.json

```json
{
  "repo_path": "/path/to/repo",
  "tool_label": "cursor",
  "adoption_date": "2024-06-01",
  "window_days": 90,
  "confidence": {
    "score": 0.7,
    "level": "high",
    "anchor_source": "manual",
    "caveats": []
  },
  "metrics": {
    "before": {
      "mean_lines": 45.2,
      "churn_rate": 0.18,
      "test_ratio": 0.22,
      ...
    },
    "after": {
      "mean_lines": 78.6,
      "churn_rate": 0.31,
      "test_ratio": 0.41,
      ...
    }
  },
  "generated_at": "2026-04-10T14:00:00+00:00",
  "caveats": [
    "Metrics show correlation only. Causality cannot be inferred."
  ]
}
```

### report.md

Markdown с таблицей сравнения before/after, секцией уверенности (confidence) и предупреждением о корреляции.

### report.html

Минималистичная HTML5-страница с той же таблицей метрик.

## Confidence score

Инструмент оценивает надёжность анализа:

| Score | Уровень | Условия снижения |
|-------|---------|-----------------|
| ≥ 0.7 | high | — |
| 0.4–0.69 | medium | дата определена эвристически (−0.3) |
| < 0.4 | low | окно < 10 коммитов до или после (−0.2 каждое) |

## Разработка

```bash
# Установить зависимости для разработки
pip install -r requirements-dev.txt

# Запустить тесты
python3 -m pytest -q

# Проверить стиль
python3 -m ruff check
python3 -m ruff format --check
```

### Структура проекта

```
ai_adoption_diff/
├── cli.py                   # Точка входа CLI
├── ingestion/
│   ├── git_reader.py        # Чтение git log
│   └── github.py            # Клонирование GitHub-репозиториев
├── analysis/
│   ├── anchor.py            # Вычисление окна анализа
│   ├── heuristic.py         # Автоопределение даты внедрения
│   ├── partitioner.py       # Разбивка коммитов до/после
│   └── confidence.py        # Оценка надёжности
├── metrics/
│   ├── commit_size.py       # Размер коммитов и файлов
│   ├── churn.py             # Churn и revert-частота
│   ├── test_ratio.py        # Тест/код-отношение и boilerplate
│   └── hot_files.py         # Горячие файлы и концентрация
├── report/
│   ├── model.py             # Pydantic v2 модель отчёта
│   ├── json_export.py       # Экспорт в JSON
│   ├── renderer.py          # Рендеринг Jinja2
│   └── templates/           # report.md.j2, report.html.j2
└── shared/
    ├── config.py            # Конфигурация из env
    └── tracing.py           # Логирование (structlog)
```

### Запуск тестов конкретного модуля

```bash
python3 -m pytest tests/unit/test_metrics_churn.py -v
python3 -m pytest tests/integration/ -v
```

## Переменные окружения

| Переменная | Назначение |
|-----------|-----------|
| `GITHUB_TOKEN` | Токен для клонирования приватных GitHub-репозиториев |
| `AI_DIFF_LOG_LEVEL` | Уровень логирования (`DEBUG`, `INFO`, `WARNING`). По умолчанию `INFO` |
| `AI_DIFF_OUTPUT_DIR` | Директория вывода по умолчанию. По умолчанию `./output` |

## Ограничения

- Инструмент работает только с репозиториями git.
- Метрики рассчитываются по заголовкам и статистике коммитов — без анализа содержимого файлов.
- Размер выборки влияет на надёжность: рекомендуется не менее 10 коммитов в каждом окне.
- Корреляция ≠ причинность. Изменения метрик могут быть вызваны другими факторами.

## Лицензия

MIT
