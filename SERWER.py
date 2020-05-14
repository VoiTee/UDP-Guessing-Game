#Importujemy potrzebne biblioteki.
import socket
import random
import time
import secrets
import datetime

#Konfiguracja serwera.
localIP = "127.0.0.1" #Adres IPv4 serwera.
localPort = 5006 #Port serwera.
bufferSize = 4096 #Maksymalna liczba odczytywanych bytow.
UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Konfiguracja gniazda UDP.
UDPSocket.bind((localIP,localPort))
ClientList = [] #Tablica przechowujaca dane klientow.
GuessList = [] #Tablica wykorzystywana do wyznaczenia liczby prob zgadniecia tajnej liczby.
GameEnd = [] #Tablica sluzaca to powiadomienia, ze ktorys z graczy zgadl liczbe.
             # Nie jest to zmienna, poniewaz operacje na zmiennych w jezyku Python sa trudniejsze do przeprowadzenia wewnatrz funkcji.
secretNumber = random.randrange(100) #Generowana losowa tajna liczba.

#Klient
class Client:
    address = "" #Adres zapamietanego klienta.
    id = "" #ID sesji zapamietanego klienta.

    def __init__(self,address): #Konstruktor objektu klasy Client. Przyjmuje jako wartosc adres z ktorego niezapamietany klient wyslal wiadomosc.
        self.address = address
        if(address != "0.0.0.0"): #Jezeli adres nie jest rowny 0.0.0.0 to przyznawane jest wygenerowane, unikatowe ID sesji o dlugosci osmiu bytow.
            self.id = secrets.token_urlsafe(8)
        else:
            self.id = "" #Jezeli adres jest rowny 0.0.0.0 to ID sesji pozostaje puste.

#Metoda potwierdzania otrzymania wiadomosci.
def answer(data,address): #Metoda przyjmuje naglowek wiadomosci oraz adres z ktorego ta zostala nadana.
    data = data.decode() #Naglowek zostaje przywrocony do formy string.
    data = data[:-11] #Usuwane sa dane z pola Odpowiedz.
    UDPSocket.sendto(str.encode(data+"POTWIERDZONO<"), address) #Potwierdzona wiadomosc zostaje odeslana.


#Metoda dodawania klientow
def AddClient(address): #Przyjmuje adres z ktorego wyslano zapytanie
    if(len(ClientList) >= 2): #Jezeli jest juz dwoch klientow, serwer nie przyjmuje nastepnych.
        UDPSocket.sendto(str.encode("Operacja>KONCZ<Dane>KONCZ<Identyfikator><Znacznik_Czasu>"+str(datetime.datetime.now())+"<Odpowiedz>OCZEKIWANA<"),address)
    else: #W przeciwnym razie nowy klient jest zapisywany w tablicy ClientList i przydzielane zostaje mu ID sesji.
        newClient = Client(address)
        ClientList.append(newClient)
        UDPSocket.sendto(str.encode("Operacja>NADAJID<Dane>"+newClient.id+"<Identyfikator>"+newClient.id+"<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"),address)

#Funkcja przeszukujaca tablice klientow.
def find(filter): #Przyjmuje kryterium wyszukiwania.
    for x in ClientList:
        if filter(x):
            return x
    return Client("0.0.0.0") #Jezeli nie znajdzie klienta zwraca wygenerowanego, pustego klienta.

