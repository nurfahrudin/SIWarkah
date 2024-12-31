from django.db import models
from django.db import connection
import datetime


class User(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    departemen = models.CharField(max_length=100)
    bidang = models.CharField(max_length=50)
    create_date = models.DateTimeField(default=datetime.datetime.today, null=False)
    update_date = models.DateTimeField(null=True)


class Kecamatan(models.Model):
    kode = models.CharField(max_length=3, unique=True)
    nama = models.CharField(max_length=50)
    
    def id_bykode(kode):
        kec = Kecamatan.objects.get(kode=kode)
        return kec.id

    def __str__(self):
        return self.nama


class Kelurahan(models.Model):
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE)
    kode = models.CharField(max_length=6, unique=True)
    nama = models.CharField(max_length=50)
    
    def id_bykode(kode):
        kel = Kelurahan.objects.get(kode=kode)
        return kel.id

    def __str__(self):
        return self.nama


def upload_dest(instance, filename):
    path = '/'.join([instance.kecamatan.nama, instance.kelurahan.nama, instance.tahun, filename])
    return path.replace(' ', '_')

class Warkah(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE)
    kelurahan = models.ForeignKey(Kelurahan, on_delete=models.CASCADE)
    nama_subjek = models.CharField(max_length=128)
    no_berkas = models.CharField(max_length=4)
    tahun = models.IntegerField(null=False)
    document = models.FileField(upload_to=upload_dest, max_length=500)
    create_date = models.DateTimeField(default=datetime.datetime.today, null=False)

    def get_warkah_byid(id):
        warkah = Warkah.objects.get(pk=id)
        return warkah

    def __str__(self):
        return self.nama_subjek


# --------------------------
# TOOLS MODELS
# --------------------------
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]