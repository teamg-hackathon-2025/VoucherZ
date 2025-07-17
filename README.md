# Hackathon2025sumTeamG

# 開発環境のセットアップ
1. **環境変数ファイルの準備**

   - `.env` ファイルをルートディレクトリに作成し、以下の情報を記載してください
     ```.env
     # Django settings
     DJANGO_SECRET_KEY=your-very-secret-key
     DJANGO_DEBUG=False
     DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

     # MySQL settings
     MYSQL_ROOT_PASSWORD=rootpassword
     MYSQL_DATABASE=myappdb
     MYSQL_USER=myappuser
     MYSQL_PASSWORD=mysecretpassword
     ```

2. **起動** 
     ```bash
     docker compose -f docker-compose.dev.yml up --build
     ```



