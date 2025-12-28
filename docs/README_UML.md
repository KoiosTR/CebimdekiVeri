@startuml
skinparam packageStyle rectangle

class Islem {
  user_id: str
  tutar: float
  aciklama: str
  tarih: datetime
}

class Gelir extends Islem {
  kaynak: str
}

class Gider extends Islem {
  kategori_id: str
}

class Kategori {
  id: str
  ad: str
  aciklama: str
}

class ButceLimiti {
  user_id: str
  kategori_id: str
  limit_tutar: float
}

class Bildirim {
  user_id: str
  mesaj: str
  tarih: datetime
  okundu_mu: bool
}

interface Gozlemci {
  +update(bildirim: Bildirim)
}

class Kullanici implements Gozlemci {
  uid: str
  ad: str
  soyad: str
  email: str
}

class ButceYonetici {
  islemler: List<Islem>
  bakiye: float
  gozlemciler: List<Kullanici>
}

Islem <|-- Gelir
Islem <|-- Gider

Gider --> Kategori : kategori_id
ButceLimiti --> Kategori
ButceLimiti --> Kullanici

ButceYonetici --> Islem
ButceYonetici --> Kullanici : gözlemci

Kullanici --> Bildirim : alır
@enduml
