"""Rebuild revision 2.0 diagrams from the public source model. No application data is read."""
from pathlib import Path
import json, subprocess, textwrap, datetime, re, html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Ellipse, Rectangle, Circle
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/diagrams'; SRC=OUT/'source'
DATA=json.loads((ROOT/'docs/review/requirements.json').read_text())
NAVY='#19384B'; TEAL='#167C80'; PALE='#EDF4F7'; GREY='#5F7280'; GOLD='#B46A23'
BASE='''digraph G {
graph [bgcolor="white", pad="0.25", nodesep="0.40", ranksep="0.55", fontname="DejaVu Sans", fontsize=13];
node [shape=box, style="rounded,filled", fillcolor="#EDF4F7", color="#8EA8B7", fontcolor="#19384B", fontname="DejaVu Sans", fontsize=13, margin="0.20,0.13", penwidth=1.2];
edge [color="#5F7280", fontcolor="#334F60", fontname="DejaVu Sans", fontsize=10, arrowsize=0.8, penwidth=1.2];
'''
graphs={
'01_system_architecture':'''rankdir=TB;
browser [label="Student / Organizer browser\nDjango HTML + CSS + JavaScript",fillcolor="#DDEEEF"];
repo [label="GitHub repository\nVersioned source + tests + review documents"];
subgraph cluster_host {label="PythonAnywhere web deployment"; color="#BBCDD6"; style="rounded";
 gateway [label="HTTPS / WSGI\nProduction configuration outside Git"];
 static [label="Collected static files\n/static/ → staticfiles/"];
 auth [label="Authentication + role checks\nCSRF + server validation"];
 accounts [label="accounts\nStudent identity + account controls"];
 events [label="events + registrations\nLifecycle / atomic allocation / FIFO"];
 reports [label="reports\nDerived dashboard and roster counts"];
 db [shape=cylinder,label="SQLite database\nUsers, profiles, events, registrations\nDatabase-backed sessions",fillcolor="#DDEEEF"];
 gateway -> auth; auth -> accounts; auth -> events; auth -> reports;
 accounts -> db [label="atomic writes"];
 events -> db [label="serialized allocation"];
 reports -> db [label="read queries"];
}
backup [label="Private consistent backup\nNever committed to public repository"];
restore [label="Separate restored database\nVerify before any deployment switch"];
browser -> gateway [label="HTTPS requests / responses",dir=both];
browser -> static [label="assets",dir=both];
repo -> gateway [label="pull source, collect assets, reload",style=dashed];
db -> backup [label="backup_database"];
backup -> restore [label="restore_database"];
''',
'02_use_cases':'''rankdir=TB; nodesep=0.25; ranksep=0.45;
student [shape=ellipse,label="Student",fillcolor="#DDEEEF"];
organizer [shape=ellipse,label="Organizer",fillcolor="#DDEEEF"];
subgraph cluster_shared {label="Shared access";color="#BBCDD6";
 uc1 [shape=ellipse,label="UC001\nSign in / sign out"];
 uc2 [shape=ellipse,label="UC002\nEnforce role / ownership"];
}
subgraph cluster_student {label="Student event workflows";color="#BBCDD6";
 uc5 [shape=ellipse,label="UC005\nBrowse / view event"];
 uc6 [shape=ellipse,label="UC006\nRegister / waitlist"];
 uc7 [shape=ellipse,label="UC007\nReview own history"];
 uc8 [shape=ellipse,label="UC008\nCancel / rejoin\nwith FIFO promotion"];
}
subgraph cluster_org {label="Organizer event workflows";color="#BBCDD6";
 uc3 [shape=ellipse,label="UC003\nCreate / edit event"];
 uc4 [shape=ellipse,label="UC004\nPublish draft"];
 uc9 [shape=ellipse,label="UC009\nCancel event"];
 uc10 [shape=ellipse,label="UC010\nView roster"];
 uc11 [shape=ellipse,label="UC011\nMark / correct attendance"];
 uc12 [shape=ellipse,label="UC012\nView dashboard"];
}
student -> {uc1 uc2 uc5 uc6 uc7 uc8} [dir=none];
organizer -> {uc1 uc2 uc3 uc4 uc9 uc10 uc11 uc12} [dir=none];
{rank=same;student;organizer;}
{rank=same;uc1;uc2;}
{rank=same;uc5;uc6;uc3;uc4;}
{rank=same;uc7;uc8;uc9;uc10;}
{rank=same;uc11;uc12;}
uc5 -> uc7 [style=invis]; uc6 -> uc8 [style=invis];
uc3 -> uc9 -> uc11 [style=invis]; uc4 -> uc10 -> uc12 [style=invis];
note [shape=note,label="FR001–FR018\nAccount administration continues in D08.\nThe backend enforces every permission.",fillcolor="white"];
uc12 -> note [style=invis];
''',
'03_entity_relationships':'''rankdir=TB; node [shape=record,style=filled,fontsize=12];
u [label="{auth_user|PK id\\lusername UNIQUE (Student login = ID)\\lpassword hash\\lfirst_name / last_name / email\\lis_active / is_staff / is_superuser\\l}"];
p [label="{accounts_studentprofile|PK, FK user_id → User (PROTECT)\\lstudent_number UNIQUE, max 20\\l}"];
g [label="{auth_group|PK id\\lname UNIQUE\\lStudent or Organizer business role\\l}"];
ug [label="{auth_user_groups|PK id\\lFK user_id / FK group_id\\lUNIQUE(user_id, group_id)\\l}"];
e [label="{events_event|PK id\\lFK created_by_id / cancelled_by_id\\ltitle / description / category / venue\\lstart_at / end_at / registration_closes_at\\lcapacity / status / allocation_version\\lcreated_at / updated_at\\lcancelled_at / cancellation_reason\\l}"];
r [label="{registrations_registration|PK id\\lFK event_id / student_id\\lstatus / joined_at / confirmed_at\\lcancelled_at / cancellation_source\\lattended / attendance_updated_at\\lFK attendance_updated_by_id (nullable)\\lUNIQUE(event_id, student_id)\\l}"];
s [label="{django_session|PK session_key\\lsession_data / expire_date\\lEncoded user ID; no relational User FK\\l}",fillcolor="#FFF7EA"];
{rank=same;g;ug;u;}
{rank=same;e;p;s;}
u -> p [label="1 → 0..1\nStudent requires profile"];
u -> ug [label="1 → 0..*"];
g -> ug [label="1 → 0..*"];
u -> e [label="creator 1 → 0..*\ncanceller 0..1 → 0..*\nPROTECT"];
u -> r [label="student 1 → 0..*\nattendance actor 0..1 → 0..*\nPROTECT"];
e -> r [label="1 → 0..*\nPROTECT"];
u -> s [style=dashed,label="decoded identity\nnot a database FK"];
note [shape=note,label="Role exclusivity and case-insensitive ID collisions are checked by the application.\nDeletion explicitly removes an unused profile before its User in one transaction.\nAny registration or audit reference blocks deletion; event history is never cascaded.",fillcolor="white",fontsize=11];
r -> note [style=invis];
''',
'04_registration_activity':'''rankdir=TB; nodesep=0.25; ranksep=0.35;
start [shape=oval,label="Student submits Register",fillcolor="#DDEEEF"];
auth [label="Check session, Student role and CSRF"];
tx [label="BEGIN atomic write transaction\nSerialize on event allocation write"];
valid [shape=diamond,label="Published and\nnow < closes?",fillcolor="white"];
reject [label="Reject with no change\nRollback on failure",fillcolor="#FFF1E8"];
existing [shape=diamond,label="Already Confirmed\nor Waitlisted?",fillcolor="white"];
same [label="Return existing record/status\nNo second allocation"];
space [shape=diamond,label="Seat available and\nno earlier waiter?",fillcolor="white"];
confirmed [label="Create / reuse row as Confirmed\nSet confirmation time"];
wait [label="Create / reuse row as Waitlisted\nOrder by joined_at, then id"];
rejoin [label="For a previously Cancelled row:\nnew joined_at; clear cancellation / attendance\nKeep the unique student + event record"];
commit [shape=oval,label="COMMIT and return own result",fillcolor="#DDEEEF"];
start -> auth -> tx -> valid;
valid -> reject [label="no"];
valid -> existing [label="yes"];
existing -> same [label="yes"];
same -> commit;
existing -> space [label="no"];
space -> confirmed [label="yes"];
space -> wait [label="no"];
confirmed -> rejoin; wait -> rejoin; rejoin -> commit;
note [shape=note,label="No GET mutation; one row per Student/event.\nBusy/locked database: rollback, HTTP 503\nwith Retry-After. At the closing instant,\nregistration is already closed.",fillcolor="white"];
commit -> note [style=invis];
''',
'06_event_lifecycle':'''rankdir=TB;
create [shape=oval,label="Organizer creates valid event"];
draft [label="Draft\nHidden from Student catalog\nAll fields editable before start",fillcolor="#EDF4F7"];
published [label="Published\nFuture events appear in catalog\nOnly descriptive edits before start",fillcolor="#DDEEEF"];
cancelled [label="Cancelled\nReason + actor + time retained\nAll active registrations Cancelled\nNo promotion",fillcolor="#FFF1E8"];
create -> draft [label="valid fields, capacity 1–200\nnow < closes < start < end"];
draft -> published [label="Publish\nclosing time still in future"];
draft -> cancelled [label="Cancel before start\nnonblank reason"];
published -> cancelled [label="Cancel before start\nnonblank reason"];
published -> published [label="Repeat publish: no-op"];
cancelled -> cancelled [label="Repeat cancel: no-op"];
guard [shape=note,label="Time is a guard, not a stored event state.\nAt closing: registration / student cancellation stop.\nAt start: event edits / organizer cancellation stop.\nAt or after start: attendance may be marked or cleared\nfor Confirmed participants of a non-Cancelled event.\nPast Published events remain Published; there is no Completed state.",fillcolor="white"];
published -> guard [style=dashed,arrowhead=none];
''',
'08_account_use_cases':'''rankdir=LR;
org [shape=ellipse,label="Organizer",fillcolor="#DDEEEF"];
student [shape=ellipse,label="Student",fillcolor="#DDEEEF"];
subgraph cluster_admin {label="Manage users · eligible Student targets only";color="#BBCDD6";
u13 [shape=ellipse,label="UC013 · FR019\nSearch / browse students"];
u14 [shape=ellipse,label="UC014 · FR020 / FR023\nEdit details + Student ID login"];
u15 [shape=ellipse,label="UC015 · FR021\nReset password"];
u16 [shape=ellipse,label="UC016 · FR022 / FR023\nCreate Student"];
u17 [shape=ellipse,label="UC017 · FR024\nDeactivate / reactivate"];
u18 [shape=ellipse,label="UC018 · FR025\nDelete unused Student"];
}
login [shape=ellipse,label="UC001 · FR001 / FR023\nSign in with saved Student ID"];
org -> {u13 u14 u15 u16 u17 u18} [dir=none];
student -> login [dir=none];
u14 -> login [style=dashed,label="sets login ID",constraint=false];
u16 -> login [style=dashed,label="creates ID login",constraint=false];
note [shape=note,label="Organizer / staff / superuser / mixed-role accounts are excluded.\nStudent controls cannot grant roles or privileges.\nOrganizer/master login is unchanged.",fillcolor="white"];
u18 -> note [style=invis];
''',
'09_account_lifecycle':'''rankdir=TB;
org [label="Organizer-only eligible Student target\nSingle Student role + profile; no staff/superuser",fillcolor="#DDEEEF"];
active [label="Active\nFresh login allowed",fillcolor="#DDEEEF"];
inactive [label="Inactive\nLogin denied",fillcolor="#FFF7EA"];
check [shape=diamond,label="Exact typed ID and\nno registration or\naudit references?",fillcolor="white"];
blocked [label="Deletion blocked\nKeep account + all records",fillcolor="#FFF1E8"];
deleted [label="Deleted (record removed)\nUser + profile + membership + sessions\ncommitted in one transaction",fillcolor="#EDF4F7"];
org -> active [label="Create Student"];
active -> inactive [label="Confirm Deactivate\nexpire stored sessions"];
inactive -> active [label="Confirm Reactivate\nexpire stored sessions; fresh login"];
active -> check [label="Review deletion → confirmed POST"];
inactive -> check [label="Review deletion → confirmed POST"];
check -> blocked [label="no"];
check -> deleted [label="yes; rechecked in transaction"];
note [shape=note,label="GET only displays confirmation. Repeating the current active state is a no-op.\nDeactivation preserves identity, password, reserved places, waitlist eligibility and attendance.\nAny registration status, past record or event/attendance audit link blocks deletion.\nProtected master accounts are outside this state machine.",fillcolor="white"];
deleted -> note [style=invis];
'''}

