import requests
import json
import base64
import os
import re
from datetime import datetime

# --- Functions ---

def load_config():
    """設定ファイル(settings.json)を読み込む"""
    try:
        # スクリプト自身の場所を基準にsettings.jsonを探す
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "settings.json"), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("エラー: settings.json が見つかりません。")
        exit()
    except json.JSONDecodeError:
        print("エラー: settings.json の形式が正しくありません。")
        exit()

def markdown_to_html_blocks(md_content):
    """MarkdownをGutenbergのブロック形式HTMLに変換する（スマホ改行・太字対応）"""
    html_content = ""
    # テキストを一行ずつに分割
    lines = md_content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 空行は無視
        if not line:
            continue

        # **text** を <span style...> に変換 (テーマCSSによる無効化を回避する最終手段)
        line = re.sub(r'\*\*(.*?)\*\*', r'<span style="font-weight: bold;">\1</span>', line)
        
        if line.startswith('## '):
            heading_text = line.lstrip('# ').strip()
            html_content += f"<!-- wp:heading {{\"level\":2}} --><h2>{heading_text}</h2><!-- /wp:heading -->\n"
        elif line.startswith('### '):
            heading_text = line.lstrip('# ').strip()
            html_content += f"<!-- wp:heading {{\"level\":3}} --><h3>{heading_text}</h3><!-- /wp:heading -->\n"
        elif "<!-- image_placeholder" in line:
            # 画像プレースホルダーはそのまま出力
            html_content += f"{line}\n"
        else:
            # 各行を独立した段落ブロックとして扱う
            html_content += f"<!-- wp:paragraph --><p>{line}</p><!-- /wp:paragraph -->\n"
            
    return html_content

