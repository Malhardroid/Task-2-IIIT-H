import requests
from bs4 import BeautifulSoup
import pysrt
import difflib



def scrape_transcript(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    transcript_text = [p.get_text() for p in soup.find_all('p')]

    return transcript_text



def parse_srt(file):
    subs = pysrt.open(file)
    asr_output = []
    for sub in subs:
        asr_output.append({
            'start': sub.start.to_time(),
            'end': sub.end.to_time(),
            'text': sub.text.strip()
        })
    return asr_output, subs



def replace_asr_text_with_transcript(transcript, asr_output, subs):
    transcript_words = [word for line in transcript for word in line.split()]
    transcript_idx = 0
    last_sub_idx = 0

    for i, asr in enumerate(asr_output):
        asr_text = asr['text'].lower()
        asr_words = asr_text.split()
        new_text = []
        
        for asr_word in asr_words:
            if transcript_idx < len(transcript_words) and transcript_words[transcript_idx] == asr_word:
                new_text.append(asr_word)
            else:
                if transcript_idx < len(transcript_words):
                    new_text.append(transcript_words[transcript_idx])
                    transcript_idx += 1
                else:
                    new_text.append(asr_word)

        updated_text = ' '.join(new_text)
        subs[i].text = updated_text

        while transcript_idx < len(transcript_words):
            if i > 0:  
                subs[last_sub_idx].text += ' ' + transcript_words[transcript_idx]
            transcript_idx += 1

        last_sub_idx = i  

        print(f"Original ASR text: '{asr_text}'")
        print(f"Updated Subtitle text: '{updated_text}'")
        print("-----")

    return subs



def save_srt_file(subs, output_file):
    subs.save(output_file, encoding='utf-8')



  url = 'https://pib.gov.in/PressReleasePage.aspx?PRID=2045561'
  transcript = scrape_transcript(url)
  asr_output, subs = parse_srt('/content/modi_independence_iitm.srt')

  updated_subs = replace_asr_text_with_transcript(transcript, asr_output, subs)
  save_srt_file(updated_subs, 'updated_asr_output.srt')
