"""Generate the current SRS and an evidence-based completion report from requirements.json."""
from pathlib import Path
import json, math
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START, WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
DATA=json.loads((ROOT/'docs/review/requirements.json').read_text())
REQ=DATA['requirements']; NAVY='19384B';TEAL='167C80';GREY='5F7280'

def shade(cell,color):
    pr=cell._tc.get_or_add_tcPr();e=OxmlElement('w:shd');e.set(qn('w:fill'),color);pr.append(e)

class Book:
    def __init__(self,title):
        self.doc=Document();self.page=1;self.outline=[];self.landscape=False
        sec=self.doc.sections[0]
        sec.page_width=Inches(8.5);sec.page_height=Inches(11)
        sec.top_margin=Inches(.68);sec.bottom_margin=Inches(.65);sec.left_margin=sec.right_margin=Inches(.7)
        sec.header_distance=sec.footer_distance=Inches(.3)
        normal=self.doc.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(11)
        normal.font.color.rgb=RGBColor.from_string(NAVY)
        normal.paragraph_format.space_after=Pt(6);normal.paragraph_format.line_spacing=1.08
        for n,size,col in [('Title',27,NAVY),('Heading 1',19,NAVY),('Heading 2',13,TEAL),('Heading 3',11,NAVY)]:
            st=self.doc.styles[n];st.font.name='Calibri';st.font.size=Pt(size);st.font.color.rgb=RGBColor.from_string(col)
            st.paragraph_format.space_before=Pt(10);st.paragraph_format.space_after=Pt(7)
        hp=sec.header.paragraphs[0];hp.text='CAMPUS EVENTS  /  '+title.upper();hp.style='Caption'
        for r in hp.runs:r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREY)
        fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        fp.add_run('Revision 2.0  |  18 November 2026  |  ')
        fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');fp._p.append(fld)
        for r in fp.runs:r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string(GREY)
        self.doc.core_properties.author='Alam Shahriya; Hossain Md Miraj'
        self.doc.core_properties.title=title+' — Campus Event Registration and Waitlist Management System'
        self.doc.core_properties.subject='Current requirements, traceability and evidence against source b3d900f'
    def p(self,text='',style=None,bold=False):
        p=self.doc.add_paragraph(style=style);r=p.add_run(text);r.bold=bold
        return p
    def h(self,text,level=2):return self.doc.add_heading(text,level)
    def new(self,title,include=False,landscape=False):
        if landscape!=self.landscape:
            sec=self.doc.add_section(WD_SECTION_START.NEW_PAGE)
            sec.orientation=WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
            sec.page_width=Inches(11 if landscape else 8.5);sec.page_height=Inches(8.5 if landscape else 11)
            self.landscape=landscape
        else:self.doc.add_page_break()
        self.page+=1;self.h(title,1)
        if include:self.outline.append((title,self.page))
    def table(self,headers,rows,widths=None,size=9.5):
        t=self.doc.add_table(rows=1,cols=len(headers));t.autofit=False
        if widths:
            for col,w in zip(t.columns,widths):col.width=Inches(w)
        for c,txt in zip(t.rows[0].cells,headers):
            c.text=txt;shade(c,NAVY)
            for r in c.paragraphs[0].runs:r.bold=True;r.font.color.rgb=RGBColor(255,255,255)
        trPr=t.rows[0]._tr.get_or_add_trPr();rep=OxmlElement('w:tblHeader');trPr.append(rep)
        for n,row in enumerate(rows):
            cells=t.add_row().cells
            for c,txt in zip(cells,row):
                c.text=str(txt)
                if n%2==0:shade(c,'EDF4F7')
        for row in t.rows:
            trPr=row._tr.get_or_add_trPr();cant=OxmlElement('w:cantSplit');trPr.append(cant)
            for i,c in enumerate(row.cells):
                if widths:c.width=Inches(widths[i])
                for p in c.paragraphs:
                    p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4);p.paragraph_format.line_spacing=1
                    for r in p.runs:r.font.name='Calibri';r.font.size=Pt(size)
        self.p().paragraph_format.space_after=Pt(1)
        return t
    def image(self,file,maxh=5.9,width=7.0):
        pth=ROOT/'docs/diagrams'/file
        with Image.open(pth) as im:w,h=im.size
        wi=min(width,maxh*w/h)
        p=self.doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(pth),width=Inches(wi))
    def save(self,path):self.doc.save(str(path))

