import time, datetime
import requests
from xml.etree import ElementTree
import Logfile
      
def GetTempAEMET(TempAemet, CieloAemet, nVerbose):
    #####################################
    # General Params
    #####################################
    
    # http://www.aemet.es/xml/municipios_h/localidad_h_28079.xml
    szRootUrl = 'http://www.aemet.es'
        
    #####################################
    # Homepage sock1
    #####################################
    dateToday = datetime.datetime.now()
    szDateToday=dateToday.strftime ("%Y-%m-%d")
    szTimeHour=dateToday.strftime ("%H")

    dateAfter1 = dateToday + datetime.timedelta(hours=1)
    szDateAfter1=dateAfter1.strftime ("%Y-%m-%d")
    szTimeHour1=dateAfter1.strftime ("%H")

    dateAfter2 = dateAfter1 + datetime.timedelta(hours=1)
    szDateAfter2=dateAfter2.strftime ("%Y-%m-%d")
    szTimeHour2=dateAfter2.strftime ("%H")

    if nVerbose > 0:
        Logfile.printError ('[AEMET] Load homepage......')
    
    szUriParams = '/xml/municipios_h/localidad_h_28079.xml'
    url = szRootUrl+szUriParams
    s=requests.session()
    try:
        response = s.get(url,stream=False, timeout=15)
    except requests.exceptions.RequestException as e:
        Logfile.printError ('[AEMET] Error conectando a server')
        return()
        
    s.close()

    xmlroot = ElementTree.fromstring(response.content)
    #xmlroot=xmlTree.getroot()
    szDay=xmlroot[4][0].get('fecha');

    if (szDateToday == szDay):
        xmlDia1=xmlroot[4][0]
    else:
        xmlDia1=xmlroot[4][1]

    for cielo in xmlDia1.findall('estado_cielo'):
        szPeriodo = cielo.get('periodo')
        szTexto=cielo.text
        if szPeriodo.find(szTimeHour) >=0:
            CieloAemet[0]=szTexto
            if nVerbose > 0:
                Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
        if szPeriodo.find(szTimeHour1) >=0:
            CieloAemet[1]=szTexto
            if nVerbose > 0:
                Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
        if szPeriodo.find(szTimeHour2) >=0:
            if nVerbose > 0:
                Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
            CieloAemet[2]=szTexto
            
    for xmlTemp in xmlDia1.findall('temperatura'):
        szPeriodo = xmlTemp.get('periodo')
        szTexto=xmlTemp.text
        if szPeriodo.find(szTimeHour) >=0:
            TempAemet[0]=szTexto
            if nVerbose > 0:
                Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
        if szPeriodo.find(szTimeHour1) >=0:
            TempAemet[1]=szTexto
            if nVerbose > 0:
                Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
        if szPeriodo.find(szTimeHour2) >=0:
            if nVerbose > 0:
                Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
            TempAemet[2]=szTexto
            
    if int(szTimeHour)==22:
        xmlDia1=xmlroot[4][1]
        for cielo in xmlDia1.findall('estado_cielo'):
            szPeriodo = cielo.get('periodo')
            szTexto=cielo.text
            if szPeriodo.find(szTimeHour2) >=0:
                if nVerbose > 0:
                    Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
                CieloAemet[2]=szTexto
        for xmlTemp in xmlDia1.findall('temperatura'):
            szPeriodo = xmlTemp.get('periodo')
            szTexto=xmlTemp.text
            if szPeriodo.find(szTimeHour2) >=0:
                TempAemet[2]=szTexto
                if nVerbose > 0:
                    Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
    if int(szTimeHour)==23:
        xmlDia1=xmlroot[4][1]
        for cielo in xmlDia1.findall('estado_cielo'):
            szPeriodo = cielo.get('periodo')
            szTexto=cielo.text
            if szPeriodo.find(szTimeHour1) >=0:
                CieloAemet[1]=szTexto
                if nVerbose > 0:
                    Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
            if szPeriodo.find(szTimeHour2) >=0:
                if nVerbose > 0:
                    Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
                CieloAemet[2]=szTexto
        for xmlTemp in xmlDia1.findall('temperatura'):
            szPeriodo = xmlTemp.get('periodo')
            szTexto=xmlTemp.text
            if szPeriodo.find(szTimeHour1) >=0:
                TempAemet[1]=szTexto
                if nVerbose > 0:
                    Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
            if szPeriodo.find(szTimeHour2) >=0:
                if nVerbose > 0:
                    Logfile.printError ('[AEMET] ' + szPeriodo+' '+szTexto)
                TempAemet[2]=szTexto 	



def main():
    TempAemet = ['Null' for i in range(7)]
    CieloAemet = ['Null' for i in range(7)]
    GetTempAEMET(TempAemet, CieloAemet, 0)
    #print (ZonaName[1]+': '+ZonaTemp[1]+'C')
    
#####################################
# Main
#####################################    
if __name__ == "__main__":
    main()
    

