#!/bin/bash
# Amazon Linux 2023 向け初回セットアップスクリプト
#
# 【事前に手動で実施してください】
#
# 1. Python 3.11 インストール
#   （Amazon Linux 2023 のデフォルト python3 は 3.9 のため、3.10+ が必要）
#   sudo dnf install -y python3.11
#   python3.11 --version  # Python 3.11.x と表示されることを確認
#
# 2. PostgreSQL インストール & 起動
#   sudo dnf install -y postgresql15 postgresql15-server
#   sudo postgresql-setup --initdb
#   sudo systemctl enable --now postgresql
#
# 3. DB・ユーザー作成 & リポジトリクローン & .env 作成
#   # DB作成
#   sudo -u postgres psql
#     CREATE USER scheduleapp WITH PASSWORD 'yourpassword';
#     CREATE DATABASE schedule_app OWNER scheduleapp;
#     \q
#
#   # リポジトリクローン
#   sudo mkdir -p /opt/schedule-app
#   sudo chown ec2-user:ec2-user /opt/schedule-app
#   git clone <REPO_URL> /opt/schedule-app
#   cd /opt/schedule-app
#
#   # .env 作成
#   cp .env.example .env
#   vi .env  # 以下を設定:
#     SECRET_KEY=<python3.11 -c "import secrets; print(secrets.token_urlsafe(50))"> の出力値
#     DEBUG=False
#     DATABASE_URL=postgres://scheduleapp:yourpassword@localhost:5432/schedule_app
#     ALLOWED_HOSTS=<サーバーのIPアドレスまたはドメイン>
#
# 上記が完了したらこのスクリプトを実行してください。
# --------------------------------------------------

set -e

APP_DIR="/opt/schedule-app"
LOG_DIR="/var/log/schedule-app"

# 事前準備の確認
echo "=== Schedule App セットアップ ==="
echo ""
echo "事前準備が完了しているか確認します。"
echo ""

read -p "Python 3.11 のインストールが完了していますか？ (yes/no): " py_ready
if [ "$py_ready" != "yes" ]; then
    echo "先頭のコメントを参照して手順 1 を実施してください。"
    exit 1
fi

read -p "PostgreSQL が起動し、DB・ユーザーの作成が完了していますか？ (yes/no): " db_ready
if [ "$db_ready" != "yes" ]; then
    echo "先頭のコメントを参照して手順 2〜3 を実施してください。"
    exit 1
fi

read -p "/opt/schedule-app のクローンと .env の作成が完了していますか？ (yes/no): " env_ready
if [ "$env_ready" != "yes" ]; then
    echo "先頭のコメントを参照して手順 3 を実施してください。"
    exit 1
fi

echo ""
echo "事前準備 OK。セットアップを開始します。"
echo ""

cd "$APP_DIR"

echo "=== 4. 仮想環境作成 & パッケージインストール ==="
python3.11 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "=== 5. マイグレーション & 静的ファイル収集 ==="
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput

echo "=== 6. ログディレクトリ作成 ==="
sudo mkdir -p "$LOG_DIR"
sudo chown ec2-user:ec2-user "$LOG_DIR"

echo "=== 7. systemd ユニットファイル配置 & 有効化 ==="
sudo cp "$APP_DIR/deploy/schedule-app.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now schedule-app

echo "=== 8. 動作確認 ==="
sleep 2
sudo systemctl status schedule-app
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/

echo ""
echo "=== セットアップ完了 ==="
echo "ブラウザで http://<サーバーIP>:8000/ にアクセスしてください"
