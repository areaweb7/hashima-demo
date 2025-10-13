import requests
import json
import base64
import os
import re
from datetime import datetime

# --- Functions ---

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "settings.json"), 'r', encoding='utf-8') as f:
        return json.load(f)

def markdown_to_html_blocks(md_content):
    html_content = ""
    lines = md_content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r'\*\*(.*?)\*\*', r'<span style="font-weight: bold;">\1</span>', line)
        if line.startswith('## '):
            html_content += f"<!-- wp:heading {{\"level\":2}} --><h2>{line.lstrip('# ').strip()}</h2><!-- /wp:heading -->\n"
        elif line.startswith('### '):
            html_content += f"<!-- wp:heading {{\"level\":3}} --><h3>{line.lstrip('# ').strip()}</h3><!-- /wp:heading -->\n"
        elif "<!-- image_placeholder" in line:
            html_content += f"{line}\n"
        else:
            html_content += f"<!-- wp:paragraph --><p>{line}</p><!-- /wp:paragraph -->\n"
    return html_content

def upload_image(config, image_path, alt_text=''):
    wp_config = config['wordpress']
    media_api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/media"
    credentials = f"{wp_config['username']}:{wp_config['password']}"
    token = base64.b64encode(credentials.encode())
    auth_headers = {'Authorization': f'Basic {token.decode("utf-8")}'}
    
    filename = os.path.basename(image_path)
    
    try:
        with open(image_path, 'rb') as img:
            content_type = 'image/png' if filename.endswith('.png') else 'image/jpeg'
            headers = {**auth_headers, 'Content-Disposition': f'attachment; filename={filename}', 'Content-Type': content_type}
            upload_response = requests.post(media_api_url, headers=headers, data=img)
            upload_response.raise_for_status()
            media_object = upload_response.json()
            media_id = media_object['id']
            print(f"画像 {filename} のアップロードに成功しました (ID: {media_id})。")
    except Exception as e:
        print(f"画像アップロードエラー ({filename}): {e}")
        return None

    try:
        update_url = f"{media_api_url}/{media_id}"
        update_data = {'alt_text': alt_text, 'title': os.path.splitext(filename)[0].replace('-', ' ').replace('_', ' ').title()}
        update_response = requests.post(update_url, headers=auth_headers, json=update_data)
        update_response.raise_for_status()
        print(f"メディアID {media_id} の代替テキストを更新しました。")
        return update_response.json()
    except Exception as e:
        print(f"代替テキストの更新エラー ({filename}): {e}")
        return media_object

def create_image_block(media_object, alt_text):
    media_id = media_object['id']
    source_url = media_object['source_url']
    return f'<!-- wp:image {{\"id":{media_id},"sizeSlug":"large","linkDestination":"none"}} --><figure class="wp-block-image size-large"><img src="{source_url}" alt="{alt_text}" class="wp-image-{media_id}"/></figure><!-- /wp:image -->\n'
    
def get_post_id_by_slug(config, slug):
    wp_config = config['wordpress']
    api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts"
    params = {'slug': slug, 'status': 'any'}
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
        return None
    except Exception:
        return None

def post_to_wordpress(config, article_content_html, seo_settings, category_id, featured_media_id=None, post_id=None):
    wp_config = config['wordpress']
    api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts/{post_id}" if post_id else f"https://{wp_config['domain']}/wp-json/wp/v2/posts"
    credentials = f"{wp_config['username']}:{wp_config['password']}"
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': f'Basic {token.decode("utf-8")}'}

    post_data = {
        'title': seo_settings['h1'], 'slug': seo_settings['slug'], 'content': article_content_html,
        'status': "publish", 'categories': [category_id], 'featured_media': featured_media_id
    }

    try:
        core_response = requests.post(api_url, headers=headers, json=post_data)
        core_response.raise_for_status()
        
        updated_post = core_response.json()
        post_link = updated_post.get('link')
        new_post_id = updated_post.get('id')

        meta_update_data = {
            'meta': {
                '_seopress_titles_title': seo_settings['h1'],
                '_seopress_titles_desc': seo_settings['meta_description'],
                '_seopress_analysis_target_kw': seo_settings.get('keywords', '')
            }
        }
        
        meta_api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts/{new_post_id}"
        meta_response = requests.post(meta_api_url, headers=headers, json=meta_update_data)
        meta_response.raise_for_status()

        print(f"\nブログ投稿の{'更新' if post_id else '作成'}が成功しました！")
        print("URL:", post_link)
    except Exception as e:
        print(f"投稿エラー: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print("サーバーからのエラーメッセージ:", e.response.text)

# --- Main Logic ---
if __name__ == "__main__":
    config = load_config()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    ARTICLE_PATH = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/article.md")
    IMG_FEAT = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/chubu-daiichi-vietnam-interns-welcome-illustration.png")
    IMG_HOAI = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/chubu-daiichi-technical-intern-tran-thi-hoai.jpg")
    IMG_HUONG = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/chubu-daiichi-technical-intern-chinh-thi-huong.jpg")
    CATEGORY_ID = 13 # ニュース

    seo_settings = {
        "h1": "ベトナムから新たな仲間！2名の技能実習生が入社しました",
        "meta_description": "9月3日、中部第一グループにベトナムから2名の技能実習生、チャン・ティ・ホアイさんとチン・ティ・フォンさんが入社しました。ご家族のために日本で働くことを決意したお二人を、社員一同温かく歓迎します。",
        "slug": "welcome-vietnam-technical-interns-20251006",
        "keywords": "技能実習生, ベトナム, 中部第一グループ, 入社"
    }
    alt_texts = {
        IMG_FEAT: "中部第一グループがベトナムからの技能実習生、ホアイさんとフォンさんを歓迎するイラスト",
        IMG_HOAI: "ベトナムから中部第一グループに入社した、技能実習生のチャン・ティ・ホアイさん",
        IMG_HUONG: "ベトナムから中部第一グループに入社した、技能実習生のチン・ティ・フォンさん"
    }

    with open(ARTICLE_PATH, 'r', encoding='utf-8') as f:
        original_article_md = f.read()

    print("\n--- 既存の投稿を検索 ---")
    post_id = get_post_id_by_slug(config, seo_settings['slug'])
    if not post_id:
        print("致命的エラー：更新対象の記事が見つかりません。")
        exit()

    print("\n--- 画像のアップロードを開始 ---")
    feat_obj = upload_image(config, IMG_FEAT, alt_texts[IMG_FEAT])
    hoai_obj = upload_image(config, IMG_HOAI, alt_texts[IMG_HOAI])
    huong_obj = upload_image(config, IMG_HUONG, alt_texts[IMG_HUONG])
    print("--- 画像のアップロードが完了 ---")

    base_html = markdown_to_html_blocks(original_article_md)
    final_html = base_html
    if hoai_obj:
        final_html = final_html.replace("<!-- image_placeholder_1 -->", create_image_block(hoai_obj, alt_texts[IMG_HOAI]))
    if huong_obj:
        final_html = final_html.replace("<!-- image_placeholder_2 -->", create_image_block(huong_obj, alt_texts[IMG_HUONG]))
    
    print("\n--- WordPressへの投稿（または更新）を開始 ---")
    feat_id = feat_obj['id'] if feat_obj else None
    post_to_wordpress(config, final_html, seo_settings, CATEGORY_ID, feat_id, post_id)
    print("--- 投稿プロセスが完了 ---")
