#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE
REG = BASE

REGULATIONS = {
    'mobile_device_policy.md': {'title':'生輔組－行動載具管理規則','keywords':['行動載具','手機','平板','載具']},
    'conduct_and_class_order.md': {'title':'生輔組－品德教育暨班級生活秩序競賽實施要點','keywords':['品德','生活秩序','秩序競賽','班級競賽']},
    'student_rewards_discipline.md': {'title':'生輔組－學生獎懲規定','keywords':['獎懲','嘉獎','警告','小過','大過','懲處','銷過']},
    'student_leave_rules.md': {'title':'生輔組－學生請假規則','keywords':['請假','病假','事假','公假','補假','喪假','身心調適假']},
}


def load_json(name):
    p = DATA / name
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}


def compact(s):
    return re.sub(r'\s+', '', str(s or '')).lower()


def place_variants(s):
    q = compact(s)
    vals = {q}
    vals.add(re.sub(r'^\d+樓', '', q))
    vals |= {v.replace('資處科', '資處') for v in list(vals)}
    vals |= {v.replace('資料處理科', '資處') for v in list(vals)}
    return {v for v in vals if v}


def room_match(query, row):
    q = compact(query)
    place = compact(row.get('場所', ''))
    building = compact(row.get('大樓', ''))
    if not place:
        return False
    variants = place_variants(place)
    if any(v in q for v in variants):
        return True
    core = compact(re.sub(r'^\d+樓', '', place).replace('資處科', '資處').replace('資料處理科', '資處'))
    # 只有具辨識度的場所核心才可直接命中；避免「電腦教室」把所有電腦教室一起命中
    if core and core in q and re.search(r'[a-z0-9]', core):
        return True
    # 像「6D電腦教室」這種省略科別與樓層的自然說法
    m = re.search(r'([A-Za-z]\s*[A-Za-z0-9]*).*?電腦教室', q)
    if m and '電腦教室' in q:
        token = compact(m.group(1))
        if token and token in compact(place) and '電腦教室' in compact(place):
            return True
    if building and building in q and re.sub(r'^\d+樓', '', place) in q:
        return True
    return False


def staff_hits(q):
    data = load_json('staff_extensions.json')
    rec = data.get('分機紀錄', [])
    out = []
    cq = compact(q)
    for r in rec:
        name = compact(r.get('姓名'))
        role = compact(r.get('職稱'))
        unit = compact(r.get('單位'))
        if (name and name in cq) or (role and role in cq and len(role) >= 2) or (unit and unit in cq and len(unit) >= 2):
            out.append({'單位': r.get('單位',''), '職稱': r.get('職稱',''), '姓名': r.get('姓名',''), '分機': r.get('分機',[])})
    return out[:12]


def extension_results(q):
    data = load_json('staff_extensions.json')
    classes = load_json('class_extensions.json')
    out = {}
    cq = compact(q)
    class_hits = [{'班級': k, '分機': v} for k, v in classes.get('班級分機', {}).items() if compact(k) in cq]
    if class_hits:
        out['班級分機'] = class_hits
    rooms = data.get('場館分機', [])
    room_hits = [r for r in rooms if room_match(q, r)]
    if room_hits:
        out['場館分機'] = room_hits
    if not room_hits:
        sh = staff_hits(q)
        if sh:
            out['分機總表紀錄'] = sh
    if out:
        out['分機資料來源'] = {
            '文件': data.get('資料名稱', '鶯歌工商分機公告版'),
            '公告日期': data.get('資料日期', ''),
            '來源檔案': data.get('來源檔案', ''),
            '校方網站': 'https://www.ykvs.ntpc.edu.tw/'
        }
    return out


def calendar_results(q):
    d = load_json('english_center.json')
    weeks = d.get('calendar_weeks', [])
    cq = compact(q)
    dates = re.findall(r'(\d{1,2})\s*(?:月|/|-)(\d{1,2})\s*日?', cq)
    months = re.findall(r'(\d{1,2})月', cq)
    current_week = any(x in cq for x in ['本週', '這週', '本星期', '這星期'])
    today = None
    if current_week:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        today = datetime.now(ZoneInfo('Asia/Taipei')).date().isoformat()
    out = []
    for w in weeks:
        ds = w.get('每日日期', [])
        if current_week and today not in ds:
            continue
        if dates and not any(str(x).endswith(f'-{int(dates[0][0]):02d}-{int(dates[0][1]):02d}') for x in ds):
            continue
        if not dates and months and not any(f'-{int(months[0]):02d}-' in str(x) for x in ds):
            continue
        out.append({'週別': w.get('週別'), '日期起': w.get('日期起'), '日期迄': w.get('日期迄'), '各處室行程': w.get('各處室行程', {})})
        if len(out) >= 8:
            break
    return {'行事曆': out, '來源': d.get('calendar_source', '請查校方最新公告')}


