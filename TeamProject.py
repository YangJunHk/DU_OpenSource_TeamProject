import os
from hangulize import hangulize
from gtts import gTTS
from googletrans import Translator
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, filedialog

# Translator 객체 생성
translator = Translator()

# 번역 및 발음 생성 함수
def translate_to_korean(text, src_lang):
    translation = translator.translate(text, src=src_lang, dest='ko')
    return translation.text

def text_to_korean_pronunciation(text, filepath):
    tts = gTTS(text, lang='ko')
    tts.save(filepath)
    print(f"한국어 발음 파일이 '{filepath}'로 저장되었습니다.")

def japanese_to_korean_pronunciation(text):
    return hangulize(text, 'jpn')

def save_pronunciation():
    filepath = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])
    if filepath:
        text_to_korean_pronunciation(translated_text.get(), filepath)

def translate_and_display():
    try:
        text = input_text.get()
        src_lang = language_var.get()
        translated = translate_to_korean(text, src_lang)
        translated_text.set(translated)
        pronunciation = japanese_to_korean_pronunciation(text)
        korean_pronunciation.set(pronunciation)
    except Exception as e:
        translated_text.set("번역 중 오류가 발생했습니다.")
        korean_pronunciation.set(str(e))

# GUI 설정
root = Tk()
root.title("번역 및 발음 변환기")

# 입력 텍스트 레이블과 입력 상자
Label(root, text="번역할 텍스트:").grid(row=0, column=0, padx=10, pady=10)
input_text = StringVar()
Entry(root, textvariable=input_text, width=50).grid(row=0, column=1, padx=10, pady=10)

# 언어 선택 메뉴
Label(root, text="원본 언어:").grid(row=1, column=0, padx=10, pady=10)
language_var = StringVar(value='ja')
OptionMenu(root, language_var, 'ja').grid(row=1, column=1, padx=10, pady=10)

# 번역된 텍스트 레이블
Label(root, text="번역된 텍스트:").grid(row=2, column=0, padx=10, pady=10)
translated_text = StringVar()
Label(root, textvariable=translated_text, wraplength=400).grid(row=2, column=1, padx=10, pady=10)

# 한글 외래어 발음 레이블
Label(root, text="한글 외래어 발음:").grid(row=3, column=0, padx=10, pady=10)
korean_pronunciation = StringVar()
Label(root, textvariable=korean_pronunciation, wraplength=400).grid(row=3, column=1, padx=10, pady=10)

# 번역 및 발음 변환 버튼
Button(root, text="번역 및 발음 변환", command=translate_and_display).grid(row=4, column=0, columnspan=2, pady=10)

# 발음 파일 저장 버튼
Button(root, text="발음 파일 저장", command=save_pronunciation).grid(row=5, column=0, columnspan=2, pady=10)

root.mainloop()
