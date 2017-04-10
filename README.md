yaml2ical
=========
yamlをiCalにしてｼｭｯ

Usage
=====

```sh
$ python yaml2ical.py <your_schedule.yaml> [-o <outfile.ics>]
```

Requirements
------------

```sh
$ pip install -r requirements.txt
```

YAML Format
-----------

```yaml
year: 2017
name: Riku Matsubara
mailto: 14rd169@ms.dendai.ac.jp

# 前期の予定
first:
  - summary: 研究
    description: 研究室にいる
    time: 11:00 - 16:00
    # period: 2 to 4
    weekday: MO # SU / MO / TU / WE / TH / FR / SA

  - summary: 授業
    description: なんちゃらって授業
    period: 1 to 2
    weekday: TU


# 後期の予定
second:
  - summary: 研究
    description: 研究室にいる
    time: 11:00 - 16:00
    weekday: MO
```

- `year` 予定の年
- `name` 君の名は
- `mailto` メアド
- `first` 前期の予定
    - `summary` タイトル
    - `description` 説明
    - `time` or `period` その時間。`time`なら時間、`period`なら何限目ってやつ
    - `weekday` 何曜日の予定なん
- `second` 後期の予定。前期と書き方は一緒
