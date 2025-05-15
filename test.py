import requests

isim = input("Kitap adı: ")
yazar = input("Yazar: ")
aciklama = input("Açıklama: ")

veri = {
    "isim": isim,
    "yazar": yazar,
    "aciklama": aciklama
}

res = requests.post("http://127.0.0.1:5000/kitap-ekle", json=veri)
print(res.json())