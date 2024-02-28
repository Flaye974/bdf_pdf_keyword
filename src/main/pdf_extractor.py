import datetime
import os
import csv
import time
import re
from PyPDF2 import PdfReader

DIR_RESSOURCE = "./ressources/"
KEYWORD_LIST = ["Newton", "loi"]
NB_LINES = 3


def read_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    return reader


def get_text_from_all_pages(reader: PdfReader) -> str:
    text = ""
    for p in reader.pages:
        text += "" + p.extract_text()
    return text


def rename(name: str) -> str:
    return re.sub(" ", "_", name)
    # return re.sub(" ", "_", re.sub("[éèê]", "e", re.sub("à", "a", re.sub(r"[^\w\s]", "", name.lower()))))


def get_dict_from_all_pdf(files: list[str], directory: str) -> dict:
    dict_pdf_text = dict()
    for f in files:
        dict_pdf_text[rename(f)] = get_text_from_all_pages(read_pdf(directory + f))
    return dict_pdf_text


def get_list_of_paragraph_with_keywords(paragraphs: list[str], keyword: str) -> list[str]:
    result = []
    for paragraph in paragraphs:
        if paragraph.lower().__contains__(keyword.lower()):
            index_para = paragraphs.index(paragraph)
            context = get_context_from_keyword(keyword, paragraphs, index_para)
            result.append(context)
    return result


def get_dict_of_text_with_keyword(dict_pdf: dict) -> dict:
    dict_keyword_paragraphs = {}
    for title, text in dict_pdf.items():
        for keyword in KEYWORD_LIST:
            if not title in dict_keyword_paragraphs.keys():
                dict_keyword_paragraphs[title] = {}
            dict_keyword_paragraphs[title][keyword] = get_list_of_paragraph_with_keywords(text.split("\n"), keyword)
    return dict_keyword_paragraphs


def get_context_from_keyword(keyword, paragraphs, index_para):
    debut = max(0, index_para - NB_LINES + 1)
    fin = min(len(paragraphs), index_para + NB_LINES)
    return "\n".join(paragraphs[debut:fin])


def export_to_csv(dict_para_keyword: dict):
    date_time = datetime.datetime.fromtimestamp(time.time())
    with open(
            f"./result/result_{date_time.year}_{date_time.month}_{date_time.day}_{date_time.hour}{date_time.minute}.csv",
            "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        for title, child_keyword in dict_para_keyword.items():
            for keyword, values in child_keyword.items():
                for value in values:
                    writer.writerow([title, keyword, re.sub(r"[\n\t]", "", value.strip())])


if __name__ == '__main__':
    print("==== Début de l'execution du programme ====")
    print("==== Récupération de la liste des PDF ====")
    files = [f for f in os.listdir(DIR_RESSOURCE) if f.endswith('.pdf')]
    print("Liste de fichiers : ")
    for f in files:
        print(f"\t- {f}")
    print("==== Récupération du texte des PDF ====")
    dict_pdf_text = get_dict_from_all_pdf(files, DIR_RESSOURCE)
    print(".........Récupération terminé")
    print("==== Analyse des textes ====")
    dict_para_keyword = get_dict_of_text_with_keyword(dict_pdf_text)
    print("==== Export to csv ====")
    export_to_csv(dict_para_keyword)
