# Hackathon2025sumTeamG

## 開発環境の使い方
### 起動方法
1. 環境変数ファイルの準備
    .env.devのファイル名を.envに変更。 

2. 起動 
     ```bash
     docker compose -f docker-compose.dev.yml up --build
     ```
3. Webアプリにブラウザからアクセス。\
    [http://127.0.0.1:8000/account/](http://127.0.0.1:8000/account/)

### デバックツール
1. Django Debug Toolbar\
    [公式ドキュメント](https://django-debug-toolbar.readthedocs.io/en/latest/index.html)

2. django-extensions
    一つの機能として、 shell_plusが使用できる。\
    shell_plusは開発環境を起動してから、下記コマンドを実行。
    ```bash
    docker exec -it django_app python manage.py shell_plus
    ```
    shellモードになるので、以下のようにモデル操作や環境確認等ができる。
    **モデル操作**
    ```python
    # 全ユーザー一覧
    User.objects.all()
    # 新しいユーザー作成
    User.objects.create(username='testuser', password='pass')
    # フィルタ
    Order.objects.filter(status='pending')
    ```
    **環境確認**
    ```python
    settings.DEBUG
    settings.DATABASES
    ```
    > [!TIP]
    > shell_plusとは\
    > 標準の Django シェル（python manage.py shell）の上位互換。\
    > 主な特徴：\
    > 全てのモデルが自動でインポートされている。\
    > いちいち from app.models import MyModel と書く必要なし。\
    > 環境変数や settings もロード済み。\
    > ORM がそのまま使える。\
    > IPython や bpython にも対応（補完やシンタックスハイライト付き）\
    > 簡易 DB 操作やテストコードの実行がしやすい。\
    [公式ドキュメント](https://django-extensions.readthedocs.io/en/latest/#)
    
3. Werkzeug
    ブラウザ上で使える高機能なデバッガー。エラー発生時に、ブラウザ上で詳細なトレースバックと「インタラクティブなデバッグコンソール」が表示される。\
    [django-extensionsをインストールしてrunserverより便利なrunserver_plusを使う](https://qiita.com/komiya_____/items/72b543fdaddab47a6449)
]
