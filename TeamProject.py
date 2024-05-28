import os
import json
import sys

# 현재 파일의 디렉토리 경로를 가져옵니다.
current_dir = os.path.dirname(os.path.abspath(__file__))

# PYTHONPATH 설정
sys.path.append(os.path.join(current_dir, 'hangulize'))
sys.path.append(os.path.join(current_dir, 'openvoice'))

import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
from hangulize import hangulize
from gtts import gTTS
from googletrans import Translator
from hgtk.text import compose, decompose
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, filedialog, Toplevel, Text, Scrollbar, VERTICAL, END

# ffmpeg 경로 설정
ffmpeg_path = "C:\\Program Files (x86)\\ffmpeg\\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

# 체크포인트 경로 및 장치 설정
ckpt_base_en = os.path.join(current_dir, 'checkpoints', 'base_speakers', 'EN')
ckpt_converter = os.path.join(current_dir, 'checkpoints', 'converter')
device = "cuda:0" if torch.cuda.is_available() else "cpu"
output_dir = os.path.join(current_dir, 'outputs')
os.makedirs(output_dir, exist_ok=True)

# 모델 로드 함수
def load_models(base_path, converter_path, device):
    base_speaker_tts = BaseSpeakerTTS(f'{base_path}/config.json', device=device)
    base_speaker_tts.load_ckpt(f'{base_path}/checkpoint.pth')
    
    tone_color_converter = ToneColorConverter(f'{converter_path}/config.json', device=device)
    tone_color_converter.load_ckpt(f'{converter_path}/checkpoint.pth')
    
    return base_speaker_tts, tone_color_converter

# 음성 스타일 추출 함수
def extract_style(reference_speaker, converter, device):
    return se_extractor.get_se(reference_speaker, converter, target_dir='processed', vad=True)[0].to(device)

# 음성 생성 및 변환 함수
def generate_and_convert_audio(text, base_speaker, converter, source_se, target_se, speaker, language, speed, output_path):
    tmp_path = os.path.join(output_dir, 'tmp.wav')
    
    # 음성 생성
    base_speaker.tts(text, tmp_path, speaker=speaker, language=language, speed=speed)
    
    # 톤 컬러 변환
    converter.convert(
        audio_src_path=tmp_path, 
        src_se=source_se, 
        tgt_se=target_se, 
        output_path=output_path,
        message="@MyShell"
    )

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
        
        # 번역된 한국어 텍스트를 로마자 발음 표기법으로 변환
        romanized_pronunciation = korean_pronunciation_romanization(translated)
        romanized_text.set(romanized_pronunciation)
        
        # 히스토리에 번역 내용 추가
        translation_history[text] = translated
        save_translation_history(translation_history)
        
    except Exception as e:
        translated_text.set("번역 중 오류가 발생했습니다.")
        korean_pronunciation.set(str(e))

def synthesize_speech():
    try:
        text = input_text.get()
        src_lang = language_var.get()
        
        # 영어 기본 모델 및 톤 컬러 변환기 로드
        base_speaker_tts_en, tone_color_converter = load_models(ckpt_base_en, ckpt_converter, device)
        
        # 영어 기본 스타일 음성 임베딩 로드
        source_se_en_default = torch.load(f'{ckpt_base_en}/en_default_se.pth').to(device)
        
        # 참조 음성 파일로부터 대상 스타일 음성 임베딩 추출
        reference_speaker = 'resources/example_reference.mp3'
        target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)
        
        # 영어 음성 생성 및 변환 (기본 스타일)
        output_path_en_default = os.path.join(output_dir, 'output_en_default.wav')
        generate_and_convert_audio(
            text=text,
            base_speaker=base_speaker_tts_en,
            converter=tone_color_converter,
            source_se=source_se_en_default,
            target_se=target_se,
            speaker='default',
            language='English',
            speed=1.0,
            output_path=output_path_en_default
        )
        translated_text.set("음성 합성이 완료되었습니다. 파일 경로: " + output_path_en_default)
    except Exception as e:
        translated_text.set("음성 합성 중 오류가 발생했습니다.")
        korean_pronunciation.set(str(e))

def view_history():
    history_window = Toplevel(root)
    history_window.title("번역 히스토리")
    
    scrollbar = Scrollbar(history_window, orient=VERTICAL)
    history_text = Text(history_window, wrap="word", yscrollcommand=scrollbar.set)
    scrollbar.config(command=history_text.yview)
    scrollbar.pack(side="right", fill="y")
    history_text.pack(side="left", fill="both", expand=True)
    
    history_text.insert(END, "번역 히스토리:\n")
    for original, translated in translation_history.items():
        history_text.insert(END, f"{original} -> {translated}\n")

# GUI 설정
root = Tk()
root.title("번역 및 발음 변환기")

# 이전 번역 히스토리 로드
translation_history = load_translation_history()

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

# 로마자 발음 표기 레이블
Label(root, text="로마자 발음 표기:").grid(row=4, column=0, padx=10, pady=10)
romanized_text = StringVar()
Label(root, textvariable=romanized_text, wraplength=400).grid(row=4, column=1, padx=10, pady=10)

# 번역 및 발음 변환 버튼
Button(root, text="번역 및 발음 변환", command=translate_and_display).grid(row=5, column=0, columnspan=2, pady=10)

# 음성 합성 버튼
Button(root, text="음성 합성", command=synthesize_speech).grid(row=6, column=0, columnspan=2, pady=10)

# 발음 파일 저장 버튼
Button(root, text="발음 파일 저장", command=save_pronunciation).grid(row=7, column=0, columnspan=2, pady=10)

# 히스토리 보기 버튼
Button(root, text="히스토리 보기", command=view_history).grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()