def build_graphs():
    for name,body in graphs.items():
        if name=='03_entity_relationships':
            def html_record(m):
                fields=[html.escape(x) for x in m.group(3).split('\\l') if x]
                return m.group(1)+' [shape=plain,style="",label=<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6" COLOR="#8EA8B7" BGCOLOR="#EDF4F7"><TR><TD><B>'+html.escape(m.group(2))+'</B></TD></TR><TR><TD ALIGN="LEFT">'+'<BR ALIGN="LEFT"/>'.join(fields)+'<BR ALIGN="LEFT"/></TD></TR></TABLE>>];'
            body=re.sub(r'(\w+) \[label="\{([^|]+)\|([^"]*)\}"(?:,[^\]]+)?\];',html_record,body)
        dot=SRC/(name+'.dot');dot.write_text(BASE+body+'}\n')
        subprocess.run(['dot','-Tpng','-Gdpi=160',str(dot),'-o',str(OUT/(name+'.png'))],check=True)
        subprocess.run(['dot','-Tsvg',str(dot),'-o',str(OUT/(name+'.svg'))],check=True)

def sequence(name,actors,events,notes):
    fig,ax=plt.subplots(figsize=(12,7.2));fig.patch.set_facecolor('white')
    xs=[.09,.36,.64,.91]; ytop=.91; step=.072
    for x,a in zip(xs,actors):
        ax.text(x,ytop,a,ha='center',va='center',fontsize=12,color=NAVY,bbox=dict(boxstyle='round,pad=.65',fc=PALE,ec='#A6BCC8'))
        ax.plot([x,x],[.17,ytop-.04],color='#A6BCC8',lw=1,ls=(0,(3,3)),zorder=0)
    for i,(a,b,text) in enumerate(events):
        y=.80-i*step
        if a==b:
            ax.text(xs[a]+.025,y,text,ha='left',va='center',fontsize=10,color=NAVY,bbox=dict(fc='white',ec='none',pad=2))
        else:
            ax.annotate('',xy=(xs[b],y),xytext=(xs[a],y),arrowprops=dict(arrowstyle='->',color=TEAL,lw=1.6))
            ax.text((xs[a]+xs[b])/2,y+.014,text,ha='center',va='bottom',fontsize=10,color=NAVY,bbox=dict(fc='white',ec='none',pad=1))
    ax.text(.02,.08,notes,ha='left',va='center',fontsize=10.5,color=GREY,linespacing=1.6)
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');fig.tight_layout(pad=.6)
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig)

