#import functions
from PyPDF2 import PdfReader

# creating a pdf reader object
reader = PdfReader('home/s4bin86/dev/proyectos/BD_Medicamentos_aprobados/dataset/Prospectos/1.3.1_pil_at_LevodopaCarbidopaEntacapon ratiopharm 100 mg25 mg200 mg Filmta_UA_cl.pdf')

# printing number of pages in pdf file
print(len(reader.pages))

# getting a specific page from the pdf file
page = reader.pages[0]

# extracting text from page
text = page.extract_text()
print(text)