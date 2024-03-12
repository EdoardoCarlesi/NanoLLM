import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from langdetect import detect


def link_from_title(title, band_name):
    
    link = ''
    album = ''
    band_name = band_name.replace(' ', '').lower()
    #title = title.replace("<h2>", "").replace("</h2>", "")
    #print(title.split("\""))
    title = str(title).split("\"")
    append = False

    if len(title) == 3:
        link = title[1].lower().replace(' ', '').replace('!', '').replace(',', '')
        link = f'http://www.darklyrics.com/lyrics/{band_name}/{link}.html'
        album = title[1]
        append = True
    #print(link, title, len(title))

    return append, album, link


def get_titles(titles):

    titles = str(titles).split('h3')
    print(titles)

    return titles


def song_text(page):

    text = ''

    return text


def scrape_lyrics(band_name, band_url):
 
    band_dir = band_name.replace(' ', '_').lower()

    columns = ['Album', 'Title', 'Lyrics', 'Language']
    all_data = pd.DataFrame() #columns=columns)

    # Get the band's page
    response = requests.get(band_url)
    album_links = []
    titles = []

    all_albums, all_titles, all_lyrics, all_languages = [], [], [], []

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        album_titles = soup.find_all('h2')

        for title in album_titles:
            append, title_clean, link = link_from_title(title, band_name)
            
            if append:
                album_links.append(link)
                titles.append(title_clean)

        for link, album_name in zip(album_links, titles):
            album_url = link
            print(f"Scraping album: {album_name}")

            # Get the album's page
            album_response = requests.get(album_url)
            if album_response.status_code == 200:
                album_soup = BeautifulSoup(album_response.content, 'html.parser')
                song_names = album_soup.find_all('h3') 
                all_texts = album_soup.find_all('div', class_='lyrics')
                titles = []
                
                for song_name in song_names:
                    title = song_name.text.strip()
                    titles.append(title)
                
                rest_texts = str(all_texts)

                for title in titles[::-1]:
                    
                    try:
                        [rest_texts, text] = rest_texts.split(title)
                    except:
                        rest_texts, text = '', ''
                    
                    text = BeautifulSoup(text, 'html.parser').get_text()
                    
                    if "Thanks to" in text:
                        text = text.split("Thanks to")[0]

                    try:
                        language = detect(text)
                    except:
                        language = 'unknown'

                    all_albums.append(album_name)
                    all_titles.append(title)
                    all_lyrics.append(text)
                    all_languages.append(language)
                    #print(text)
                    #print('-----------------------')
            
    all_data['Album'] = all_albums
    all_data['Title'] = all_titles
    all_data['Lyrics'] = all_lyrics
    all_data['Language'] = all_languages

    all_data.to_csv(f'{band_dir}_lyrics.csv')

if __name__ == "__main__":
    #band_name = input("Enter the band name: ")
    band_name = "nanowar"# of steel" #input("Enter the band name: ")
    band_url = f"http://www.darklyrics.com/{band_name[0].lower()}/{band_name.replace(' ', '').lower()}.html"

    scrape_lyrics(band_name, band_url)

