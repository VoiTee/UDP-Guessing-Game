#Importujemy potrzebne biblioteki.
import socket
import time
import datetime
import random
import sys

#Konfiguracja klienta.
serverAddresPort = ("127.0.0.1",5006) #Konfiguracja adresu i portu klienta.
bufferSize = 4096 #Maksymalna liczba odbieranych bytow.
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
id = "" #Zmienna zawierajaca ID sesji. Z powodu struktury funkcji glownej klienta mozliwe jest nieskomplikowane wykorzystanie zmiennej zamiast tablicy.
close = False #Zmienna informujaca o tym, czy klient ma skonczyc prace.
guessNumber = 0 #Zmienna okreslajaca ilosc prob zgadniec.

#Metoda potwierdzajaca otrzymanie wiadomosci.
def answer(data): #Przyjmuje naglowek otrzymanej wiadomosci.
    data = data.decode() #Wiadomosc przywracana jest do formy string.
    data = data[:-11] #Kasowane zostaje pole danych w Odpowiedz.
    UDPClientSocket.sendto(str.encode(data+"POTWIERDZONO<"), serverAddresPort) #Potwierdzona wiadomosc zostaje odeslana.

#Funkcja wyodrebniajaca pola w otrzymanym naglowku.
def shaveData(data): #Przyjmuje naglowek otrzymanej wiadomosci.
    data = data.decode() #Dziala identycznie jak funkcja o tej samej nazwie w kodzie serwera.
    data = data.replace(" ", "__")
    data = data.replace("><", " brak__danych ")
    data = data.replace(">", " ")
    data = data.replace("<", " ")
    data = data.split()
    return data

#Funkcja otrzymania ID sesji.
def getSession():
    UDPClientSocket.sendto(str.encode("Operacja>OTRZYMAJID<Dane><Identyfikator>"+id+"<Znacznik_Czasu>"+str(datetime.datetime.now())+"<Odpowiedz>OCZEKIWANA<"), serverAddresPort)
    #Do serwera zostaje wyslana prozba przydzielenia ID sesji.
    data,adress = UDPClientSocket.recvfrom(bufferSize)
    print(data.decode())

    data,adress = UDPClientSocket.recvfrom(bufferSize) #Serwer odsyla wiadomosc zawierajaca ID sesji lub rozkaz zakonczenia pracy, gdy jest juz dwoch graczy.
    answer(data)
    print(data.decode())
    dataList = shaveData(data)
    return dataList #Zwrocone zostaja wyodrebnione pola danych naglowka.

#Funkcja otrzymania ilosci prob zgadniecia tajnej liczby.
def guessSetter():

    guesses = 1 #Na potrzeby funkcji wykorzystujemy zmienna ktora inicjowana jest jako 1, aby wejsc w petle while.
    while(guesses % 2 != 0): #Petla zapobiegajaca podania nieparzystej liczby.
        guesses = int(input("Podaj parzysta liczbe ")) #Gracz moze wyznaczyc ile razy chcialby probowac zgadnac tajna liczbe.


    UDPClientSocket.sendto(str.encode("Operacja>ILEPROB<Dane>"+str(guesses)+"<Identyfikator>"+id+"<Znacznik_Czasu>"+str(datetime.datetime.now())+"<Odpowiedz>OCZEKIWANA<"), serverAddresPort)
    #Przez uzytkownika wyznaczona liczba jest wysylana na serwer.
    data, adress = UDPClientSocket.recvfrom(bufferSize)
    print(data.decode())

    data, adress = UDPClientSocket.recvfrom(bufferSize) #Otrzymana zostaje odpowiedz serwera.
    answer(data)
    print(data.decode())
    dataList = shaveData(data)
    if(dataList[1] == "CZEKAJ"): #Jezeli odpowiedz zawierala rozkaz czekania na drugiego gracza, klient czeka na kolejna wiadomosc.
        print(dataList[3])
        data, adress = UDPClientSocket.recvfrom(bufferSize) #W razie czekania otrzymywana jest druga wiadomosc.
        answer(data)
        print(data.decode())
        dataList = shaveData(data)
    return int(dataList[3]) #Do funkcji glownej przekazywana jest liczba prob zgadniecia.

#Funkcja zgadywania tajnej liczby.
def doGuess():

    inp=101 #Na potrzeby funkcji wykorzystujemy zmienna ktora inicjowana jest jako 101, aby wejsc w petle while.

    while inp<0 or inp>100: #Petla while zapobiegajaca wpisaniu nieprawidlowych liczb.
        inp = int(input("Probuj zgadnac (Liczby miedzy 0 - 100): ")) #Uzytkownik wpisuje liczbe o ktorej mysli, ze moze to byc tajna liczba.

    UDPClientSocket.sendto(str.encode("Operacja>ZGADUJE<Dane>" + str(inp) + "<Identyfikator>" + id + "<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), serverAddresPort)
    #Wybrana przez uzytkownika liczba jest przesylana na serwer.
    data, adress = UDPClientSocket.recvfrom(bufferSize)
    print(data.decode())

    data, adress = UDPClientSocket.recvfrom(bufferSize) #Otrzymana zostaje odpowiedz serwera.
    answer(data)
    dataList = shaveData(data)
    print(data.decode())
    return dataList[1] #Do funkcji glownej przekazywana zostaje informacja o tym, czy gracz zgadl, nie zgadl czy drugi gracz zdazyl zgadnac pierwszy.

#Odpowiednik funkcji main.
data = getSession() #Wyslana zostaje prozba o przydzielenie ID sesji.
if(data[3] == "KONCZ"): #Jezeli jest juz dwoch graczy na serwerze, odpowiedza bedzie rozkaz zakonczenia pracy.
    sys.exit() #Praca klienta zostaje zakonczona.
else: #W innym wypadku zapisane i wypisane zostaje otrzymane ID sesji.
    id = data[3]
    print("ID sesji to: " + id)
val = ""

guessNumber = guessSetter() #Wywolywana zostaje funkcja otrzymania ilosci prob zgadniecia i zapisana zostaje odpowiedz serwera.
print("Masz: "+str(guessNumber)+" prob zgadniecia") #Ostateczna ilosc prob zostaje wypisana.

while(guessNumber): #Dopoki nie wyczerpaly sie proby lub jeden z graczy nie zgadnie tajnej liczby mozna probowac ta zgadnac.
    val = doGuess()
    if(val == "ZGADNIETO"):
        break
    elif(val == "KONCZ"):
        break
    guessNumber = guessNumber - 1

if(val == "ZGADNIETO"): #W zaleznosci od wyniku gry zostaje wyswietlony odpowiedni komunikat.
    print("Hurra, udalo Ci sie zgadnac jako pierwszy!!!")
elif(guessNumber == 0):
    print("Skonczyly sie Twoje proby zgadniecia")
else:
    print("Twoj przeciwnik wygral jako pierwszy")

UDPClientSocket.sendto(str.encode("Operacja>KASUJ<Dane><Identyfikator>" + id + "<Znacznik_Czasu>" + str(datetime.datetime.now()) + "<Odpowiedz>OCZEKIWANA<"), serverAddresPort)
#Na serwer zostaje wyslane zadanie usuniecia uzytkownika z listy klientow.
data, adress = UDPClientSocket.recvfrom(bufferSize)
print(data.decode())

input("Wcisnij enter aby zakonczyc") #Uzytkownik moze zakonczyc prace.