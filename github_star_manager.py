import os
import sqlite3
import requests
from datetime import datetime
from jinja2 import Template

GITHUB_TOKEN = "your_github_token"
DB_NAME = "stars.db"
HTML_TEMPLATE = "template.html"
OUTPUT_HTML = "stars_manager.html"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stars
                 (id INTEGER PRIMARY KEY,
                 name TEXT,
                 full_name TEXT,
                 html_url TEXT,
                 description TEXT,
                 language TEXT,
                 tags TEXT,
                 created_at DATETIME)''')
    conn.commit()
    conn.close()

def fetch_stars():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = "https://api.github.com/user/starred"
    stars = []
    
    while url:
        response = requests.get(url, headers=headers)
        stars.extend(response.json())
        url = response.links.get('next', {}).get('url')
    
    return [{
        'id': s['id'],
        'name': s['name'],
        'full_name': s['full_name'],
        'html_url': s['html_url'],
        'description': s['description'],
        'language': s['language'],
        'tags': '',
        'created_at': datetime.strptime(s['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    } for s in stars]

def save_to_db(stars):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 清空旧数据
    c.execute("DELETE FROM stars")
    
    # 插入新数据
    for star in stars:
        c.execute('''INSERT OR REPLACE INTO stars 
                     (id, name, full_name, html_url, description, language, tags, created_at)
                     VALUES (?,?,?,?,?,?,?,?)''',
                  (star['id'], star['name'], star['full_name'], star['html_url'],
                   star['description'], star['language'], star['tags'], star['created_at']))
    conn.commit()
    conn.close()

def generate_html():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM stars ORDER BY created_at DESC")
    stars = c.fetchall()
    conn.close()

    with open(HTML_TEMPLATE, encoding='utf-8') as f:
        template = Template(f.read())
    
    html = template.render(stars=stars)
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    init_db()
    stars = fetch_stars()
    save_to_db(stars)
    generate_html()
    print(f"管理页面已更新：{OUTPUT_HTML}")