def build_sequences():
    sequence('05_cancellation_sequence',['Student browser','View / permission checks','Cancellation service','SQLite'],[
        (0,1,'POST cancel + session + CSRF'),(1,2,'Student role; owned registration'),
        (2,3,'BEGIN atomic; serialize event write'),(3,2,'Current record, state and closing time'),
        (2,3,'If active and before closing: set Cancelled'),
        (2,3,'If formerly Confirmed: select first Waitlisted'),
        (3,2,'Oldest joined_at; registration id breaks ties'),
        (2,3,'Promote selected row, then COMMIT'),(2,0,'Return only requester’s result; refresh view')],
        'Repeated cancellation: no further allocation change. Waitlisted cancellation: no promotion.\nAny failure rolls back cancellation and promotion together. Busy database returns a retryable error.')
    sequence('10_student_identity_sequence',['Organizer browser','Account view / form','Atomic service','User / Profile / Group'],[
        (0,1,'POST create or edit + session + CSRF'),(1,2,'Check Organizer and eligible target'),
        (2,3,'BEGIN; validate ID / case-insensitive collisions'),
        (2,3,'CREATE: active User + Student membership + profile'),
        (2,3,'EDIT: same User id; username = profile Student ID'),
        (3,2,'Save both records; COMMIT'),(2,0,'Redirect with result; show saved login ID')],
        'Create and edit are alternative paths. Invalid input or failed profile write rolls back all changes.\nEdit preserves password, role, active state and registration/attendance history. ID-only edits retain sessions.\nPassword reset is a separate UC015 action: validate two entries, hash password, invalidate old student sessions.')

