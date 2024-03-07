import openai
from config import API_KEY  # APIキーをconfig.pyから読み込む
import logging
import pdfplumber
from pdf2image import convert_from_path
import os
import sys
from tkinter import filedialog
import pytesseract
from llama_index.core import SimpleDirectoryReader,StorageContext, load_index_from_storage,VectorStoreIndex

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True) # ログレベルの設定

## OpenAIのAPIキーが必要となります。
# API_KEY = "openai_api_key"
openai.api_key = API_KEY

template = """あなたは世界中で信頼されているQAシステムです。
事前知識ではなく、常に提供されたコンテキスト情報を使用して回答してください。
従うべきいくつかのルール:
1. 回答内で指定されたコンテキストを直接参照しないでください。
2. 「コンテキストに基づいて、...」や「コンテキスト情報は...」、またはそれに類するような記述は避けてください。
3. 回答は日本語で提供してください。
4. 情報が多い場合も省略せずに箇条書きで回答してください。
    例：・これは1つ目の情報です。
            - 1つ目の情報の詳細な内容を具体的に記載してください
        ・これは2つ目の情報です。
            - 2つ目の情報の詳細な内容を具体的に記載してください
5. 回答は曖昧にせず具体的な内容で回答してください。
6. 回答する前に、ファクトチェックを行ってください。
以下質問内容です。

"""

# PDFファイルをpdfplumberでMarkdown形式に変換する関数
def pdf_to_markdown(pdf_path, output_md_path):
    # PDFファイルを開く
    with pdfplumber.open(pdf_path) as pdf:
        markdown_content = ""
        # 各ページを処理
        for page in pdf.pages:
            # テキストを抽出
            text = page.extract_text()
            if text:
                # ここで必要に応じてMarkdown形式に整形する
                # 例: 簡易的にパラグラフを改行で区切る
                markdown_content += text.replace('\n', '  \n') + '\n\n'
    
    # Markdownファイルに書き出す
    with open(output_md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_content)
    
def replace_circle_numbers(text):
    # 丸数字の対応表
    circle_number_map = {
        '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
        '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10',
        '⑪': '11', '⑫': '12', '⑬': '13', '⑭': '14', '⑮': '15',
        '⑯': '16', '⑰': '17', '⑱': '18', '⑲': '19', '⑳': '20'
    }

    for circle_num, arabic_num in circle_number_map.items():
        text = text.replace(circle_num, arabic_num)
    
    return text

def pdf_to_markdown_ocr(pdf_path, output_md_path):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # PDFを画像に変換
    images = convert_from_path(pdf_path)
    
    markdown_content = ""
    # 各画像についてOCRを実行
    for i, image in enumerate(images):
        # PSM 6を指定してOCRを実行
        text = pytesseract.image_to_string(image, lang='jpn', config='--psm 6')
        # 丸数字をアラビア数字に変換
        text = replace_circle_numbers(text)
        # 不要なスペースを削除
        text = text.replace(' ', '')
        # ここでMarkdown形式に整形する
        markdown_content += text.replace('\n', '  \n') + '\n\n'
    
    # Markdownファイルに書き出す
    with open(output_md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_content)




### ドキュメント作成　###
def create_document(input_file_path):
    # 入力ファイルパスからファイル名（拡張子なし）を取得
    file_name = os.path.splitext(os.path.basename(input_file_path))[0]
    # 出力Markdownファイルのパスを生成
    output_md_path = f'input/{file_name}.md'

    # pdf_to_markdown(pdf_path, output_md_path) # pdfplumberを使った場合の変換
    pdf_to_markdown_ocr(input_file_path, output_md_path)# OCRを使った場合の変換



### indexを作成する関数 ###
def create_index():
    # ドキュメントの読み込み
    documents = SimpleDirectoryReader("input").load_data()
    # インデックスの作成
    index = VectorStoreIndex.from_documents(documents)
    # インデックスの保存
    index.storage_context.persist()

## インデックスを読み込む関数 ##
def load_index():
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    # load index
    index = load_index_from_storage(storage_context)
    return index

### 回答出力 ###
def main():
    index = load_index()
    # query_engine = index.as_query_engine()  # データに対して質問するためのエンジン
    query_engine = index.as_chat_engine()  # チャットボットとして使うためのエンジン
    res = query_engine.query(f"{template} 卒業に必要な単位について教えてください。")
    print(f"回答：{res}")

if __name__ == "__main__":
    # pdf_path = 'HANDBOOK_2023.pdf'  # PDFファイルのパス
    pdf_path = file_path = filedialog.askopenfilename()  # PDFファイルのパス
    if pdf_path:
        create_document(pdf_path)
        create_index()
        main()