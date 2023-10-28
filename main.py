from readgmail import initiate_download
from convertfolder import generate_table
import pandas as pd

if __name__ == '__main__':
    print('Starting the process')
    initiate_download()
    print('Done fetching new pdf files from the mailbox')
    first_page = generate_table(folder_path='pdf_files/', maxscore=4, pagenum=1, qnum=5)
    print('Done with the results of the surveys of page 1')
    second_page = generate_table(folder_path='pdf_files/', maxscore=5, pagenum=2, qnum=22)
    print('Done with the results of the surveys of page 2')
    merged_df = pd.merge(first_page, second_page, on=['id', 'date'], how='outer')
    merged_df.to_excel(f'New responses from pages 1-2.xlsx')
    print('Huge success')