def build_core_use_cases():
    """Two actor panels keep all twelve use cases legible on one printed page."""
    fig,ax=plt.subplots(figsize=(12,7.5));fig.patch.set_facecolor('white')
    panels=[(.02,'Student',[
        ('UC001','Sign in / sign out'),('UC002','Role / ownership checks'),
        ('UC005','Browse / view event'),('UC006','Register / waitlist'),
        ('UC007','Review own history'),('UC008','Cancel / rejoin + FIFO')]),
        (.51,'Organizer',[
        ('UC001','Sign in / sign out'),('UC002','Role / ownership checks'),
        ('UC003','Create / edit event'),('UC004','Publish draft'),
        ('UC009','Cancel event'),('UC010','View participant roster'),
        ('UC011','Mark / correct attendance'),('UC012','View dashboard')])]
    for left,actor,cases in panels:
        mid=left+.235
        ax.add_patch(Rectangle((left,.08),.47,.88,fill=False,edgecolor='#BBCDD6',linewidth=1.2))
        ax.text(mid,.925,actor,ha='center',fontsize=15,fontweight='bold',color=NAVY)
        ax.add_patch(Circle((mid,.875),.012,fill=False,edgecolor=NAVY,lw=1.4))
        ax.plot([mid,mid],[.86,.817],color=NAVY,lw=1.4)
        ax.plot([mid-.025,mid+.025],[.845,.845],color=NAVY,lw=1.4)
        ax.plot([mid-.022,mid,mid+.022],[.793,.817,.793],color=NAVY,lw=1.4)
        bottom=.68-.165*((len(cases)-1)//2)
        ax.plot([mid,mid],[.79,bottom],color='#8EA8B7',lw=1.2)
        for i,(uid,title) in enumerate(cases):
            x=left+(.12 if i%2==0 else .35); y=.68-.165*(i//2)
            edge=x+(.103 if i%2==0 else -.103)
            ax.plot([mid,edge],[y,y],color='#8EA8B7',lw=1.2)
            ax.add_patch(Ellipse((x,y),.208,.115,facecolor=PALE,edgecolor='#8EA8B7',lw=1.1))
            label=uid+'\n'+'\n'.join(textwrap.wrap(title,23))
            ax.text(x,y,label,ha='center',va='center',fontsize=11.5,color=NAVY,linespacing=1.35)
    ax.text(.025,.035,'UC001 and UC002 are shown in both actor panels; they refer to the same shared behaviors.\nStudent account administration is expanded in D08. All permissions are enforced by the backend.',fontsize=10.5,color=GREY,va='center')
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');fig.tight_layout(pad=.7)
    for ext in ['png','svg']:fig.savefig(OUT/('02_use_cases.'+ext),dpi=180,bbox_inches='tight')
    plt.close(fig)

def build_gantt():
    fig,ax=plt.subplots(figsize=(12,6.9));fig.patch.set_facecolor('white')
    start=datetime.datetime(2026,10,30)
    labels=['Foundation and data model','Event management','Registration and waitlist','Organizer tools','Integration and deployment','Verification and defect fixes','Demonstration preparation']
    starts=[0,7,14,21,28,35,42];lengths=[7,7,7,7,7,7,6]
    for i,(lab,off,duration) in enumerate(zip(labels,starts,lengths)):
        ax.barh(i,duration,left=mdates.date2num(start+datetime.timedelta(days=off)),height=.45,color='#4C7894' if i<4 else TEAL)
    now=datetime.datetime(2026,11,18);exam=datetime.datetime(2026,12,17)
    ax.axvline(now,color=GOLD,lw=1.8,ls='--');ax.text(mdates.date2num(now)+.5,-.7,'18 Nov review',color=GOLD,fontsize=10)
    ax.axvline(exam,color=NAVY,lw=1.2,ls=':')
    ax.set_yticks(range(7),labels,fontsize=11,color=NAVY);ax.invert_yaxis()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.FR));ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.set_xlim(start-datetime.timedelta(days=1),exam+datetime.timedelta(days=1));ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
    for spine in ax.spines.values():spine.set_visible(False)
    ax.tick_params(length=0);ax.set_title('Original implementation plan • 30 October–17 December 2026',loc='left',fontsize=15,color=NAVY,pad=25)
    fig.subplots_adjust(left=.27,right=.97,top=.86,bottom=.27)
    fig.text(.035,.16,'Recorded by 18 November: live core app, account update deployed (team report), 110 Linux tests passed.',fontsize=11,color=NAVY)
    fig.text(.035,.11,'Still open: five NFR acceptance evidence items, professor evaluation, final presentation and submission report.',fontsize=11,color=GREY)
    fig.text(.035,.055,'Bars are the submitted plan, not actual effort or completion dates. Baseline submitted 29 October; final exam 17 December.',fontsize=10,color=GREY)
    fig.savefig(OUT/'07_project_gantt.png',dpi=180);fig.savefig(OUT/'07_project_gantt.svg');plt.close(fig)

