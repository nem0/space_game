"""Procedural 2048 sheet for the damaged parts kit (models/parts): chipped painted hull plates, light steel, equipment box faces.
Run: blender --background --python make_parts_sheet.py   -> parts_sheet/textures/parts_*.png + parts_sheet/parts_layout.json
Same conventions as make_trim_sheet.py: 512 px per metre, strips span the full width and tile in U, rects are (x, y, w, h) with y from the TOP.
Look target: concept_art/new_style.png - warm white riveted plates, desaturated green / red / blue paint flaking down to the white primer,
light grey steel, yellow pipes, red cables. Everything stays nearly non-metallic (metal <= 0.3): the game sun has no sky light, so metallic
surfaces render black in Studio."""
import bpy, json, numpy as np
from pathlib import Path
OUT=Path('C:/projects/space_game/models/parts_sheet'); TEX=OUT/'textures'; TEX.mkdir(parents=True,exist_ok=True)
S=2048; rng=np.random.default_rng(11)

LAYOUT={
 'HULL_WHITE':(0,0,1024,512),      # 4x2 hull plates, 256 px (0.5 m) each
 'HULL_GREEN':(1024,0,512,512),    # 2x2 plates each
 'HULL_RED':(1536,0,512,512),
 'HULL_BLUE':(0,512,512,512),
 'HULL_SCRAP':(512,512,512,512),   # mismatched salvage plates + riveted patches
 'BOX':(1024,512,256,256),         # generic equipment box face
 'BOX_VENT':(1280,512,256,256),
 'BOX_ELEC':(1536,512,256,256),
 'CRATE':(1792,512,256,256),
 'HATCH':(1024,768,256,256),
 'SOLAR':(1280,768,256,256),
 'HAZARD':(1536,768,128,128),
 'BRACKET':(1664,768,128,128),
 'GRILLE':(1536,896,256,128),
 'RIB':(0,1032,S,32),              # hull ring frames (mapped along the circumference)
 'RAIL':(0,1072,S,32),             # tube strips: U = along the tube, V = around it
 'PIPE_YELLOW':(0,1112,S,32),
 'CABLE_RED':(0,1152,S,32),
 'CABLE_DARK':(0,1192,S,32),
 'GASKET':(0,1232,S,48),
 'DOCK':(0,1288,S,128),            # 16 bolted plates around a docking ring
 'DOCK_DARK':(0,1424,S,96),
 'TANK_WHITE':(0,1528,S,192),
 'TANK_BLUE':(0,1728,S,192),
 'BEAM':(0,1928,S,64),             # white painted structural bar with bolts
 'FLANGE':(0,1996,S,48),           # machined steel face of the docking flange, bolt holes every 12.5 cm
}
SWATCH=['SW_WHITE','SW_STEEL','SW_DARK','SW_RUBBER','SW_YELLOW','SW_RED','SW_BLUE','SW_GREEN','SW_GLASS','SW_LIGHT','SW_BARE','SW_ORANGE','SW_WINDOW','SW_LED_GREEN','SW_LED_RED']
for k,n in enumerate(SWATCH): LAYOUT[n]=(1792+(k%4)*64,768+(k//4)*64,64,64)

c=lambda *v: np.array(v,np.float32)/255
WHITE=c(192,188,178); PRIMER=c(196,193,185); BARE=c(146,148,148); STEEL=c(182,184,182); DARK=c(54,57,60); SEAM=c(50,50,48); RUBBER=c(30,31,33)
GREEN=c(108,122,100); RED=c(148,88,74); BLUE=c(80,100,134); YELLOW=c(204,158,40); CABLE=c(152,46,38); DIRT=c(74,62,48); GLASS=c(14,26,36)

alb=np.tile(SEAM,(S,S,1)).astype(np.float32); hgt=np.zeros((S,S),np.float32)
rgh=np.full((S,S),.6,np.float32); met=np.zeros((S,S),np.float32); emi=np.zeros((S,S,3),np.float32); cav=np.ones((S,S),np.float32)

def noise(h,w,sy,sx,periodic=False):
    """bilinear value noise; periodic in x so strips wrap"""
    ny,nx=h//sy+2,w//sx+2; low=rng.random((ny,nx)).astype(np.float32)
    if periodic: low[:,-1]=low[:,0]
    ys=np.linspace(0,ny-2,h,endpoint=False); xs=np.linspace(0,nx-2,w,endpoint=False)
    y0=ys.astype(int); x0=xs.astype(int); fy=(ys-y0)[:,None]; fx=(xs-x0)[None,:]
    a=low[np.ix_(y0,x0)]; b=low[np.ix_(y0,x0+1)]; cc=low[np.ix_(y0+1,x0)]; d=low[np.ix_(y0+1,x0+1)]
    return (a*(1-fx)+b*fx)*(1-fy)+(cc*(1-fx)+d*fx)*fy
def fbm(h,w,sy,sx,periodic=False):
    return .55*noise(h,w,sy,sx,periodic)+.3*noise(h,w,max(sy//2,1),max(sx//2,1),periodic)+.15*noise(h,w,max(sy//4,1),max(sx//4,1),periodic)
def flake(h,w,periodic=False):
    """blobby noise for paint flakes: big patches broken up by small chips"""
    return .36*noise(h,w,min(26,h),26,periodic)+.34*noise(h,w,9,9,periodic)+.30*noise(h,w,3,3,periodic)
def sstep(x): x=np.clip(x,0,1); return x*x*(3-2*x)
def rrsdf(w,h,r,ox,oy,W,H):
    """signed distance (px, negative inside) of a rounded rect (ox,oy,w,h) on a W x H grid"""
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    cx,cy=ox+w/2,oy+h/2; qx=np.abs(xx+.5-cx)-(w/2-r); qy=np.abs(yy+.5-cy)-(h/2-r)
    return np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-r

class Reg:
    """drawing surface bound to one layout rect; `plates` / `edge` collect what plate() drew so paint and grime can follow the plate edges"""
    def __init__(s,name,color=SEAM,rough=.7,metal=.1):
        s.name=name; s.x,s.y,s.w,s.h=LAYOUT[name]; sy,sx=slice(s.y,s.y+s.h),slice(s.x,s.x+s.w)
        s.alb=alb[sy,sx]; s.hgt=hgt[sy,sx]; s.rgh=rgh[sy,sx]; s.met=met[sy,sx]; s.emi=emi[sy,sx]; s.cav=cav[sy,sx]
        s.alb[...]=color; s.rgh[...]=rough; s.met[...]=metal
        s.plates=np.zeros((s.h,s.w),bool); s.edge=np.full((s.h,s.w),99.,np.float32); s.tone=np.ones((s.h,s.w),np.float32)
    def plate(s,x,y,w,h,r,bevel,height,color,rough=.5,metal=0.,jitter=0.,track=True):
        d=rrsdf(w,h,r,x,y,s.w,s.h); m=d<0; prof=sstep(-d/bevel)*height
        s.hgt[m]=np.maximum(s.hgt[m],prof[m]) if height>0 else s.hgt[m]+prof[m]
        t=1+rng.uniform(-jitter,jitter); s.alb[m]=np.clip(np.array(color)*t,0,1); s.rgh[m]=rough; s.met[m]=metal
        s.cav[m]*=(.75+.25*sstep(-d[m]/(bevel*1.5)))
        if track: s.plates|=m; s.edge[m]=-d[m]; s.tone[m]=t
        return m
    def box(s,x,y,w,h,color=None,dh=0.,rough=None,metal=None,mul=None):
        x0,y0,x1,y1=max(int(x),0),max(int(y),0),min(int(x+w),s.w),min(int(y+h),s.h)
        if color is not None: s.alb[y0:y1,x0:x1]=color
        if mul is not None: s.alb[y0:y1,x0:x1]*=mul; s.cav[y0:y1,x0:x1]*=mul
        if rough is not None: s.rgh[y0:y1,x0:x1]=rough
        if metal is not None: s.met[y0:y1,x0:x1]=metal
        s.hgt[y0:y1,x0:x1]+=dh
    def _win(s,cx,cy,rad):
        x0,x1,y0,y1=max(int(cx-rad-3),0),min(int(cx+rad+4),s.w),max(int(cy-rad-3),0),min(int(cy+rad+4),s.h)
        yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32); return (slice(y0,y1),slice(x0,x1)),xx+.5-cx,yy+.5-cy
    def rivet(s,cx,cy,rad=3.0,h=.55):
        """small dome that keeps whatever paint is under it (lighter top, dark ring)"""
        w,dx,dy=s._win(cx,cy,rad); d=np.hypot(dx,dy)-rad; m=d<0; ring=(d>=0)&(d<1.6)
        s.hgt[w][m]+=h*sstep(-d[m]/1.5); s.alb[w][m]*=1.10; s.alb[w][ring]*=.58; s.cav[w][ring]*=.6
    def bolt(s,cx,cy,rad=7.,color=STEEL,h=.7):
        """hex bolt head in its own colour"""
        w,dx,dy=s._win(cx,cy,rad); d=np.maximum(np.abs(dx)*.866+np.abs(dy)*.5,np.abs(dy))-rad; m=d<0; ring=(d>=0)&(d<2.5)
        s.hgt[w][m]=np.maximum(s.hgt[w][m],0)+h*sstep(-d[m]/2); s.alb[w][m]=color*(.85+.3*sstep(-d[m]/rad))[:,None]; s.rgh[w][m]=.42; s.met[w][m]=.3
        s.alb[w][ring]*=.55; s.cav[w][ring]*=.55
    def disc(s,cx,cy,rad,color,dh=0.,rough=.5,metal=0.,ring=None):
        w,dx,dy=s._win(cx,cy,rad); d=np.hypot(dx,dy)-rad; m=d<0
        if ring: m=(d<0)&(d>-ring)
        s.alb[w][m]=color; s.hgt[w][m]+=dh; s.rgh[w][m]=rough; s.met[w][m]=metal
    def paint(s,color,amount,under=None,bias=.42,periodic=False,raise_=.18):
        """paint over the plates; `amount` of the area flakes off (mostly along plate edges) and shows what is underneath, with a feathered rim"""
        n=flake(s.h,s.w,periodic)+bias*np.clip(1-s.edge/16,0,1); P=s.plates
        thr=np.quantile(n[P],1-amount); keep=P&(n<=thr-.03); fade=P&(n>thr-.03)&(n<=thr); bare=P&(n>thr)
        col=np.clip(np.array(color)*((1+(fbm(s.h,s.w,min(64,s.h),64,periodic)-.5)*.24)*s.tone)[...,None],0,1)
        if under is not None: s.alb[bare]=(np.array(under)*s.tone[...,None])[bare]
        s.alb[keep]=col[keep]; s.alb[fade]=np.clip(col[fade]*.6+s.alb[fade]*.4,0,1)
        s.hgt[keep|fade]+=raise_; s.rgh[keep|fade]=.62; s.met[keep|fade]=0; s.hgt[bare]-=.05
    def grime(s,amount=.4,edge=.3,periodic=False):
        g=fbm(s.h,s.w,min(48,s.h),48,periodic); st=.6+.4*noise(s.h,s.w,min(96,s.h),5,periodic)
        dirt=(np.clip((g-.40)*2.2,0,1)*amount*st)[...,None]
        s.alb[...]=s.alb*(1-dirt*.55)+DIRT*dirt*.16; s.rgh[...]=np.clip(s.rgh+dirt[...,0]*.2,0,1)
        if edge>0: e=(1-edge)+edge*sstep(s.edge/9); s.alb[s.plates]*=e[s.plates][:,None]
    def scratches(s,n,alpha=.4,length=(14,70),color=PRIMER):
        for _ in range(n):
            x0,y0,a,ln=rng.uniform(0,s.w),rng.uniform(0,s.h),rng.uniform(0,6.283),rng.uniform(*length)
            t=np.linspace(0,ln,int(ln)+1); xs=(x0+t*np.cos(a)).astype(int); ys=(y0+t*np.sin(a)).astype(int)
            ok=(xs>=0)&(xs<s.w)&(ys>=0)&(ys<s.h); xs,ys=xs[ok],ys[ok]
            s.alb[ys,xs]=s.alb[ys,xs]*(1-alpha)+color*alpha; s.hgt[ys,xs]-=.08
    def warp(s,amp=1.2,scale=72,periodic=False): s.hgt+=(fbm(s.h,s.w,min(scale,s.h),scale,periodic)-.5)*amp       # oil-canning of thin sheet
    def micro(s,amount=.03): s.hgt+=(noise(s.h,s.w,2,2)-.5)*amount

# --- hull plates ---------------------------------------------------------------------------------------------------
def hull(name,paint=None,chip=.26,scrap=False):
    r=Reg(name); P=256
    for i in range(r.w//P):
        for j in range(r.h//P): r.plate(i*P+3,j*P+3,P-6,P-6,7,5,1.0,BARE,.45,.3,.07)
    r.paint(WHITE,.05,BARE,.28)                                       # everything is white first: bare metal only where that has flaked too
    if paint is not None: r.paint(paint,chip,None,.5)
    for i in range(r.w//P):
        for j in range(r.h//P):
            x,y=i*P,j*P; k=rng.integers(5)
            if scrap:                                                # salvage: random colour per plate + a riveted patch
                q=Reg.__new__(Reg); q.__dict__.update(r.__dict__); sl=(slice(y,y+P),slice(x,x+P))
                for a in ('alb','hgt','rgh','met','cav','plates','edge','tone'): setattr(q,a,getattr(r,a)[sl])
                q.w=q.h=P; col=[GREEN,RED,BLUE,YELLOW][(i*2+j)%4]; q.paint(col,.45,None,.6)
                px,py,pw,ph=rng.integers(40,110),rng.integers(40,110),rng.integers(70,110),rng.integers(60,100)
                m=r.plate(x+px,y+py,pw,ph,5,4,1.6,WHITE*rng.uniform(.8,1.0),.5,.1,0,track=False)
                for ax,ay in ((8,8),(pw-8,8),(8,ph-8),(pw-8,ph-8),(pw//2,8),(pw//2,ph-8)): r.rivet(x+px+ax,y+py+ay,3.2,.6)
            if k in (1,3): r.box(x+6,y+P//2-1,P-12,2,mul=.55,dh=-.4)     # sub-panel seams
            if k in (2,3): r.box(x+[P//2,P//3,2*P//3][rng.integers(3)]-1,y+6,2,P-12,mul=.55,dh=-.4)
            for t in range(16,P,32):                                 # rivet rows along the plate edges
                for cx,cy in ((x+t,y+13),(x+t,y+P-13),(x+13,y+t),(x+P-13,y+t)): r.rivet(cx,cy)
    r.grime(.32,.22); r.scratches(14*(r.w//P)*(r.h//P),.35); r.warp(1.0); r.micro()
hull('HULL_WHITE'); hull('HULL_GREEN',GREEN,.13); hull('HULL_RED',RED,.15); hull('HULL_BLUE',BLUE,.13); hull('HULL_SCRAP',None,0,True)

# --- equipment faces -----------------------------------------------------------------------------------------------
def boxface(name,amount=.10):
    r=Reg(name); r.plate(2,2,r.w-4,r.h-4,14,7,1.0,BARE,.45,.3); r.paint(WHITE,amount,BARE,.7); return r
def finish(r,grime=.45,scr=8):
    for p in ((22,22),(r.w-22,22),(22,r.h-22),(r.w-22,r.h-22)): r.bolt(p[0],p[1],6,STEEL)
    r.grime(grime,.38); r.scratches(scr,.3); r.micro()
def label(r,x,y,w=44,h=30):
    r.box(x,y,w,h,YELLOW*.95,.1,.55,0)
    yy,xx=np.mgrid[0:h,0:w]; tri=(np.abs(xx-w/2)<(yy-5)*.62)&(yy>5)&(yy<h-5); r.alb[y:y+h,x:x+w][tri]=DARK*.6
r=boxface('BOX')
for a,b_,w_,h_ in ((30,30,196,2),(30,224,196,2),(30,30,2,196),(224,30,2,196)): r.box(a,b_,w_,h_,mul=.6,dh=-.4)
label(r,44,180); finish(r)
r=boxface('BOX_VENT'); r.plate(36,52,184,160,8,5,-1.0,DARK*.75,.7,.1,track=False)
for k in range(9): r.plate(44,60+k*17,168,9,3,3,1.1,WHITE*.92,.5,.1,track=False)
finish(r)
r=boxface('BOX_ELEC'); r.plate(34,34,188,150,8,4,1.3,WHITE*1.02,.5,.05,track=False)
for yy_ in (56,150): r.box(30,yy_,12,22,DARK,.4,.5,.3)                                  # hinges
r.plate(190,92,14,40,5,3,1.2,DARK,.5,.3,track=False); label(r,52,58,52,36)
for k in range(4): r.disc(60+k*46,218,11,DARK*.8,-.5,.6,.2); r.disc(60+k*46,218,14,STEEL,.3,.45,.3,ring=3)
finish(r)
r=boxface('CRATE',.14)
for x_ in (70,178): r.plate(x_-10,10,20,236,5,4,1.6,WHITE*.94,.5,.05,track=False)
r.box(8,127,240,3,mul=.55,dh=-.5); r.plate(108,108,40,40,5,4,1.4,STEEL,.45,.3,track=False); r.bolt(128,128,8,DARK)
finish(r,.5,10)
r=boxface('HATCH'); yy,xx=np.mgrid[0:256,0:256].astype(np.float32); d=np.hypot(xx-128,yy-128)
m=d<92; r.hgt[m]+=.9*sstep((92-d[m])/6); r.alb[m]*=1.04; ring=(d>=92)&(d<96); r.alb[ring]*=.5; r.cav[ring]*=.5
for k in range(12): a=k*np.pi/6; r.bolt(128+106*np.cos(a),128+106*np.sin(a),6,STEEL)
for k in range(3): a=k*np.pi/3; t=np.linspace(-40,40,81); r.alb[(128+t*np.sin(a)).astype(int)[:,None]+np.arange(-2,3),(128+t*np.cos(a)).astype(int)[:,None]+np.arange(1)]=DARK
r.disc(128,128,44,DARK,.5,.5,.3,ring=6); r.disc(128,128,12,STEEL,.8,.45,.3); r.plate(176,60,16,52,6,3,1.4,YELLOW,.5,0,track=False)
finish(r,.4)
r=Reg('SOLAR',STEEL*.9,.45,.25)
for i in range(4):
    for j in range(6):
        x,y=8+i*60,8+j*40; r.plate(x+2,y+2,56,36,3,2,.5,c(40,56,104),.22,.1,.10,track=False)
        for bx in (20,38): r.box(x+bx,y+3,1,34,c(150,170,210))
        r.box(x+3,y+19,54,1,c(110,135,190))
r.edge[...]=99; r.plates[...]=True; r.grime(.3,0); r.scratches(10,.35,color=c(170,185,215))
r=Reg('HAZARD'); r.plate(2,2,124,124,8,5,1.0,BARE,.45,.3); r.paint(YELLOW,.12,BARE,.7)
yy,xx=np.mgrid[0:128,0:128]; hz=((xx+yy)%40<20)&(r.edge>6)&(r.alb[...,2]<.3); r.alb[hz]=DARK*.55; r.grime(.4,.3); r.scratches(6)
r=Reg('BRACKET'); r.plate(2,2,124,124,10,6,1.0,STEEL,.42,.3)
for p in ((30,30),(98,30),(30,98),(98,98)): r.bolt(p[0],p[1],11,STEEL*.7)
r.box(10,61,108,6,mul=.62,dh=-.4); r.grime(.45,.35); r.micro()
r=Reg('GRILLE',DARK*.7,.7,.1)
for k in range(15): r.plate(6+k*16.4,8,9,112,3,3,1.0,WHITE*.9,.5,.1,track=False)
r.box(0,0,256,5,WHITE*.85); r.box(0,123,256,5,WHITE*.85); r.edge[...]=99; r.plates[...]=True; r.grime(.4,0)

# --- strips (periodic in x) ------------------------------------------------------------------------------------------
def strip(name,color,rough,metal,bevel=5,height=1.0):
    r=Reg(name); r.plate(-20,1,S+40,r.h-2,2,bevel,height,color,rough,metal); return r
r=strip('RIB',STEEL,.42,.3); r.alb*=(.9+.2*noise(r.h,r.w,1,48,True)[...,None])
for x in range(0,S,128): r.box(x,3,3,r.h-6,mul=.55,dh=-.4)
r.grime(.4,.35,True)
def tubestrip(name,color,rough,metal,coupler=None,every=256,cw=14,chips=0.):
    """for tubes: U runs along the tube, V around it, so there is no bevel - only wear, stains and couplers"""
    r=Reg(name,color,rough,metal); r.plates[...]=True
    if chips>0: r.alb[...]=BARE; r.met[...]=.3; r.paint(color,chips,None,0,True,.1)
    r.alb*=(.9+.2*noise(r.h,r.w,8,40,True)[...,None])
    if coupler is not None:
        for x in range(every//2,S,every): r.box(x-cw//2,0,cw,r.h,coupler,.5,.45,.3); r.box(x-cw//2-2,0,2,r.h,mul=.6); r.box(x+cw//2,0,2,r.h,mul=.6)
    r.grime(.35,0,True); return r
tubestrip('RAIL',STEEL,.42,.3,STEEL*.72); tubestrip('PIPE_YELLOW',YELLOW,.55,0,STEEL,256,16,.14)
tubestrip('CABLE_RED',CABLE,.6,0,DARK*.7,128,8); tubestrip('CABLE_DARK',c(50,52,56),.65,0,c(120,122,124),128,8)
r=Reg('GASKET',RUBBER,.75,0)
for y in (8,28): r.plate(-20,y,S+40,12,5,4,1.0,RUBBER*1.4,.7,0)
r=Reg('DOCK')
for i in range(16): r.plate(i*128+2,3,124,122,6,5,1.0,BARE,.45,.3,.06)
r.paint(WHITE,.12,BARE,.6,True)
for i in range(16):
    for y in (22,106): r.bolt(i*128+64,y,7,STEEL)
    for y in (42,86): r.rivet(i*128+20,y); r.rivet(i*128+108,y)
r.grime(.5,.36,True); r.scratches(60,.3); r.micro()
r=Reg('DOCK_DARK',DARK,.5,.3)
for y in (8,38,68): r.plate(-20,y,S+40,20,5,5,1.0,c(92,96,100),.45,.3)
for x in range(64,S,128): r.bolt(x,48,7,STEEL)
r.grime(.4,.3,True)
def tank(name,paint):
    r=Reg(name); r.plate(-20,2,S+40,r.h-4,2,4,.6,BARE,.45,.3); r.paint(WHITE,.05,BARE,.3,True)
    if paint is not None: r.paint(paint,.14,None,.3,True)
    for x in range(0,S,512):
        r.box(x,4,3,r.h-8,mul=.55,dh=-.4)
        for y in range(16,r.h,24): r.rivet(x+12,y); r.rivet((x-10)%S,y)
    for y in (48,144): r.box(0,y,S,2,mul=.7,dh=-.25)
    r.grime(.5,.2,True); r.scratches(50,.3); r.warp(.6,64,True); r.micro()
tank('TANK_WHITE',None); tank('TANK_BLUE',BLUE)
r=strip('BEAM',BARE,.45,.3,6); r.paint(WHITE,.12,BARE,.7,True)
for x in range(64,S,128): r.bolt(x,32,7,STEEL)
for x in range(0,S,128): r.box(x,6,2,r.h-12,mul=.6,dh=-.3)
r.grime(.45,.35,True); r.micro()
r=strip('FLANGE',STEEL*.92,.4,.3,4); r.alb*=(.9+.2*noise(r.h,r.w,1,40,True)[...,None])
for x in range(32,S,64): r.plate(x-8,20,16,8,4,2,-.5,DARK*.8,.6,.2,track=False)      # bolt holes, squashed: the 48 px strip is stretched over a 20 cm face
for x in range(0,S,128): r.box(x,4,2,r.h-8,mul=.6,dh=-.3)
r.grime(.4,.3,True)
# emissive swatches (the material multiplies them by Emission 4): lamp, lit window seen through glass, status / beacon LEDs
GLOW={'SW_LIGHT':(1.0,.62,.25),'SW_WINDOW':(.34,.22,.10),'SW_LED_GREEN':(.08,1.0,.28),'SW_LED_RED':(1.0,.06,.04)}
# --- swatches (sampled at their centre) ----------------------------------------------------------------------------
for name,col,rough,metal in [('SW_WHITE',WHITE,.55,0),('SW_STEEL',STEEL,.42,.3),('SW_DARK',DARK,.55,.3),('SW_RUBBER',RUBBER,.75,0),('SW_YELLOW',YELLOW,.55,0),
                             ('SW_RED',CABLE,.6,0),('SW_BLUE',BLUE,.6,0),('SW_GREEN',GREEN,.6,0),('SW_GLASS',GLASS,.08,0),('SW_LIGHT',c(255,215,150),.3,0),
                             ('SW_BARE',BARE,.45,.3),('SW_ORANGE',c(214,112,28),.5,0),
                             ('SW_WINDOW',c(120,96,62),.12,0),('SW_LED_GREEN',c(60,230,110),.3,0),('SW_LED_RED',c(240,50,40),.3,0)]:
    r=Reg(name,col,rough,metal)
    if name in GLOW: r.emi[...]=GLOW[name]
# status LED on every electrical box face (drawn straight into the arrays: no random numbers, so nothing above changes)
def led(region,cx,cy,rad,color):
    x,y=LAYOUT[region][:2]; yy,xx=np.mgrid[-rad-2:rad+3,-rad-2:rad+3]; d=np.hypot(xx,yy); sl=(slice(y+cy-rad-2,y+cy+rad+3),slice(x+cx-rad-2,x+cx+rad+3))
    m=d<rad; ring=(d>=rad)&(d<rad+2); alb[sl][ring]=DARK*.6; alb[sl][m]=np.clip(np.array(color)*.9+.1,0,1); emi[sl][m]=color; rgh[sl][m]=.3; met[sl][m]=0
led('BOX_ELEC',150,62,5,(.1,1.0,.3)); led('BOX_ELEC',168,62,5,(1.0,.45,.05))

# --- normal from height + export -----------------------------------------------------------------------------------
def gradient(hf,k):
    dx=np.roll(hf,-1,1)-np.roll(hf,1,1); dy=np.roll(hf,-1,0)-np.roll(hf,1,0)
    n=np.dstack([-dx*k,dy*k,np.ones_like(hf)]); n/=np.linalg.norm(n,axis=2,keepdims=True); return n*.5+.5
normal=gradient(hgt,3.5)
blur=hgt.copy()
for _ in range(3): blur=(np.roll(blur,3,0)+np.roll(blur,-3,0)+np.roll(blur,3,1)+np.roll(blur,-3,1)+blur)/5
ao=np.clip(cav*(1-np.clip((blur-hgt)*.35,0,.5)),0,1)
def save(name,arr,srgb):
    h,w=arr.shape[:2]; img=bpy.data.images.new(name,w,h,alpha=False); img.colorspace_settings.name='sRGB' if srgb else 'Non-Color'
    out=np.ones((h,w,4),np.float32); out[...,:3]=np.clip(arr,0,1); out=out[::-1]      # image rows start at the bottom
    img.pixels.foreach_set(out.ravel()); img.filepath_raw=str(TEX/(name+'.png')); img.file_format='PNG'; img.save()
save('parts_basecolor',alb,True); save('parts_normal',normal,False); save('parts_orm',np.dstack([ao,rgh,met]),False); save('parts_emissive',emi,True)
(OUT/'parts_layout.json').write_text(json.dumps({'size':S,'px_per_metre':512,'rects_xywh_from_top':LAYOUT},indent=1))
print('PARTS SHEET DONE')
