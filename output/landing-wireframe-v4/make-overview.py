"""Draw a source-backed layout sheet, not a browser screenshot."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re, math

ROOT = Path(__file__).resolve().parent
source = (ROOT.parents[1]/'docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md').read_text(encoding='utf-8-sig')
parts = re.split(r'<a id="([^"]+)"></a>',source)
sections = dict(zip(parts[1::2],parts[2::2]))
W,H=1440,8000
img=Image.new('RGB',(W,H),'#ffffff'); d=ImageDraw.Draw(img)
INK='#273138'; MUTED='#5d676e'; LINE='#cdd3d7'; BLUE='#276188'
def font(size,bold=False,ko=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('malgunbd.ttf' if bold else 'malgun.ttf') if ko else 'C:/Windows/Fonts/'+('msyhbd.ttc' if bold else 'msyh.ttc'),size)
def plain(s):
    s=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',s)
    return re.sub(r'^#{1,3} |\*\*','',s).strip()
def text(s,x,y,width,size=18,bold=False,color=INK,ko=False):
    f=font(size,bold,ko); step=int(size*1.65); line=''
    for ch in plain(s):
        if ch=='\n' or d.textlength(line+ch,font=f)>width:
            d.text((x,y),line,font=f,fill=color);y+=step;line='' if ch=='\n' else ch
        else:line+=ch
    if line:d.text((x,y),line,font=f,fill=color);y+=step
    return y
def box(x,y,w,h,fill='#f6f7f8'):
    d.rectangle((x,y,x+w,y+h),fill=fill,outline=LINE,width=1)
def button(s,x,y,w=150,primary=True):
    box(x,y,w,40,INK if primary else '#fff');text(s,x+14,y+7,w-20,15,color='#fff' if primary else INK)
def note(title,body,y):
    text(title,1165,y,240,17,True,BLUE,True)
    text(body,1165,y+36,240,15,color=MUTED,ko=True)
def heading(sid,y):
    d.line((0,y,1135,y),fill=LINE)
    text(sid.upper(),60,y+28,1000,13,color=BLUE)
    lines=sections[sid].strip().splitlines()
    y=text(lines[0],60,y+58,1010,30,True)
    return y+16
def intro(sid,y):
    blocks=sections[sid].strip().split('\n\n')
    if len(blocks)>1 and not blocks[1].startswith(('|','#')):return text(blocks[1],60,y,1000,18,color=MUTED)+22
    return y

d.rectangle((1136,0,1440,H),fill='#f0f5f8')
d.rectangle((0,0,1440,60),fill='#e8eef2')
text('PNPLINE  /  单页线框 V4',30,15,760,20,True)
text('구조 검토 이미지 · 브라우저 캡처 아님',950,19,460,16,color=BLUE,ko=True)
text('PNPLINE',60,87,200,28,True)
text('服务范围     仓库与系统     费用说明     常见问题',420,96,510,16)
button('获取物流报价',932,86,155)
box(0,145,1135,580,'#edf0f2')
for x in range(570,1135,40):d.line((x,145,x,725),fill='#dbe0e3')
for y in range(165,725,40):d.line((570,y,1135,y),fill='#dbe0e3')
d.ellipse((640,310,1060,640),fill='#e4e9ec',outline='#8d999f',width=2)
d.ellipse((750,310,950,640),outline='#9eabb3',width=2)
d.line((640,475,1060,475),fill='#9eabb3',width=2)
d.arc((680,330,1000,600),185,355,fill='#63737e',width=3)
for x,y in [(695,427),(943,525),(835,598)]:box(x,y,35,28,'#9caab3')
text('PNPLINE · 跨境物流服务',60,190,500,15)
hero=sections['journey'].strip().split('\n\n')
y=text(hero[0],60,235,520,43,True)
y=text(hero[2],60,y+24,505,18,color=MUTED)
y=text(hero[3],60,y+14,505,18,color=MUTED)
button('获取物流报价',60,y+25);button('查看服务范围',225,y+25,155,False)
text('영상 영역 / 스크롤 위치와 영상 시점을 연결',620,675,480,17,color=BLUE,ko=True)
note('01  고정 히어로','문구·CTA는 웹 UI로 유지합니다. 스크롤 구간 동안 영상 영역을 고정합니다.',170)
note('스크롤 → 시점','0% → 영상 시작\n25% → 0.25 × T\n50% → 0.50 × T\n75% → 0.75 × T\n100% → 영상 끝\n\nT = 최종 영상 길이\n위로 스크롤하면 이전 시점, 멈추면 현재 시점을 유지합니다.',330)
y=775
start=y;y=heading('services',y);y=intro('services',y)
blocks=re.split(r'\n### ',sections['services'])[1:]
left_y=y;right_y=y
for i,b in enumerate(blocks):
    title,body=b.split('\n',1);body=re.sub(r'\[获取物流报价\]\(#quote\)','',body).strip()
    x=60 if i==0 else 590; top=left_y if i==0 else right_y; width=485
    # Measure on a temporary draw surface to determine card height.
    old=d; temp=Image.new('RGB',(W,H));d=ImageDraw.Draw(temp)
    bottom=text(title,x+24,top+24,width-48,23,True)
    for para in body.split('\n\n'):bottom=text(para,x+24,bottom+12,width-48,16,color=MUTED)
    d=old; box(x,top,width,bottom-top+22)
    btm=text(title,x+24,top+24,width-48,23,True)
    for para in body.split('\n\n'):btm=text(para,x+24,btm+12,width-48,16,color=MUTED)
    if i==0:left_y=bottom+42
    else:right_y=bottom+42
y=max(left_y,right_y);button('获取物流报价',60,y);y+=90
note('02  서비스 선택','창고·주문 이행을 먼저 보여 줍니다. 나머지 세 영역은 같은 섹션 안에서 비교합니다. 별도 서비스 페이지로 이동하지 않습니다.',start+45)

for sid in ['customers','evidence','process','pricing','faq','quote']:
    start=y;y=heading(sid,y)
    if sid not in ('faq','process'):y=intro(sid,y)
    if sid in ['customers','pricing']:
        rows=[line for line in sections[sid].splitlines() if line.startswith('|') and '---' not in line]
        for i,row in enumerate(rows):
            cells=[c.strip() for c in row.strip('|').split('|')]
            old=d;d=ImageDraw.Draw(Image.new('RGB',(W,H)))
            h=max(text(cells[0],78,0,270,17,True),text(cells[1],380,0,665,17))+26;d=old
            box(60,y,1015,h,'#e8ecef' if i==0 else '#fff')
            text(cells[0],78,y+13,270,17,True);text(cells[1],380,y+13,665,17);y+=h
        after=sections[sid].split(rows[-1])[-1].strip().split('\n\n')[0]
        y=text(after,60,y+20,1015,16,color=MUTED)+20
        button('获取物流报价',60,y);y+=65
    elif sid=='evidence':
        blocks=re.split(r'\n### ',sections[sid])[1:];bottoms=[]
        for i,b in enumerate(blocks):
            title,body=b.split('\n',1);body=re.sub(r'\[获取物流报价\]\(#quote\)','',body).strip()
            x=60+i*530;box(x,y,485,220)
            yy=text(title,x+24,y+24,437,22,True);yy=text(body,x+24,yy+12,437,17,color=MUTED);bottoms.append(yy)
        y=max(max(bottoms),y+220)+24;button('获取物流报价',60,y);y+=65
    elif sid=='process':
        steps=[line for line in sections[sid].splitlines() if re.match(r'\d\. ',line)]
        bottoms=[]
        for i,line in enumerate(steps):
            x=60+i*350;d.line((x,y,x+315,y),fill='#8d999f',width=2)
            yy=text('0'+str(i+1),x,y+18,300,32,color=MUTED)
            yy=text(line[3:],x,yy+10,315,17);bottoms.append(yy)
        y=max(bottoms)+25
    elif sid=='faq':
        questions=re.findall(r'^### (.*)$',sections[sid],re.M)
        for q in questions:
            d.line((60,y,1075,y),fill=LINE);text(q,60,y+17,940,18,True);text('+',1040,y+14,35,24);y+=65
    elif sid=='quote':
        box(60,y,1015,465,'#f1f3f5');top=y+25
        fields=[('产品类目','商品名称或所属类目。'),('发货方式','未定  ▾'),('月出货量','预计货量与单位，或填写“未定”。'),('目的地','未定  ▾'),('是否需要IOR服务','不清楚  ▾'),('联系邮箱','用于本次询价联系的邮箱。')]
        for i,(label,placeholder) in enumerate(fields):
            x=85+(i%2)*500;yy=top+(i//2)*100;text(label,x,yy,450,16,True);box(x,yy+32,465,47,'#fff');text(placeholder,x+12,yy+42,440,15,color=MUTED)
        yy=top+315;box(85,yy+3,18,18,'#fff');text('我已阅读《隐私政策》，同意为处理本次询价使用所填信息。',115,yy,900,15)
        button('提交询价需求',85,yy+50,185);y+=490
        text('报价与执行条件将在资料及服务范围确认后沟通。',60,y,1015,16,color=MUTED);y+=48
    notes={
    'customers':('03  고객별 요구','판매 방식에 따라 필요한 작업을 비교합니다.'),
    'evidence':('04  운영 확인','검증된 사진이 없으므로 텍스트로 구성합니다. 가짜 시설 사진·수치·인증 표시는 넣지 않습니다.'),
    'process':('05  상담 절차','물류 영상의 7개 장면과 구분되는 고객 상담 3단계입니다.'),
    'pricing':('06  비용 이해','미확정 가격표 대신 비용 항목과 확인 조건을 보여 줍니다.'),
    'faq':('07  질문 해소','8개 질문을 펼쳐 답을 확인합니다. 원고의 답변은 HTML에 모두 포함됩니다.'),
    'quote':('08  견적 문의','원고의 6개 필드를 유지합니다. 입력 배치 검토용이며 전송하지 않습니다. 개인정보만 별도 페이지로 연결합니다.')}
    note(*notes[sid],start+45);y+=38
d.line((0,y,1135,y),fill=LINE);text('PNPLINE — 美国自营海外仓与跨境物流服务',60,y+25,1015,18,True)
text('服务范围    仓库与系统    费用说明    常见问题    获取物流报价    隐私政策',60,y+65,1015,15)
img.crop((0,0,W,y+120)).save(ROOT/'overview.png')
print('Saved overview.png',W,y+120)
