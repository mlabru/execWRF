import sys, os
import requests
from datetime import timedelta, date, datetime


class downloadFNL():
    def __init__(self, v_data, v_hora_inicio, v_duracao, logging):
        self.v_data = v_data
        self.logging = logging
        self.v_data = v_data
        self.v_ano = v_data[0:4]
        self.v_mes = v_data[4:6]
        self.v_dia = v_data[6:8]
        self.v_periodo = v_duracao
        self.v_hora_ini = v_hora_inicio
    
        url = 'https://rda.ucar.edu/cgi-bin/login'
        values = {'email' : 'pgiriart@gmail.com', 'passwd' : 'R0mLnAoB', 'action' : 'login'}
        # Authenticate
        ret = requests.post(url,data=values)
        if ret.status_code != 200:
            print('Bad Authentication')
            print(ret.text)
            self.logging.error('Bad Authentication : ' + ret.text)
            exit(1)
        dspath = 'https://rda.ucar.edu/data/ds083.2/'

        inc = 0
        aux_inc = int(v_hora_inicio)
        data_temp = datetime.strptime(self.v_data,'%Y%m%d')
        data_str = data_temp.strftime('%Y%m%d')
        if not os.path.exists('/home/webpca/WRF/data/fnl/' + data_str):
            os.mkdir('/home/webpca/WRF/data/fnl/' + data_str )
        os.chdir('/home/webpca/WRF/data/fnl/' + data_str )
        while( inc <= int(self.v_periodo)):
            hora = '{:0>2d}'.format(aux_inc)
            file = 'grib2/' + self.v_ano + '/' + self.v_ano + '.' + self.v_mes + '/' + 'fnl_' + data_str + '_' + hora + '_00.grib2'
            aux_inc = aux_inc + 6
            inc = inc + 6
            print (file)
            print (inc)
            if (aux_inc > 18) :
                aux_inc=0
                data_temp = data_temp + timedelta(days=1)
                data_str = data_temp.strftime('%Y%m%d')
                v_ano = sys.argv[1][0:4]
                v_mes = sys.argv[1][4:6]
                v_dia = sys.argv[1][6:8]
            filename=dspath+file
            file_base = os.path.basename(file)
            print('Downloading',file_base)
            self.logging.debug( 'Downloading : '+ file_base )
            req = requests.get(filename, cookies = ret.cookies, allow_redirects=True, stream=True)
            filesize = int(req.headers['Content-length'])
            with open(file_base, 'wb') as outfile:
                chunk_size=1048576
                for chunk in req.iter_content(chunk_size=chunk_size):
                    outfile.write(chunk)
                    if chunk_size < filesize:
                        self.check_file_status(file_base, filesize)

    def check_file_status(self,filepath, filesize):
        sys.stdout.write('\r')
        sys.stdout.flush()
        size = int(os.stat(filepath).st_size)
        percent_complete = (size/filesize)*100
        sys.stdout.write('%.3f %s' % (percent_complete, '% Completed'))
        sys.stdout.flush()