def academic_regulation_results(q):
    data = load_json('additional_regulations.json')
    cq = compact(q)
    matches = []
    for row in data.get('records', []):
        hits = [compact(k) for k in row.get('keywords', []) if compact(k) and compact(k) in cq]
        if hits:
            matches.append((len(hits), max(map(len, hits)), row))
    if not matches:
        return []
    matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [
        {'類別': row.get('category', ''), '標題': row.get('title', ''), '摘要': row.get('content', '')}
        for _, _, row in matches[:2]
    ]


def search_school_info(query: str):
    q = str(query or '').strip()
    cq = compact(q)
    if not q:
        return {'錯誤': '請輸入查詢內容。'}
    for fn, meta in REGULATIONS.items():
        if any(compact(k) in cq for k in meta['keywords']):
            p = REG / fn
            text = p.read_text(encoding='utf-8') if p.exists() else ''
            return {'查詢': q, '法規結果': [{'文件': meta['title'], '原文摘錄': text[:5000], '來源': 'https://www.ykvs.ntpc.edu.tw/'}]}
    if any(x in cq for x in ['行事曆','行事历','行程']) or re.search(r'\d{1,2}\s*(?:月|/|-)\s*\d{1,2}', cq):
        return {'查詢': q, **calendar_results(q)}
    ext = extension_results(q)
    if ext:
        return {'查詢': q, **ext}
    academic_rules = academic_regulation_results(q)
    if academic_rules:
        return {'查詢': q, '校務規定結果': academic_rules}
    return {'查詢': q, '結果': '在目前校方資料中找不到明確紀錄。', '官方首頁': 'https://www.ykvs.ntpc.edu.tw/'}


TOOLS = [
 {'name':'search_rules','description':'搜尋公開校規、請假、獎懲、手機規範與教務規定；返回可引用的文件摘錄與來源標籤。','inputSchema':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}},
 {'name':'search_calendar','description':'查詢既有學期行事曆日期與活動，若資料過期要提醒。','inputSchema':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}},
 {'name':'search_contacts','description':'查詢公開教職員、班級、場館分機；不得查個資。','inputSchema':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}},
 {'name':'search_procedures','description':'查詢公開校務辦理流程及法規，不代辦任何行政操作。','inputSchema':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}},
 {'name':'search_announcements','description':'搜尋本地公告資料；若沒有公告資料必須明確回報不可確認停辦或異動。','inputSchema':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}},
 {'name':'search_school_info','description':'相容舊版：跨資料類別搜尋校務資訊。','inputSchema':{'type':'object','properties':{'query':{'type':'string'}},'required':['query']}}
]

def ev(title, excerpt, source_id, kind, version='', url=''):
    return {'title':title,'excerpt':str(excerpt)[:1400],'source_id':source_id,'category':kind,'version':version or '未標示','url':url or None,'url_type':'document' if url and '11369' in url else ('directory' if url else 'unverified'),'citation_status':'verified_official_document' if url and '11369' in url else ('official_directory_only' if url else 'local_snapshot_only')}

OFFICIAL_SOURCES = {
 'student_leave_rules.md':'https://www.ykvs.ntpc.edu.tw/p/450-1000-11369%2Cc0.php?Lang=zh-tw',
 'student_rewards_discipline.md':'https://www.ykvs.ntpc.edu.tw/p/403-1000-287-1.php',
 'mobile_device_policy.md':'https://www.ykvs.ntpc.edu.tw/p/403-1000-287-1.php',
 'conduct_and_class_order.md':'https://www.ykvs.ntpc.edu.tw/p/403-1000-287-1.php',
}