#Metoda przyznajaca ilosc prob zgadniec
def setGuess(number,id): #Przyjmuje wyznaczona przez gracza liczbe oraz jego ID sesji.
    GuessList.append(number) #Liczba podana przez klienta dodawana jest do tablicy GuessList.
    if(len(GuessList) == 1): #Jezeli po dodaniu liczby do tablicy GuessList tablica zawiera jedna wartosc klient musi poczekac na drugiego gracza.
        client = find(lambda x: x.id == id) #Na podstawie ID sesji, znajdywany jest odpowiedni klient do ktorego wyslany zostanie rozkaz czekania.
        UDPSocket.sendto(str.encode("Operacja>CZEKAJ<Dane>OCZEKIWANIE<Identyfikator>"+str(client.id)+"<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), client.address)
        data, address = UDPSocket.recvfrom(bufferSize)
        print(data.decode())
    elif(len(GuessList) == 2): #Jezeli tablica GuessList zawiera dwa wpisy obliczana zostaje ilosc prob dla obu graczy.
        final = int((int(GuessList[0]) + int(GuessList[1]))/2) #Liczba prob wynosi polowe sumy obu liczb podanych przez graczy.
        GuessList.append(final)
        for x in ClientList: #Koncowa ilosc prob wysylana jest do obu graczy.
            UDPSocket.sendto(str.encode("Operacja>NADAJPROBY<Dane>"+str(final)+"<Identyfikator>" + str(x.id) + "<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), x.address)
            data, address = UDPSocket.recvfrom(bufferSize)
            print(data.decode())

#Metoda sprawdzajaca czy gracze odgadli tajna liczbe.
def play(number,id): #Przyjmuje liczbe podana przez gracza oraz jego ID sesji.
    client = find(lambda x: x.id == id) #Na podstawie ID sesji odnajdywany jest odpowiedni gracz z listy.
    if(len(GameEnd) == 0): #Jezeli gra sie jeszcze nie skonczyla serwer sprawdza, czy podana przez gracza liczba jest rowna tajnej liczbie.
        if(int(number) == secretNumber): #Jezeli liczby sa identyczne gracz wygrywa i zostaje o tym powiadomiony.
            GameEnd.append(True) #W tablice GameEnd jest wpisywana wartosc true, aby zasygnalizowac, ze jeden z graczy skonczyl gre.
            UDPSocket.sendto(str.encode("Operacja>ZGADNIETO<Dane>POWODZENIE<Identyfikator>" + str(client.id) + "<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), client.address)
            data, address = UDPSocket.recvfrom(bufferSize)
            print(data.decode())
        else: #Jezeli liczba podana przez gracza nie jest identyczna z liczba.
            UDPSocket.sendto(str.encode("Operacja>NIEZGADNIETO<Dane>NIEPOWODZENIE<Identyfikator>" + str(client.id) + "<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), client.address)
            data, address = UDPSocket.recvfrom(bufferSize)
            print(data.decode())
    else: #Jezeli zostal zasygnalizowany koniec gry drugi gracz otrzyma rozkaz skonczenia gry.
        UDPSocket.sendto(str.encode("Operacja>KONCZ<Dane>KONCZ<Identyfikator>" + str(client.id) + "<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), client.address)
        data, address = UDPSocket.recvfrom(bufferSize)
        print(data.decode())

#Kasowanie klientow.
def delete():
    if(len(GuessList) > 0): #Jezeli wyloguje sie jeden z graczy kasowana jest tablica GuessList. Sygnalizuje to, ze jeden z graczy sie wylogowal, a tablicz nie jest juz potrzebna.
        GuessList.clear()
    else: #Jezeli tablica GuessList jest juz pusta, a wyloguje sie gracz wszystkie pozostale tablice serwera zostaja wyczyszczone i wraca on do ustawien przed rozpoczeciem gry.
        ClientList.clear()
        GameEnd.clear()


#Metoda ustalajaca jak nalezy postapic z otrzymana wiadomoscia na podstawie danych w polu Operacja.
def recive():
    data, address = UDPSocket.recvfrom(bufferSize)
    dataList = shaveData(data) #Wywolywana jest funkcja wyodrebniajaca dane zawarte w naglowku.
    print(data.decode()) #Kazda otrzymana wiadomosc jest wypisywana.

    if(dataList[1] == "ZGADUJE"): #W zaleznosci od danych w polu Operacja otrzymanej wiadomosci wywolywana jest odpowiednia metoda.
        answer(data, address)
        play(dataList[3],dataList[5])
    elif(dataList[1] == "OTRZYMAJID"):
        answer(data, address)
        AddClient(address)
    elif(dataList[1] == "ILEPROB"):
        answer(data, address)
        setGuess(dataList[3],dataList[5])
    elif(dataList[1] == "KASUJ"):
        answer(data, address)
        delete()

#Metoda wyodrebniajaca pola naglowka.
def shaveData(data): #Przyjmuje tresc wiadomosci.
    data = data.decode()
    data = data.replace(" ", "__") #Wszystkie spacje musza zostac zamienione w podwojny podkreslnik, aby dwiadomosc zostala podzielona w odpowiednim miejscu.
    data = data.replace("><", " no_data ") #Wiadomosc jest dzielona przy kazdej spacji, dla tego trzeba odpowiednio przetransformowac dane naglowka.
    data = data.replace(">", " ")
    data = data.replace("<", " ")
    data = data.split()
    return data

#Odpowiednik funkcji main
print("The secret Number is: "+str(secretNumber)) #Wypisana zostaje tajna liczba, widoczna tylko dla serwera.

while True: #Na czas trwania programu wykonywana jest zapetlona metoda odbierajaca wiadomosci.
    recive()
