import os
import json
import shutil
import datetime
from django.db import connection
from django.conf import settings
from django.core import serializers
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password

from .models import Warkah, Kecamatan, Kelurahan, dictfetchall



def error_404(request, exception):
    return render(request, 'warkah/404.html', status=404)
def error_500(request):
    return render(request, 'warkah/404.html', status=500)


def say(request):
    hour_now = datetime.datetime.now().strftime('%H')
    time_now = int(hour_now)
    if (time_now >= 12) and (time_now < 15):
        request.session['say'] = 'siang'
        return 'siang'
    elif (time_now >= 15) and (time_now < 19):
        request.session['say'] = 'sore'
        return 'sore'
    elif (time_now >= 19) and (time_now < 24):
        request.session['say'] = 'malam'
        return 'malam'
    else:
        request.session['say'] = 'pagi'
        return 'pagi'


def items():
    kec = Kecamatan.objects.all()
    kel = Kelurahan.objects.all()
    tgl = HARI()+' - '+PASARAN()+', '+str(datetime.date.today().day)+' '\
            +BULAN[datetime.date.today().month-1]+' '+str(datetime.date.today().year)
    items = {'items_kec': kec, 'items_kel': kel, 'tgl': tgl, 'tahun': datetime.date.today().year}
    return items


BULAN = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
def HARI():
    day = datetime.date.today().strftime('%a')
    if day == 'Sun':
        return 'Minggu'
    elif day == 'Mon':
        return 'Senin'
    elif day == 'Tue':
        return 'Selasa'
    elif day == 'Wed':
        return 'Rabu'
    elif day == 'Thu':
        return 'Kamis'
    elif day == 'Fri':
        return 'Jumat'
    elif day == 'Sat':
        return 'Sabtu'

def PASARAN():
    PASAR = ['Pon', 'Wage', 'Kliwon', 'Legi','Pahing']
    day     = datetime.date.today().day
    month   = datetime.date.today().month
    year    = datetime.date.today().year

    d1  = datetime.date(2019, 7, 7) # Pon
    d2  = datetime.date(year, month, day)

    delta   = d2 - d1
    mod     = delta.days % 5
    return PASAR[mod]



