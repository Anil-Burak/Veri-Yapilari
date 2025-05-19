from flask import Flask, request, jsonify, render_template
import boto3
import uuid
import os
import dotenv

dotenv.load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb',aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='eu-north-1')

kitaplar_tablosu = dynamodb.Table('kitaplar')


# Dümenden bir html ile denemek için
@app.route('/')
def ana_sayfa():
    return render_template('index.html')

@app.route('/kitap-ekle', methods=['POST'])
def kitap_ekle():
    veri = request.get_json()
    kitap_id = str(uuid.uuid4())
    veri['kitap_id'] = kitap_id

    mevcut_kitaplar = kitaplar_tablosu.scan().get('Items', [])
    veri['sira'] = len(mevcut_kitaplar) + 1

    veri.setdefault('sube', 'Genel')  # Şube girilmezse genel
    veri.setdefault('durum', 'mevcut')  # 'mevcut' ya da 'mevcut degil'

    kitaplar_tablosu.put_item(Item=veri)
    return jsonify({'durum': 'eklendi', 'kitap_id': kitap_id})

# Sonraki ve önceki butonunu gerekli yerlerde deaktif etmek için
@app.route('/kitap-sayisi', methods=['GET'])
def kitap_sayisi():
    response = kitaplar_tablosu.scan(Select='COUNT')
    return jsonify({'toplam': response.get('Count', 0)})

@app.route('/kitaplar', methods=['GET'])
def kitaplari_getir():
    response = kitaplar_tablosu.scan()
    kitaplar = response.get('Items', [])
    kitaplar.sort(key=lambda x: int(x.get('sira', 0)))
    return jsonify(kitaplar)

@app.route('/kitap/<int:sira>', methods=['GET'])
def kitabi_getir(sira):
    response = kitaplar_tablosu.scan()
    kitaplar = response.get('Items', [])
    kitaplar_dict = {int(k['sira']): k for k in kitaplar}

    kitap = kitaplar_dict.get(sira)
    if not kitap:
        return jsonify({'hata': 'Kitap bulunamadı'}), 404

    onceki = kitaplar_dict.get(sira - 1)
    sonraki = kitaplar_dict.get(sira + 1)

    return jsonify({
        'kitap': kitap,
        'onceki': onceki['isim'] if onceki else "Yok",
        'sonraki': sonraki['isim'] if sonraki else "Yok"
    })

if __name__ == '__main__':
    app.run(debug=True)