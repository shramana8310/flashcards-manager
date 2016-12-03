from tkinter import Tk, messagebox, simpledialog, filedialog
import os
import sys
import re
import urllib.request
import urllib.parse
import urllib.error
import json
import csv
import time
import traceback

def request_glosbe_translate(phrase, lan_from, lan_dest, include_examples=True):
    query = {
        'from' : lan_from,
        'dest' : lan_dest,
        'phrase' : phrase,
        'tm' : 'true' if include_examples else 'false',
        'format' : 'json'
    }
    glosbe_url = 'https://glosbe.com/gapi/'
    glosbe_function = 'translate'
    query_string = urllib.parse.urlencode(query)
    url = glosbe_url + glosbe_function + '?' + query_string
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    if len(data['tuc']) > 0:
        return data
    else:
        return None

def list_from_data(original_phrase, data):
    lst = []
    try:
        separator = '<br />'
        phrase = data['phrase']
        lst.append(phrase)
        meanings = []
        for idx, item in enumerate(data['tuc']):
            if idx == 10:
                break
            try:
                meanings.append(item['phrase']['text'])
            except (TypeError, IndexError, KeyError):
                continue
        lst.append(separator.join(meanings))
        examples = []
        for idx, item in enumerate(data['examples']):
            if idx == 3:
                break
            try:
                examples.append((item['first'], item['second']))
            except (TypeError, IndexError, KeyError):
                continue
        examples_in_lan_from = [first for first, second in examples]
        examples_in_lan_dest = [second for first, second in examples]
        lst.append((separator + separator).join(examples_in_lan_from))
        lst.append((separator + separator).join(examples_in_lan_dest))
        return lst
    except (TypeError, IndexError, KeyError):
        return lst

def do_work(lan_from, lan_dest, phrases, out_filename):
    result = {'success' : 0, 'failure' : 0, 'started_at' : time.time()}
    with open(out_filename, 'w', encoding='utf-8', newline='\n') as fo:
        writer = csv.writer(fo, delimiter='\t')
        writer.writerow(['Text 1', 'Text 2', 'Text 3', 'Text 4'])
        for phrase in phrases:
            data = request_glosbe_translate(phrase, lan_from, lan_dest)
            lst = list_from_data(phrase, data)
            if len(lst) >= 2 and len(lst[1]) > 0:
                result['success'] += 1
            else:
                result['failure'] += 1
            writer.writerow(lst)
    result['finished_at'] = time.time()
    result['elapsed_time'] = result['finished_at'] - result['started_at']
    return result

def read_phrases(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        alist = [line.rstrip() for line in f if len(line.rstrip()) > 0]
    return alist

def lan_code_input_routine():
    def aux_input_routine(title, message):
        while True:
            lan_code = simpledialog.askstring(title, message)
            try:
                if not re.match(r'^[a-z]{3}$', lan_code):
                    messagebox.showerror('잘못된 언어 코드', '잘못된 언어 코드입니다. 언어 코드는 다음 주소를 참고하세요.\nhttp://www-01.sil.org/iso639-3/codes.asp')
                else:
                    return lan_code
            except:
                pass
    lan_from = aux_input_routine('언어 코드 입력', '검색 대상 언어 코드 (ISO 639-3) 세자리를 입력하십시오.\n'
        '예: 영단어의 경우 "eng"를 입력')
    lan_dest = aux_input_routine('뜻풀이 언어 코드 입력', '뜻풀이 언어 코드 (ISO 639-3) 세자리를 입력하십시오.\n'
        '예: 우리말 뜻풀이의 경우 "kor"을 입력')
    return (lan_from, lan_dest)

def main():
    Tk().withdraw()
    try:
        lan_from, lan_dest = lan_code_input_routine()
        messagebox.showinfo('입력 파일 선택', '단어 목록 텍스트 파일을 선택하십시오.')
        in_filename = filedialog.askopenfilename()
        phrases = read_phrases(in_filename)
        messagebox.showinfo('단어장 파일 선택', '검색 결과가 저장될 파일을 선택하십시오.')
        out_filename = filedialog.asksaveasfilename(filetypes=[('Text files', '*.txt')], 
            initialfile='flashcards.txt')
        if len(phrases) > 50:
            messagebox.showinfo('알림', '인터넷에서 자료를 가져오기 때문에 단어가 많으면 시간이 제법 걸립니다.\n(접속이 원활한 경우 50개당 1분 정도 소요)')
        result = do_work(lan_from, lan_dest, phrases, out_filename)
        messagebox.showinfo('결과', '성공: {success}\n실패: {failure}\n소요시간: {elapsed_time:.2f}초\n\n프로그램을 종료합니다.'.format(**result))
    except urllib.error.HTTPError as err:
        if err.getcode() == 429:
            messagebox.showerror(type(err), '지나친 서버 요청으로 접근이 차단되었습니다. 나중에 다시 시도해보세요.')
            sys.exit(1)
    except Exception as err:
        messagebox.showerror(type(err), traceback.format_exc())
        sys.exit(1)

main()