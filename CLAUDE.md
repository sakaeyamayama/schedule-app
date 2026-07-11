# CLAUDE.md — AI向けプロジェクトガイド

## プロジェクト概要

チームのスケジュール・業績管理WebアプリをDjangoで構築する。
詳細はREADME.mdを参照。

## 技術スタック

- Python 3.11+
- Django 5.x
- PostgreSQL
- Linux稼働

## ディレクトリ構成（予定）

```
schedule-app/
├── manage.py
├── config/              # Djangoプロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── master/          # メンバー・プロジェクト・作業マスタ
│   ├── schedule/        # 予定管理
│   ├── actual/          # 実績管理
│   ├── gantt/           # ガントチャート
│   ├── comparison/      # 予実比較
│   └── importer/        # CSVインポート
├── templates/
├── static/
├── requirements.txt
└── .env
```

## データモデル

```python
# master/models.py
Member: id, name
Project: id, name
Task: id, project(FK), name

# schedule/models.py
Schedule: id, member(FK), task(FK), date, hours(int)

# actual/models.py
Actual: id, member(FK), task(FK), date, hours(int)
```

## 設計方針・制約

- 認証なし。全ユーザーが全操作可能
- 時間単位は1時間（整数のみ）
- 1人が同じ日に複数タスクを持てる
- CSVインポートはプロジェクト・作業のみ（メンバーアサインはアプリ上で行う）
- CSVフォーマット: `project,task` の2列

## 仮想環境

プロジェクトルートの `.venv` を使用する。`manage.py` を実行する際は必ず `.venv` の Python を使うこと。
グローバルの `python` / `pip` は使わない。

```bash
# 仮想環境を有効化してから実行
.venv\Scripts\Activate.ps1
python manage.py ...

# または直接指定
.venv\Scripts\python.exe manage.py ...

# パッケージ追加も .venv で
.venv\Scripts\pip.exe install <package>
```

## よく使うコマンド

```bash
# 開発サーバー起動
.venv\Scripts\python.exe manage.py runserver

# マイグレーション
.venv\Scripts\python.exe manage.py makemigrations
.venv\Scripts\python.exe manage.py migrate

# テスト
.venv\Scripts\python.exe manage.py test

# シェル
.venv\Scripts\python.exe manage.py shell
```

## コーディング規約

- Djangoのclass-based viewを基本とする
- テンプレートはBulmaまたはBootstrapを使用（未決定）
- グラフはChart.jsを使用（ガントチャート含む）
- 日本語UIとする
