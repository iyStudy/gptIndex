##  使用したver
python 3.10  
llama_index version v0.10.16

## 事前準備
- OpenAIのAPIKeyを取得  
- Tesseractのインストール
  - 以下からTesseractをインストール。  
    Windows: https://github.com/UB-Mannheim/tesseract/wiki  
    macOS: `brew install tesseract`  
    Linux: `sudo apt install tesseract-ocr`  
  - 環境変数にパスを入れる。
    - windowsの場合 `C:\Program Files\Tesseract-OCR`
  - 日本語の学習データ（jpn.traineddata）を配置する
    - Tesseractの日本語の学習データ（jpn.traineddata）は以下。
    - https://github.com/tesseract-ocr/tessdata/blob/main/jpn.traineddata
    - ダウンロード後、jpn.traineddata ファイルを `Tesseract-OCR\tessdata` フォルダに配置する。
## インストール
`pip install llama-index=0.10.16 pytesseract Pillow openai`


