import os
import json
from hangulize import hangulize
from gtts import gTTS
from googletrans import Translator
from hgtk.text import compose, decompose

# Translator 객체 생성
translator = Translator()

def translate_to_korean(text, src_lang='ja'):
    """
    입력된 텍스트를 src_lang에서 한국어로 번역합니다.
    
    :param text: 번역할 텍스트
    :param src_lang: 원본 텍스트의 언어 (기본값은 일본어)
    :return: 번역된 텍스트 (한국어)
    """
    translation = translator.translate(text, src=src_lang, dest='ko')
    return translation.text

def text_to_korean_pronunciation(text):
    """
    한국어 텍스트의 발음을 mp3 파일로 저장합니다.
    
    :param text: 발음을 생성할 텍스트 (한국어)
    """
    tts = gTTS(text, lang='ko')
    tts.save("korean_pronunciation.mp3")
    print("한국어 발음 파일이 'korean_pronunciation.mp3'로 저장되었습니다.")

def japanese_to_korean_pronunciation(text):
    """
    일본어 텍스트를 한글 외래어 발음으로 변환합니다.
    
    :param text: 변환할 일본어 텍스트
    :return: 한글 외래어 발음
    """
    return hangulize(text, 'jpn')

def korean_pronunciation_romanization(text):
    """
    한국어 텍스트를 로마자 발음 표기법으로 변환합니다.
    
    :param text: 변환할 한국어 텍스트
    :return: 로마자 발음 표기
    """
    decomposed = decompose(text)
    romanized = []

    # 한글 자모를 로마자로 변환
    hangul_to_roman = {
        'ㄱ': 'g', 'ㄲ': 'kk', 'ㄴ': 'n', 'ㄷ': 'd', 'ㄸ': 'tt', 'ㄹ': 'r', 'ㅁ': 'm', 'ㅂ': 'b', 'ㅃ': 'pp',
        'ㅅ': 's', 'ㅆ': 'ss', 'ㅇ': '', 'ㅈ': 'j', 'ㅉ': 'jj', 'ㅊ': 'ch', 'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 'ㅎ': 'h',
        'ㅏ': 'a', 'ㅐ': 'ae', 'ㅑ': 'ya', 'ㅒ': 'yae', 'ㅓ': 'eo', 'ㅔ': 'e', 'ㅕ': 'yeo', 'ㅖ': 'ye', 'ㅗ': 'o',
        'ㅘ': 'wa', 'ㅙ': 'wae', 'ㅚ': 'oe', 'ㅛ': 'yo', 'ㅜ': 'u', 'ㅝ': 'wo', 'ㅞ': 'we', 'ㅟ': 'wi', 'ㅠ': 'yu',
        'ㅡ': 'eu', 'ㅢ': 'ui', 'ㅣ': 'i'
    }

    for char in decomposed:
        romanized.append(hangul_to_roman.get(char, char))
    
    return ''.join(romanized)

def save_translation_history(history):
    """
    번역 히스토리를 JSON 파일로 저장합니다.
    
    :param history: 번역 히스토리 딕셔너리
    """
    with open("translation_history.json", "w") as file:
        json.dump(history, file)

def load_translation_history():
    """
    JSON 파일에서 번역 히스토리를 로드합니다.
    
    :return: 번역 히스토리 딕셔너리
    """
    if os.path.exists("translation_history.json"):
        with open("translation_history.json", "r") as file:
            history = json.load(file)
            return history
    else:
        return {}

if __name__ == "__main__":
    # 이전 번역 히스토리 로드
    translation_history = load_translation_history()

    # 사용자 입력 받기
    foreign_text = input("번역할 일본어 텍스트를 입력하세요: ")

    # 번역
    translated_text = translate_to_korean(foreign_text)
    print(f"번역된 텍스트: {translated_text}")

    # 히스토리에 번역 내용 추가
    translation_history[foreign_text] = translated_text
    save_translation_history(translation_history)

    # 한국어 발음 변환 및 저장
    text_to_korean_pronunciation(translated_text)

    # 일본어를 한글 외래어 발음으로 변환
    korean_pronunciation = japanese_to_korean_pronunciation(foreign_text)
    print(f"한글 외래어 발음: {korean_pronunciation}")

    # 번역된 한국어 텍스트를 로마자 발음 표기법으로 변환
    romanized_pronunciation = korean_pronunciation_romanization(translated_text)
    print(f"로마자 발음 표기: {romanized_pronunciation}")

    # 사용자가 번역 히스토리를 확인할 수 있도록 출력
    print("\n번역 히스토리:")
    for idx, (original, translated) in enumerate(translation_history.items(), start=1):
        print(f"{idx}. {original} -> {translated}")