OFFICIAL_SOURCES = {
 'student_leave_rules.md':'https://www.ykvs.ntpc.edu.tw/p/450-1000-11369%2Cc0.php?Lang=zh-tw',
 'student_rewards_discipline.md':'https://www.ykvs.ntpc.edu.tw/p/403-1000-287-1.php',
 'mobile_device_policy.md':'https://www.ykvs.ntpc.edu.tw/p/403-1000-287-1.php',
 'conduct_and_class_order.md':'https://www.ykvs.ntpc.edu.tw/p/403-1000-287-1.php',
}

def query_tool(name, q):
    q=str(q or '').strip()[:500]
    if not q: return {'evidence':[],'note':'空查詢'}
    evidence=[]
    if name in ('search_rules','search_procedures','search_school_info'):
        cq=compact(q)
        for fn,meta in REGULATIONS.items():
            if any(compact(k) in cq for k in meta['keywords']):
                p=REG/fn
                if p.exists():
                    txt=p.read_text(encoding='utf-8')
                    lines=[x.strip() for x in txt.splitlines() if x.strip()]
                    scored=sorted(((sum(1 for k in meta['keywords'] if k in x)+sum(1 for t in re.findall(r'[\u4e00-\u9fff]{2,5}',q) if t in x),i,x) for i,x in enumerate(lines)),reverse=True)
                    snippets=[x for score,i,x in scored[:5] if score>0] or lines[:5]
                    evidence.append(ev(meta['title'],'\n'.join(snippets),f'data/regulations/{fn}','regulation',url=OFFICIAL_SOURCES.get(fn,'')))
        for r in academic_regulation_results(q):
            evidence.append(ev(r.get('標題','教務規定'),r.get('摘要',''),'data/additional_regulations.json','procedure'))
    if name in ('search_contacts','search_school_info'):
        d=extension_results(q)
        if d:
            for key in ('班級分機','場館分機','分機總表紀錄'):
                for row in d.get(key,[]):
                    evidence.append(ev('公開分機資料',json.dumps(row,ensure_ascii=False),f'data/{"class_extensions.json" if key=="班級分機" else "staff_extensions.json"}','contact',d.get('分機資料來源',{}).get('公告日期','')))
    if name in ('search_calendar','search_school_info'):
        if name=='search_calendar' or any(k in compact(q) for k in ('行事曆','行程','活動','校外教學')) or re.search(r'\d{1,2}月\d{1,2}',q):
            d=calendar_results(q)
            for row in d.get('行事曆',[]):
                evidence.append(ev('學期行事曆',json.dumps(row,ensure_ascii=False), 'data/english_center.json','calendar','資料版本請以校方最新公告為準'))
    if name=='search_announcements':
        return {'query':q,'evidence':[],'note':'本專案未接入即時官方公告 API，無法確認活動是否取消或更改；請以校方最新公告為準。'}
    return {'query':q,'evidence':evidence[:12],'note':'無匹配資料，請改寫查詢或轉介官方窗口。' if not evidence else '來源為本地校務資料快照，非即時同步；未驗證文件直連。'}

def send(obj):
    sys.stdout.write(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n');sys.stdout.flush()

def main():
    for line in sys.stdin:
        msg={}
        try:
            msg=json.loads(line);mid=msg.get('id');method=msg.get('method');params=msg.get('params') or {}
            if method=='initialize':
                if mid is not None:send({'jsonrpc':'2.0','id':mid,'result':{'protocolVersion':params.get('protocolVersion','2025-06-18'),'capabilities':{'tools':{}},'serverInfo':{'name':'ykvs_campus_agent','version':'2.0'}}})
            elif method=='notifications/initialized':continue
            elif method=='tools/list':
                if mid is not None:send({'jsonrpc':'2.0','id':mid,'result':{'tools':TOOLS}})
            elif method=='tools/call':
                name=params.get('name');args=params.get('arguments') or {}
                if name not in {t['name'] for t in TOOLS}:raise ValueError('不支援的工具')
                payload=json.dumps(query_tool(name,args.get('query','')),ensure_ascii=False)
                if mid is not None:send({'jsonrpc':'2.0','id':mid,'result':{'content':[{'type':'text','text':payload}],'isError':False}})
            elif mid is not None:send({'jsonrpc':'2.0','id':mid,'error':{'code':-32601,'message':'未知方法'}})
        except Exception as e:
            if msg.get('id') is not None:send({'jsonrpc':'2.0','id':msg['id'],'error':{'code':-32000,'message':str(e)}})

if __name__=='__main__':main()
