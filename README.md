# 中部第一輸送株式会社 Webサイト

## 📁 プロジェクト概要

中部第一輸送株式会社のWebサイトプロジェクトです。

## 🌐 サイト構成

### 羽島営業所（岐阜羽島サーキュラーエコノミー営業所）

リニューアルオープンに伴う新規ページ

- **ディレクトリ**: `羽島営業所/`
- **メインページ**: `羽島営業所/index.html`
- **デモサイト**: ノーインデックス設定済み

## 🚀 デプロイ方法

詳細は [`羽島営業所/DEPLOY.md`](羽島営業所/DEPLOY.md) を参照してください。

### クイックスタート

```bash
# 1. Gitリポジトリを初期化（初回のみ）
git init
git add .
git commit -m "Initial commit"

# 2. GitHubリポジトリに接続
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main

# 3. GitHub Pagesを有効化
# GitHubリポジトリの Settings > Pages で設定
```

## 📂 ディレクトリ構造

```
中部第一グループ/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions設定
├── 羽島営業所/
│   ├── index.html              # メインHTML
│   ├── style.css               # スタイルシート
│   ├── script.js               # JavaScript
│   ├── robots.txt              # SEO制御
│   ├── .nojekyll               # Jekyll無効化
│   ├── README.md               # プロジェクト説明
│   └── DEPLOY.md               # デプロイ手順
├── logo/                       # 画像素材
├── .gitignore                  # Git除外設定
└── README.md                   # このファイル
```

## 🔒 SEO設定

デモサイトは検索エンジンにインデックスされません：

- `<meta name="robots" content="noindex, nofollow">`
- `robots.txt` で全クローラーをブロック

## 🛠️ 技術スタック

- **HTML5**: セマンティックマークアップ
- **CSS3**: レスポンシブデザイン、Flexbox、Grid
- **JavaScript**: バニラJS（モバイルメニュー制御）
- **Google Fonts**: Noto Sans JP

## 📱 対応デバイス

- ✅ PC（1200px以上）
- ✅ タブレット（768px - 1199px）
- ✅ スマートフォン（〜767px）

## 🎨 主な機能

### 羽島営業所ページ

1. **レスポンシブデザイン**
   - PC/タブレット/スマホで最適表示
   - スマホ用バーガーメニュー

2. **Hero Header**
   - PC: 背景画像＋テキストオーバーレイ
   - スマホ: 画像とテキストを分離表示

3. **問題解決セクション**
   - 問題と解決策のペア表示
   - アニメーション付き矢印

4. **モダンなUI/UX**
   - スムーズスクロール
   - アニメーション効果
   - 視認性の高いデザイン

## 📞 お問い合わせ

**中部第一輸送株式会社**  
岐阜羽島サーキュラーエコノミー営業所

- 📍 〒501-6244 岐阜県羽島市桑原町小沼午南1156番1
- ☎️ TEL: (0567) 96-0081
- 📠 FAX: (0567) 96-3357
- 🌐 Website: https://cdy.co.jp/

---

**作成日**: 2025年10月13日  
**最終更新**: 2025年10月13日

