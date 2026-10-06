# Erzeugt Showtec-Spectral-M800-Q4-IP65.qxf (QLC+) aus dem Herstellerhandbuch 43571 V2, S. 36-39 (Odoo #1906).
from xml.sax.saxutils import escape as e

def cap(a, b, txt, preset=None):
    p = f' Preset="{preset}"' if preset else ''
    return f'  <Capability Min="{a}" Max="{b}"{p}>{e(txt)}</Capability>'

makros = [(0,10,'Keine Funktion'),(11,30,'Rot 100 % / Grün auf / Blau 0 %'),(31,50,'Rot ab / Grün 100 % / Blau 0 %'),
          (51,70,'Rot 0 % / Grün 100 % / Blau auf'),(71,90,'Rot 0 % / Grün ab / Blau 100 %'),(91,110,'Rot auf / Grün 0 % / Blau 100 %'),
          (111,130,'Rot 100 % / Grün 0 % / Blau ab'),(131,150,'Rot 100 % / Grün auf / Blau auf'),(151,170,'Rot ab / Grün ab / Blau 100 %'),
          (171,200,'RGBW 100 %')]
for i,k in enumerate([3200,3400,4200,4900,5600,5900,6500,7200,8000,8500,10000]):
    makros.append((201+5*i, 205+5*i, f'Weiß {i+1}: {k} K'))
progs = [(0,20,'Keine Funktion')] + [(21+10*i,30+10*i,f'AUTO{i+1:02d}') for i in range(10)] \
      + [(121+10*i,130+10*i,f'PR.{i+1:02d} (Time/Fade Time auf Rot/Grün)') for i in range(10)] + [(221,255,'Keine Funktion')]

