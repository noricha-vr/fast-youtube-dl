# YouTube Downloader API

YouTubeの動画や音声をダウンロードするためのRESTful APIサービスです。FastAPIとyoutube-dlを使用して実装されています。

## 機能

- YouTube動画のダウンロード（複数の品質オプション対応）
- YouTube音声のMP3形式でのダウンロード
- 自動ファイルクリーンアップ（24時間経過後）
- ヘルスチェックエンドポイント

## 必要条件

- Docker (version 20.10.0以上)
- Docker Compose (version 2.0.0以上)

## セットアップと起動方法

### 1. 環境構築

1. リポジトリをクローン：

   ```bash
   git clone https://github.com/yourusername/youtube-downloader-api.git
   cd youtube-downloader-api
   ```

2. 環境変数ファイルの作成：

   ```bash
   cp .env.example .env
   ```

3. 必要に応じて.envファイルを編集

### 2. アプリケーションの起動

1. Dockerコンテナのビルドと起動：

   ```bash
   docker-compose up -d --build
   ```

2. アプリケーションの稼働確認：

   ```bash
   curl http://localhost:8000/health
   ```

## API エンドポイント

### 動画のダウンロード

- **エンドポイント**: `/api/v1/download/video`
- **メソッド**: POST
- **パラメータ**:
  - `url`: YouTube動画のURL（必須）
  - `quality`: 動画品質（オプション、デフォルト: "best"）

### 音声のダウンロード

- **エンドポイント**: `/api/v1/download/audio`
- **メソッド**: POST
- **パラメータ**:
  - `url`: YouTube動画のURL（必須）

### ヘルスチェック

- **エンドポイント**: `/health`
- **メソッド**: GET

## エラーハンドリング

APIは以下のHTTPステータスコードを返します：

- 200: リクエスト成功
- 400: 不正なリクエスト
- 404: リソースが見つからない
- 500: サーバーエラー

## 開発環境での実行

1. Python仮想環境の作成と有効化：

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
   ```

2. 依存パッケージのインストール：

   ```bash
   pip install -r requirements.txt
   ```

3. 開発サーバーの起動：

   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## ライセンス

MIT License

## 貢献について

1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 注意事項

- このAPIは教育目的で作成されています
- YouTubeの利用規約を遵守してください
- 著作権で保護されたコンテンツのダウンロードには十分注意してください
