import json
import os
import webbrowser

def find_bookmarks_file():
    """
    Chromeのブックマークファイル 'Bookmarks' のパスを見つけます。
    OSによってパスが異なります。
    """
    home = os.path.expanduser("~")

    if os.name == 'posix':  # macOS, Linux
        # macOS
        chrome_path_mac = os.path.join(home, 'Library', 'Application Support', 'Google', 'Chrome', 'Default', 'Bookmarks')
        if os.path.exists(chrome_path_mac):
            return chrome_path_mac
        # Linux (一般的なパス)
        chrome_path_linux = os.path.join(home, '.config', 'google-chrome', 'Default', 'Bookmarks')
        if os.path.exists(chrome_path_linux):
            return chrome_path_linux
    elif os.name == 'nt':  # Windows
        appdata = os.getenv('LOCALAPPDATA')
        if appdata:
            chrome_path_win = os.path.join(appdata, 'Google', 'Chrome', 'User Data', 'Default', 'Bookmarks')
            if os.path.exists(chrome_path_win):
                return chrome_path_win
    return None

def get_urls_from_bookmark_folder(bookmark_file_path, folder_name):
    """
    ブックマークファイルから指定されたフォルダ内のURLをすべて抽出します。
    """
    urls = []
    try:
        with open(bookmark_file_path, 'r', encoding='utf-8') as f:
            bookmarks_data = json.load(f)

        # ブックマークのツリーを再帰的に探索する関数
        def traverse_bookmarks(node):
            if 'children' in node:
                for child in node['children']:
                    if child.get('type') == 'folder' and child.get('name') == folder_name:
                        # 指定されたフォルダが見つかった場合、その中のURLを収集
                        for item in child['children']:
                            if item.get('type') == 'url' and 'url' in item:
                                urls.append(item['url'])
                    elif child.get('type') == 'folder':
                        # フォルダの場合はさらに深く探索
                        traverse_bookmarks(child)
            return urls

        # rootの'bookmark_bar'と'other'の両方を探索
        if 'roots' in bookmarks_data:
            if 'bookmark_bar' in bookmarks_data['roots']:
                traverse_bookmarks(bookmarks_data['roots']['bookmark_bar'])
            if 'other' in bookmarks_data['roots']:
                traverse_bookmarks(bookmarks_data['roots']['other'])
            # 'synced' も含める場合
            if 'synced' in bookmarks_data['roots']:
                traverse_bookmarks(bookmarks_data['roots']['synced'])

    except FileNotFoundError:
        print(f"Error: Bookmark file not found at {bookmark_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {bookmark_file_path}. The file might be corrupted.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    return urls

def open_urls_in_chrome(urls):
    """
    取得したURLをGoogle Chromeの新しいタブで開きます。
    """
    if not urls:
        print("No URLs found to open.")
        return

    # Google Chromeの実行可能ファイルのパスをここに指定してください。
    # ご自身の環境に合わせて、上記で調べたパスに置き換えてください。
    # 例: CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' # <-- ここをあなたのパスに修正！

    try:
        # Chromeのパスをwebbrowserモジュールに登録
        # 'google-chrome' は登録名で、任意の文字列でOKですが、ここでは一般的な名前を使用
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(CHROME_PATH))
        chrome = webbrowser.get('chrome')

        for i, url in enumerate(urls):
            # 最初のURLはopen()で新しいウィンドウ/タブを開く
            # 以降のURLはopen_new_tab()で新しいタブを開く
            if i == 0:
                chrome.open(url)
            else:
                chrome.open_new_tab(url)
            
            # 連続でタブを開くとブラウザが一時的に固まることがあるため、少し間隔を空ける
            time.sleep(0.5) # 0.5秒待つ

    except webbrowser.Error as e:
        print(f"Error opening Chrome: {e}")
        print(f"Please ensure Google Chrome is installed at '{CHROME_PATH}'")
        print("Or update the CHROME_PATH variable in the script.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # ここに開きたいブックマークフォルダの名前を指定してください
    target_folder_name = "流行り" # 例: "仕事用サイト", "Daily Links" など

    bookmarks_file = find_bookmarks_file()

    if bookmarks_file:
        print(f"Bookmarks file found at: {bookmarks_file}")
        urls_to_open = get_urls_from_bookmark_folder(bookmarks_file, target_folder_name)

        if urls_to_open:
            print(f"Found {len(urls_to_open)} URLs in folder '{target_folder_name}':")
            for url in urls_to_open:
                print(f"- {url}")
            
            open_urls_in_chrome(urls_to_open)
            print("Finished opening URLs.")
        else:
            print(f"No URLs found in the folder '{target_folder_name}' or the folder does not exist.")
    else:
        print("Could not locate Google Chrome's Bookmarks file. Please check your Chrome installation and user profile.")
