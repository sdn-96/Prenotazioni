import requests
from bs4 import BeautifulSoup
from config import URL_LOGIN, URL_RESERVATIONS
from config import USERNAME, PASSWORD

START_DATE = '01/01/2024'
END_DATE = '31/12/2026'


def login():
    # Inizializza sessione
    session = requests.Session()

    # Step 1: Ottieni token hidden dinamico
    login_page = session.get(URL_LOGIN)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    hidden_input = soup.find('input', {'type': 'hidden'})
    hidden_name = hidden_input['name']
    hidden_value = hidden_input['value']

    # Step 2: Dati login
    login_data = {
        'property_id': 'quokka360it',
        'username': USERNAME,
        'password': PASSWORD,
        hidden_name: hidden_value
    }

    # Step 3: Effettua login
    response = session.post(URL_LOGIN, data=login_data)

    # Verifica login
    if "logout" not in response.text.lower():
        print("Errore nel login")
        exit()

    print("Login riuscito!")
    return session

def request_data(session):
    # Step 4: Richiesta pagina prenotazioni
    params = {
        'from': START_DATE,
        'to': END_DATE
    }
    res = session.get(URL_RESERVATIONS, params=params)

    if res.status_code != 200:
        print("Errore nel caricamento delle prenotazioni")
        exit()
    return res

def analize(res):
    # Step 5: Parsing HTML
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find('table')  # Puoi specificare class_ se necessario

    if not table:
        print("Tabella non trovata")
        exit()

    # Step 6: Estrai intestazione e righe
    header_row = table.find('tr')
    headers = [th.text.strip() for th in header_row.find_all('th')]
    data_rows = []

    for row in table.find_all('tr')[1:]:  # salta header
        cols = row.find_all('td')
        if cols:
            data_rows.append([td.text.encode('ascii', 'ignore').decode().strip() for td in cols])
    return headers, data_rows
