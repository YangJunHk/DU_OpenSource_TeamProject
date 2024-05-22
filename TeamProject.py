# 필요한 패키지 설치
!pip install gtts googletrans==4.0.0-rc1 hangulize

from hangulize import hangulize
from gtts import gTTS
from googletrans import Translator

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

if __name__ == "__main__":
    # 사용자 입력 받기
    foreign_text = input("번역할 일본어 텍스트를 입력하세요: ")

    # 번역
    translated_text = translate_to_korean(foreign_text)
    print(f"번역된 텍스트: {translated_text}")

    # 한국어 발음 변환 및 저장
    text_to_korean_pronunciation(translated_text)

    # 일본어를 한글 외래어 발음으로 변환
    korean_pronunciation = japanese_to_korean_pronunciation(foreign_text)
    print(f"한글 외래어 발음: {korean_pronunciation}")