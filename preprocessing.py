import re
import requests
from bs4 import BeautifulSoup
from pymystem3 import Mystem


def main(file_name):
    file = open(file_name, 'w', encoding='utf8')
    file.write(get_text())
    file.close()


def get_text():
    result_paragraphs = []
    words_counter = 0

    url_template = 'http://book-online.com.ua/read.php?book=111&page={}' #last_page_num = 115
    page_number = 1
    while page_number < 115 and words_counter < 5000:
        try:
            # get page
            request = requests.get(url_template.format(str(page_number)))
            if request.status_code != 200:
                print('Loop stopped at page', str(page_number), 'with request code', str(request.status_code))
                break

            # find text
            soup = BeautifulSoup(request.text, 'html.parser')
            text = soup.find('div', id='ptext')
            for unwanted_tag in text.find_all(re.compile('(em|h3)')):
                unwanted_tag.clear()
            for epigraph in text.find_all('div', class_='epigraph'):
                epigraph.clear()

            # lemmatise it and add to the overall text
            for paragraph in text.find_all('p'):
                lemmatization = clean_and_lemmatize(paragraph.text)
                if lemmatization['text']:
                    result_paragraphs.append(lemmatization['text'])
                words_counter += lemmatization['word_counter']

            page_number += 1
        except Exception as err:
            print('Error at page', page_number, ': ', err)
            break
    print('Looked through', page_number - 1, 'http pages')
    print('Collected', words_counter, 'words')

    whole_book = '\n'.join(result_paragraphs)
    return whole_book


def clean_and_lemmatize(text):
    result_strings = []
    word_counter = 0
    m = Mystem()
    sentences = re.split('[.!?]', text)
    for sentence in sentences:
        lemmas = m.lemmatize(sentence)
        lemmas = tuple(filter(lambda lemma: re.search('\w', lemma), lemmas))
        word_counter += len(lemmas)
        string = ' '.join(lemmas)
        if string:
            result_strings.append(string)
    result = '\n'.join(result_strings)
    return {'text': result, 'word_counter': word_counter}
