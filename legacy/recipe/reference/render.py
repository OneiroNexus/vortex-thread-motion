from PIL import Image,ImageDraw,ImageFilter,ImageFont
import numpy as np, math, subprocess
W,H=720,836
fps=24; n=288; nu=.13; tf=4.2
T=2*math.pi
font=lambda n,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',n)
title=font(35,True); subtitle=font(20); f=font(17); small=font(15); pill=font(17,True)
def ease(a,b,x):
    x=min(max((x-a)/(b-a),0),1)
    return x*x*(3-2*x)
def rhs(z,t):
    x,y=z[...,0],z[...,1]; a=np.exp(-2*nu*t)
    return a*np.stack((np.cos(x)*np.sin(y),-np.sin(x)*np.cos(y)),axis=-1)
def step(z,t,dt):
    k1=rhs(z,t);k2=rhs(z+dt*k1/2,t+dt/2);k3=rhs(z+dt*k2/2,t+dt/2);k4=rhs(z+dt*k3,t+dt)
    return (z+dt*(k1+k2*2+k3*2+k4)/6)%T
u=np.linspace(0,T,141)
curves=[]
for h in np.linspace(0,T,34,endpoint=False): curves.append(np.stack((u,np.full_like(u,h)),axis=1))
for h in np.linspace(0,T,25,endpoint=False): curves.append(np.stack((np.full_like(u,h),u),axis=1))
for h in np.linspace(0,T,12,endpoint=False): curves.append(np.stack(((u+h)%T,(2*u+h*.24)%T),axis=1))
P=np.stack(curves)
rng=np.random.default_rng(117)
seeds=rng.uniform(0,T,(204,2))
def shape(P,s):
    x,y=P[...,0],P[...,1]
    squash=ease(.12,.42,s); b=ease(.40,.83,s)
    rho=(1-b)*(1.04+.20*squash)*np.abs(np.cos(y))+b*(1.03+.49*np.cos(y))
    z=((1-b)*(1.04-.56*squash)+b*.45)*np.sin(y)
    return rho*np.cos(x),rho*np.sin(x),z
def camera(p,s):
    x,y,z=p
    theta=0.08+.85*s
    x,y=np.cos(theta)*x-np.sin(theta)*y,np.sin(theta)*x+np.cos(theta)*y
    tilt=.72+.15*ease(.37,.83,s)
    dep=np.sin(tilt)*z+np.cos(tilt)*y
    up=np.cos(tilt)*z-np.sin(tilt)*y
    scale=195/(1-.10*dep)
    return 360+scale*x,419-scale*up,dep
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-threads','3','-movflags','+faststart','Vortex Threads - Sphere to Torus.mp4'],stdin=subprocess.PIPE)
dt=tf/(n-1)
assert np.max(np.abs(rhs(P,tf))) < np.max(np.abs(rhs(P,0)))*.35
assert abs(shape(np.array([[0,np.pi]]),1)[0][0]-.54)<1e-10
gx,gy=np.meshgrid(np.linspace(-1,1,W),np.linspace(-1,1,H))
a=np.exp(-1.2*(gx**2+(gy+.03)**2))
noise=(np.random.default_rng(332).normal(0,.7,(H,W)))
background=Image.fromarray(np.clip(np.stack([5+8*a+noise,8+12*a+noise,10+13*a+noise],axis=-1),0,255).astype('uint8')).convert('RGB')
palette=np.array([[60,172,146],[164,78,52],[192,158,91]],dtype=float)
for i in range(n):
    s=i/(n-1);t=i*dt
    im=background.copy();d=ImageDraw.Draw(im)
    X,Y,D=camera(shape(P,s),s)
    dseg=(D[:,:-1]+D[:,1:])/2
    ang=np.cos(P[:,:-1,0])*np.cos(P[:,:-1,1])
    dep=np.clip((dseg+1.37)/2.74,0,1)
    pcolor=palette[np.where(ang>.10,0,np.where(ang<-.10,1,2))]
    color=np.clip(pcolor*(.16+.81*dep[...,None])+dep[...,None]*34,0,255).astype(np.uint8)
    for j in np.argsort(dseg.ravel()):
        l,k=divmod(int(j),X.shape[1]-1)
        if l<59 or k%3!=1:
            d.line((X[l,k],Y[l,k],X[l,k+1],Y[l,k+1]),fill=tuple(color[l,k]),width=2 if dep[l,k]>.63 else 1)
    X2,Y2,D2=camera(shape(seeds,s),s)
    for j in np.argsort(D2):
        x,y,z=X2[j],Y2[j],D2[j]
        if z<-.16: continue
        k=min(1,max(0,(z+.16)/1.4)); r=1.1+1.6*k
        color=(int(92+145*k),int(61+146*k),int(34+93*k))
        d.ellipse((x-r,y-r,x+r,y+r),fill=color)
    d.text((42,31),'VORTEX THREADS',font=title,fill='#e8eedf')
    d.text((43,84),'From a sphere to a torus',font=subtitle,fill='#8cc5b2')
    stage='SPHERE' if s<.13 else ('COMPRESSION' if s<.42 else ('OPENING' if s<.81 else 'TORUS'))
    d.text((43,126),stage,font=pill,fill='#dfb382')
    d.line((44,155,676,155),fill='#314442',width=1)
    d.line((44,741,676,741),fill='#314442',width=1)
    d.text((43,757),'Taylor–Green flow advects the threads.',font=f,fill='#afc6bc')
    d.text((43,786),'Shape change is prescribed, not caused by viscosity.',font=small,fill='#9eadab')
    if i in (0,106,177,287): im.save(f'frame-{i}.png')
    proc.stdin.write(im.tobytes())
    P=step(P,t,dt);seeds=step(seeds,t,dt)
proc.stdin.close()
assert proc.wait()==0
