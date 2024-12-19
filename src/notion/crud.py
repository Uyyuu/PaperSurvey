import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

# queryからそのデータベースの構造を取得して自動でテンプレート化できるようにしたい。
class NotionRepository:
    def __init__(self, * ,token: str=None, db_id: str=None):
        if not token:
            token = os.environ.get("NOTION_TOKEN")
        self.notion = Client(auth=token)

        if not db_id:
            self.database_id = os.environ.get("NOTION_DB_ID")
    
    def create_markdown_page(self, title, markdown_content):
        """
        マークダウンコンテンツを含むNotionページを作成する
        
        Parameters:
        - notion: Notion Client インスタンス
        - database_id: データベースID
        - title: ページタイトル
        - markdown_content: マークダウンコンテンツ
        """
        
        # マークダウンをNotionブロックに変換する関数
        def convert_heading_to_blocks(text, level):
            return {
                'object': 'block',
                'type': f'heading_{level}',
                f'heading_{level}': {
                    'rich_text': [{'type': 'text', 'text': {'content': text}}]
                }
            }
        
        # コンテンツをブロックに変換
        blocks = []
        current_text = []
        
        for line in markdown_content.split('\n'):
            # 見出し1の処理 (#)
            if line.startswith('# '):
                if current_text:
                    blocks.append({
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(current_text)}}]
                        }
                    })
                    current_text = []
                blocks.append(convert_heading_to_blocks(line[2:].strip(), 1))
                
            # 見出し2の処理 (##)
            elif line.startswith('## '):
                if current_text:
                    blocks.append({
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(current_text)}}]
                        }
                    })
                    current_text = []
                blocks.append(convert_heading_to_blocks(line[3:].strip(), 2))
                
            # 空行の処理
            elif line.strip() == '':
                if current_text:
                    blocks.append({
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(current_text)}}]
                        }
                    })
                    current_text = []
                
            # 通常のテキスト処理
            else:
                current_text.append(line)
        
        # 残りのテキストを処理
        if current_text:
            blocks.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(current_text)}}]
                }
            })

        # ページの作成
        return self.notion.pages.create(
            **{
                'parent': {'database_id': self.database_id},
                'properties': {
                    'title': {
                        'title': [
                            {
                                'text': {
                                    'content': title
                                }
                            }
                        ]
                    }
                },
                'children': blocks
            }
        )