kanaele = {
 'Master Dimmer': '<Channel Name="Master Dimmer" Preset="IntensityMasterDimmer"/>',
 'Dimmer fine':   '<Channel Name="Dimmer fine" Preset="IntensityMasterDimmerFine"/>',
 'Red': '<Channel Name="Red" Preset="IntensityRed"/>', 'Red fine': '<Channel Name="Red fine" Preset="IntensityRedFine"/>',
 'Green': '<Channel Name="Green" Preset="IntensityGreen"/>', 'Green fine': '<Channel Name="Green fine" Preset="IntensityGreenFine"/>',
 'Blue': '<Channel Name="Blue" Preset="IntensityBlue"/>', 'Blue fine': '<Channel Name="Blue fine" Preset="IntensityBlueFine"/>',
 'White': '<Channel Name="White" Preset="IntensityWhite"/>', 'White fine': '<Channel Name="White fine" Preset="IntensityWhiteFine"/>',
 'Color Macros': '<Channel Name="Color Macros">\n  <Group Byte="0">Colour</Group>\n' + '\n'.join(cap(a,b,t) for a,b,t in makros) + '\n </Channel>',
 'Strobe': '<Channel Name="Strobe">\n  <Group Byte="0">Shutter</Group>\n'
    + cap(0,9,'Offen','ShutterOpen') + '\n' + cap(10,99,'Strobe 0-20 Hz','StrobeSlowToFast') + '\n'
    + cap(100,109,'Offen (bei Classic Strobe: Strobe)','ShutterOpen') + '\n' + cap(110,179,'Pulse-Strobe langsam-schnell (Special Strobe)','PulseSlowToFast') + '\n'
    + cap(180,189,'Offen (bei Classic Strobe: Strobe)','ShutterOpen') + '\n' + cap(190,255,'Zufalls-Strobe langsam-schnell (Special Strobe)','StrobeRandomSlowToFast')
    + '\n </Channel>',
 'Programs': '<Channel Name="Programs">\n  <Group Byte="0">Effect</Group>\n' + '\n'.join(cap(a,b,t) for a,b,t in progs) + '\n </Channel>',
 'Program Speed': '<Channel Name="Program Speed">\n  <Group Byte="0">Speed</Group>\n' + cap(0,255,'Programmgeschwindigkeit langsam-schnell','SlowToFast') + '\n </Channel>',
 'Dimmer Speed': '<Channel Name="Dimmer Speed">\n  <Group Byte="0">Speed</Group>\n' + '\n'.join(cap(a,b,t) for a,b,t in
    [(0,9,'Voreinstellung aus dem Gerätemenü'),(10,29,'Linear'),(30,69,'Nicht-linear 1 (schnellste)'),(70,129,'Nicht-linear 2'),
     (130,189,'Nicht-linear 3'),(190,255,'Nicht-linear 4 (langsamste)')]) + '\n </Channel>',
}
modi = {
 'AR1.D (RGB 4 Kanäle)': ['Master Dimmer','Red','Green','Blue'],
 'TOUR (RGB 9 Kanäle)':  ['Master Dimmer','Red','Green','Blue','Color Macros','Strobe','Programs','Program Speed','Dimmer Speed'],
 'TR16 (RGB 13 Kanäle)': ['Master Dimmer','Dimmer fine','Red','Red fine','Green','Green fine','Blue','Blue fine','Color Macros','Strobe','Programs','Program Speed','Dimmer Speed'],
 'ARC.2 (RGBW 4 Kanäle)': ['Red','Green','Blue','White'],
 'AR2.D (RGBW 5 Kanäle)': ['Master Dimmer','Red','Green','Blue','White'],
 'AR2.S (RGBW 6 Kanäle)': ['Master Dimmer','Red','Green','Blue','White','Strobe'],
 'SSP (RGBW 7 Kanäle)':   ['Master Dimmer','Red','Green','Blue','White','Strobe','Programs'],
 '8BIT (RGBW 10 Kanäle)': ['Master Dimmer','Red','Green','Blue','White','Color Macros','Strobe','Programs','Program Speed','Dimmer Speed'],
 '16BI (RGBW 15 Kanäle)': ['Master Dimmer','Dimmer fine','Red','Red fine','Green','Green fine','Blue','Blue fine','White','White fine',
                           'Color Macros','Strobe','Programs','Program Speed','Dimmer Speed'],
}
for n,k in modi.items():
    assert len(k) == int(n.split()[-2]), n
out = ['<?xml version="1.0" encoding="UTF-8"?>','<!DOCTYPE FixtureDefinition>',
 '<FixtureDefinition xmlns="http://www.qlcplus.org/FixtureDefinition">',
 ' <Creator>\n  <Name>Q Light Controller Plus</Name>\n  <Version>4.13.1</Version>\n  <Author>FraWo (Claude) nach Handbuch 43571 V2</Author>\n </Creator>',
 ' <Manufacturer>Showtec</Manufacturer>',' <Model>Spectral M800 Q4 IP65</Model>',' <Type>Color Changer</Type>']
out += [' ' + v for v in kanaele.values()]
for n,k in modi.items():
    out.append(f' <Mode Name="{e(n)}">')
    if 'RGBW' in n or 'RGB' in n: pass
    out += [f'  <Channel Number="{i}">{c}</Channel>' for i,c in enumerate(k)]
    out.append(' </Mode>')
out += [' <Physical>','  <Bulb Type="LED" Lumens="1452" ColourTemperature="0"/>','  <Dimensions Weight="4.3" Width="235" Height="323" Depth="180"/>',
        '  <Lens Name="Other" DegreesMin="16" DegreesMax="16"/>','  <Focus Type="Fixed" PanMax="0" TiltMax="0"/>',
        '  <Technical PowerConsumption="65" DmxConnector="3-pin"/>',' </Physical>','</FixtureDefinition>']
open('Showtec-Spectral-M800-Q4-IP65.qxf','w',encoding='utf-8',newline='\n').write('\n'.join(out)+'\n')
print('ok', len(modi), 'Modi')