def requirement(b,r):
    b.h(f"{r['SRS Section']}  {r['Req. ID']} — {r['Title']}",2)
    p=b.p(f"{r['Priority']} priority  |  {r['Use Case ID']}  |  {r['Test Case ID']}  |  {r['Status']}")
    for run in p.runs:run.font.size=Pt(9);run.font.color.rgb=RGBColor.from_string(GREY)
    b.p(r['Requirement Description'])
    p=b.p();p.add_run('Acceptance: ').bold=True;p.add_run(r['Acceptance Criteria'])
    p=b.p(f"Model: {r['Diagram IDs']}   •   Evidence: {r['Evidence IDs']}")
    for run in p.runs:run.font.size=Pt(9);run.font.color.rgb=RGBColor.from_string(GREY)

def build_srs():
    b=Book('Software Requirements Specification')
    b.p('SOFTWARE DESIGN PART 2',bold=True);b.p()
    b.p('Software Requirements\nSpecification',style='Title')
    b.h('Campus Event Registration\nand Waitlist Management System',1)
    b.p('Django web application • SQLite • Online deployment')
    b.p('Revision 2.0\nReview date: 18 November 2026\nOriginal submission: 29 October 2026')
    b.h('Prepared by')
    b.p('Alam Shahriya — Student ID 2677517\nHossain Md Miraj — Student ID 2677529')
    b.h('Organization')
    b.p('Dongshin University\nGraduate School of Software Convergence\nCourse: Software Design Part 2')
    b.h('Current review scope')
    b.p('25 functional requirements and 7 non-functional requirements. Includes student creation, Student ID login, editing, password resets, deactivation/reactivation and protected deletion.')
    b.p('Application source: b3d900f4ac7c516c086708305f53ebfdebd0422d')
    b.p('This revision documents the current application and its evidence. Professor acceptance, the final presentation and the final submission report are separate milestones.')
    b.new('Document control and contents')
    b.table(['Version','Date','Change'],[
        ['1.0','29 Oct 2026','Submitted baseline: FR001–FR018 and NFR001–NFR007; retained unchanged under docs/archive/.'],
        ['2.0','18 Nov 2026','Integrates FR019–FR025, revises ID editing and account controls, updates diagrams/RTM, and records current evidence.']],[.6,1.05,5.45])
    b.p('The original requirement IDs remain stable. Existing FR020 is clarified by FR023: saving a Student’s details now synchronizes username to Student ID. FR025 permits removal only when no event or audit history references the student.')
    toc=b.table(['Section','Page'],[['1  Introduction','3'],['2  Overall description','4'],['2.4 / 3.1  Environment and interfaces','5'],['3.2  Functional requirements','6–14'],['3.3  Non-functional requirements','15–17'],['4  Data definitions, states and APIs','18–21'],['5  System models and use cases','22–25'],['6  Traceability summary','26–27'],['7  Appendices and references','28']],[6.3,.8])
    b.p('Companion files: RTM.xlsx / RTM.csv; System_Diagrams.pdf; COMPLETION_REPORT.pdf; requirements.json; TESTCASE_INDEX.md. The same requirement IDs and evidence register are used throughout.')
    b.new('1  Introduction',True)
    b.h('1.1  Purpose')
    b.p('This specification defines the implemented campus event system, its current acceptance criteria and the boundaries of the supporting evidence. It enables the course instructor to trace a requirement to its use case, data model, code and tests.')
    b.h('1.2  Scope')
    b.p('Students authenticate, browse published events, reserve available places or join a waitlist, inspect their own history, and cancel or rejoin before registration closes. Organizers create and manage events, review rosters, record attendance, inspect totals and administer Student accounts.')
    b.p('The current account extension allows Organizers to create more students, use Student IDs as login names, edit details, reset passwords, deactivate/reactivate accounts and delete unused accounts. Existing records survive identity and access changes. Accounts with history cannot be permanently removed through these controls.')
    b.p('Public self-registration, bulk CSV import, automatic sequential ID assignment, email notifications, payments, calendar synchronization, role administration and a native mobile app are outside scope. The mobile experience is the responsive website. There is no separate Django admin interface in the configured URL routes.')
    b.h('1.3  Definitions')
    b.table(['Term','Meaning'],[
        ['Student ID','Textual institutional identifier stored in StudentProfile; it becomes the username on creation or Organizer save.'],['Internal user ID','Stable database primary key. It does not change when the displayed name or login ID changes.'],['Active account','User.is_active is true; this permits authentication subject to role/profile checks.'],['Active registration','A Confirmed or Waitlisted row. This is distinct from the account’s active flag.'],['FIFO','First-in, first-out queue ordered by joined_at, then registration ID.'],['RTM / SRS','Requirements Traceability Matrix / Software Requirements Specification.'],['KST','Asia/Seoul display timezone; stored datetimes are timezone-aware UTC.']],[1.3,5.8])
    b.h('1.4  References and document authority')
    b.p('The source commit, saved test output and team deployment evidence are listed in the separate completion report (E01–E09). Technical references are in section 7. The revised SRS and RTM replace the main review copies; the original submitted baseline remains available for comparison.')
    b.new('2  Overall description',True)
    b.h('2.1  Product perspective and functions')
    b.p('A same-origin Django application serves HTML pages and JSON APIs over HTTPS. SQLite stores accounts, profiles, events, registrations and sessions. Backend services decide permissions, allocation, deadlines and state transitions; browser code does not decide capacity or authorization. D01 shows the module/deployment boundary.')
    b.h('2.2  User classes and access')
    b.table(['Capability','Student','Organizer'],[
        ['Sign in and sign out','Yes, if active and valid Student profile','Yes, if active and valid Organizer role'],['Browse event catalog / details','Future Published catalog; own historical cancellation details','All events for management'],['Register / cancel own registration','Before registration closes','No Student allocation as Organizer'],['View personal history','Own records only','Rosters and reporting instead'],['Create, edit, publish, cancel event','No','All campus events, subject to time/state rules'],['Participant identities / attendance / dashboard','No','Yes'],['Student account administration','No','Eligible Student targets only'],['Edit Organizer/staff/superuser accounts','No','Not through Student management']],[3.15,1.9,2.05])
    b.h('2.3  Account boundaries')
    b.p('A signed-in account must have exactly one business role, Student or Organizer. Student accounts need a StudentProfile. The management list excludes Organizers, staff, superusers, mixed-role accounts and users without a Student profile. Master-account protection uses role and privilege checks rather than a hard-coded username.')
    b.p('An Organizer supplies each new Student’s ID and initial password. The system creates only the Student role and grants no staff/superuser privileges. There is no four-student limit; list pages contain 25 accounts and tests cover adding 30 students. The examples used for testing are not an enrollment policy or a maximum.')
    b.p('The Organizer login can remain “organizer”. A Student example such as “26677-507” is treated as text. Saving an existing student’s details can change a legacy login such as “student1”; installing the software alone changes no account.')
    b.new('2.4 / 3.1  Environment and interfaces',True)
    b.h('2.4  Operating environment')
    b.table(['Layer','Current implementation'],[
        ['Backend','Python 3.12; Django 5.2.19; pinned requirements.txt.'],['Frontend','Django templates, bundled Bootstrap 5.3.8, CSS and JavaScript; desktop and mobile browsers.'],['Persistence','SQLite with migrations, uniqueness/check constraints, IMMEDIATE write transactions and database-backed Django sessions.'],['Local development','Windows Command Prompt / virtual environment; Linux automated checks.'],['Hosting','PythonAnywhere provider subdomain; Python 3.12.8 observed on host; HTTPS and WSGI.'],['Source and deployment','GitHub repository; pull source, collect static files and reload WSGI after code changes.'],['Configuration','Private environment settings: secret key, DEBUG=False, exact allowed host and HTTPS CSRF origin. No secrets in this document.']],[1.5,5.6])
    b.h('2.5  Constraints and dependencies')
    b.p('Event capacity is 1–200. Student IDs are 1–20 ASCII characters, beginning with a letter/digit and otherwise allowing letters, digits, hyphens and underscores. IDs preserve leading zeros. ID/login uniqueness is checked case-insensitively across all accounts. Passwords use Django validators, including a 10-character minimum.')
    b.p('SQLite serializes writes; a busy database returns a retryable response. Availability depends on the hosting account and its renewal status. The expiry shown earlier was 18 December 2026 and must be checked again before evaluation. Session-removal logic assumes the configured database session backend.')
    b.h('3.1  User and software interfaces')
    b.p('Student navigation offers Discover and My registrations. Organizer navigation offers Overview, Manage events and Manage users. Account forms use normal CSRF-protected POST submissions and work without JavaScript. Event actions use same-origin JSON APIs; all mutations require authorization and CSRF protection.')
    b.p('Forms display validation errors and preserve safe non-secret input. Passwords are never redisplayed. Dangerous account actions have separate confirmation pages. Dates are labeled KST. Account pages are sent with no-store cache headers.')
    b.h('Verification terminology used below')
    b.p(DATA['counting_rule'])
    chunks=[(0,3),(3,6),(6,9),(9,12),(12,15),(15,18),(18,21),(21,23),(23,25)]
    for a,z in chunks:
        b.new(f'3.2  Functional requirements — {REQ[a]["Req. ID"]}–{REQ[z-1]["Req. ID"]}')
        for r in REQ[a:z]:requirement(b,r)
        if a==23:
            b.h('Account action safeguards',3)
            b.p('Confirmation pages do not mutate on GET. Unexpected role/privilege fields are rejected. A stale deletion review is rechecked on POST, so a newly linked registration or changed target role blocks removal. These actions add no schema migration and do not alter historical event rows.')
    for a,z in [(25,27),(27,29),(29,32)]:
        b.new(f'3.3  Non-functional requirements — {REQ[a]["Req. ID"]}–{REQ[z-1]["Req. ID"]}')
        for r in REQ[a:z]:
            requirement(b,r)
            p=b.p();p.add_run('Evidence / remaining: ').bold=True;p.add_run(r['Verification']+' '+r['Remaining Acceptance'])
            for run in p.runs:run.font.size=Pt(10)
    b.new('4  Data definitions — identity and sessions',True)
    b.h('4.1  Identity model')
    b.table(['Entity / field','Definition and constraints'],[
        ['auth_user.id','Internal primary key; referenced by profile, registration and audit relations.'],['auth_user.username','Unique login string; new/updated Student username equals saved Student ID. Organizer names remain unchanged.'],['auth_user.password','Django password hash; no cleartext password column.'],['first_name / last_name','Django name fields (150 characters each). Student management requires first name; last name is optional.'],['email','Optional email, max 254 characters; form validation applies.'],['is_active / is_staff / is_superuser','Authentication and privilege flags. Student forms do not grant privileged flags.'],['StudentProfile.user_id','One-to-one primary/foreign key to User with PROTECT. A Student account must have one profile.'],['StudentProfile.student_number','Unique string, max 20; current UI format/collision rules apply.'],['auth_group / auth_user_groups','Django groups and membership table. Exactly one business role is enforced by the application; the database relationship itself is many-to-many.'],['django_session','session_key primary key, encoded session_data and expire_date; authenticated user ID is encoded data, not a relational foreign key.']],[2.1,5])
    b.h('4.2  Identity-preserving updates')
    b.p('Student creation commits User, Student membership and profile together. Student editing commits the username and profile ID together, preserving the user primary key, password, role, active state and all related registrations. Existing sessions remain valid for an ID-only change because the same account and password hash remain.')
    b.p('Password reset changes the hash, invalidating previous authenticated student sessions. Deactivation and reactivation remove that student’s unexpired database sessions within the same transaction. Other users’ sessions remain. A repeated request for the current active state makes no transition and does not expire a fresh session.')
    b.h('4.3  Deletion policy')
    b.p('Any registration, including Cancelled or past records, or any event/attendance audit reference blocks deletion. An unused Student profile is explicitly removed before its User within one transaction; the PROTECT relation is not changed to cascade. Protected errors and write failures roll back profile, account and session changes. A deleted account has no in-app undo; recovery uses a private verified backup.')
    b.new('4  Data definitions — events and registrations')
    b.table(['Event field(s)','Definition'],[
        ['id','Event primary key.'],['title / description','Required text; maximum 120 / 2,000 characters.'],['category / venue','Required text; maximum 60 / 120 characters.'],['start_at / end_at / registration_closes_at','Timezone-aware datetimes; closes < start < end. Creation/publication also require closes in the future.'],['capacity / status','Integer 1–200; Draft, Published or Cancelled only.'],['created_by / created_at / updated_at','Creator FK protected from deletion; creation and update timestamps.'],['cancelled_by / cancelled_at / cancellation_reason','Nullable protected actor FK/time; nonblank reason of 1–500 characters for cancellation.'],['allocation_version','Internal incrementing field used as the first event write to serialize allocation-related operations.']],[2.65,4.45],9.5)
    b.table(['Registration field(s)','Definition'],[
        ['id / event / student','Primary key and protected foreign keys. UNIQUE(event, student) permits at most one row for the pair.'],['status','Confirmed, Waitlisted or Cancelled only.'],['joined_at','Queue timestamp; refreshed on rejoin. Queue ties use registration ID.'],['confirmed_at / cancelled_at','Nullable lifecycle timestamps.'],['cancellation_source','Nullable Student or Event value.'],['attended','Boolean. Database constraint permits attended=True only for Confirmed rows.'],['attendance_updated_by / attendance_updated_at','Nullable protected actor FK and time of the latest attendance change.']],[2.65,4.45],9.5)
    b.h('Derived values and relationships')
    b.p('Remaining seats, confirmed totals, waitlist ranks and attendance totals are calculated from saved rows. They are not client-submitted counts. Each Event has zero or more registrations; each registration belongs to one Event and one User. D03 shows cardinalities and audit references. No separate Waitlist table is required.')
    b.new('4  States, deadlines and atomic behavior')
    b.h('4.4  Event and registration rules')
    b.table(['Rule','Required behavior'],[
        ['Draft → Published','Organizer publishes valid data while closing time is in the future. Repeat publication returns the same Published event.'],['Draft / Published → Cancelled','Organizer cancels before start with a reason; all active registrations become Cancelled together, without promotion.'],['Time-based event restrictions','Closing and event start are time guards, not extra stored states. Past Published events remain Published; no Completed state exists.'],['Register','Before closing and only for Published events. Allocate a free seat only if no earlier waiter is entitled to it; otherwise Waitlisted.'],['Repeated register','Return the existing Confirmed or Waitlisted row; allocate no second place.'],['Student cancellation','Owned record, before closing. Confirmed cancellation promotes the oldest Waitlisted row in the same transaction.'],['Rejoin','Reuse the Cancelled row; reset queue timestamp and cancellation/attendance fields. Old priority is lost.'],['Attendance','At or after start, Confirmed participants of non-Cancelled events only. Corrections store the latest actor/time.'],['Inactive Student','Cannot log in; saved places and Waitlisted entries remain. Deactivation does not free capacity and does not remove promotion eligibility.']],[1.7,5.4])
    b.h('4.5  Transaction boundaries')
    b.p('Allocation, registration cancellation/promotion, event cancellation and account writes use atomic transactions. SQLite IMMEDIATE transactions serialize writers; event operations first increment allocation_version rather than assuming SQLite provides row-level locks. Failed writes roll back the related changes. Lock/busy errors become HTTP 503 with Retry-After; the browser may retry without creating duplicate allocations.')
    b.p('The backend reads current state and server time during the transaction. It rechecks account eligibility and deletion blockers at submission. Validation and permissions apply even when a caller bypasses the normal page controls.')
    b.new('4  Route and API summary')
    b.table(['Route','Methods / access / purpose'],[
        ['/accounts/login/ ; /accounts/logout/','Login GET/POST; logout POST. Student or Organizer session.'],['/events/ ; /events/<id>/','GET catalog/details with role-based visibility.'],['/events/new/ ; /events/<id>/edit/','Organizer editor pages.'],['/my-registrations/','Student’s own history.'],['/events/<id>/participants/ ; /organizer/','Organizer roster and dashboard.'],['/organizer/users/','Organizer list/search; GET/HEAD.'],['/organizer/users/new/','Organizer creation; GET review / POST write.'],['/organizer/users/<id>/{edit,password}/','Organizer detail edit or password reset; GET/POST.'],['/organizer/users/<id>/{deactivate,reactivate,delete}/','Organizer confirmations; GET/POST. Separate routes, not a toggle.'],['/api/events/ ; /api/events/<id>/','GET list/detail; Organizer POST create and PATCH edit.'],['/api/events/<id>/{publish,cancel}/','Organizer POST; event lifecycle.'],['/api/events/<id>/register/','Student POST; Confirmed/Waitlisted allocation.'],['/api/my-registrations/','Student GET own rows.'],['/api/registrations/<id>/cancel/','Student POST own cancellation.'],['/api/events/<id>/participants/','Organizer GET roster.'],['/api/registrations/<id>/attendance/','Organizer PATCH mark/clear attendance.'],['/api/reports/dashboard/','Organizer GET summary.']],[3.95,3.15],9.3)
    b.p('Braced actions above abbreviate separate routes. Account administration uses HTML forms, not new JSON endpoints. See docs/development/API.md and config/urls.py for the complete contract.')
    b.p('Anonymous protected HTML requests redirect to login; APIs return 401. Wrong roles return 403; missing or protected account targets return 404. Invalid account input returns 400; linked-record/integrity conflicts return 409; busy writes return 503. Unsupported methods are rejected and GET never changes business data.')
    b.new('5  System models — diagram register',True)
    b.table(['ID','Model','Related scope'],[[d['id'],d['title'],d['scope']] for d in DATA['diagrams']],[.5,2.2,4.4],9.2)
    b.p('The complete figures are printed at readable size in System_Diagrams.pdf. PNG/SVG copies and editable DOT/Python sources are included. Every requirement lists its relevant model IDs; D07 is a planning artifact and receives no requirement-completion credit.')
    b.h('D01  Architecture relationships')
    b.table(['Connection','Purpose'],[
        ['Browser → HTTPS / WSGI','Deliver protected HTML and JSON responses; static assets use the collected static directory.'],
        ['Role checks → account/event services','Enforce authorization before identity, allocation, lifecycle or attendance changes.'],
        ['Services → SQLite','Commit related writes atomically; derive counts from persisted registrations.'],
        ['GitHub → deployment','Pull versioned source, collect assets and reload WSGI for application updates.'],
        ['SQLite → private backup → separate restore','Recover and compare data without overwriting a running database.']],[2.3,4.8],9.5)
    b.new('5  System models — entity relationships',landscape=True)
    b.image('03_entity_relationships.png',maxh=5.4,width=9.4)
    b.p('D03 corresponds to section 4 and the Django models. Arrow labels state parent-to-child cardinality. Nullable audit actors are shown separately from mandatory student/creator relationships. Dashed session linkage is logical, not a database foreign key. Full field definitions and deletion guards are in section 4.')
    b.new('5  System models — use-case catalog')
    uc_table=b.table(['ID / actor','Use case','Requirement IDs'],[[u['id']+'\n'+u['actor'],u['title'],u['requirements']] for u in DATA['use_cases']],[1.15,3.6,2.35],9.5)
    for row in uc_table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:p.paragraph_format.space_before=Pt(2);p.paragraph_format.space_after=Pt(2)
    b.p('UC001–UC012 retain their baseline IDs. UC013–UC018 add account administration. FR023 applies to login, creation and editing rather than creating a duplicate login use case. FR018 supplies common backend validation across UC003–UC018; NFRs apply across the relevant flows.')
    b.p('Preconditions: all protected flows require a valid active role. Organizer account mutations additionally require an eligible Student target; action-specific guards appear in FR019–FR025 and D09–D10. Students cannot use these management flows.')
    b.new('5  System models — account lifecycle')
    b.image('09_account_lifecycle.png',maxh=6.7)
    b.h('Identity and access are separate')
    b.p('D09 captures access changes and removal. D10 shows creation and Student ID edits. Changing a login ID preserves the account and its history; changing active state preserves history but expires stored sessions. Deletion is permitted only when the current account has no protected business references.')
    for a,z in [(0,16),(16,32)]:
        b.new('6  Traceability summary'+(' — continued' if a else ''),include=a==0)
        b.table(['Req. ID','SRS','Use case(s)','Test family','Diagrams'],[[r['Req. ID'],r['SRS Section'],r['Use Case ID'],r['Test Case ID'],r['Diagram IDs']] for r in REQ[a:z]],[.7,.55,1.7,1.35,2.8],9.8)
        b.p('RTM.xlsx contains the full requirement text, acceptance criterion, status, source/test paths, evidence IDs and remaining work. TC IDs are acceptance-test families. Some have several automated methods; TC023 and TC024 also require setup/evaluator evidence. The saved suite contains 110 methods, not 110 independent SRS requirements.')
        if a:
            b.h('Completion rule')
            b.p('Original functional scope: 18/18 (100%). Added functional scope: 7/7 (100%). Current functional scope: 25/25 (100%). Original total scope: 20/25 (80.0%). Current total scope: 27/32 (84.4%). The five Partial NFRs are NFR001, NFR002, NFR003, NFR004 and NFR006.')
            b.p(DATA['counting_rule'])
    b.new('7  Appendices and references',True)
    b.h('7.1  Team and planned milestones')
    b.p('Alam Shahriya (2677517): frontend, event forms, student workflows and configuration review. Hossain Md Miraj (2677529): backend services, constraints, organizer functions and tests review. Both share integration, deployment and presentation. These are review responsibilities, not measured contribution percentages; commit history and individual explanations provide contribution evidence.')
    b.p('Original baseline: 29 October 2026. Current evidence review: 18 November 2026. Final examination: 17 December 2026. D07 retains the submitted implementation plan and separately marks known progress. It does not invent actual effort dates. The final presentation and final submission report remain separate deliverables.')
    b.h('7.2  Demonstration outline')
    for txt in ['Show the live HTTPS URL and repository commit; provide private Student/Organizer credentials separately.','Show a two-seat event, a third Student on its waitlist, and cancellation promoting the earliest waiter.','Show Organizer roster/attendance and Student own-history boundaries.','Create a disposable Student with an ID, edit that ID while preserving history, and demonstrate password/access controls.','Delete an unused Student with exact-ID confirmation; demonstrate that a linked Student cannot be deleted.','Open RTM.xlsx, follow FR025 → UC018 → D09 → TC032, then explain the remaining five NFR evidence items.']:
        b.p(txt,'List Number')
    b.h('7.3  Source and technical references')
    refs=[DATA['repository'],DATA['live_url'],'https://docs.djangoproject.com/en/5.2/topics/db/transactions/','https://docs.djangoproject.com/en/5.2/topics/auth/default/','https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/','https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/','https://help.pythonanywhere.com/pages/FreeAccountsFeatures/']
    for ref in refs:
        p=b.p(ref)
        for r in p.runs:r.font.size=Pt(9)
    b.p('Source/configuration evidence and framework guidance reviewed 18 November 2026. The demonstration uses private credentials and databases; neither is included in the public review package.')
    assert b.page==28,b.page
    b.save(ROOT/'docs/srs/SRS.docx')
    print('SRS planned pages',b.page)