def upload_image(config, image_path, alt_text=''):
    """画像をWordPressにアップロードし、メディア情報を返す (メタデータ更新処理を含む)"""
    wp_config = config['wordpress']
    media_api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/media"
    credentials = f"{wp_config['username']}:{wp_config['password']}"
    token = base64.b64encode(credentials.encode())
    auth_headers = {'Authorization': f'Basic {token.decode("utf-8")}'}
    
    filename = os.path.basename(image_path)
    
    # Step 1: Upload the image file
    try:
        with open(image_path, 'rb') as img:
            headers = {
                **auth_headers,
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'image/jpeg' 
            }
            upload_response = requests.post(media_api_url, headers=headers, data=img)
            upload_response.raise_for_status()
            media_object = upload_response.json()
            media_id = media_object['id']
            print(f"画像 {filename} のアップロードに成功しました (ID: {media_id})。")
    except Exception as e:
        print(f"画像アップロードエラー: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print("サーバーからのエラーメッセージ:", e.response.text)
        return None

    # Step 2: Update the media item with alt text and other metadata
    try:
        update_url = f"{media_api_url}/{media_id}"
        update_data = {
            'alt_text': alt_text,
            'title': os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()
        }
        update_response = requests.post(update_url, headers=auth_headers, json=update_data)
        update_response.raise_for_status()
        print(f"メディアID {media_id} の代替テキストを更新しました。")
        return update_response.json() # Return the updated object
    except Exception as e:
        print(f"代替テキストの更新エラー: {e}")
        # Even if this fails, we can still proceed with the original media object
        return media_object

def create_image_block(media_object, alt_text):
    """メディアオブジェクトから画像ブロックのHTMLを生成する"""
    media_id = media_object['id']
    source_url = media_object['source_url']
    # srcに実際のURLを埋め込むように変更
    return f'<!-- wp:image {{"id":{media_id},"sizeSlug":"large","linkDestination":"none"}} --><figure class="wp-block-image size-large"><img src="{source_url}" alt="{alt_text}" class="wp-image-{media_id}"/></figure><!-- /wp:image -->\n'

def get_post_id_by_slug(config, slug):
    """スラッグから投稿IDを取得する"""
    wp_config = config['wordpress']
    api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts"
    params = {'slug': slug}
    credentials = f"{wp_config['username']}:{wp_config['password']}"
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': f'Basic {token.decode("utf-8")}'}
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        posts = response.json()
        if posts:
            print(f"既存の投稿ID: {posts[0]['id']} を見つけました。")
            return posts[0]['id']
        else:
            print(f"スラッグ '{slug}' に一致する投稿が見つかりませんでした。新規投稿します。")
            return None
    except requests.exceptions.RequestException as e:
        print(f"投稿取得エラー: {e}")
        return None

def post_to_wordpress(config, article_content_html, seo_settings, category_id, featured_media_id=None, post_id=None):
    """WordPress REST APIを使ってブログ記事を投稿または更新する"""
    wp_config = config['wordpress']
    
    # post_idがあれば更新、なければ新規作成
    if post_id:
        api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts/{post_id}"
    else:
        api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts"

    credentials = f"{wp_config['username']}:{wp_config['password']}"
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': f'Basic {token.decode("utf-8")}'}

    post_data = {
        'title': seo_settings['h1'],
        'slug': seo_settings['slug'],
        'content': article_content_html,
        'status': "publish",
        'categories': [category_id],
        'meta': {
            '_seopress_titles_title': seo_settings['h1'],
            '_seopress_titles_desc': seo_settings['meta_description'],
            '_seopress_analysis_target_kw': seo_settings.get('keywords', '')
        }
    }
    if featured_media_id:
        post_data['featured_media'] = featured_media_id

    try:
        # SEOPressのキーワードは `json` パラメータではなく `data` パラメータで送信する必要がある
        # そのため、リクエストを2段階に分ける
        
        # Step 1: 記事本体を投稿/更新
        core_data = post_data.copy()
        del core_data['meta'] # metaは別で更新
        
        response = requests.post(api_url, headers=headers, json=core_data)
        response.raise_for_status()
        
        updated_post = response.json()
        post_link = updated_post.get('link')
        new_post_id = updated_post.get('id')

        # Step 2: SEOメタデータを更新
        meta_update_data = {
            'meta': {
                '_seopress_titles_title': seo_settings['h1'],
                '_seopress_titles_desc': seo_settings['meta_description'],
                '_seopress_analysis_target_kw': seo_settings.get('keywords', '')
            }
        }
        
        # 更新時は new_post_id を使う
        meta_api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts/{new_post_id}"
        meta_response = requests.post(meta_api_url, headers=headers, json=meta_update_data)
        meta_response.raise_for_status()


        message = "ブログ投稿の更新が成功しました！" if post_id else "ブログ投稿が成功しました！"
        print(f"\n{message}")
        print("URL:", post_link)
    except requests.exceptions.RequestException as e:
        error_type = "更新" if post_id else "投稿"
        print(f"{error_type}エラー: {e}")
        if hasattr(e.response, 'text'):
            print("サーバーからのエラーメッセージ:", e.response.text)

# --- Main Logic ---

if __name__ == "__main__":
    # 1. Load Configurations
    config = load_config()
    
    # スクリプトの場所を基準にパスを構築
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Define Article and Image Paths
    ARTICLE_FILE = os.path.join(script_dir, "ブログ/0930/0716　送別会/final_article.md")
    IMG_FEAT = os.path.join(script_dir, "ブログ/0930/0716　送別会/chubu-daiichi-farewell-party-01.jpg")
    IMG_IN_1 = os.path.join(script_dir, "ブログ/0930/0716　送別会/chubu-daiichi-farewell-party-02.jpg")
    IMG_IN_2 = os.path.join(script_dir, "ブログ/0930/0716　送別会/chubu-daiichi-farewell-party-03.jpg")
    CATEGORY_ID = 6

    # 3. Define SEO and Alt Texts
    slug_date = datetime.now().strftime('%Y%m%d')
    seo_settings = {
        "h1": "3年間の感謝を込めて｜中部第一の仲間、技能実習生送別会",
        "meta_description": "3年間、中部第一グループを支えてくれた技能実習生のイェンさんとホアさんの送別会を開催しました。パレット検品業務への貢献に感謝し、会長からの温かい言葉と共に、社員一同で彼らの輝かしい未来を願う感動的な時間となりました。",
        "slug": f"farewell-party-technical-interns-{slug_date}",
        "keywords": "技能実習生, 送別会, 中部第一グループ, 国際交流" # キーワードを追加
    }
    alt_texts = {
        IMG_FEAT: "中部第一グループの送別会で、感謝のプレゼントを受け取る技能実習生",
        IMG_IN_1: "送別会で技能実習生に温かい言葉を贈る中部第一グループの会長",
        IMG_IN_2: "中部第一グループの社員一同がテーブルを囲み、技能実習生の門出を祝う送別会の様子"
    }

    # 4. Load Original Markdown
    original_article_md = """## 🌸 3年間の感謝を込めて、大切な仲間たちの送別会を開催しました

去る7月16日、
私たち**中部第一グループ**は、
大切な仲間である技能実習生の
**イェンさん**と**ホアさん**の送別会を執り行いました。

お二人は、約3年という長きにわたり、
日々、パレット検品という重要な業務に、
真摯に取り組んでくれました。

その誠実な仕事ぶりと明るい笑顔は、
職場に活気を与えてくれるだけでなく、
会社の成長にとっても、
かけがえのない大きな力となっていました。

<!-- image_placeholder_0 -->

### 温かい言葉に包まれた、なごやかな時間

送別会では、
共に働いた仲間たちと思い出話に花を咲かせ、
笑顔と、少しの寂しさが入り混じる、
温かい時間が流れました。

会の終盤には、
会長よりお二人への**感謝**の気持ちと共に、
未来に向けた温かい励ましの言葉が贈られました。

その言葉一つひとつに、
会社の誰もが、
深く頷いていたのが印象的でした。

<!-- image_placeholder_1 -->

### 未来へのエール ✈️

イェンさん、ホアさん、
3年間、本当にお疲れさまでした。
そして、たくさんの貢献をありがとう。

皆さんと一緒に働くことができて、
社員一同、本当に嬉しく思っています。

日本での貴重な経験が、
お二人の今後の人生にとって、
大きな糧となることを、心から願っています。

母国でのご健闘と、
輝かしい未来、そしてご多幸を、
**中部第一グループ**社員一同、
心よりお祈り申し上げます。

また、いつかどこかで会いましょう！✨

<!-- image_placeholder_2 -->
"""

    # 5. Upload images and get their IDs
    print("\n--- 画像のアップロードを開始 ---")
    featured_media_object = upload_image(config, IMG_FEAT, alt_texts[IMG_FEAT])
    in_post_media_object_1 = upload_image(config, IMG_IN_1, alt_texts[IMG_IN_1])
    in_post_media_object_2 = upload_image(config, IMG_IN_2, alt_texts[IMG_IN_2])
    print("--- 画像のアップロードが完了 ---")

    # 6. Convert final markdown to HTML and insert image blocks
    base_html = markdown_to_html_blocks(original_article_md)
    
    final_html = base_html
    if featured_media_object:
        final_html = final_html.replace("<!-- image_placeholder_0 -->", create_image_block(featured_media_object, alt_texts[IMG_FEAT]))
    if in_post_media_object_1:
        final_html = final_html.replace("<!-- image_placeholder_1 -->", create_image_block(in_post_media_object_1, alt_texts[IMG_IN_1]))
    if in_post_media_object_2:
        final_html = final_html.replace("<!-- image_placeholder_2 -->", create_image_block(in_post_media_object_2, alt_texts[IMG_IN_2]))
    
    # 7. Get existing post ID to update it
    print("\n--- 既存の投稿を検索 ---")
    # Note: Using the slug from the previous attempt. If that slug changes, this needs to be updated.
    previous_slug = f"farewell-party-technical-interns-20251006"
    post_id = get_post_id_by_slug(config, previous_slug)
    
    # If post not found, fallback to creating a new one with today's slug
    if not post_id:
        print("既存の投稿が見つからなかったため、新しいスラッグで新規投稿を試みます。")
        seo_settings['slug'] = f"farewell-party-technical-interns-{datetime.now().strftime('%Y%m%d%H%M')}"


    # 8. Post to WordPress
    print("\n--- WordPressへの投稿（または更新）を開始 ---")
    featured_media_id = featured_media_object['id'] if featured_media_object else None
    post_to_wordpress(config, final_html, seo_settings, CATEGORY_ID, featured_media_id, post_id)
    print("--- 投稿プロセスが完了 ---")
