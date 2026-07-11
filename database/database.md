# データベース情報

## 接続情報

| 項目 | 値 |
|------|----|
| エンジン | PostgreSQL |
| ホスト | localhost |
| ポート | 5432 |
| データベース名 | schedule_app |
| ユーザー名 | dbuser |
| パスワード | （.env参照） |

## .env 設定値

```
DATABASE_URL=postgres://dbuser:パスワード@localhost:5432/schedule_app
```

## セットアップ手順

Linux上でのPostgreSQLセットアップは `database/setup_postgres.sh` を実行します。

```bash
chmod +x database/setup_postgres.sh
sudo bash database/setup_postgres.sh
```

スクリプト実行後、パスワードを設定します。

```bash
sudo -u postgres psql -c "ALTER USER schedule_user WITH PASSWORD '任意のパスワード';"
```

設定したパスワードを `.env` の `DATABASE_URL` に反映してください。

## バックアップ

```bash
# バックアップ
pg_dump -U schedule_user -h localhost schedule_app > backup_$(date +%Y%m%d).sql

# リストア
psql -U schedule_user -h localhost schedule_app < backup_YYYYMMDD.sql
```