def lines(c,text,x,y,width=100,size=10,leading=14):
    c.setFont('Helvetica',size)
    for line in textwrap.wrap(text,width):c.drawString(x,y,line);y-=leading
    return y

def build_pdf():
    c=canvas.Canvas(str(OUT/'System_Diagrams.pdf'),pagesize=(612,792))
    c.setTitle('Campus Events — System Diagrams, revision 2.0');c.setAuthor('Alam Shahriya; Hossain Md Miraj')
    c.setFillColor(HexColor(NAVY));c.setFont('Helvetica-Bold',26);c.drawString(42,732,'System diagrams')
    c.setFont('Helvetica',13);c.drawString(42,704,'Campus Event Registration and Waitlist Management System')
    c.setFillColor(HexColor(GREY));c.setFont('Helvetica',10);c.drawString(42,680,'Revision 2.0 | 18 November 2026 | source b3d900f')
    y=638
    for i,d in enumerate(DATA['diagrams'],2):
        c.setFillColor(HexColor(NAVY));c.setFont('Helvetica-Bold',12);c.drawString(42,y,f"{d['id']}  {d['title']}");c.drawRightString(570,y,str(i))
        c.setFillColor(HexColor(GREY));y=lines(c,d['scope'],42,y-18,91,9.5,13)-17
    lines(c,'Traceability: each requirement row in RTM.xlsx and requirements.json names its diagram IDs. D07 records the schedule and is not counted as a requirement.',42,111,95,10,14)
    c.setFont('Helvetica',9);c.drawString(42,44,'Editable DOT/Python and SVG/PNG files are included with this package.');c.drawRightString(570,44,'1 / 11');c.showPage()
    for page,d in enumerate(DATA['diagrams'],2):
        img=ImageReader(str(OUT/(d['file']+'.png')));iw,ih=img.getSize()
        pw,ph=(612,792) if d['id']=='D04' or ih/iw>1.1 else (842,595)
        c.setPageSize((pw,ph));c.setFillColor(HexColor(NAVY));c.setFont('Helvetica-Bold',19);c.drawString(32,ph-36,f"{d['id']}  {d['title']}")
        c.setFillColor(HexColor(GREY));lines(c,d['scope'],32,ph-57,132 if pw>700 else 94,9,12)
        reqids=[r['Req. ID'] for r in DATA['requirements'] if d['id'] in r['Diagram IDs'].split(', ')]
        footer='Requirements: '+(', '.join(reqids) if reqids else 'Project schedule only; no completion credit')
        lines(c,footer,32,51,140 if pw>700 else 90,8,11)
        scale=min((pw-64)/iw,(ph-150)/ih)
        c.drawImage(img,(pw-iw*scale)/2,88+(ph-150-ih*scale)/2,iw*scale,ih*scale,mask='auto')
        c.setFont('Helvetica',8);c.drawString(32,22,'Revision 2.0 • 18 November 2026 • source b3d900f');c.drawRightString(pw-32,22,f'{page} / 11');c.showPage()
    c.save()

if __name__=='__main__':
    build_graphs();build_core_use_cases();build_sequences();build_gantt();build_pdf()
    print('Built 10 diagrams (PNG/SVG), editable sources and 11-page System_Diagrams.pdf')
