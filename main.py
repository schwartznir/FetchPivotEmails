from readgmail import initiate_download
from convertfolder import generate_table

if __name__ == '__main__':
    print('Starting the process')
    initiate_download()
    print('Done fetching new pdf files from the mailbox')
    generate_table(folder_path='pdf_files/', maxscore=4, pagenum=1, qnum=5)
    print('Done with the results of the surveys of page 1')
    generate_table(folder_path='pdf_files/', maxscore=5, pagenum=2, qnum=22)
    print('Done with the results of the surveys of page 2')
    print('Huge success')
