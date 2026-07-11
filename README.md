# チームスケジュール・業績管理アプリ

チームメンバーの作業予定と実績を管理し、予実比較やガントチャートで可視化するWebアプリケーションです。

## 技術スタック

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.11+ |
| フレームワーク | Django 5.x |
| DB | PostgreSQL |
| 稼働環境 | Linux |
| 認証 | なし（認証不要） |

## 機能

- **予定管理** — メンバー・プロジェクト・作業ごとに作業予定時間を登録・編集・表示
- **実績管理** — 実際の作業時間を登録・編集・表示
- **スケジュール表示** — 日別・週別・月別の切り替え表示
- **ガントチャート** — 人別・プロジェクト別の切り替え表示
- **予実比較** — 人別・プロジェクト別の予定 vs 実績をグラフで表示
- **CSVインポート** — プロジェクト・作業をCSVで一括登録

## データモデル

```
Member（メンバー）
  - name

Project（プロジェクト）
  - name

Task（作業）
  - project (FK → Project)
  - name

Schedule（予定）
  - member (FK → Member)
  - task   (FK → Task)
  - date
  - hours  （1時間単位の整数）

Actual（実績）
  - member (FK → Member)
  - task   (FK → Task)
  - date
  - hours  （1時間単位の整数）
```

## ワークフロー

```
① CSVインポート  → project, task 列のみ。プロジェクト・作業を一括登録
② アサイン       → アプリ上で誰が・いつ・何時間かを予定として登録
③ 実績入力       → 実際にかかった時間を登録
④ 可視化         → ガントチャート・予実比較で確認
```

## CSVフォーマット（インポート用）

```csv
project,task
XX案件,基本設計
XX案件,詳細設計
XX案件,レビュー
YY案件,要件定義
```

- ヘッダー行必須
- 存在しないプロジェクト・作業は自動生成
- 既存のプロジェクト・作業は重複登録しない（upsert）
- テンプレートCSVをアプリからダウンロード可能

## 画面構成

| 画面 | パス | 内容 |
|------|------|------|
| ダッシュボード | `/` | 週次サマリー・直近の予実概況 |
| スケジュール | `/schedule/` | 日別/週別/月別 切り替え表示 |
| ガントチャート | `/gantt/` | 人別/プロジェクト別 切り替え |
| 予実比較 | `/comparison/` | 人別/プロジェクト別 棒グラフ |
| 予定入力 | `/schedule/create/` | 予定の新規登録フォーム |
| 実績入力 | `/actual/create/` | 実績の新規登録フォーム |
| CSVインポート | `/import/` | プロジェクト・作業の一括インポート |
| マスタ管理 | `/master/` | メンバー・プロジェクト・作業の管理 |

## セットアップ

```bash
# リポジトリクローン後
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .env を編集してDB接続情報を設定

# DB初期化
python manage.py migrate

# 初期データ投入（任意）
python manage.py loaddata fixtures/initial.json

# 開発サーバー起動
python manage.py runserver
```

## 環境変数（.env）

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/schedule_app
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 開発状況

- [ ] Djangoプロジェクト初期セットアップ
- [ ] モデル定義・マイグレーション
- [ ] マスタ管理CRUD
- [ ] 予定・実績の登録/編集
- [ ] スケジュール表示（日別/週別/月別）
- [ ] ガントチャート
- [ ] 予実比較グラフ
- [ ] CSVインポート