METRICS=[['Original functional requirements','18 / 18','100.0%'],['Added account requirements','7 / 7','100.0%'],['Current functional requirements','25 / 25','100.0%'],['Non-functional requirements','2 / 7','28.6%'],['Original total scope','20 / 25','80.0%'],['Current total scope','27 / 32','84.4%'],['Mapped current requirements','32 / 32','100.0%']]

def build_report():
    b=Book('Requirements Completion Report')
    b.p('PROFESSOR REVIEW  /  18 NOVEMBER 2026',bold=True)
    b.p('Requirements\nCompletion Report',style='Title')
    b.h('Campus Event Registration and Waitlist Management System',1)
    b.p('Prepared by Alam Shahriya (2677517) and Hossain Md Miraj (2677529)\nSoftware Design Part 2 • Dongshin University')
    b.p('All 25 functional requirements are implemented and supported by automated checks. Under the evidence rule below, 27 of the 32 current SRS requirements are complete: 84.4%. Five non-functional requirements have partial evidence and still need the specified acceptance records.',bold=True)
    b.table(['Scope','Complete / total','Percentage'],METRICS,[4.2,1.5,1.4],10.5)
    b.p('Separate test metric: the saved current Linux run passed 110/110 tests (100%) in 3.087 seconds. Test pass rate, requirement completion and professor acceptance are different measures.')
    b.h('How the percentage is calculated')
    b.p('Completed requirements ÷ total requirements × 100. Current scope: (25 functional + 2 non-functional) ÷ (25 functional + 7 non-functional) × 100 = 84.375%, rounded to 84.4%. Original scope: (18 + 2) ÷ (18 + 7) = 80.0%. Each row has equal weight; Partial receives no full-completion credit.')
    b.p('Verified means the specified evidence rule is met. Functional rows use inspected source and automated checks; hosted/browser/evaluator requirements are assessed separately. This percentage is a requirements-count measure, not effort completed, a grade, or instructor sign-off.')
    b.new('1  What has been completed')
    b.table(['Requirement group','Implemented outcome','Evidence'],[
        ['FR001–FR003','Session authentication, logout, role enforcement and own-record access.','E01–E02; hosted sign-in E05'],['FR004–FR006','Draft creation, controlled editing and publication.','E01–E02'],['FR007–FR008','Published catalog/search/filter, availability and participant privacy.','E01–E02'],['FR009–FR010','Atomic seat/waitlist allocation and one registration per student/event.','E01–E02'],['FR011–FR013','Personal history/rank, cancellation/rejoin and FIFO promotion.','E01–E02; hosted cancellation/promotion E05'],['FR014–FR018','Event cancellation, rosters, attendance/audit, dashboards and backend validation.','E01–E02; hosted roster/attendance E05']],[1.3,4.1,1.7],10)
    b.h('Seven account requirements integrated into SRS 2.0')
    b.table(['ID','Current feature','Acceptance support'],[
        ['FR019','Search/browse eligible students; 25 per page.','TC026'],['FR020','Edit details and synchronize ID/login while preserving records.','TC027, TC030'],['FR021','Reset validated password; old sessions/password fail.','TC028'],['FR022','Add students from Organizer account; fixed Student privileges.','TC029'],['FR023','Student ID as login; preserve leading zeros/hyphens and history.','TC030'],['FR024','Deactivate/reactivate; expire stored sessions and retain registrations.','TC031'],['FR025','Delete only unused Student with exact-ID confirmation; block linked history.','TC032']],[.8,5,1.3],10)
    b.p('Current source is commit b3d900f4ac7c516c086708305f53ebfdebd0422d. A host screenshot shows this update was pulled after a private backup. The team then reported completing deployment and confirmed that deletion works live (E08–E09). Exact current 110-test Windows and host terminal results were not supplied.')
    b.new('2  Remaining acceptance evidence — part 1')
    for r in REQ[25:28]:
        b.h(f"{r['Req. ID']} / {r['Test Case ID']} — {r['Title']} · Partial")
        b.p('Required: '+r['Acceptance Criteria'])
        b.p('Available: '+r['Verification'])
        b.p('To finish: '+r['Remaining Acceptance'])
    b.h('Record results against the same release')
    b.p('For each check record the date, tester, code commit, browser/device or host configuration, test data, expected result, actual result and evidence location. Use the supplied ACCEPTANCE_RECORD.md. Save private screenshots and credentials outside the public repository.')
    b.p('For performance, measure the deployed HTTP/browser request rather than manage.py’s in-process test client. For restart persistence, record data before and after a full Web-tab reload; simply refreshing the page does not establish an application restart. No code change is assumed to be necessary for either check.')
    b.new('2  Remaining acceptance evidence — part 2')
    for r in [REQ[28],REQ[30]]:
        b.h(f"{r['Req. ID']} / {r['Test Case ID']} — {r['Title']} · Partial")
        b.p('Required: '+r['Acceptance Criteria'])
        b.p('Available: '+r['Verification'])
        b.p('To finish: '+r['Remaining Acceptance'])
    b.h('Two non-functional requirements counted complete')
    b.table(['ID','Basis for completion','Evidence boundary'],[
        ['NFR005 / TC023','Modular source/services, pins, migrations, setup instructions and critical-rule tests; earlier clean Windows/host setup.','No remote CI or verified batch-launcher execution is claimed.'],
        ['NFR007 / TC025','Consistent host backup and separate restore shown; restored local instance ran; team confirmed requested data comparison; automated recovery checks passed.','Manual completion is team-reported. The private database was not supplied for independent row inspection.']],[1.2,3.6,2.3],10)
    b.p('If the instructor requires independent raw evidence for the restore comparison, change NFR007 to Partial until that evidence is provided. The workbook will then show 26/32 = 81.3% (exactly 81.25%). The current 84.4% explicitly accepts the team’s reported restore result.')
    b.new('3  Evidence register and limitations')
    b.table(['ID / source','Recorded result'],[[e['id']+'\n'+e['name']+'\n'+e['type'],e['detail']] for e in DATA['evidence']],[1.7,5.4],9.8)
    b.p('E02 is preserved in docs/development/student-lifecycle-tests.txt. E01 links to the public code commit. E03–E09 summarize supplied screenshots and team statements, with supporting detail in HOSTED_VERIFICATION.md, TEST_REPORT.md and BACKUP_RESTORE.md. Original screenshots and private database contents are not reproduced here.')
    b.p('Historical 62-test runs are not relabeled as current 110-test runs. HTML rendering tests do not establish complete Chrome/Edge/mobile interaction. A functioning live site does not establish professor access or approval. No claim is made that every current acceptance case has already been manually demonstrated on the host.')
    b.new('4  Professor review guide and handover')
    b.h('Open these files in this order')
    b.table(['Document','Use during review'],[
        ['COMPLETION_REPORT.pdf','Explain the denominator and remaining evidence items.'],['SRS.pdf / SRS.docx','Read the revised 25 functional and 7 non-functional requirements.'],['RTM.xlsx / RTM.csv','Follow IDs to SRS sections, use cases, diagrams, source, test families and evidence.'],['System_Diagrams.pdf','Review 10 models including the current account lifecycle and identity updates.'],['TESTCASE_INDEX.md / saved test log','Trace TC001–TC032 to 110 executable test methods and manual criteria.'],['ACCEPTANCE_RECORD.md','Record the remaining checks without inventing results.'],['docs/archive/2026-10-29-baseline/','Compare the original submitted scope and unchanged baseline files.']],[2.6,4.5],10)
    b.h('Example requirement walk-through')
    b.p('FR025 → SRS section 3.2.25 → UC018 → D03/D08/D09 → accounts/user_views.py and accounts/user_lifecycle.py → TC032 in tests/test_student_lifecycle.py → saved 110-test pass (E02) and team-reported live deletion (E09). Demonstrate successful unused-account deletion and rejection when a Student has saved registrations.')
    b.h('Suggested progress statement')
    b.p('“We have implemented all 25 functional requirements: the original 18 plus 7 account-management requirements. The application is live and the source is on GitHub. Our saved Linux suite passes 110 tests. On an equal-weight requirement count, 27 of 32 requirements are complete, or 84.4%. Five quality/deployment acceptance records still need to be finished. The final presentation and submission report will be delivered separately.”')
    b.h('Review record — to be completed during evaluation')
    b.table(['Item','Record'],[['Reviewer / date','________________________________________'],['Acceptance evidence reviewed','________________________________________'],['Required corrections','________________________________________']],[2.3,4.8],10)
    b.p('Live: '+DATA['live_url']);b.p('Repository: '+DATA['repository'])
    assert b.page==6
    b.save(ROOT/'docs/review/COMPLETION_REPORT.docx')
    print('Completion report planned pages',b.page)

if __name__=='__main__':build_srs();build_report()
