# GitHub Pagesデプロイ手順

このドキュメントは、岐阜羽島サーキュラーエコノミー営業所のデモサイトをGitHub Pagesにデプロイする手順を説明します。

## 📋 前提条件

- GitHubアカウントを持っていること
- Gitがインストールされていること
- コマンドライン（ターミナル）の基本操作ができること

## 🚀 デプロイ手順

### 1. GitHubリポジトリの作成

1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ設定：
   - **Repository name**: `hashima-demo` (任意の名前)
   - **Description**: 「岐阜羽島サーキュラーエコノミー営業所 デモサイト」
   - **Public** または **Private** を選択
   - 「Create repository」をクリック

### 2. ローカルでGitリポジトリを初期化

ターミナルを開き、プロジェクトのルートディレクトリ（`中部第一グループ`）に移動：

```bash
cd "/Users/yi/Documents/Obsidian Vault/中部第一グループ"
```

Gitリポジトリを初期化：

```bash
# Gitリポジトリを初期化
git init

# .gitignoreファイルを作成（必要に応じて）
echo ".DS_Store" > .gitignore

# すべてのファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit: 岐阜羽島サーキュラーエコノミー営業所デモサイト"
```

### 3. GitHubリポジトリにプッシュ

GitHubで作成したリポジトリのURLを使用（`YOUR_USERNAME`を実際のユーザー名に置き換え）：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/hashima-demo.git

# mainブランチにプッシュ
git branch -M main
git push -u origin main
```

### 4. GitHub Pagesを有効化

1. GitHubのリポジトリページに移動
2. 「Settings」タブをクリック
3. 左サイドバーの「Pages」をクリック
4. 「Source」セクションで：
   - **Branch**: `main`
   - **Folder**: `/ (root)`
5. 「Save」をクリック

### 5. デプロイ完了

数分後、以下のURLでサイトが公開されます：

```
https://YOUR_USERNAME.github.io/hashima-demo/羽島営業所/
```

または、カスタムドメインを設定することも可能です。

## 📁 ディレクトリ構造

デプロイされるファイル構造：

```
中部第一グループ/
├── 羽島営業所/
│   ├── index.html          # メインHTMLファイル
│   ├── style.css           # スタイルシート
│   ├── script.js           # JavaScriptファイル
│   ├── robots.txt          # 検索エンジン制御
│   ├── .nojekyll           # Jekyll無効化
│   ├── README.md           # プロジェクト説明
│   └── DEPLOY.md           # このファイル
└── logo/
    ├── chubu-daiichi_logo.png
    ├── recruit_banner-300x119.png
    ├── Generated Image October 13, 2025 - 4_04PM.png
    └── 20251013_1533_Eco-Friendly Facility Mascot_remix_01k7e7p1a3e3gb8350zm54zpff.png
    └── images/
        └── common/
            └── permits_network_visual.png
```

## 🔒 SEO対策（ノーインデックス）

以下の設定により、検索エンジンにインデックスされません：

- ✅ `<meta name="robots" content="noindex, nofollow">`
- ✅ `<meta name="googlebot" content="noindex, nofollow">`
- ✅ `robots.txt` ファイル

## 🔄 更新方法

サイトを更新する場合：

```bash
# ファイルを編集後

# 変更をステージング
git add .

# コミット
git commit -m "Update: [変更内容の説明]"

# プッシュ
git push origin main
```

数分後、自動的にGitHub Pagesに反映されます。

## 🛠️ トラブルシューティング

### 画像が表示されない場合

相対パスが正しいか確認：
- `index.html`は`羽島営業所/`フォルダ内
- 画像は`logo/`フォルダ内
- パスは`../logo/画像ファイル名.png`

### 404エラーが出る場合

URLが正しいか確認：
```
https://YOUR_USERNAME.github.io/hashima-demo/羽島営業所/
```

日本語ディレクトリ名がエンコードされる場合があります。

### CSSが適用されない場合

1. ブラウザのキャッシュをクリア（Ctrl+Shift+R / Cmd+Shift+R）
2. `style.css`へのパスが正しいか確認

## 📞 サポート

問題が発生した場合は、GitHubのIssuesセクションで報告してください。

---

**作成日**: 2025年10月13日  
**最終更新**: 2025年10月13日

