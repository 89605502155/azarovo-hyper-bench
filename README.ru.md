# azarovo-hyper-bench

Воспроизводимые замеры к статье о библиотеке
[azarovo-hyper](https://github.com/89605502155/azarovo-hyper)
([PyPI](https://pypi.org/project/azarovo-hyper/)), высокоуровневой Python-библиотеке
для KVM и Xen. Все числа и рисунки статьи можно получить заново из этого
репозитория.

[English version](README.md)

## Что сравнивается

| Замер | Вопрос | Модуль |
|---|---|---|
| Импорт | Сколько длится `import` и сколько памяти он добавляет | `bench.imports` |
| Установка | Время, число пакетов и объём чистой установки | `bench.install` |
| Операции | Время на стороне клиента: состояние, балунинг, vCPU, метрики, определение | `bench.operations` |
| Объём кода | Число операторов для одной и той же задачи управления | `bench.loc`, `tasks/` |
| Гонка | Переподписка при 16 одновременных запусках: «проверка, затем действие» и атомарный допуск | `bench.race` |
| Контекст KVM | Длительность тех же операций на настоящем госте KVM | `bench.kvm_context` |

Библиотеки: azarovo-hyper 0.0.2, libvirt-python 12.9.0, pyvmomi 9.1.1.0,
proxmoxer 2.3.0, openstacksdk 4.22.0, pylxd 2.4.2, python-vagrant 1.0.0
(точные версии зафиксированы в `uv.lock`).

Замеры операций идут на встроенном драйвере libvirt `test:///default`. Он
работает внутри вызывающего процесса и почти ничего не делает, поэтому
измеряется стоимость самой библиотеки, а не гипервизора. Для VMware, Proxmox,
OpenStack, LXD и Vagrant нужны работающие серверы, поэтому у них сравниваются
только импорт и установка.

## Что нужно

Проверено на **Ubuntu 26.04** (пока только Linux).

```bash
sudo apt install -y qemu-utils libvirt-daemon-system libvirt-clients \
                    pkg-config libvirt-dev python3-dev gcc      # gcc и др. собирают libvirt-python
curl -LsSf https://astral.sh/uv/install.sh | sh                  # если uv нет
```

Компилятор и заголовки нужны только потому, что `libvirt-python`, одна из
сравниваемых библиотек, публикуется исходным кодом. Самой azarovo-hyper они не
нужны. `/dev/kvm` не обязателен: без него `bench.kvm_context` пропускается.

## Запуск

```bash
git clone https://github.com/89605502155/azarovo-hyper-bench
cd azarovo-hyper-bench
uv sync --locked                       # точные версии из uv.lock
uv run python -m bench.run_all         # около 15 минут, пишет results/*.json
uv run python -m plots.make_all        # figures/*.tiff, 600 dpi
```

Отдельные замеры принимают объём выборки, например
`uv run python -m bench.operations --repeats 500` или
`uv run python -m bench.race --trials 20`.

Результаты, использованные в статье, лежат в `results/`, поэтому
`uv run python -m plots.make_all` перерисует рисунки без повторных замеров.

## Результаты статьи

Стенд: Intel Core i5-2500 (4 ядра, 3,3 ГГц), 19 ГиБ ОЗУ, Ubuntu 26.04.1,
ядро 7.0, Python 3.12.13, libvirt 12.0.0, QEMU 10.2.1.

| Рисунок | Файл | Скрипт |
|---|---|---|
| 1. Этапы запуска машины | `figures/fig1_scheme.tiff` | `plots/fig_scheme.py` |
| 2. Импорт и установка | `figures/fig2_footprint.tiff` | `plots/fig_footprint.py` |
| 3. Стоимость операций и доля от времени KVM | `figures/fig3_operations.tiff` | `plots/fig_operations.py` |
| 4. Переподписка при одновременных запусках | `figures/fig4_race.tiff` | `plots/fig_race.py` |

Каждый JSON-файл в `results/` хранит рядом с выборками окружение (процессор,
ядро, версии Python и библиотек): медиану, квартили, 95-й процентиль.

## Структура

```
bench/     замеры (по модулю на вопрос) и run_all.py
tasks/     одна и та же задача на azarovo-hyper и на libvirt-python
plots/     скрипты рисунков; в style.py шрифты, размеры и экспорт TIFF 600 dpi
results/   измеренные данные статьи
figures/   готовые рисунки
```

## Лицензия

[MIT](LICENSE)
