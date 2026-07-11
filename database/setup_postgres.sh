#!/bin/bash
# PostgreSQL セットアップスクリプト
# 実行方法: sudo bash database/setup_postgres.sh

set -e

DB_NAME="schedule_app"
DB_USER="schedule_user"

echo "=== PostgreSQL セットアップ開始 ==="

# --- 1. パッケージインストール ---
echo "[1/5] PostgreSQL をインストールします..."
apt-get update -y
apt-get install -y postgresql postgresql-contrib

# --- 2. サービス起動・自動起動設定 ---
echo "[2/5] PostgreSQL サービスを起動します..."
systemctl start postgresql
systemctl enable postgresql

# --- 3. データベース作成 ---
echo "[3/5] データベース '$DB_NAME' を作成します..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" \
  | grep -q 1 || sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"

# --- 4. ユーザー作成 ---
echo "[4/5] ユーザー '$DB_USER' を作成します..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" \
  | grep -q 1 || sudo -u postgres psql -c "CREATE USER $DB_USER WITH LOGIN;"

# --- 5. 権限付与 ---
echo "[5/5] 権限を付与します..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"

echo ""
echo "=== セットアップ完了 ==="
echo ""
echo "次のステップ: パスワードを設定してください"
echo ""
echo "  sudo -u postgres psql -c \"ALTER USER $DB_USER WITH PASSWORD '任意のパスワード';\""
echo ""
echo "設定後、プロジェクトの .env を更新してください:"
echo ""
echo "  DATABASE_URL=postgres://$DB_USER:パスワード@localhost:5432/$DB_NAME"
echo ""
