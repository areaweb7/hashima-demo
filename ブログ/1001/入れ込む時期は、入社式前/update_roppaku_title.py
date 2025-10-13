import requests
import json
import base64
import os

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, "../../..", "settings.json"), 'r', encoding='utf-8') as f:
        return json.load(f)

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
    except Exception as e:
        print(f"投稿検索エラー: {e}")
        return None

def update_post_title(config, post_id, new_title):
    wp_config = config['wordpress']
    api_url = f"https://{wp_config['domain']}/wp-json/wp/v2/posts/{post_id}"
    credentials = f"{wp_config['username']}:{wp_config['password']}"
    token = base64.b64encode(credentials.encode())
    headers = {'Authorization': f'Basic {token.decode("utf-8")}'}

    update_data = {
        'title': new_title,
        'meta': {
            '_seopress_titles_title': new_title,
        }
    }

    try:
        response = requests.post(api_url, headers=headers, json=update_data)
        response.raise_for_status()
        print(f"投稿ID {post_id} のタイトル更新に成功しました。")
        post_link = response.json().get('link')
        print("URL:", post_link)
        return True
    except Exception as e:
        print(f"タイトル更新エラー: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print("サーバーからのエラーメッセージ:", e.response.text)
        return False

# --- Main Logic ---
if __name__ == "__main__":
    config = load_config()
    SLUG = "roppaku-dormitory-completed-20251010"
    NEW_TITLE = "心安らぐ、新たな我が家。「六白寮」が完成しました！"

    print(f"--- スラッグ '{SLUG}' の投稿を検索 ---")
    post_id = get_post_id_by_slug(config, SLUG)
    
    if post_id:
        print(f"--- 投稿ID {post_id} のタイトルを更新 ---")
        update_post_title(config, post_id, NEW_TITLE)
        print("--- 更新プロセスが完了 ---")
    else:
        print("エラー: 更新対象の記事が見つかりませんでした。")
