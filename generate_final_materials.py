import requests
import json
import base64
import os
import re

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

def upload_image_and_get_object(config, image_path, alt_text=''):
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
        return update_response.json()
    except Exception as e:
        print(f"代替テキストの更新エラー ({filename}): {e}")
        return media_object

def create_image_block(media_object, alt_text):
    media_id = media_object['id']
    source_url = media_object['source_url']
    return f'<!-- wp:image {{\"id":{media_id},"sizeSlug":"large","linkDestination":"none"}} --><figure class="wp-block-image size-large"><img src="{source_url}" alt="{alt_text}" class="wp-image-{media_id}"/></figure><!-- /wp:image -->\n'

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = load_config()
    
    ARTICLE_PATH = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/article.md")
    IMG_HOAI = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/chubu-daiichi-technical-intern-tran-thi-hoai.jpg")
    IMG_HUONG = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/chubu-daiichi-technical-intern-chinh-thi-huong.jpg")
    OUTPUT_PATH = os.path.join(script_dir, "ブログ/0930/0903　２名のベトナム技能実習生入社/final_post_materials.md")

    seo_settings = {
        "h1": "ベトナムから新たな仲間！2名の技能実習生が入社しました",
        "meta_description": "9月3日、中部第一グループにベトナムから2名の技能実習生、チャン・ティ・ホアイさんとチン・ティ・フォンさんが入社しました。ご家族のために日本で働くことを決意したお二人を、社員一同温かく歓迎します。",
        "slug": "welcome-vietnam-technical-interns-20251006",
        "keywords": "技能実習生, ベトナム, 中部第一グループ, 入社"
    }
    alt_texts = {
        IMG_HOAI: "ベトナムから中部第一グループに入社した、技能実習生のチャン・ティ・ホアイさん",
        IMG_HUONG: "ベトナムから中部第一グループに入社した、技能実習生のチン・ティ・フォンさん"
    }

    hoai_obj = upload_image_and_get_object(config, IMG_HOAI, alt_texts[IMG_HOAI])
    huong_obj = upload_image_and_get_object(config, IMG_HUONG, alt_texts[IMG_HUONG])
    
    with open(ARTICLE_PATH, 'r', encoding='utf-8') as f:
        original_article_md = f.read()

    base_html = markdown_to_html_blocks(original_article_md)
    final_html = base_html
    if hoai_obj:
        final_html = final_html.replace("<!-- image_placeholder_1 -->", create_image_block(hoai_obj, alt_texts[IMG_HOAI]))
    if huong_obj:
        final_html = final_html.replace("<!-- image_placeholder_2 -->", create_image_block(huong_obj, alt_texts[IMG_HUONG]))

    output_content = f"""# 手動投稿用・最終稿データ

この度は、自動投稿が完了せず、大変申し訳ございませんでした。
以下のデータをご利用いただき、手動での投稿をお願いいたします。

---

## 1. 本文用HTMLコード

下記コードを全文コピーし、WordPress投稿編集画面の「コードエディター」に貼り付けてください。

```html
{final_html}
```

---

## 2. SEO設定

下記の内容を、SEOPressの各項目にコピー＆ペーストしてください。

- **タイトル (H1):** `{seo_settings['h1']}`
- **URLスラッグ:** `{seo_settings['slug']}`
- **メタディスクリプション:** `{seo_settings['meta_description']}`
- **キーワード:** `{seo_settings['keywords']}`

---

## 3. アイキャッチ画像

お手数ですが、以下の画像を手動でアップロードし、アイキャッチとして設定してください。

- **ファイル名:** `chubu-daiichi-vietnam-interns-welcome-illustration.png`

"""

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(output_content)
        
    print(f"最終稿データが '{OUTPUT_PATH}' に作成されました。")

if __name__ == "__main__":
    main()