# ----------------------------
# function ajax chart
# ----------------------------
def ajax_chart(request):
    label = Kecamatan.objects.values_list('nama', flat=True).order_by('nama')
    cursor = connection.cursor()
    cursor.execute('select count(w.kecamatan_id) from warkah_kecamatan kec left outer join warkah_warkah w on w.kecamatan_id == kec.id \
                    group by kec.nama order by kec.nama')
    data = cursor.fetchall()

    print ('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print ((data))
    print (say(request))
    print (request.session.get_expiry_age())
    print (PASARAN())
    base_url = settings.BASE_DIR+'\\media\\'
    print (base_url, type(base_url))
    print ('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    result = json.dumps({"label": list(label), "data": list(data)})
    return HttpResponse(result, content_type="application/json")


# ----------------------------
# function home (index)
# ----------------------------
def index(request):
    return render(request, 'warkah/index.html', items())


# ----------------------------
# function ajax combobox
# ----------------------------
def ajax_combo(request, params):
    params = params or '001'
    id_kec = Kecamatan.id_bykode(params)
    kel = Kelurahan.objects.all().filter(kecamatan_id=id_kec).order_by('nama')
    data = serializers.serialize("json", kel)
    return HttpResponse(data, content_type="application/javascript")

def ajax_combo_edit(request, params_id, params):
    id_kec = Kecamatan.id_bykode(params)
    kel = Kelurahan.objects.all().filter(kecamatan_id=id_kec).order_by('nama')
    data = serializers.serialize("json", kel)
    return HttpResponse(data, content_type="application/javascript")


# ----------------------------
# function ajax datatable
# ----------------------------
def ajax_table(request):
    get     = request.GET.get
    kd_kec  = get('kec_') or ''
    kd_kel  = get('kel_') or ''
    tahun   = get('tahun_') or ''
    nomor   = get('no_berkas_') or ''
    nama    = get('nm_subjek_') or ''

    query   = "select w.id, k.nama as kecamatan, l.nama as kelurahan, w.tahun, w.no_berkas, w.nama_subjek, w.document from warkah_warkah w \
                join warkah_kelurahan l on w.kelurahan_id == l.id \
                join warkah_kecamatan k on l.kecamatan_id == k.id "
    f = 0

    if kd_kec != '':
        f +=1
        if f > 0:
            query += " and k.kode = "+"'"+kd_kec+"'"
        else:
            query += " where k.kode = "+"'"+kd_kec+"'"
        print ('***********************************************')
        print (query)
        print (get('kd_kec_'))
    if kd_kel != '':
        f +=1
        if f > 0:
            query += " and l.kode = "+"'"+kd_kel+"'"
        else:
            query += " where l.kode = "+"'"+kd_kel+"'"
        print ('***********************************************')
        print (query)
    if tahun != '':
        f +=1
        if f > 0:
            query += " and w.tahun like "+"'%"+tahun+"%'"
        else:
            query += " where w.tahun like "+"'%"+tahun+"%'"
        print ('***********************************************')
        print (query)
    if nomor != '':
        f +=1
        if f > 0:
            query += " and w.no_berkas like "+"'%"+nomor+"%'"
        else:
            query += " where w.no_berkas like "+"'%"+nomor+"%'"
        print ('***********************************************')
        print (query)
    if nama != '':
        f +=1
        if f > 0:
            query += " and w.nama_subjek like "+"'%"+nama+"%'"
        else:
            query += " where w.nama_subjek like "+"'%"+nama+"%'"
        print ('***********************************************')
        print (query)
    
    cursor = connection.cursor()
    cursor.execute(query)
    warkah = dictfetchall(cursor)
    # cursor.close()
    result = json.dumps({"data": list(warkah)})
    print ('=======================================================')
    print (result)

    return HttpResponse(result, content_type="application/json")



# ----------------------------
# function CRUD warkah start
# ----------------------------
def input(request):
    if request.method == 'POST' and request.FILES['file_berkas']:
        form = request.POST
        kecamatan   = Kecamatan.objects.get(kode=form['kecamatan'])
        kelurahan   = Kelurahan.objects.get(kode=form['kelurahan'])
        no_berkas   = form['no_berkas']
        nm_subjek   = form['nm_subjek']
        tahun       = form['tahun']
        file        = request.FILES['file_berkas']

        data = Warkah(user_id=request.session['uid'], kecamatan_id=kecamatan.id, kelurahan_id=kelurahan.id,\
                        nama_subjek=nm_subjek, no_berkas=no_berkas, document=file, tahun=tahun)
        data.save()
        messages.success(request, 'Data warkah atas nama '+nm_subjek+' berhasil disimpan.')
        return redirect('/warkah')
        
    if ('user' in request.session) and ('uid' in request.session):
        return render(request, 'warkah/input_warkah.html', items())
    else:
        return redirect('/login')

def edit(request, id):
    session = request.session
    warkah = Warkah.get_warkah_byid(id)
    session = {}
    session['old_file'] = warkah.document

    if request.method == 'POST':
        form                = request.POST
        kecamatan           = Kecamatan.objects.get(kode=form['kecamatan'])
        kelurahan           = Kelurahan.objects.get(kode=form['kelurahan'])

        warkah.kecamatan_id = kecamatan.id
        warkah.kelurahan_id = kelurahan.id
        warkah.no_berkas    = form['no_berkas']
        warkah.nama_subjek  = form['nm_subjek']
        warkah.tahun        = form['tahun']
        file_name           = str(warkah.document).split('/',3)[3]
        locate              = 'media/'+str(kecamatan)+'/'+str(kelurahan)+'/'+str(form['tahun'])
        file_locat          = locate.replace(' ','_')
        file_locate         = os.path.join(settings.BASE_DIR, file_locat)

        if not 'check_upload' in request.POST and request.POST['document']=='':
            doc = 'media/'+str(warkah.document)
            docs = os.path.join(settings.BASE_DIR, doc)
            print (request.POST)

            if not os.path.isdir(file_locate):
                os.makedirs(file_locate)
                copy = shutil.move(docs, file_locate+'/'+file_name)
            elif os.path.isdir(file_locate):
                copy = shutil.move(docs, file_locate+'/'+file_name)
            else:
                copy = shutil.move(docs, file_locate+'/'+file_name)

            base_media      = copy.replace(str(settings.BASE_DIR+'\\media/'),'')
            warkah.document = base_media.replace(' ', '_')
            warkah.save()
        else:
            warkah.document     = request.FILES['document']
            docs_path = os.path.join(settings.BASE_DIR, 'media/'+str(session['old_file']))
            os.remove(docs_path)
            warkah.save()

        messages.success(request, 'Data warkah atas nama '+warkah.nama_subjek+' berhasil dirubah.')
        return redirect('/warkah')

    tgl = HARI()+', '+str(datetime.date.today().day)+' '+BULAN[datetime.date.today().month-1]+' '+str(datetime.date.today().year)
    return render(request, 'warkah/edit_warkah.html', {'dt_warkah': warkah, 'items_kec': Kecamatan.objects.all(),\
                    'items_kel': Kelurahan.objects.all(), 'tgl': tgl})

def delete(request, id):
    warkah      = Warkah.get_warkah_byid(id)
    docs        = 'media\\'+str(warkah.document)
    docs_path   = os.path.join(settings.BASE_DIR, docs)
    os.remove(docs_path)
    warkah.delete()
    messages.success(request, 'Data atas nama '+warkah.nama_subjek+' berhasil dihapus.')
    return redirect('/warkah')
# ----------------------------
# function CRUD warkah end
# ----------------------------


def session_out(request):
    return render(request, 'warkah/session.html', {})