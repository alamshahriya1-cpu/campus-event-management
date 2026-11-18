import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pathlib import Path
out=Path(__file__).resolve().parents[1]/"05_cancellation_sequence.png"
fig,ax=plt.subplots(figsize=(12,8));ax.set_xlim(0,12);ax.set_ylim(0,12);ax.axis("off")
xs=[1,4,7.4,10.9]
for x,name in zip(xs,["Student","Browser","Django backend","SQLite database"]):
 ax.add_patch(Rectangle((x-.95,11.15),1.9,.6,facecolor="#DFEAF2",edgecolor="#567086"));ax.text(x,11.45,name,ha="center",va="center",fontsize=11);ax.plot([x,x],[11.15,.5],ls="--",color="#B6C3CC",lw=.8)
def msg(a,b,y,label,dashed=False):
 ax.annotate("",xy=(xs[b],y),xytext=(xs[a],y),arrowprops=dict(arrowstyle="->",lw=1.1,color="#173B56",linestyle="--" if dashed else "-"));ax.text((xs[a]+xs[b])/2,y+.13,label,ha="center",fontsize=10)
msg(0,1,10.55,"Cancel my confirmed place")
msg(1,2,9.9,"POST /api/registrations/{id}/cancel/")
ax.text(7.4,9.4,"Validate session, CSRF, role and ownership",ha="center",fontsize=10)
msg(2,3,8.95,"Begin atomic transaction; acquire event write")
msg(2,3,8.2,"Recheck event, deadline and current status")
ax.add_patch(Rectangle((6.1,3.0),5.75,4.65,fill=False,edgecolor="#718797"))
ax.text(6.23,7.37,"alt",weight="bold",fontsize=10)
ax.text(9.0,7.37,"[eligible confirmed cancellation]",ha="center",fontsize=10)
msg(2,3,6.8,"Set this registration to Cancelled")
msg(2,3,6.1,"Select earliest active waitlist entry")
msg(2,3,5.4,"Promote if present; commit both changes")
ax.plot([6.1,11.85],[4.9,4.9],ls="--",color="#718797")
ax.text(9,4.57,"[deadline/state conflict or database failure]",ha="center",fontsize=9.5)
msg(2,3,3.8,"Rollback; preserve all prior registration states")
msg(2,1,2.4,"Return own status or an error",True)
msg(1,0,1.55,"Display cancellation result",True)
fig.subplots_adjust(left=.02,right=.98,top=.99,bottom=.02)
fig.savefig(out,dpi=200,facecolor="white");plt.close(fig)
