#!/usr/bin/env python3
"""Render a small, north-up location map from the archived OSM XML only."""
from pathlib import Path
import math, json, hashlib, subprocess, xml.etree.ElementTree as ET
from html import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
W,H=66,43
PIN=(9.0566625,48.5171469)
EUROPAPLATZ_LABEL=(9.0557,48.51645)
XMIN,XMAX,YMAX=9.0515,9.0623,48.5194
YMIN=YMAX-(XMAX-XMIN)*math.cos(math.radians(PIN[1]))*H/W
INK='#103D3A'; CREAM='#FFF5D4'; WATER='#A8CECA'; TEAL='#007F78'; BUILDING='#C99D92'
PDF=ROOT/'output/pdf/lichtcafe-standortkarte.pdf'
PNG=ROOT/'output/preview/lichtcafe-standortkarte.png'
SVG=HERE/'output/lichtcafe-standortkarte.svg'

def main():
    for p in [PDF,PNG,SVG]: p.parent.mkdir(parents=True,exist_ok=True)
    for name,query in [('Map','Arial'),('MapBold','Arial:style=Bold')]:
        font=subprocess.check_output(['fc-match','-f','%{file}',query]).decode()
        pdfmetrics.registerFont(TTFont(name,font))
    root=ET.parse(HERE/'data/location.osm').getroot()
    nodes={e.get('id'):(float(e.get('lon')),float(e.get('lat'))) for e in root.findall('node')}
    ways={e.get('id'):([nodes[n.get('ref')] for n in e.findall('nd') if n.get('ref') in nodes],
                     {t.get('k'):t.get('v') for t in e.findall('tag')}) for e in root.findall('way')}
    c=canvas.Canvas(str(PDF),pagesize=(W*mm,H*mm),invariant=1,pageCompression=1)
    c.setTitle('Lichtcafé am Europaplatz - Standortkarte')
    c.setAuthor('Was macht Licht?; map data © OpenStreetMap contributors')
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         '<defs><clipPath id="map"><rect width="66" height="43"/></clipPath></defs>']
    def poly(points,fill=None,stroke=None,width=.2,closed=True):
        if not points:return
        p=c.beginPath();p.moveTo(points[0][0]*mm,(H-points[0][1])*mm)
        for x,y in points[1:]:p.lineTo(x*mm,(H-y)*mm)
        if closed:p.close()
        if fill:c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(width*mm)
        c.drawPath(p,fill=bool(fill),stroke=bool(stroke),fillMode=0)
        tag='polygon' if closed else 'polyline'
        svg.append(f'<{tag} points="'+ ' '.join(f'{x:.5f},{y:.5f}' for x,y in points)+f'" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
    def rect(x,y,w,h,fill):poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill)
    def circle(x,y,r,fill,stroke=None,width=.2):
        c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke));c.setLineWidth(width*mm)
        c.circle(x*mm,(H-y)*mm,r*mm,stroke=bool(stroke),fill=1)
        svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{width}"/>')
    def text(s,x,y,size=8,bold=False,color=INK,anchor='start',back=False):
        font='MapBold' if bold else 'Map';tw=pdfmetrics.stringWidth(s,font,size)/mm
        left=x-(tw/2 if anchor=='middle' else tw if anchor=='end' else 0)
        if back:rect(left-.8,y-size/mm-.2,tw+1.6,size/mm+1.2,'#FFFCF2')
        c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(left*mm,(H-y)*mm,s)
        svg.append(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size/mm:.6f}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>')
    def project(p):return ((p[0]-XMIN)/(XMAX-XMIN)*W,(YMAX-p[1])/(YMAX-YMIN)*H)
    def geo(points,**kw):poly([project(p) for p in points],**kw)
    rect(0,0,66,43,'#FFFCF2')
    c.saveState();clip=c.beginPath();clip.rect(0,0,W*mm,H*mm);c.clipPath(clip,stroke=0,fill=0)
    svg.append('<g clip-path="url(#map)">')
    rect(0,0,W,H,CREAM)
    # Real water outline and real island holes from relation 161200.
    geo(ways['169617936'][0],fill=WATER)
    for wid in ['186159996','36694821']:geo(ways[wid][0],fill='#E2E7C9')
    for pts,t in ways.values():
        if len(pts)<3:continue
        if t.get('leisure') in ['park','garden'] or t.get('landuse') in ['grass','forest']:
            if pts[0]==pts[-1]:geo(pts,fill='#E4E8CE')
        if t.get('building') and t.get('building')!='roof' and pts[0]==pts[-1]:
            geo(pts,fill=BUILDING)
    # A hierarchy of actual street centre lines; no route or invented connectors.
    roads={'primary':1.35,'secondary':1.15,'tertiary':.95,'residential':.75,'unclassified':.75,'living_street':.6,'pedestrian':.65}
    for pts,t in ways.values():
        if t.get('highway') in roads and t.get('area')!='yes':
            geo(pts,fill=None,stroke='#D6CEB7',width=roads[t['highway']]+.25,closed=False)
            geo(pts,fill=None,stroke='#FFFEF8',width=roads[t['highway']],closed=False)
    for pts,t in ways.values():
        if t.get('railway')=='rail' and t.get('service') not in ['siding','yard','spur']:
            geo(pts,stroke='#A7B0A8',width=.16,closed=False)
    geo(ways['24796099'][0],fill='#8FB7A3',stroke=TEAL,width=.22)
    # Labels are annotations, anchored to verified OSM features.
    _,station_y=project((9.05552509,48.51601074))
    text('Hauptbahnhof',25.1,station_y+4.5,8,bold=True,anchor='middle',back=True)
    # Area label over the station forecourt/ZOB, checked against the city plan.
    europa_x,europa_y=project(EUROPAPLATZ_LABEL)
    text('Europaplatz',europa_x,europa_y+.9,7.4,anchor='middle',back=True)
    px,py=project(PIN)
    # The pointer tip is exactly at the supplied coordinate.
    poly([(px-1.5,py-2.7),(px+1.5,py-2.7),(px,py)],fill='#F48432',stroke=INK,width=.2)
    circle(px,py-3.0,2.0,'#FFD52D',INK,.35);circle(px,py-3.0,.65,INK)
    text('Lichtcafé',px+3.0,py-2.1,8.4,bold=True,back=True)
    # A small north arrow, never a walking route.
    text('N',62.0,3.5,6.3,bold=True,anchor='middle')
    poly([(62,4.6),(61.1,7.7),(62,7.1),(62.9,7.7)],fill=INK)
    text('© OpenStreetMap contributors',1.5,41.7,6,back=True)
    c.restoreState();svg.append('</g>')
    c.showPage();c.save();svg.append('</svg>');SVG.write_text('\n'.join(svg))
    subprocess.run(['pdftoppm','-r','600','-png','-singlefile',str(PDF),str(PNG.with_suffix(''))],check=True)
    provenance={'source_url':'https://api.openstreetmap.org/api/0.6/map?bbox=9.0515,48.5147,9.0623,48.5195',
                'downloaded_utc':'2026-11-15','source_bbox':[9.0515,48.5147,9.0623,48.5195],
                'display_bbox':[XMIN,YMIN,XMAX,YMAX],'pin':{'lat':PIN[1],'lon':PIN[0]},
                'map_size_mm':[66,43],'map_area_mm':[66,43],'north_up':True,
                'projection':'Local equirectangular, cos(latitude) correction at pin latitude',
                'license':'Open Database License (ODbL)','copyright_url':'https://www.openstreetmap.org/copyright',
                'osm_sha256':hashlib.sha256((HERE/'data/location.osm').read_bytes()).hexdigest(),
                'landmark_ids':{'station_building':'way/24796099','station_forecourt_bus_area':'way/1159357124','neckar_water':'relation/161200'},
                'label_anchors':{'Europaplatz':{'lon':EUROPAPLATZ_LABEL[0],'lat':EUROPAPLATZ_LABEL[1],
                    'kind':'area_label','context':'Bahnhofsvorplatz / ZOB',
                    'within_osm_area':'way/1159357124',
                    'verification_sources':['https://www.tuebingen.de/gemeinderat/getfile.php?id=99136&type=do',
                                            'https://www.tuebingen.de/europaplatz/']}},
                'no_route':True,'no_pdf_annotations':True}
    (HERE/'data/provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'pdf':str(PDF),'svg':str(SVG),'png':str(PNG),'display_bbox':provenance['display_bbox']}))

if __name__=='__main__':main()
