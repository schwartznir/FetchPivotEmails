import pdfplumber
import pandas as pd

# PDF extraction and data transformation
# pdf_path = "signed (1).pdf"


def extract_data_from_pdf(pdf_path, page_num, maxscore=5):
    data = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num - 1]  # Adjust page index since it's 0-based
        table = page.extract_table()
        if table:
            for row_index, row in enumerate(table):
                for col_index, cell in enumerate(row):
                    if cell and 'X' in cell:
                        data.append((row_index, abs(maxscore - col_index)))

    return pd.DataFrame(data, columns=['Question number', 'Column Marked with X'])


import os


def generate_table(folder_path, maxscore=5, pagenum=1, qnum=22):
    result = pd.DataFrame(columns=[f'Response to Question number {i}' for i in range(-1, qnum + 1)])
    result = result.rename(columns={'Response to Question number -1': 'id'})
    result = result.rename(columns={'Response to Question number 0': 'date'})
    idx = 0
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            df_page = extract_data_from_pdf(pdf_path, page_num=pagenum, maxscore=maxscore)
            result.at[idx, 'id'], result.at[idx, 'date'] = filename.split('.')[0].split('Q')
            for jdx, row in df_page.iterrows():
                col_name = f'Response to Question number {row["Question number"]}'
                result.at[idx, col_name] = row['Column Marked with X']
            file_path = os.path.join(folder_path, filename)
            print(f'Treated {filename}. Deleting it from disk.')
            os.remove(file_path)
            idx += 1
    result.to_excel(f'New responses from page {pagenum}.xlsx')
    return result
